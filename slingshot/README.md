# Slingshot Stock Scanner

A Python-based stock scanner that identifies high-probability "slingshot" setups by combining:

1. **Technical Compression** - Stocks coiling like a spring (Bollinger Band squeeze, low ATR, volume dry-up)
2. **Smart Money Activity** - Institutional buying, insider purchases, unusual options flow
3. **Theme/Narrative Strength** - Strong sector themes with positive news momentum

## The Slingshot Pattern

A "slingshot" setup occurs when a stock shows:
- **Compression**: Price is consolidating with decreasing volatility (coiled spring)
- **Accumulation**: Smart money is quietly buying (institutions, insiders, options buyers)
- **Narrative**: Strong sector theme or catalyst building in the background

When all three align, the stock is "loaded" and ready to launch on its next catalyst.

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/slingshot.git
cd slingshot

# Install dependencies
pip install -r requirements.txt

# Or install as a package
pip install -e .
```

## Quick Start

### Scan Popular Stocks

```bash
# Scan top 10 most liquid stocks
python -m slingshot scan --top 10

# Scan top 50, show only slingshot candidates
python -m slingshot scan --top 50 --candidates-only
```

### Scan by Theme

```bash
# List available themes
python -m slingshot themes

# Scan AI theme
python -m slingshot scan --theme AI

# Scan Semiconductors theme
python -m slingshot scan --theme Semiconductors
```

### Deep Dive on a Ticker

```bash
# Get detailed analysis for NVDA
python -m slingshot ticker NVDA

# Save analysis to JSON
python -m slingshot ticker NVDA --output nvda_analysis.json
```

### Scan Specific Tickers

```bash
# Scan your watchlist
python -m slingshot scan --tickers NVDA,AMD,TSLA,AAPL
```

## Architecture

### Modules

- **`models.py`** - Data structures (TickerScore, CompressionData, etc.)
- **`compression.py`** - Technical compression analysis (BB squeeze, ATR, volume)
- **`smart_money.py`** - Smart money tracking (13F, insider, options flow)
- **`theme_manager.py`** - Theme baskets and narrative scoring
- **`data_fetcher.py`** - Market data via yfinance
- **`scoring_engine.py`** - Main orchestration and scoring
- **`__main__.py`** - CLI interface

### Scoring Methodology

Each ticker receives scores (0-100) across three dimensions:

1. **Compression Score** (40% weight)
   - Bollinger Band squeeze (35%)
   - ATR compression (30%)
   - Volume dry-up (20%)
   - Price range compression (15%)

2. **Smart Money Score** (35% weight)
   - Institutional buying from 13F filings (40%)
   - Insider buying from Form 4 (35%)
   - Unusual options flow (25%)

3. **Theme Score** (25% weight)
   - News sentiment and relevance (60%)
   - Theme momentum/trending (40%)

**Total Score** = Weighted combination of all three

**Slingshot Candidate** = Compression > 70 AND Smart Money > 60 AND Theme > 65 AND Total > 70

## Extending Slingshot

### Wire Up Real News API

The theme scoring currently uses stub data. To make it real, wire up a news API:

```python
# In theme_manager.py, update fetch_news()
import requests

def fetch_news(self, ticker: str, days: int = 7) -> List[NewsItem]:
    # Option 1: NewsAPI.org (100 req/day free)
    response = requests.get(
        'https://newsapi.org/v2/everything',
        params={
            'q': ticker,
            'apiKey': 'YOUR_API_KEY',
            'from': (datetime.now() - timedelta(days=days)).isoformat(),
            'sortBy': 'publishedAt'
        }
    )
    # Parse response and return NewsItem objects
```

### Wire Up Smart Money Data

Replace stub implementations in `smart_money.py`:

```python
# 13F Filings - Use SEC EDGAR or WhaleWisdom API
def get_institutional_buying_score(self, ticker: str) -> float:
    # Fetch recent 13F filings
    # Compare Q-over-Q institutional holdings
    # Return score based on net buying

# Insider Trades - Use SEC Form 4 or services like OpenInsider
def get_insider_buying_score(self, ticker: str) -> float:
    # Fetch Form 4 filings
    # Filter for open market purchases
    # Weight by insider role
    # Return score

# Options Flow - Use CBOE, Unusual Whales, or FlowAlgo
def get_options_flow_score(self, ticker: str) -> float:
    # Monitor large premium trades
    # Identify sweep orders
    # Return bullish/bearish score
```

## Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_compression.py

# Run with coverage
pytest --cov=slingshot tests/
```

## Configuration

Customize scoring weights programmatically:

```python
from slingshot import ScoringEngine

engine = ScoringEngine(
    compression_weight=0.50,  # Emphasize compression
    smart_money_weight=0.30,
    theme_weight=0.20
)

# Or update after initialization
engine.set_weights(compression=0.60, smart_money=0.25, theme=0.15)
```

## Themes

Built-in theme baskets:

- **AI** - NVDA, AMD, MSFT, GOOGL, META, PLTR, SNOW, etc.
- **Semiconductors** - NVDA, AMD, INTC, TSM, ASML, MU, etc.
- **Cloud** - MSFT, AMZN, GOOGL, SNOW, DDOG, NET, etc.
- **Cybersecurity** - CRWD, ZS, PANW, FTNT, OKTA, etc.
- **Electric Vehicles** - TSLA, RIVN, LCID, NIO, F, GM, etc.
- **Fintech** - SQ, PYPL, SHOP, COIN, SOFI, AFRM, etc.
- **Biotech** - MRNA, BNTX, REGN, VRTX, BIIB, GILD, etc.
- **Defense** - LMT, RTX, NOC, GD, BA, PLTR, etc.
- **Energy** - XOM, CVX, COP, SLB, EOG, etc.
- **Cannabis** - TLRY, CGC, SNDL, ACB, etc.

## Limitations

- **News/Smart Money Data**: Current implementation uses stubs. Wire up real APIs for production use.
- **Historical Data**: yfinance provides good coverage but may have gaps for some tickers.
- **Real-time**: Not designed for HFT or day trading - focuses on swing/position setups.
- **No Financial Advice**: This is a research tool, not investment advice.

## Roadmap

- [ ] Integrate real news API (NewsAPI.org or Polygon.io)
- [ ] Add 13F filing analysis (SEC EDGAR)
- [ ] Add insider transaction tracking (Form 4)
- [ ] Add options flow integration
- [ ] Web dashboard with charts
- [ ] Alerting system for new slingshot candidates
- [ ] Backtesting framework
- [ ] Portfolio tracking

## License

MIT License - see LICENSE file for details.

## Disclaimer

This software is for educational and research purposes only. It is not financial advice. Trading stocks involves risk of loss. Always do your own research and consult with a financial advisor before making investment decisions.
