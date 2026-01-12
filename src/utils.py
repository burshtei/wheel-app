"""
Utility functions for the Wheel Strategy Analyzer
"""

import os
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import yaml
import logging


def load_config(config_path: str = "config/settings.yaml") -> Dict[str, Any]:
    """
    Load configuration from YAML file.

    Args:
        config_path: Path to configuration file

    Returns:
        Dictionary containing configuration settings
    """
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        return config
    except FileNotFoundError:
        logging.warning(f"Config file not found at {config_path}, using defaults")
        return get_default_config()
    except Exception as e:
        logging.error(f"Error loading config: {e}")
        return get_default_config()


def get_default_config() -> Dict[str, Any]:
    """
    Get default configuration settings.

    Returns:
        Dictionary with default configuration
    """
    return {
        'screening': {
            'min_market_cap': 10_000_000_000,
            'min_price': 10.0,
            'max_price': 500.0,
            'min_avg_volume': 1_000_000,
            'min_options_volume': 500,
            'min_iv_rank': 25
        },
        'strategy': {
            'put_selling': {
                'target_delta_min': 0.20,
                'target_delta_max': 0.35,
                'min_premium_pct': 1.0,
                'preferred_dte': 30
            },
            'covered_calls': {
                'target_delta_min': 0.20,
                'target_delta_max': 0.35,
                'min_premium_pct': 0.5,
                'preferred_dte': 30
            }
        }
    }


def setup_logging(log_level: str = "INFO", log_dir: str = "logs") -> None:
    """
    Set up logging configuration.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_dir: Directory for log files
    """
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_file = os.path.join(log_dir, f"wheel_analyzer_{datetime.now().strftime('%Y%m%d')}.log")

    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )


def calculate_days_to_expiration(expiration_date: datetime) -> int:
    """
    Calculate days to expiration from today.

    Args:
        expiration_date: Option expiration date

    Returns:
        Number of days until expiration
    """
    if isinstance(expiration_date, str):
        expiration_date = datetime.strptime(expiration_date, '%Y-%m-%d')

    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    delta = expiration_date - today
    return max(0, delta.days)


def annualize_return(return_pct: float, days: int) -> float:
    """
    Annualize a return based on holding period.

    Args:
        return_pct: Return percentage (e.g., 2.5 for 2.5%)
        days: Number of days in holding period

    Returns:
        Annualized return percentage
    """
    if days <= 0:
        return 0.0

    # Use compound interest formula
    periods_per_year = 365.0 / days
    annualized = ((1 + return_pct / 100) ** periods_per_year - 1) * 100
    return annualized


def format_currency(amount: float, currency: str = "USD") -> str:
    """
    Format a number as currency.

    Args:
        amount: Amount to format
        currency: Currency symbol/code

    Returns:
        Formatted currency string
    """
    if currency == "USD":
        return f"${amount:,.2f}"
    return f"{amount:,.2f} {currency}"


def format_percentage(value: float, decimal_places: int = 2) -> str:
    """
    Format a number as percentage.

    Args:
        value: Value to format (e.g., 0.15 or 15 for 15%)
        decimal_places: Number of decimal places

    Returns:
        Formatted percentage string
    """
    # Assume if value > 1, it's already in percentage form
    if abs(value) > 1:
        return f"{value:.{decimal_places}f}%"
    return f"{value * 100:.{decimal_places}f}%"


def validate_ticker(ticker: str) -> str:
    """
    Validate and normalize ticker symbol.

    Args:
        ticker: Ticker symbol

    Returns:
        Normalized ticker symbol

    Raises:
        ValueError: If ticker is invalid
    """
    if not ticker:
        raise ValueError("Ticker cannot be empty")

    # Remove whitespace and convert to uppercase
    ticker = ticker.strip().upper()

    # Basic validation
    if not ticker.isalnum() and '.' not in ticker:
        raise ValueError(f"Invalid ticker format: {ticker}")

    return ticker


def get_next_monthly_expiration(base_date: Optional[datetime] = None) -> datetime:
    """
    Get the next monthly options expiration (3rd Friday of the month).

    Args:
        base_date: Starting date (defaults to today)

    Returns:
        Next monthly expiration date
    """
    if base_date is None:
        base_date = datetime.now()

    # Start with the first day of next month
    if base_date.month == 12:
        next_month = base_date.replace(year=base_date.year + 1, month=1, day=1)
    else:
        next_month = base_date.replace(month=base_date.month + 1, day=1)

    # Find the third Friday
    first_day_weekday = next_month.weekday()
    days_until_friday = (4 - first_day_weekday) % 7  # Friday is 4
    third_friday = next_month + timedelta(days=days_until_friday + 14)

    return third_friday


def calculate_iv_rank(current_iv: float, iv_history: list) -> float:
    """
    Calculate IV rank (where current IV stands in 52-week range).

    Args:
        current_iv: Current implied volatility
        iv_history: List of historical IV values

    Returns:
        IV rank as percentage (0-100)
    """
    if not iv_history or len(iv_history) < 2:
        return 50.0  # Default to middle if no history

    min_iv = min(iv_history)
    max_iv = max(iv_history)

    if max_iv == min_iv:
        return 50.0

    iv_rank = ((current_iv - min_iv) / (max_iv - min_iv)) * 100
    return max(0, min(100, iv_rank))
