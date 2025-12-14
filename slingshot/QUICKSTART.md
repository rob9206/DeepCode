# Slingshot Stock Scanner - Quick Start Guide

## 🚀 Three Ways to Use Slingshot

### Option 1: Web UI (Easiest!)

The web interface is the easiest way to use Slingshot - no command line needed!

**Windows:**
```powershell
cd slingshot
pip install -r requirements.txt
python webapp.py
```

**Mac/Linux:**
```bash
cd slingshot
pip install -r requirements.txt
python webapp.py
```

Then open your browser to: **http://localhost:5000**

---

### Option 2: Command Line Interface (CLI)

For power users who want scriptable commands:

```bash
# List all themes
python -m slingshot themes

# Scan top 10 stocks
python -m slingshot scan --top 10

# Scan AI theme
python -m slingshot scan --theme AI

# Deep dive on NVDA
python -m slingshot ticker NVDA

# Get help
python -m slingshot --help
```

---

### Option 3: Python API

Use Slingshot in your own Python scripts:

```python
from slingshot import ScoringEngine

# Initialize
engine = ScoringEngine()

# Scan top stocks
result = engine.scan_popular(limit=10)

# Get slingshot candidates
for candidate in result.top_candidates:
    print(f"{candidate.ticker}: {candidate.total_score:.1f}/100")

# Deep dive on a ticker
analysis = engine.deep_dive('NVDA')
print(analysis)
```

---

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- Internet connection (for market data)

### Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `yfinance` - Market data
- `pandas` - Data processing
- `numpy` - Numerical computing
- `flask` - Web UI (optional)
- `pytest` - Testing (optional)

---

## 🎯 What is Slingshot?

Slingshot identifies high-probability stock setups by combining three factors:

1. **🔧 Compression** (40% weight)
   - Bollinger Band squeeze
   - ATR compression
   - Volume dry-up
   - Price range compression

2. **💰 Smart Money** (35% weight)
   - Institutional buying (13F filings)
   - Insider transactions
   - Unusual options flow

3. **📰 Theme/Narrative** (25% weight)
   - Sector theme strength
   - News sentiment
   - Theme momentum

When all three align, the stock is "loaded" like a slingshot ready to launch! 🚀

---

## 🌐 Web UI Features

### Home Page
- Overview of Slingshot methodology
- Quick links to scan and themes

### Scan Stocks
- **Top Stocks**: Scan most liquid stocks
- **Theme Scan**: Scan entire sectors (AI, Semiconductors, etc.)
- **Custom Tickers**: Scan your watchlist

### Browse Themes
- 10 pre-built theme baskets
- View all tickers in each theme
- One-click theme scanning

### Deep Dive
- Detailed breakdown of all scores
- Recent news with sentiment
- Interpretation and trading signals

---

## 📊 CLI Examples

**Scan and save to JSON:**
```bash
python -m slingshot scan --top 20 --output results.json
```

**Show only slingshot candidates:**
```bash
python -m slingshot scan --top 50 --candidates-only
```

**Scan specific tickers:**
```bash
python -m slingshot scan --tickers NVDA,AMD,MSFT,GOOGL
```

**Deep dive with JSON output:**
```bash
python -m slingshot ticker NVDA --json
```

---

## 🔧 Troubleshooting

**"No module named slingshot"**
- Make sure you're in the `slingshot` folder
- Check: `pwd` (Mac/Linux) or `cd` (Windows)

**"yfinance is not installed"**
- Run: `pip install yfinance pandas numpy`

**Web UI not starting**
- Install Flask: `pip install flask`
- Check port 5000 isn't in use

**Network errors when scanning**
- yfinance requires internet connection
- Some networks block Yahoo Finance
- Try a different network or VPN

---

## 📚 Documentation

- **README.md** - Full documentation
- **INSTALL_WINDOWS.md** - Detailed Windows setup
- **Code Review Report** - Quality assessment

---

## 🎓 Next Steps

### For Traders
1. Start with web UI: `python webapp.py`
2. Scan top 10 stocks
3. Review slingshot candidates
4. Deep dive on interesting tickers

### For Developers
1. Explore the CLI: `python -m slingshot --help`
2. Read the code in `slingshot/` folder
3. Run tests: `pytest tests/`
4. Wire up production APIs (see README.md)

### Production Deployment
The scanner currently uses stub data for smart money and news.
To make it production-ready:

1. **News API**: Wire up NewsAPI.org or Polygon.io
   - Edit `theme_manager.py:fetch_news()`

2. **Smart Money**: Add 13F, insider, options data
   - Edit `smart_money.py` functions

3. **See README.md** for detailed API integration guide

---

## 💡 Tips

- **Start small**: Scan top 5-10 stocks first
- **Use themes**: Pre-filtered lists reduce noise
- **Deep dive**: Always analyze before trading
- **Monitor**: Re-scan daily for changing setups
- **Combine**: Use with your own technical analysis

---

## 🆘 Get Help

- Run: `python -m slingshot --help`
- Read: `README.md`
- Check: GitHub issues

---

**Ready to find your next slingshot setup? Let's go! 🎯🚀**
