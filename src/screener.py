"""
Stock screening for wheel strategy candidates
"""

from typing import List, Dict, Optional
import logging
import yfinance as yf
import pandas as pd
from src.options_chain import OptionsChain
from src.utils import load_config


class StockScreener:
    """
    Screen stocks for wheel strategy suitability.
    """

    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize screener.

        Args:
            config: Configuration dictionary (will load from file if not provided)
        """
        self.config = config or load_config()
        self.screening_criteria = self.config.get('screening', {})
        self.logger = logging.getLogger(__name__)

    def screen_ticker(self, ticker: str) -> Optional[Dict]:
        """
        Screen a single ticker against wheel strategy criteria.

        Args:
            ticker: Stock ticker symbol

        Returns:
            Dictionary with screening results or None if doesn't meet criteria
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info

            # Basic validation
            if not info:
                self.logger.warning(f"No data available for {ticker}")
                return None

            # Extract key metrics
            market_cap = info.get('marketCap', 0)
            price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
            avg_volume = info.get('averageVolume', 0)
            sector = info.get('sector', 'Unknown')
            industry = info.get('industry', 'Unknown')

            # Check basic criteria
            min_market_cap = self.screening_criteria.get('min_market_cap', 10_000_000_000)
            min_price = self.screening_criteria.get('min_price', 10.0)
            max_price = self.screening_criteria.get('max_price', 500.0)
            min_avg_volume = self.screening_criteria.get('min_avg_volume', 1_000_000)

            if market_cap < min_market_cap:
                self.logger.debug(f"{ticker}: Market cap too low ({market_cap})")
                return None

            if price < min_price or price > max_price:
                self.logger.debug(f"{ticker}: Price out of range ({price})")
                return None

            if avg_volume < min_avg_volume:
                self.logger.debug(f"{ticker}: Volume too low ({avg_volume})")
                return None

            # Check sector/industry exclusions
            excluded_sectors = self.screening_criteria.get('excluded_sectors', [])
            excluded_industries = self.screening_criteria.get('excluded_industries', [])

            if sector in excluded_sectors or industry in excluded_industries:
                self.logger.debug(f"{ticker}: Excluded sector/industry ({sector}/{industry})")
                return None

            # Check options availability and volume
            options_chain = OptionsChain(ticker)
            volume_stats = options_chain.get_options_volume_stats()

            min_options_volume = self.screening_criteria.get('min_options_volume', 500)
            min_open_interest = self.screening_criteria.get('min_open_interest', 1000)

            if volume_stats['avg_volume'] < min_options_volume:
                self.logger.debug(f"{ticker}: Options volume too low ({volume_stats['avg_volume']})")
                return None

            if volume_stats['total_open_interest'] < min_open_interest:
                self.logger.debug(f"{ticker}: Open interest too low ({volume_stats['total_open_interest']})")
                return None

            # Get IV if available
            expirations = options_chain.get_expiration_dates()
            iv = None
            if expirations:
                iv = options_chain.get_implied_volatility(expirations[0])

            # Compile results
            result = {
                'ticker': ticker,
                'price': price,
                'market_cap': market_cap,
                'avg_volume': avg_volume,
                'sector': sector,
                'industry': industry,
                'options_volume': volume_stats['avg_volume'],
                'open_interest': volume_stats['total_open_interest'],
                'implied_volatility': iv,
                'passes_screen': True
            }

            self.logger.info(f"{ticker}: Passed screening")
            return result

        except Exception as e:
            self.logger.error(f"Error screening {ticker}: {e}")
            return None

    def screen_multiple_tickers(self, tickers: List[str]) -> pd.DataFrame:
        """
        Screen multiple tickers.

        Args:
            tickers: List of ticker symbols

        Returns:
            DataFrame with screening results
        """
        results = []

        for ticker in tickers:
            self.logger.info(f"Screening {ticker}...")
            result = self.screen_ticker(ticker)
            if result:
                results.append(result)

        if not results:
            return pd.DataFrame()

        df = pd.DataFrame(results)
        return df.sort_values('market_cap', ascending=False)

    def get_popular_wheel_tickers(self) -> List[str]:
        """
        Get a list of popular tickers commonly used for wheel strategy.

        Returns:
            List of ticker symbols
        """
        # Common large-cap stocks with active options markets
        popular_tickers = [
            # Tech
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'AMD', 'TSLA',
            # Finance
            'JPM', 'BAC', 'WFC', 'GS', 'MS',
            # Consumer
            'DIS', 'NKE', 'SBUX', 'MCD', 'HD', 'TGT', 'WMT',
            # Healthcare
            'JNJ', 'UNH', 'PFE', 'ABBV', 'TMO',
            # Industrial
            'BA', 'CAT', 'GE', 'MMM',
            # Energy
            'XOM', 'CVX', 'COP',
            # ETFs
            'SPY', 'QQQ', 'IWM', 'DIA'
        ]
        return popular_tickers

    def run_default_screen(self) -> pd.DataFrame:
        """
        Run screening on popular wheel strategy candidates.

        Returns:
            DataFrame with screening results
        """
        tickers = self.get_popular_wheel_tickers()
        self.logger.info(f"Screening {len(tickers)} popular tickers...")
        return self.screen_multiple_tickers(tickers)

    def screen_by_sector(self, sector: str, universe: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Screen stocks within a specific sector.

        Args:
            sector: Sector name
            universe: List of tickers to check (defaults to popular tickers)

        Returns:
            DataFrame with screening results for the sector
        """
        if universe is None:
            universe = self.get_popular_wheel_tickers()

        results = []
        for ticker in universe:
            result = self.screen_ticker(ticker)
            if result and result.get('sector') == sector:
                results.append(result)

        if not results:
            return pd.DataFrame()

        return pd.DataFrame(results).sort_values('market_cap', ascending=False)

    def rank_candidates(self, screened_df: pd.DataFrame) -> pd.DataFrame:
        """
        Rank screened candidates by attractiveness for wheel strategy.

        Args:
            screened_df: DataFrame from screening results

        Returns:
            DataFrame with ranking scores
        """
        if screened_df.empty:
            return screened_df

        df = screened_df.copy()

        # Initialize score
        df['wheel_score'] = 0

        # Score based on options liquidity (higher is better)
        if 'options_volume' in df.columns:
            max_vol = df['options_volume'].max()
            if max_vol > 0:
                df['wheel_score'] += (df['options_volume'] / max_vol) * 30

        # Score based on open interest (higher is better)
        if 'open_interest' in df.columns:
            max_oi = df['open_interest'].max()
            if max_oi > 0:
                df['wheel_score'] += (df['open_interest'] / max_oi) * 30

        # Score based on implied volatility (moderate is better)
        if 'implied_volatility' in df.columns:
            # Prefer IV between 0.25 and 0.50
            df['iv_score'] = df['implied_volatility'].apply(
                lambda x: 40 if pd.notna(x) and 0.25 <= x <= 0.50 else
                         30 if pd.notna(x) and 0.20 <= x <= 0.60 else
                         20 if pd.notna(x) else 0
            )
            df['wheel_score'] += df['iv_score']

        # Sort by score
        df = df.sort_values('wheel_score', ascending=False)

        return df

    def export_results(self, df: pd.DataFrame, filename: str = "wheel_candidates.csv") -> None:
        """
        Export screening results to file.

        Args:
            df: DataFrame with results
            filename: Output filename
        """
        try:
            df.to_csv(filename, index=False)
            self.logger.info(f"Results exported to {filename}")
        except Exception as e:
            self.logger.error(f"Error exporting results: {e}")
