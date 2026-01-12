"""
Main wheel strategy analyzer
"""

from typing import Dict, List, Optional, Tuple
import logging
import pandas as pd
from src.options_chain import OptionsChain
from src.calculator import ReturnCalculator
from src.screener import StockScreener
from src.utils import load_config, calculate_days_to_expiration


class WheelAnalyzer:
    """
    Main analyzer for wheel strategy opportunities.
    """

    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize analyzer.

        Args:
            config: Configuration dictionary (will load from file if not provided)
        """
        self.config = config or load_config()
        self.calculator = ReturnCalculator(
            risk_free_rate=self.config.get('returns', {}).get('risk_free_rate', 0.045)
        )
        self.screener = StockScreener(self.config)
        self.logger = logging.getLogger(__name__)

    def screen_stocks(
        self,
        tickers: Optional[List[str]] = None,
        min_market_cap: Optional[float] = None,
        min_iv_rank: Optional[float] = None,
        min_options_volume: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Screen stocks for wheel strategy suitability.

        Args:
            tickers: List of tickers to screen (uses popular list if not provided)
            min_market_cap: Minimum market cap filter
            min_iv_rank: Minimum IV rank filter
            min_options_volume: Minimum options volume filter

        Returns:
            DataFrame with screening results
        """
        # Update screening criteria if provided
        if min_market_cap:
            self.screener.screening_criteria['min_market_cap'] = min_market_cap
        if min_iv_rank:
            self.screener.screening_criteria['min_iv_rank'] = min_iv_rank
        if min_options_volume:
            self.screener.screening_criteria['min_options_volume'] = min_options_volume

        # Run screening
        if tickers:
            results = self.screener.screen_multiple_tickers(tickers)
        else:
            results = self.screener.run_default_screen()

        # Rank results
        if not results.empty:
            results = self.screener.rank_candidates(results)

        return results

    def analyze_ticker(self, ticker: str, target_dte: Optional[int] = None) -> 'TickerAnalysis':
        """
        Perform comprehensive analysis on a specific ticker.

        Args:
            ticker: Stock ticker symbol
            target_dte: Target days to expiration (uses config default if not provided)

        Returns:
            TickerAnalysis object with analysis results
        """
        if target_dte is None:
            target_dte = self.config.get('strategy', {}).get('put_selling', {}).get('preferred_dte', 30)

        return TickerAnalysis(ticker, self.config, self.calculator, target_dte)

    def compare_opportunities(
        self,
        tickers: List[str],
        strategy: str = 'put',
        target_dte: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Compare wheel strategy opportunities across multiple tickers.

        Args:
            tickers: List of ticker symbols
            strategy: 'put' or 'call'
            target_dte: Target days to expiration

        Returns:
            DataFrame comparing opportunities
        """
        results = []

        for ticker in tickers:
            try:
                analysis = self.analyze_ticker(ticker, target_dte)

                if strategy.lower() == 'put':
                    opportunities = analysis.get_put_opportunities()
                else:
                    opportunities = analysis.get_call_opportunities()

                if not opportunities.empty:
                    best = opportunities.iloc[0]
                    results.append({
                        'ticker': ticker,
                        'strike': best.get('strike'),
                        'premium': best.get('bid', 0),
                        'return_pct': best.get('return_pct', 0),
                        'annualized_return': best.get('annualized_return', 0),
                        'dte': best.get('dte', 0)
                    })
            except Exception as e:
                self.logger.error(f"Error analyzing {ticker}: {e}")
                continue

        if not results:
            return pd.DataFrame()

        df = pd.DataFrame(results)
        return df.sort_values('annualized_return', ascending=False)

    def find_best_wheel_candidates(
        self,
        min_annual_return: float = 20.0,
        max_results: int = 10
    ) -> pd.DataFrame:
        """
        Find the best wheel strategy candidates.

        Args:
            min_annual_return: Minimum annualized return target (%)
            max_results: Maximum number of results to return

        Returns:
            DataFrame with best candidates
        """
        # First screen stocks
        screened = self.screen_stocks()

        if screened.empty:
            self.logger.warning("No stocks passed screening")
            return pd.DataFrame()

        # Analyze top candidates
        top_tickers = screened.head(20)['ticker'].tolist()
        opportunities = self.compare_opportunities(top_tickers, strategy='put')

        if opportunities.empty:
            return pd.DataFrame()

        # Filter by minimum return
        filtered = opportunities[opportunities['annualized_return'] >= min_annual_return]

        return filtered.head(max_results)


class TickerAnalysis:
    """
    Detailed analysis for a specific ticker.
    """

    def __init__(
        self,
        ticker: str,
        config: Dict,
        calculator: ReturnCalculator,
        target_dte: int = 30
    ):
        """
        Initialize ticker analysis.

        Args:
            ticker: Stock ticker symbol
            config: Configuration dictionary
            calculator: ReturnCalculator instance
            target_dte: Target days to expiration
        """
        self.ticker = ticker
        self.config = config
        self.calculator = calculator
        self.target_dte = target_dte
        self.logger = logging.getLogger(__name__)

        self.options_chain = OptionsChain(ticker)
        self.current_price = self.options_chain.get_current_price()
        self.expiration_date = self.options_chain.find_nearest_expiration(target_dte)

    def get_put_opportunities(
        self,
        delta_range: Optional[Tuple[float, float]] = None,
        min_premium: Optional[float] = None
    ) -> pd.DataFrame:
        """
        Get cash-secured put selling opportunities.

        Args:
            delta_range: Tuple of (min_delta, max_delta)
            min_premium: Minimum premium per share

        Returns:
            DataFrame with put opportunities
        """
        if not self.expiration_date:
            self.logger.warning(f"No expiration dates available for {self.ticker}")
            return pd.DataFrame()

        # Get config defaults
        put_config = self.config.get('strategy', {}).get('put_selling', {})
        if delta_range is None:
            delta_range = (
                put_config.get('target_delta_min', 0.20),
                put_config.get('target_delta_max', 0.35)
            )
        if min_premium is None:
            min_premium = put_config.get('min_premium_pct', 1.0) * self.current_price / 100

        # Get puts
        _, puts = self.options_chain.get_options_chain(self.expiration_date)

        if puts.empty:
            return pd.DataFrame()

        # Calculate days to expiration
        from datetime import datetime
        exp_date = datetime.strptime(self.expiration_date, '%Y-%m-%d')
        dte = calculate_days_to_expiration(exp_date)

        # Enhance with return calculations
        results = []
        for _, row in puts.iterrows():
            strike = row['strike']
            premium = row.get('bid', row.get('lastPrice', 0))

            if premium < min_premium:
                continue

            # Filter for OTM puts (strike below current price)
            if strike >= self.current_price:
                continue

            # Calculate returns
            returns = self.calculator.calculate_put_return(
                self.current_price,
                strike,
                premium,
                dte
            )

            results.append({
                'strike': strike,
                'premium': premium,
                'bid': row.get('bid', 0),
                'ask': row.get('ask', 0),
                'volume': row.get('volume', 0),
                'open_interest': row.get('openInterest', 0),
                'implied_volatility': row.get('impliedVolatility', 0),
                'dte': dte,
                'return_pct': returns['return_pct'],
                'annualized_return': returns['annualized_return'],
                'breakeven': returns['breakeven_price'],
                'downside_protection': returns['downside_protection_pct']
            })

        if not results:
            return pd.DataFrame()

        df = pd.DataFrame(results)
        return df.sort_values('annualized_return', ascending=False)

    def get_call_opportunities(
        self,
        delta_range: Optional[Tuple[float, float]] = None,
        min_premium: Optional[float] = None,
        cost_basis: Optional[float] = None
    ) -> pd.DataFrame:
        """
        Get covered call selling opportunities.

        Args:
            delta_range: Tuple of (min_delta, max_delta)
            min_premium: Minimum premium per share
            cost_basis: Your cost basis (defaults to current price)

        Returns:
            DataFrame with call opportunities
        """
        if not self.expiration_date:
            self.logger.warning(f"No expiration dates available for {self.ticker}")
            return pd.DataFrame()

        if cost_basis is None:
            cost_basis = self.current_price

        # Get config defaults
        call_config = self.config.get('strategy', {}).get('covered_calls', {})
        if delta_range is None:
            delta_range = (
                call_config.get('target_delta_min', 0.20),
                call_config.get('target_delta_max', 0.35)
            )
        if min_premium is None:
            min_premium = call_config.get('min_premium_pct', 0.5) * self.current_price / 100

        # Get calls
        calls, _ = self.options_chain.get_options_chain(self.expiration_date)

        if calls.empty:
            return pd.DataFrame()

        # Calculate days to expiration
        from datetime import datetime
        exp_date = datetime.strptime(self.expiration_date, '%Y-%m-%d')
        dte = calculate_days_to_expiration(exp_date)

        # Enhance with return calculations
        results = []
        for _, row in calls.iterrows():
            strike = row['strike']
            premium = row.get('bid', row.get('lastPrice', 0))

            if premium < min_premium:
                continue

            # Filter for OTM calls (strike above current price)
            if strike <= self.current_price:
                continue

            # Calculate returns
            returns = self.calculator.calculate_call_return(
                self.current_price,
                strike,
                premium,
                cost_basis,
                dte
            )

            results.append({
                'strike': strike,
                'premium': premium,
                'bid': row.get('bid', 0),
                'ask': row.get('ask', 0),
                'volume': row.get('volume', 0),
                'open_interest': row.get('openInterest', 0),
                'implied_volatility': row.get('impliedVolatility', 0),
                'dte': dte,
                'premium_return_pct': returns['premium_return_pct'],
                'total_return_pct': returns['total_return_pct'],
                'annualized_return': returns['annualized_return'],
                'max_profit_price': returns['max_profit_price'],
                'upside_capture': returns['upside_capture_pct']
            })

        if not results:
            return pd.DataFrame()

        df = pd.DataFrame(results)
        return df.sort_values('annualized_return', ascending=False)

    def get_wheel_cycle_analysis(
        self,
        put_strike: Optional[float] = None,
        call_strike: Optional[float] = None
    ) -> Dict:
        """
        Analyze a complete wheel cycle.

        Args:
            put_strike: Put strike price (defaults to -5% from current)
            call_strike: Call strike price (defaults to +5% from current)

        Returns:
            Dictionary with cycle analysis
        """
        if put_strike is None:
            put_strike = self.current_price * 0.95

        if call_strike is None:
            call_strike = self.current_price * 1.05

        # Get put and call chains
        _, puts = self.options_chain.get_options_chain(self.expiration_date)
        calls, _ = self.options_chain.get_options_chain(self.expiration_date)

        if puts.empty or calls.empty:
            return {}

        # Find closest strikes
        put_option = puts.iloc[(puts['strike'] - put_strike).abs().argsort()[:1]]
        call_option = calls.iloc[(calls['strike'] - call_strike).abs().argsort()[:1]]

        if put_option.empty or call_option.empty:
            return {}

        # Get premiums
        put_premium = put_option.iloc[0].get('bid', 0)
        call_premium = call_option.iloc[0].get('bid', 0)
        actual_put_strike = put_option.iloc[0]['strike']
        actual_call_strike = call_option.iloc[0]['strike']

        # Calculate cycle returns
        from datetime import datetime
        exp_date = datetime.strptime(self.expiration_date, '%Y-%m-%d')
        dte = calculate_days_to_expiration(exp_date)

        cycle_returns = self.calculator.calculate_wheel_cycle_return(
            self.current_price,
            actual_put_strike,
            put_premium,
            actual_call_strike,
            call_premium,
            dte,
            dte,
            assignment_assumed=True
        )

        return cycle_returns
