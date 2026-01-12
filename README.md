# Wheel Strategy Stock Analyzer

A Python application for analyzing stocks suitable for the options wheel strategy - a popular income-generating options trading technique.

## 🚀 Quick Deploy to Cloud (FREE!)

Deploy this app to the cloud in 2 minutes - **completely FREE**!

**Easiest Option - Render.com:**
1. Fork this repo or push to your GitHub
2. Go to [render.com](https://render.com) (sign up free, no credit card)
3. Click "New +" → "Blueprint" → Select this repo
4. Done! Your API is live with automatic HTTPS

**Other free options:** Fly.io, Railway.app

📖 **[Full FREE Deployment Guide →](FREE-DEPLOYMENT.md)**

## What is the Wheel Strategy?

The wheel strategy is a systematic options trading approach that combines cash-secured puts and covered calls to generate consistent income:

1. **Sell Cash-Secured Puts**: Sell put options on quality stocks you'd like to own at a discount
2. **Assignment (Optional)**: If the stock drops below the strike price, you're assigned shares
3. **Sell Covered Calls**: Once assigned, sell call options against your shares to generate additional income
4. **Repeat**: If called away, start over; if not, continue selling calls

The strategy works best with:
- High-quality, fundamentally strong stocks
- Stocks with good liquidity and options volume
- Stocks with high implied volatility (IV) for better premiums
- Stocks trading in a range or with slight upward bias

## Features

- **Stock Screening**: Identify stocks suitable for the wheel strategy based on:
  - Market capitalization and liquidity
  - Options volume and open interest
  - Implied volatility metrics
  - Financial health indicators

- **Options Analysis**: Analyze potential returns from:
  - Cash-secured put premiums
  - Covered call premiums
  - Annualized return calculations

- **Risk Assessment**: Evaluate:
  - Technical support/resistance levels
  - Historical volatility vs implied volatility
  - Downside risk metrics

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd wheel-app
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Stock Screening

```python
from src.analyzer import WheelAnalyzer

# Initialize analyzer
analyzer = WheelAnalyzer()

# Screen for wheel strategy candidates
candidates = analyzer.screen_stocks(
    min_market_cap=10_000_000_000,  # $10B minimum
    min_iv_rank=30,                  # IV rank > 30
    min_options_volume=1000          # Minimum daily options volume
)

# Display results
for stock in candidates:
    print(f"{stock.ticker}: Expected Annual Return: {stock.expected_return:.2%}")
```

### Analyze Specific Stock

```python
# Analyze a specific ticker
analysis = analyzer.analyze_ticker('AAPL')

# Get put selling opportunities
puts = analysis.get_put_opportunities(
    delta_range=(0.20, 0.35),  # Target delta range
    min_premium=1.00            # Minimum premium per contract
)

# Get covered call opportunities
calls = analysis.get_call_opportunities(
    delta_range=(0.20, 0.35),
    min_premium=0.50
)
```

## Configuration

Edit `config/settings.yaml` to customize:
- Screening criteria
- Risk parameters
- Data sources and API keys
- Default strategy parameters

## Project Structure

```
wheel-app/
├── src/
│   ├── __init__.py
│   ├── analyzer.py           # Main analysis engine
│   ├── screener.py           # Stock screening logic
│   ├── options_chain.py      # Options data fetching
│   ├── calculator.py         # Return calculations
│   └── utils.py              # Helper functions
├── config/
│   └── settings.yaml         # Configuration file
├── tests/
│   └── test_analyzer.py      # Unit tests
├── examples/
│   └── basic_screening.py    # Example usage
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## Requirements

- Python 3.8+
- Internet connection for fetching market data
- Optional: API keys for premium data providers

## Data Sources

This app can use various data sources:
- **yfinance**: Free Yahoo Finance data (default)
- **Alpha Vantage**: Free tier available with API key
- **IEX Cloud**: Paid service with more reliable data
- **Interactive Brokers**: Direct broker integration (advanced)

## Disclaimer

This tool is for educational and informational purposes only. Options trading involves significant risk of loss. Past performance does not guarantee future results. Always do your own research and consider consulting with a financial advisor before making investment decisions.

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
