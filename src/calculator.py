"""
Return calculations for wheel strategy options
"""

from typing import Dict, Tuple, Optional
import logging


class ReturnCalculator:
    """
    Calculator for analyzing returns from wheel strategy trades.
    """

    def __init__(self, risk_free_rate: float = 0.045):
        """
        Initialize calculator.

        Args:
            risk_free_rate: Annual risk-free rate (default 4.5%)
        """
        self.risk_free_rate = risk_free_rate
        self.logger = logging.getLogger(__name__)

    def calculate_put_return(
        self,
        stock_price: float,
        strike_price: float,
        premium: float,
        days_to_expiration: int,
        contract_size: int = 100
    ) -> Dict[str, float]:
        """
        Calculate returns for selling a cash-secured put.

        Args:
            stock_price: Current stock price
            strike_price: Put strike price
            premium: Premium received per share
            days_to_expiration: Days until expiration
            contract_size: Shares per contract (default 100)

        Returns:
            Dictionary with return metrics
        """
        # Capital required (cash secured)
        capital_required = strike_price * contract_size

        # Total premium received
        total_premium = premium * contract_size

        # Return on capital
        return_pct = (total_premium / capital_required) * 100

        # Annualized return
        if days_to_expiration > 0:
            periods_per_year = 365.0 / days_to_expiration
            annualized_return = ((1 + return_pct / 100) ** periods_per_year - 1) * 100
        else:
            annualized_return = 0.0

        # Break-even price
        breakeven = strike_price - premium

        # Downside protection
        downside_protection_pct = (premium / stock_price) * 100

        return {
            'capital_required': capital_required,
            'premium_received': total_premium,
            'return_pct': return_pct,
            'annualized_return': annualized_return,
            'breakeven_price': breakeven,
            'downside_protection_pct': downside_protection_pct,
            'days_to_expiration': days_to_expiration
        }

    def calculate_call_return(
        self,
        stock_price: float,
        strike_price: float,
        premium: float,
        cost_basis: float,
        days_to_expiration: int,
        contract_size: int = 100
    ) -> Dict[str, float]:
        """
        Calculate returns for selling a covered call.

        Args:
            stock_price: Current stock price
            strike_price: Call strike price
            premium: Premium received per share
            cost_basis: Your cost basis in the stock
            days_to_expiration: Days until expiration
            contract_size: Shares per contract (default 100)

        Returns:
            Dictionary with return metrics
        """
        # Capital at risk (stock value at cost basis)
        capital_invested = cost_basis * contract_size

        # Total premium received
        total_premium = premium * contract_size

        # Return on capital from premium only
        premium_return_pct = (total_premium / capital_invested) * 100

        # Potential capital gain if called away
        if strike_price > cost_basis:
            capital_gain = (strike_price - cost_basis) * contract_size
            total_return = total_premium + capital_gain
        else:
            capital_gain = 0
            total_return = total_premium

        total_return_pct = (total_return / capital_invested) * 100

        # Annualized returns
        if days_to_expiration > 0:
            periods_per_year = 365.0 / days_to_expiration
            annualized_return = ((1 + total_return_pct / 100) ** periods_per_year - 1) * 100
        else:
            annualized_return = 0.0

        # Upside capture
        max_profit_price = strike_price + premium
        upside_capture_pct = ((max_profit_price - stock_price) / stock_price) * 100

        return {
            'capital_invested': capital_invested,
            'premium_received': total_premium,
            'potential_capital_gain': capital_gain,
            'total_return': total_return,
            'premium_return_pct': premium_return_pct,
            'total_return_pct': total_return_pct,
            'annualized_return': annualized_return,
            'upside_capture_pct': upside_capture_pct,
            'max_profit_price': max_profit_price,
            'days_to_expiration': days_to_expiration
        }

    def calculate_wheel_cycle_return(
        self,
        stock_price: float,
        put_strike: float,
        put_premium: float,
        call_strike: float,
        call_premium: float,
        put_dte: int,
        call_dte: int,
        assignment_assumed: bool = True
    ) -> Dict[str, float]:
        """
        Calculate expected return for a complete wheel cycle.

        Args:
            stock_price: Current stock price
            put_strike: Put option strike price
            put_premium: Premium for put option
            call_strike: Call option strike price
            call_premium: Premium for call option
            put_dte: Days to expiration for put
            call_dte: Days to expiration for call
            assignment_assumed: Whether to assume assignment occurs

        Returns:
            Dictionary with cycle return metrics
        """
        # Phase 1: Put selling
        put_returns = self.calculate_put_return(
            stock_price, put_strike, put_premium, put_dte
        )

        if assignment_assumed:
            # Phase 2: Covered call after assignment
            # Cost basis is strike price minus premium received
            cost_basis = put_strike - put_premium

            call_returns = self.calculate_call_return(
                put_strike,  # Stock price at assignment
                call_strike,
                call_premium,
                cost_basis,
                call_dte
            )

            # Total cycle metrics
            total_premium = put_returns['premium_received'] + call_returns['premium_received']
            total_days = put_dte + call_dte
            capital_required = put_strike * 100

            total_return_pct = (total_premium / capital_required) * 100

            if total_days > 0:
                periods_per_year = 365.0 / total_days
                annualized_cycle_return = ((1 + total_return_pct / 100) ** periods_per_year - 1) * 100
            else:
                annualized_cycle_return = 0.0

            return {
                'put_phase': put_returns,
                'call_phase': call_returns,
                'total_premium': total_premium,
                'total_return_pct': total_return_pct,
                'annualized_cycle_return': annualized_cycle_return,
                'total_days': total_days,
                'capital_required': capital_required
            }
        else:
            # Only put selling phase
            return {
                'put_phase': put_returns,
                'call_phase': None,
                'total_premium': put_returns['premium_received'],
                'total_return_pct': put_returns['return_pct'],
                'annualized_cycle_return': put_returns['annualized_return'],
                'total_days': put_dte,
                'capital_required': put_returns['capital_required']
            }

    def calculate_sharpe_ratio(
        self,
        annualized_return: float,
        annualized_volatility: float
    ) -> float:
        """
        Calculate Sharpe ratio for a strategy.

        Args:
            annualized_return: Expected annualized return (%)
            annualized_volatility: Annualized volatility (%)

        Returns:
            Sharpe ratio
        """
        if annualized_volatility == 0:
            return 0.0

        excess_return = annualized_return - (self.risk_free_rate * 100)
        sharpe = excess_return / annualized_volatility
        return sharpe

    def calculate_probability_of_profit(
        self,
        stock_price: float,
        breakeven_price: float,
        implied_volatility: float,
        days_to_expiration: int
    ) -> float:
        """
        Estimate probability of profit using simple normal distribution.

        Args:
            stock_price: Current stock price
            breakeven_price: Breakeven price for the trade
            implied_volatility: Implied volatility (annual)
            days_to_expiration: Days to expiration

        Returns:
            Probability of profit (0-1)
        """
        import math
        from scipy.stats import norm

        if days_to_expiration <= 0:
            return 1.0 if stock_price >= breakeven_price else 0.0

        # Adjust IV for time period
        time_fraction = days_to_expiration / 365.0
        expected_move = stock_price * implied_volatility * math.sqrt(time_fraction)

        # Z-score
        z_score = (stock_price - breakeven_price) / expected_move if expected_move > 0 else 0

        # Probability using normal distribution
        probability = norm.cdf(z_score)

        return probability

    def calculate_expected_value(
        self,
        premium: float,
        max_loss: float,
        probability_of_profit: float,
        contract_size: int = 100
    ) -> float:
        """
        Calculate expected value of a trade.

        Args:
            premium: Premium received per share
            max_loss: Maximum loss per share
            probability_of_profit: Probability of profit (0-1)
            contract_size: Shares per contract

        Returns:
            Expected value in dollars
        """
        total_premium = premium * contract_size
        total_max_loss = max_loss * contract_size

        expected_value = (
            probability_of_profit * total_premium -
            (1 - probability_of_profit) * total_max_loss
        )

        return expected_value
