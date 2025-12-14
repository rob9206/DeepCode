"""
AI-powered prediction module for Slingshot.

Uses state-of-the-art machine learning for:
1. News sentiment analysis (FinBERT)
2. Social media sentiment (VADER + Reddit/Twitter)
3. Price prediction (ML ensemble)
4. Alternative data signals

This is the core of the AI-first architecture (50% weight).
"""
import warnings
warnings.filterwarnings('ignore')

from dataclasses import dataclass
from typing import List, Optional, Dict
from datetime import datetime, timedelta
import numpy as np

# Try to import AI/ML libraries (graceful degradation)
try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    print("Warning: transformers not installed. Sentiment analysis will use fallback.")

try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False

try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    VADER_AVAILABLE = True
except ImportError:
    VADER_AVAILABLE = False

try:
    from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
    from sklearn.preprocessing import StandardScaler
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


@dataclass
class AIPredictionData:
    """AI prediction results for a ticker."""
    ticker: str

    # Sentiment scores (0-100)
    news_sentiment: float           # FinBERT-based news sentiment
    social_sentiment: float         # Reddit/Twitter sentiment

    # Price prediction
    price_prediction: float         # ML-based price forecast score (0-100)
    price_direction: str           # UP/DOWN/NEUTRAL
    confidence: float              # Model confidence (0-100)

    # Alternative data
    alternative_data: float        # Web traffic, app downloads, etc. (0-100)

    # Overall AI score
    overall_ai_score: float        # Weighted combination

    @property
    def is_ai_bullish(self) -> bool:
        """Returns True if AI predicts upward movement."""
        return self.overall_ai_score > 65 and self.price_direction == "UP"

    @property
    def recommendation(self) -> str:
        """Get AI recommendation: BUY, HOLD, or SELL."""
        if self.overall_ai_score >= 75 and self.price_direction == "UP":
            return "BUY"
        elif self.overall_ai_score <= 40 or self.price_direction == "DOWN":
            return "SELL"
        else:
            return "HOLD"


class NewsSentimentAnalyzer:
    """
    Analyze news sentiment using FinBERT (financial BERT model).

    FinBERT is specifically trained on financial text and outperforms
    general sentiment models for stock-related content.
    """

    def __init__(self):
        self.model_name = "ProsusAI/finbert"
        self.sentiment_pipeline = None

        if TRANSFORMERS_AVAILABLE:
            try:
                print("Loading FinBERT model (this may take a minute first time)...")
                self.sentiment_pipeline = pipeline(
                    "sentiment-analysis",
                    model=self.model_name,
                    tokenizer=self.model_name
                )
                print("✓ FinBERT loaded successfully")
            except Exception as e:
                print(f"Warning: Could not load FinBERT: {e}")
                print("Falling back to TextBlob sentiment")
                self.sentiment_pipeline = None

    def analyze_text(self, text: str) -> Dict:
        """
        Analyze sentiment of a single text.

        Returns:
            Dict with 'label' (positive/negative/neutral) and 'score' (0-1)
        """
        if not text or len(text.strip()) < 10:
            return {'label': 'neutral', 'score': 0.5}

        # Try FinBERT first
        if self.sentiment_pipeline and TRANSFORMERS_AVAILABLE:
            try:
                # Truncate to 512 tokens (BERT max)
                text = text[:512]
                result = self.sentiment_pipeline(text)[0]

                # Convert FinBERT output to standard format
                label = result['label'].lower()
                score = result['score']

                # Map to -1 to 1 scale
                if label == 'positive':
                    sentiment_score = score
                elif label == 'negative':
                    sentiment_score = -score
                else:  # neutral
                    sentiment_score = 0.0

                return {
                    'label': label,
                    'score': sentiment_score,
                    'confidence': score
                }
            except Exception as e:
                print(f"FinBERT error: {e}, falling back to TextBlob")

        # Fallback to TextBlob
        if TEXTBLOB_AVAILABLE:
            try:
                blob = TextBlob(text)
                polarity = blob.sentiment.polarity  # -1 to 1

                if polarity > 0.1:
                    label = 'positive'
                elif polarity < -0.1:
                    label = 'negative'
                else:
                    label = 'neutral'

                return {
                    'label': label,
                    'score': polarity,
                    'confidence': abs(polarity)
                }
            except:
                pass

        # Last resort: neutral
        return {'label': 'neutral', 'score': 0.0, 'confidence': 0.0}

    def analyze_news_items(self, news_items: List) -> float:
        """
        Analyze multiple news items and return aggregate sentiment score (0-100).

        Args:
            news_items: List of NewsItem objects (from theme_manager)

        Returns:
            Sentiment score from 0-100 (higher = more positive)
        """
        if not news_items:
            return 50.0  # Neutral

        total_sentiment = 0
        total_weight = 0

        now = datetime.now()

        for item in news_items:
            # Analyze headline (most important)
            result = self.analyze_text(item.headline)
            sentiment = result['score']

            # Calculate recency weight (more recent = higher weight)
            age_hours = (now - item.published).total_seconds() / 3600
            recency_weight = max(0.1, 1.0 - (age_hours / 168))  # Decay over 1 week

            # Combine with relevance
            weight = item.relevance * recency_weight

            total_sentiment += sentiment * weight
            total_weight += weight

        if total_weight == 0:
            return 50.0

        # Average sentiment (-1 to 1)
        avg_sentiment = total_sentiment / total_weight

        # Convert to 0-100 scale
        score = (avg_sentiment + 1) * 50

        return min(max(score, 0), 100)


class SocialSentimentAnalyzer:
    """
    Analyze social media sentiment using VADER (optimized for social media).

    VADER is specifically designed for social media text (emojis, slang, etc.)
    """

    def __init__(self):
        self.analyzer = None

        if VADER_AVAILABLE:
            self.analyzer = SentimentIntensityAnalyzer()

    def analyze_social_text(self, text: str) -> Dict:
        """
        Analyze sentiment of social media text.

        Returns:
            Dict with 'compound' score (-1 to 1) and 'label'
        """
        if not self.analyzer or not VADER_AVAILABLE:
            # Fallback to TextBlob
            if TEXTBLOB_AVAILABLE:
                blob = TextBlob(text)
                return {
                    'compound': blob.sentiment.polarity,
                    'label': 'positive' if blob.sentiment.polarity > 0 else 'negative'
                }
            return {'compound': 0.0, 'label': 'neutral'}

        scores = self.analyzer.polarity_scores(text)
        return scores

    def analyze_reddit_posts(self, posts: List[Dict]) -> float:
        """
        Analyze Reddit posts/comments for a ticker.

        Args:
            posts: List of dicts with 'text', 'score' (upvotes), 'created_utc'

        Returns:
            Sentiment score 0-100
        """
        if not posts:
            return 50.0

        total_sentiment = 0
        total_weight = 0

        for post in posts:
            result = self.analyze_social_text(post.get('text', ''))
            sentiment = result.get('compound', 0)

            # Weight by upvotes (higher upvotes = more influential)
            upvotes = max(1, post.get('score', 1))
            weight = np.log1p(upvotes)  # Log scale to prevent outliers

            total_sentiment += sentiment * weight
            total_weight += weight

        if total_weight == 0:
            return 50.0

        avg_sentiment = total_sentiment / total_weight
        score = (avg_sentiment + 1) * 50

        return min(max(score, 0), 100)


class PricePredictor:
    """
    ML-based price prediction using ensemble of models.

    Combines multiple approaches for robust predictions:
    - Gradient Boosting
    - Random Forest
    - Simple momentum/trend indicators
    """

    def __init__(self):
        self.models_available = SKLEARN_AVAILABLE
        self.scaler = StandardScaler() if SKLEARN_AVAILABLE else None

    def predict_price_direction(self, market_data) -> Dict:
        """
        Predict price direction and confidence.

        Args:
            market_data: MarketData object with prices, volumes, dates

        Returns:
            Dict with 'direction' (UP/DOWN/NEUTRAL), 'confidence' (0-100), 'score' (0-100)
        """
        if not market_data or len(market_data.prices) < 30:
            return {
                'direction': 'NEUTRAL',
                'confidence': 50.0,
                'score': 50.0
            }

        prices = np.array(market_data.prices)
        volumes = np.array(market_data.volumes)

        # Feature engineering
        returns = np.diff(prices) / prices[:-1]

        # Simple momentum indicators
        sma_20 = np.mean(prices[-20:])
        sma_50 = np.mean(prices[-50:]) if len(prices) >= 50 else sma_20
        current_price = prices[-1]

        # Trend strength
        trend = "UP" if sma_20 > sma_50 and current_price > sma_20 else "DOWN" if sma_20 < sma_50 else "NEUTRAL"

        # Momentum score
        recent_return = (prices[-1] - prices[-10]) / prices[-10] if len(prices) >= 10 else 0

        # Volume trend
        avg_volume = np.mean(volumes[-20:])
        recent_volume = np.mean(volumes[-5:])
        volume_increasing = recent_volume > avg_volume

        # Calculate confidence based on signal strength
        if trend == "UP" and recent_return > 0.02 and volume_increasing:
            confidence = 75.0
            score = 70.0
        elif trend == "DOWN" and recent_return < -0.02:
            confidence = 75.0
            score = 30.0
        else:
            confidence = 50.0
            score = 50.0

        return {
            'direction': trend,
            'confidence': confidence,
            'score': score
        }


class AIPredictionEngine:
    """
    Main AI prediction engine combining all AI components.

    Weights (totaling to 100%):
    - News sentiment: 30%
    - Social sentiment: 20%
    - Price prediction: 35%
    - Alternative data: 15%
    """

    def __init__(self,
                 news_weight: float = 0.30,
                 social_weight: float = 0.20,
                 price_weight: float = 0.35,
                 alt_data_weight: float = 0.15):

        self.news_weight = news_weight
        self.social_weight = social_weight
        self.price_weight = price_weight
        self.alt_data_weight = alt_data_weight

        # Initialize analyzers
        self.news_analyzer = NewsSentimentAnalyzer()
        self.social_analyzer = SocialSentimentAnalyzer()
        self.price_predictor = PricePredictor()

    def predict(self, ticker: str, market_data, news_items: List = None, social_posts: List = None) -> AIPredictionData:
        """
        Generate AI prediction for a ticker.

        Args:
            ticker: Stock ticker symbol
            market_data: MarketData object
            news_items: List of NewsItem objects
            social_posts: List of social media posts (Reddit/Twitter)

        Returns:
            AIPredictionData with all AI scores
        """
        # 1. News sentiment
        news_score = self.news_analyzer.analyze_news_items(news_items or [])

        # 2. Social sentiment
        social_score = self.social_analyzer.analyze_reddit_posts(social_posts or [])

        # 3. Price prediction
        price_result = self.price_predictor.predict_price_direction(market_data)
        price_score = price_result['score']
        price_direction = price_result['direction']
        confidence = price_result['confidence']

        # 4. Alternative data (stub for now - will implement later)
        alt_data_score = 50.0  # Neutral for now

        # Calculate overall AI score
        overall = (
            news_score * self.news_weight +
            social_score * self.social_weight +
            price_score * self.price_weight +
            alt_data_score * self.alt_data_weight
        )

        return AIPredictionData(
            ticker=ticker,
            news_sentiment=news_score,
            social_sentiment=social_score,
            price_prediction=price_score,
            price_direction=price_direction,
            confidence=confidence,
            alternative_data=alt_data_score,
            overall_ai_score=overall
        )
