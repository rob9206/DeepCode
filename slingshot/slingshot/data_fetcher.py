"""
Market data fetching module.

Fetches price, volume, and other market data using yfinance.
"""
try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False
    yf = None

from datetime import datetime, timedelta
from typing import Optional, List
import pandas as pd

from .models import MarketData


class DataFetcher:
    """
    Fetches market data for tickers.

    Uses yfinance for price/volume data. Can be extended with other
    data sources for news, fundamentals, etc.
    """

    def __init__(self, cache_duration_minutes: int = 15):
        self.cache = {}
        self.cache_duration = timedelta(minutes=cache_duration_minutes)
        self.cache_timestamps = {}

    def _is_cache_valid(self, ticker: str) -> bool:
        """Check if cached data is still valid."""
        if ticker not in self.cache:
            return False
        if ticker not in self.cache_timestamps:
            return False

        age = datetime.now() - self.cache_timestamps[ticker]
        return age < self.cache_duration

    def fetch_market_data(self,
                         ticker: str,
                         period: str = '6mo',
                         interval: str = '1d') -> Optional[MarketData]:
        """
        Fetch market data for a ticker.

        Args:
            ticker: Stock ticker symbol
            period: Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)

        Returns:
            MarketData object or None if fetch fails
        """
        if not YFINANCE_AVAILABLE:
            print("Warning: yfinance is not installed. Cannot fetch market data.")
            return None

        # Check cache
        if self._is_cache_valid(ticker):
            return self.cache[ticker]

        try:
            # Fetch data from yfinance
            stock = yf.Ticker(ticker)
            df = stock.history(period=period, interval=interval)

            if df.empty:
                return None

            # Extract data
            prices = df['Close'].tolist()
            volumes = df['Volume'].tolist()
            dates = [d.to_pydatetime() for d in df.index]

            market_data = MarketData(
                ticker=ticker,
                prices=prices,
                volumes=volumes,
                dates=dates
            )

            # Cache result
            self.cache[ticker] = market_data
            self.cache_timestamps[ticker] = datetime.now()

            return market_data

        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
            return None

    def fetch_batch(self,
                   tickers: List[str],
                   period: str = '6mo',
                   interval: str = '1d') -> dict:
        """
        Fetch market data for multiple tickers.

        Args:
            tickers: List of ticker symbols
            period: Data period
            interval: Data interval

        Returns:
            Dict mapping ticker -> MarketData (only successful fetches)
        """
        results = {}

        for ticker in tickers:
            data = self.fetch_market_data(ticker, period, interval)
            if data:
                results[ticker] = data

        return results

    def get_current_price(self, ticker: str) -> Optional[float]:
        """Get current/latest price for a ticker."""
        data = self.fetch_market_data(ticker, period='1d', interval='1m')
        if data and data.latest_price:
            return data.latest_price
        return None

    def get_ticker_info(self, ticker: str) -> dict:
        """
        Get ticker info/metadata.

        Returns company name, sector, industry, etc.
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            return {
                'ticker': ticker,
                'name': info.get('longName', ticker),
                'sector': info.get('sector', 'Unknown'),
                'industry': info.get('industry', 'Unknown'),
                'market_cap': info.get('marketCap', 0),
                'description': info.get('longBusinessSummary', '')
            }
        except Exception as e:
            print(f"Error fetching info for {ticker}: {e}")
            return {'ticker': ticker, 'name': ticker}

    def validate_ticker(self, ticker: str) -> bool:
        """Check if a ticker is valid and has data."""
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(period='5d')
            return not df.empty
        except:
            return False

    def get_popular_tickers(self) -> List[str]:
        """
        Get list of popular/liquid tickers for scanning.

        Returns a curated list of high-volume stocks across sectors.
        """
        return [
            # Tech/AI
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'AMD', 'TSLA',
            'NFLX', 'ADBE', 'CRM', 'ORCL', 'INTC', 'QCOM', 'AVGO',

            # Cloud/SaaS
            'SNOW', 'DDOG', 'NET', 'MDB', 'PLTR', 'CRWD', 'ZS', 'PANW',

            # Finance
            'JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'V', 'MA', 'PYPL', 'SQ',

            # Healthcare/Biotech
            'JNJ', 'UNH', 'PFE', 'ABBV', 'TMO', 'MRNA', 'GILD', 'REGN',

            # Consumer
            'WMT', 'HD', 'NKE', 'SBUX', 'MCD', 'DIS', 'COST',

            # Energy
            'XOM', 'CVX', 'COP', 'SLB',

            # Industrial
            'CAT', 'BA', 'GE', 'DE',

            # EV/Auto
            'F', 'GM', 'RIVN', 'LCID',

            # Semiconductor
            'TSM', 'ASML', 'MU', 'AMAT', 'LRCX',
        ]

    def get_sp500_tickers(self) -> List[str]:
        """
        Get S&P 500 ticker list.

        Stub implementation - for production, scrape from Wikipedia or use
        an API that provides index constituents.
        """
        # TODO: Implement real S&P 500 scraper
        # Can use: pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
        return self.get_popular_tickers()
