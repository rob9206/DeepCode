"""
Core data models for the Slingshot stock scanner.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict


@dataclass
class CompressionData:
    """Technical compression indicators for a ticker."""
    ticker: str
    bb_squeeze: float  # 0-100, higher = tighter squeeze
    atr_compression: float  # 0-100, lower ATR = higher compression
    volume_dryup: float  # 0-100, lower volume = higher score
    price_range_compression: float  # 0-100, tighter range = higher score
    overall_compression_score: float  # Weighted average of above

    @property
    def is_compressed(self) -> bool:
        """Returns True if overall compression score > 70."""
        return self.overall_compression_score > 70


@dataclass
class SmartMoneyData:
    """Smart money activity indicators for a ticker."""
    ticker: str
    institutional_buying: float  # 0-100, based on 13F filings
    insider_buying: float  # 0-100, based on insider transactions
    options_flow: float  # 0-100, based on unusual options activity
    overall_smart_money_score: float  # Weighted average

    @property
    def is_accumulating(self) -> bool:
        """Returns True if smart money score > 60."""
        return self.overall_smart_money_score > 60


@dataclass
class ThemeData:
    """Theme and narrative data for a ticker."""
    ticker: str
    themes: List[str]  # e.g., ["AI", "Semiconductors", "Cloud"]
    narrative_score: float  # 0-100, based on news sentiment and theme strength
    theme_momentum: float  # 0-100, based on recent news volume and sentiment trend
    overall_theme_score: float  # Weighted average

    @property
    def is_trending(self) -> bool:
        """Returns True if theme score > 65."""
        return self.overall_theme_score > 65


@dataclass
class TickerScore:
    """Complete scoring data for a ticker (AI-FIRST architecture)."""
    ticker: str
    timestamp: datetime

    # AI-first: AI prediction is the primary signal (50% weight)
    ai_prediction: Optional['AIPredictionData'] = None  # From ai_prediction.py

    # Supporting signals
    smart_money: SmartMoneyData = None
    compression: CompressionData = None  # Now 20% weight (reduced from 40%)
    theme: ThemeData = None

    total_score: float = 0.0  # 0-100, AI-weighted combination

    @property
    def is_slingshot_candidate(self) -> bool:
        """
        Returns True if this ticker meets AI-first slingshot criteria:
        - AI predicts bullish (>65 score + UP direction)
        - Smart money accumulation (>60)
        - Optional: Technical confirmation (compression >70)
        """
        # AI-first logic: prioritize AI prediction
        if self.ai_prediction:
            ai_bullish = self.ai_prediction.is_ai_bullish
            smart_money_ok = self.smart_money.is_accumulating if self.smart_money else False

            return (
                ai_bullish and
                smart_money_ok and
                self.total_score > 70
            )

        # Fallback to old logic if AI not available
        if self.compression and self.smart_money and self.theme:
            return (
                self.compression.is_compressed and
                self.smart_money.is_accumulating and
                self.theme.is_trending and
                self.total_score > 70
            )

        return False

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        result = {
            'ticker': self.ticker,
            'timestamp': self.timestamp.isoformat(),
            'total_score': self.total_score,
            'is_slingshot_candidate': self.is_slingshot_candidate,
        }

        # Add AI prediction data if available
        if self.ai_prediction:
            result['ai_prediction'] = {
                'overall_score': self.ai_prediction.overall_ai_score,
                'news_sentiment': self.ai_prediction.news_sentiment,
                'social_sentiment': self.ai_prediction.social_sentiment,
                'price_prediction': self.ai_prediction.price_prediction,
                'price_direction': self.ai_prediction.price_direction,
                'confidence': self.ai_prediction.confidence,
                'recommendation': self.ai_prediction.recommendation
            }

        # Add traditional scores
        if self.smart_money:
            result['smart_money_score'] = self.smart_money.overall_smart_money_score
        if self.compression:
            result['compression_score'] = self.compression.overall_compression_score
        if self.theme:
            result['theme_score'] = self.theme.overall_theme_score
            result['themes'] = self.theme.themes

        return result


@dataclass
class MarketData:
    """Raw market data for a ticker."""
    ticker: str
    prices: List[float]
    volumes: List[int]
    dates: List[datetime]

    @property
    def latest_price(self) -> Optional[float]:
        """Returns the most recent price."""
        return self.prices[-1] if self.prices else None

    @property
    def latest_volume(self) -> Optional[int]:
        """Returns the most recent volume."""
        return self.volumes[-1] if self.volumes else None

    @property
    def avg_volume(self) -> Optional[float]:
        """Returns average volume over the period."""
        return sum(self.volumes) / len(self.volumes) if self.volumes else None


@dataclass
class NewsItem:
    """Individual news article."""
    ticker: str
    headline: str
    published: datetime
    source: str
    sentiment: float  # -1 to 1, negative to positive
    relevance: float  # 0 to 1, how relevant to the ticker
    themes: List[str]  # Extracted themes/topics


@dataclass
class ScanResult:
    """Results from a complete market scan."""
    timestamp: datetime
    tickers_scanned: List[str]
    scores: List[TickerScore]
    top_candidates: List[TickerScore]  # Sorted by total_score, descending

    def get_top_n(self, n: int = 10) -> List[TickerScore]:
        """Get top N candidates."""
        return self.top_candidates[:n]
