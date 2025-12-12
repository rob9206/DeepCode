"""
Theme and narrative tracking module.

Manages theme baskets and tracks narrative strength through news sentiment.
"""
from typing import List, Dict, Set
from datetime import datetime, timedelta
import random

from .models import ThemeData, NewsItem


class ThemeManager:
    """
    Manages investment themes and tracks narrative strength.

    Themes are categories/sectors with strong narratives that can drive
    stock prices (AI, Semiconductors, EVs, etc.)
    """

    # Pre-defined theme baskets
    THEME_BASKETS = {
        'AI': {
            'NVDA', 'AMD', 'MSFT', 'GOOGL', 'META', 'AMZN',
            'PLTR', 'SNOW', 'AI', 'PATH', 'DDOG'
        },
        'Semiconductors': {
            'NVDA', 'AMD', 'INTC', 'TSM', 'ASML', 'QCOM',
            'AVGO', 'MU', 'AMAT', 'LRCX', 'KLAC'
        },
        'Cloud': {
            'MSFT', 'AMZN', 'GOOGL', 'SNOW', 'DDOG', 'NET',
            'CFLT', 'MDB', 'ESTC', 'ZS', 'CRWD'
        },
        'Cybersecurity': {
            'CRWD', 'ZS', 'PANW', 'FTNT', 'S', 'OKTA',
            'TENB', 'RPD', 'SAIL'
        },
        'Electric Vehicles': {
            'TSLA', 'RIVN', 'LCID', 'NIO', 'XPEV', 'LI',
            'F', 'GM', 'VWAGY'
        },
        'Fintech': {
            'SQ', 'PYPL', 'SHOP', 'COIN', 'HOOD', 'SOFI',
            'AFRM', 'NU', 'UPST'
        },
        'Biotech': {
            'MRNA', 'BNTX', 'REGN', 'VRTX', 'BIIB', 'GILD',
            'AMGN', 'ILMN', 'CRSP', 'EDIT'
        },
        'Defense': {
            'LMT', 'RTX', 'NOC', 'GD', 'BA', 'PLTR',
            'LDOS', 'HII', 'TXT'
        },
        'Energy': {
            'XOM', 'CVX', 'COP', 'SLB', 'EOG', 'PXD',
            'MPC', 'VLO', 'PSX'
        },
        'Cannabis': {
            'TLRY', 'CGC', 'SNDL', 'ACB', 'CRON', 'OGI'
        }
    }

    def __init__(self):
        self.cache: Dict[str, ThemeData] = {}
        self.news_cache: Dict[str, List[NewsItem]] = {}

    def get_ticker_themes(self, ticker: str) -> List[str]:
        """Get all themes associated with a ticker."""
        themes = []
        for theme_name, tickers in self.THEME_BASKETS.items():
            if ticker.upper() in tickers:
                themes.append(theme_name)
        return themes

    def get_theme_tickers(self, theme: str) -> Set[str]:
        """Get all tickers in a theme basket."""
        return self.THEME_BASKETS.get(theme, set())

    def fetch_news(self, ticker: str, days: int = 7) -> List[NewsItem]:
        """
        Fetch recent news for a ticker.

        Stub implementation - wire up real news API for production.

        APIs to consider:
        - NewsAPI.org: https://newsapi.org/ (100 req/day free)
        - Polygon.io: https://polygon.io/docs/stocks/get_v2_reference_news
        - Alpha Vantage: https://www.alphavantage.co/documentation/#news-sentiment
        - Benzinga: https://www.benzinga.com/apis/en/news-data.html
        """
        # Check cache
        if ticker in self.news_cache:
            return self.news_cache[ticker]

        # TODO: Replace with real news API call
        # Stub: Generate fake news items
        themes = self.get_ticker_themes(ticker)
        news_items = []

        for i in range(random.randint(3, 8)):
            news_items.append(NewsItem(
                ticker=ticker,
                headline=f"Fake news headline {i+1} for {ticker}",
                published=datetime.now() - timedelta(hours=random.randint(1, 168)),
                source=random.choice(['Reuters', 'Bloomberg', 'CNBC', 'WSJ']),
                sentiment=random.uniform(-0.5, 0.8),  # Slight positive bias
                relevance=random.uniform(0.5, 1.0),
                themes=random.sample(themes, min(len(themes), 2)) if themes else []
            ))

        self.news_cache[ticker] = news_items
        return news_items

    def calculate_narrative_score(self, news_items: List[NewsItem]) -> float:
        """
        Calculate narrative score from news sentiment (0-100).

        Higher score = more positive sentiment and higher relevance.
        """
        if not news_items:
            return 50.0

        # Weight by relevance and recency
        weighted_sentiment = 0
        total_weight = 0

        now = datetime.now()
        for item in news_items:
            # Recency weight (more recent = higher weight)
            age_hours = (now - item.published).total_seconds() / 3600
            recency_weight = max(0.1, 1.0 - (age_hours / 168))  # Decay over 1 week

            # Combined weight
            weight = item.relevance * recency_weight

            # Convert sentiment from [-1, 1] to [0, 1]
            normalized_sentiment = (item.sentiment + 1) / 2

            weighted_sentiment += normalized_sentiment * weight
            total_weight += weight

        if total_weight == 0:
            return 50.0

        # Convert to 0-100 scale
        score = (weighted_sentiment / total_weight) * 100

        return min(max(score, 0), 100)

    def calculate_theme_momentum(self, news_items: List[NewsItem]) -> float:
        """
        Calculate theme momentum from news volume and sentiment trend (0-100).

        Higher score = more news volume and improving sentiment.
        """
        if not news_items:
            return 50.0

        # Split into recent and older
        now = datetime.now()
        recent_cutoff = now - timedelta(days=2)

        recent_items = [n for n in news_items if n.published > recent_cutoff]
        older_items = [n for n in news_items if n.published <= recent_cutoff]

        # Volume score (more recent news = higher momentum)
        volume_score = min((len(recent_items) / max(len(news_items), 1)) * 100, 100)

        # Sentiment trend (improving sentiment = higher momentum)
        if recent_items and older_items:
            recent_sentiment = sum(n.sentiment for n in recent_items) / len(recent_items)
            older_sentiment = sum(n.sentiment for n in older_items) / len(older_items)

            # Convert to 0-100 scale (positive trend = high score)
            sentiment_delta = recent_sentiment - older_sentiment
            trend_score = 50 + (sentiment_delta * 50)  # -1 to 1 delta mapped to 0-100
        else:
            trend_score = 50.0

        # Combine volume and trend
        momentum = (volume_score * 0.6) + (trend_score * 0.4)

        return min(max(momentum, 0), 100)

    def analyze_theme(self,
                     ticker: str,
                     narrative_weight: float = 0.60,
                     momentum_weight: float = 0.40) -> ThemeData:
        """
        Analyze theme and narrative data for a ticker.

        Args:
            ticker: Stock ticker symbol
            narrative_weight: Weight for narrative score
            momentum_weight: Weight for theme momentum score

        Returns:
            ThemeData with theme and narrative metrics
        """
        # Check cache
        if ticker in self.cache:
            return self.cache[ticker]

        # Get themes
        themes = self.get_ticker_themes(ticker)

        # Fetch and analyze news
        news_items = self.fetch_news(ticker)
        narrative_score = self.calculate_narrative_score(news_items)
        momentum_score = self.calculate_theme_momentum(news_items)

        # Calculate overall theme score
        overall = (narrative_score * narrative_weight) + (momentum_score * momentum_weight)

        result = ThemeData(
            ticker=ticker,
            themes=themes,
            narrative_score=narrative_score,
            theme_momentum=momentum_score,
            overall_theme_score=overall
        )

        # Cache result
        self.cache[ticker] = result

        return result

    def get_theme_leaderboard(self, theme: str, scores: Dict[str, float]) -> List[tuple]:
        """
        Get top tickers in a theme by score.

        Args:
            theme: Theme name
            scores: Dict mapping ticker -> score

        Returns:
            List of (ticker, score) tuples, sorted by score descending
        """
        theme_tickers = self.get_theme_tickers(theme)
        theme_scores = [(t, scores[t]) for t in theme_tickers if t in scores]
        return sorted(theme_scores, key=lambda x: x[1], reverse=True)

    def list_themes(self) -> List[str]:
        """Get list of all available themes."""
        return sorted(self.THEME_BASKETS.keys())

    def get_theme_info(self, theme: str) -> Dict:
        """Get detailed info about a theme."""
        tickers = self.get_theme_tickers(theme)
        return {
            'name': theme,
            'ticker_count': len(tickers),
            'tickers': sorted(list(tickers))
        }
