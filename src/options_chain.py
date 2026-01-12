"""
Options chain data fetching and processing
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import logging
import yfinance as yf
import pandas as pd


class OptionsChain:
    """
    Fetch and process options chain data for stocks.
    """

    def __init__(self, ticker: str):
        """
        Initialize options chain fetcher.

        Args:
            ticker: Stock ticker symbol
        """
        self.ticker = ticker.upper()
        self.stock = None
        self.logger = logging.getLogger(__name__)
        self._fetch_stock_data()

    def _fetch_stock_data(self) -> None:
        """Fetch stock data from yfinance."""
        try:
            self.stock = yf.Ticker(self.ticker)
        except Exception as e:
            self.logger.error(f"Error fetching stock data for {self.ticker}: {e}")
            raise

    def get_current_price(self) -> Optional[float]:
        """
        Get current stock price.

        Returns:
            Current stock price or None if unavailable
        """
        try:
            info = self.stock.info
            price = info.get('currentPrice') or info.get('regularMarketPrice')
            return float(price) if price else None
        except Exception as e:
            self.logger.error(f"Error fetching price for {self.ticker}: {e}")
            return None

    def get_expiration_dates(self) -> List[str]:
        """
        Get all available options expiration dates.

        Returns:
            List of expiration dates as strings
        """
        try:
            return list(self.stock.options)
        except Exception as e:
            self.logger.error(f"Error fetching expiration dates for {self.ticker}: {e}")
            return []

    def get_options_chain(self, expiration_date: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get options chain for a specific expiration date.

        Args:
            expiration_date: Expiration date string (YYYY-MM-DD)

        Returns:
            Tuple of (calls_df, puts_df)
        """
        try:
            opt_chain = self.stock.option_chain(expiration_date)
            return opt_chain.calls, opt_chain.puts
        except Exception as e:
            self.logger.error(f"Error fetching options chain for {self.ticker} on {expiration_date}: {e}")
            return pd.DataFrame(), pd.DataFrame()

    def find_options_by_delta(
        self,
        expiration_date: str,
        option_type: str,
        delta_min: float,
        delta_max: float
    ) -> pd.DataFrame:
        """
        Find options within a specific delta range.

        Args:
            expiration_date: Expiration date string
            option_type: 'call' or 'put'
            delta_min: Minimum delta (absolute value)
            delta_max: Maximum delta (absolute value)

        Returns:
            DataFrame with matching options
        """
        calls, puts = self.get_options_chain(expiration_date)

        if option_type.lower() == 'call':
            options_df = calls
        else:
            options_df = puts

        if options_df.empty:
            return pd.DataFrame()

        # Filter by delta if available
        # Note: yfinance doesn't always provide Greeks, so we'll approximate
        # or users should integrate with a service that provides Greeks
        if 'delta' in options_df.columns:
            mask = (abs(options_df['delta']) >= delta_min) & (abs(options_df['delta']) <= delta_max)
            return options_df[mask]
        else:
            self.logger.warning(f"Delta not available for {self.ticker}, returning all options")
            return options_df

    def find_options_by_premium(
        self,
        expiration_date: str,
        option_type: str,
        min_premium: float,
        stock_price: Optional[float] = None
    ) -> pd.DataFrame:
        """
        Find options with minimum premium.

        Args:
            expiration_date: Expiration date string
            option_type: 'call' or 'put'
            min_premium: Minimum premium per contract
            stock_price: Current stock price (optional, will fetch if not provided)

        Returns:
            DataFrame with matching options
        """
        calls, puts = self.get_options_chain(expiration_date)

        if option_type.lower() == 'call':
            options_df = calls
        else:
            options_df = puts

        if options_df.empty:
            return pd.DataFrame()

        # Use bid price for premium (conservative estimate)
        if 'bid' in options_df.columns:
            mask = options_df['bid'] >= min_premium
            return options_df[mask]
        elif 'lastPrice' in options_df.columns:
            mask = options_df['lastPrice'] >= min_premium
            return options_df[mask]
        else:
            return options_df

    def get_atm_strike(self, expiration_date: str) -> Optional[float]:
        """
        Get the at-the-money strike price.

        Args:
            expiration_date: Expiration date string

        Returns:
            ATM strike price or None
        """
        stock_price = self.get_current_price()
        if not stock_price:
            return None

        calls, _ = self.get_options_chain(expiration_date)
        if calls.empty:
            return None

        # Find strike closest to current price
        strikes = calls['strike'].values
        atm_strike = min(strikes, key=lambda x: abs(x - stock_price))
        return float(atm_strike)

    def get_options_volume_stats(self) -> Dict[str, float]:
        """
        Get aggregate options volume statistics.

        Returns:
            Dictionary with volume statistics
        """
        try:
            expirations = self.get_expiration_dates()
            if not expirations:
                return {'total_volume': 0, 'avg_volume': 0, 'total_open_interest': 0}

            total_volume = 0
            total_open_interest = 0
            count = 0

            # Check first few expirations
            for exp in expirations[:3]:
                calls, puts = self.get_options_chain(exp)

                for df in [calls, puts]:
                    if not df.empty:
                        if 'volume' in df.columns:
                            total_volume += df['volume'].sum()
                        if 'openInterest' in df.columns:
                            total_open_interest += df['openInterest'].sum()
                        count += 1

            avg_volume = total_volume / count if count > 0 else 0

            return {
                'total_volume': total_volume,
                'avg_volume': avg_volume,
                'total_open_interest': total_open_interest
            }
        except Exception as e:
            self.logger.error(f"Error calculating volume stats for {self.ticker}: {e}")
            return {'total_volume': 0, 'avg_volume': 0, 'total_open_interest': 0}

    def get_implied_volatility(self, expiration_date: str) -> Optional[float]:
        """
        Get average implied volatility for an expiration.

        Args:
            expiration_date: Expiration date string

        Returns:
            Average IV or None
        """
        try:
            calls, puts = self.get_options_chain(expiration_date)

            ivs = []
            for df in [calls, puts]:
                if not df.empty and 'impliedVolatility' in df.columns:
                    ivs.extend(df['impliedVolatility'].dropna().tolist())

            if ivs:
                return sum(ivs) / len(ivs)
            return None
        except Exception as e:
            self.logger.error(f"Error calculating IV for {self.ticker}: {e}")
            return None

    def find_nearest_expiration(self, target_dte: int) -> Optional[str]:
        """
        Find expiration date nearest to target days to expiration.

        Args:
            target_dte: Target days to expiration

        Returns:
            Expiration date string or None
        """
        expirations = self.get_expiration_dates()
        if not expirations:
            return None

        target_date = datetime.now() + timedelta(days=target_dte)

        # Find closest expiration
        closest_exp = min(
            expirations,
            key=lambda x: abs((datetime.strptime(x, '%Y-%m-%d') - target_date).days)
        )

        return closest_exp

    def get_option_greeks_approximation(
        self,
        option_type: str,
        strike: float,
        expiration_date: str,
        stock_price: Optional[float] = None
    ) -> Dict[str, float]:
        """
        Get approximate option Greeks.
        Note: This is a simplified approximation. For accurate Greeks,
        use a proper options pricing library or data provider.

        Args:
            option_type: 'call' or 'put'
            strike: Strike price
            expiration_date: Expiration date
            stock_price: Current stock price

        Returns:
            Dictionary with approximate Greeks
        """
        if stock_price is None:
            stock_price = self.get_current_price()

        if not stock_price:
            return {}

        # Simple delta approximation
        moneyness = stock_price / strike

        if option_type.lower() == 'call':
            # Rough delta estimate for calls
            if moneyness > 1.1:
                delta = 0.75
            elif moneyness > 1.0:
                delta = 0.50
            elif moneyness > 0.95:
                delta = 0.30
            else:
                delta = 0.15
        else:
            # Rough delta estimate for puts
            if moneyness < 0.9:
                delta = -0.75
            elif moneyness < 1.0:
                delta = -0.50
            elif moneyness < 1.05:
                delta = -0.30
            else:
                delta = -0.15

        return {
            'delta': delta,
            'gamma': 0.05,  # Placeholder
            'theta': -0.02,  # Placeholder
            'vega': 0.10     # Placeholder
        }
