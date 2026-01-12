"""
Unit tests for wheel strategy analyzer
"""

import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.calculator import ReturnCalculator
from src.utils import (
    annualize_return,
    calculate_days_to_expiration,
    calculate_iv_rank,
    validate_ticker,
    format_percentage
)


class TestReturnCalculator:
    """Test return calculation functions."""

    def test_put_return_calculation(self):
        """Test cash-secured put return calculation."""
        calculator = ReturnCalculator()

        result = calculator.calculate_put_return(
            stock_price=100.0,
            strike_price=95.0,
            premium=2.0,
            days_to_expiration=30
        )

        assert result['capital_required'] == 9500.0  # 95 * 100
        assert result['premium_received'] == 200.0   # 2 * 100
        assert result['breakeven_price'] == 93.0     # 95 - 2
        assert result['return_pct'] > 0

    def test_call_return_calculation(self):
        """Test covered call return calculation."""
        calculator = ReturnCalculator()

        result = calculator.calculate_call_return(
            stock_price=100.0,
            strike_price=105.0,
            premium=1.5,
            cost_basis=98.0,
            days_to_expiration=30
        )

        assert result['premium_received'] == 150.0   # 1.5 * 100
        assert result['capital_invested'] == 9800.0  # 98 * 100
        assert result['potential_capital_gain'] == 700.0  # (105 - 98) * 100
        assert result['total_return'] > 0

    def test_wheel_cycle_return(self):
        """Test complete wheel cycle calculation."""
        calculator = ReturnCalculator()

        result = calculator.calculate_wheel_cycle_return(
            stock_price=100.0,
            put_strike=95.0,
            put_premium=2.0,
            call_strike=100.0,
            call_premium=1.5,
            put_dte=30,
            call_dte=30,
            assignment_assumed=True
        )

        assert 'put_phase' in result
        assert 'call_phase' in result
        assert 'total_premium' in result
        assert result['total_premium'] == 350.0  # (2.0 + 1.5) * 100

    def test_sharpe_ratio(self):
        """Test Sharpe ratio calculation."""
        calculator = ReturnCalculator()

        sharpe = calculator.calculate_sharpe_ratio(
            annualized_return=20.0,
            annualized_volatility=15.0
        )

        assert sharpe > 0
        assert isinstance(sharpe, float)


class TestUtilityFunctions:
    """Test utility functions."""

    def test_annualize_return(self):
        """Test return annualization."""
        # 2% return in 30 days
        annualized = annualize_return(2.0, 30)
        assert annualized > 2.0  # Should be significantly higher
        assert annualized > 20.0  # Rough check for 12x compounding

    def test_calculate_iv_rank(self):
        """Test IV rank calculation."""
        iv_history = [0.20, 0.25, 0.30, 0.35, 0.40]
        current_iv = 0.30

        iv_rank = calculate_iv_rank(current_iv, iv_history)

        assert 0 <= iv_rank <= 100
        assert iv_rank == 50.0  # 0.30 is exactly in the middle

    def test_validate_ticker(self):
        """Test ticker validation."""
        assert validate_ticker('aapl') == 'AAPL'
        assert validate_ticker('  MSFT  ') == 'MSFT'
        assert validate_ticker('BRK.B') == 'BRK.B'

        with pytest.raises(ValueError):
            validate_ticker('')

    def test_format_percentage(self):
        """Test percentage formatting."""
        assert '15.00%' in format_percentage(15.0)
        assert '15.00%' in format_percentage(0.15)
        assert '2.50%' in format_percentage(2.5)


class TestConfigLoading:
    """Test configuration loading."""

    def test_default_config(self):
        """Test default configuration values."""
        from src.utils import get_default_config

        config = get_default_config()

        assert 'screening' in config
        assert 'strategy' in config
        assert config['screening']['min_market_cap'] == 10_000_000_000


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
