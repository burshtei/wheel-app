# Wheel Strategy Stock Analyzer

A Python application for analyzing stocks suitable for the options wheel strategy - a popular income-generating options trading technique.

## 🚀 Deploy FREE in 5 Minutes

**[👉 Click here for FREE deployment guide](DEPLOY_FREE.md)**

Deploy to Render.com's free tier - no credit card required!
- 🌐 Live REST API with public URL
- 📚 Interactive API documentation
- 🔒 Free SSL certificate
- 750+ hours/month free

[Deploy Now →](DEPLOY_FREE.md)

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

## 🚀 Quick Start

### Option 1: REST API (Recommended for Cloud)

Deploy the REST API to any cloud platform:

```bash
# Local with Docker
docker-compose up -d

# Access API at http://localhost:8000
# API docs at http://localhost:8000/docs
```

**Deploy to cloud in minutes:**
- ☁️ [Render.com](https://render.com) (Free tier available)
- 🚂 [Railway](https://railway.app) ($5 free credits)
- 🌐 [Google Cloud Run](https://cloud.google.com/run) (2M requests free)

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

### Option 2: Python Package

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

### REST API Usage

The API provides REST endpoints for all functionality:

```bash
# Health check
curl http://localhost:8000/health

# Get popular tickers
curl http://localhost:8000/api/v1/popular-tickers

# Analyze a specific ticker
curl http://localhost:8000/api/v1/analyze/AAPL?target_dte=30

# Screen stocks
curl -X POST http://localhost:8000/api/v1/screen \
  -H "Content-Type: application/json" \
  -d '{"min_market_cap": 10000000000}'

# Find best candidates
curl http://localhost:8000/api/v1/candidates?min_annual_return=20
```

**Interactive API Documentation:**
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

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
│   ├── api.py                # FastAPI REST API
│   ├── analyzer.py           # Main analysis engine
│   ├── screener.py           # Stock screening logic
│   ├── options_chain.py      # Options data fetching
│   ├── calculator.py         # Return calculations
│   └── utils.py              # Helper functions
├── config/
│   └── settings.yaml         # Configuration file
├── deployment/
│   ├── deploy.sh             # Deployment script
│   ├── aws/                  # AWS ECS configs
│   ├── gcp/                  # Google Cloud Run configs
│   ├── render/               # Render.com configs
│   └── railway/              # Railway configs
├── tests/
│   └── test_analyzer.py      # Unit tests
├── examples/
│   └── basic_screening.py    # Example usage
├── Dockerfile                # Container definition
├── docker-compose.yml        # Docker Compose config
├── requirements.txt          # Python dependencies
├── README.md                 # This file
└── DEPLOYMENT.md             # Deployment guide
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
