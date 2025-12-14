"""
Slingshot - AI-Powered Stock Scanner for High-Probability Setups

AI-FIRST ARCHITECTURE:
1. AI Prediction (50%) - News sentiment, social sentiment, ML price prediction
2. Smart Money (30%) - Institutional/insider/options accumulation
3. Technical (20%) - Compression confirmation

The combination of these factors creates "slingshot" setups -
stocks ready to launch on their next catalyst.
"""

__version__ = '0.2.0'  # AI-first version

from .models import (
    TickerScore,
    CompressionData,
    SmartMoneyData,
    ThemeData,
    MarketData,
    NewsItem,
    ScanResult
)

from .scoring_engine import ScoringEngine
from .data_fetcher import DataFetcher
from .compression import analyze_compression
from .smart_money import SmartMoneyTracker
from .theme_manager import ThemeManager

# AI prediction module (optional import)
try:
    from .ai_prediction import (
        AIPredictionEngine,
        AIPredictionData,
        NewsSentimentAnalyzer,
        SocialSentimentAnalyzer,
        PricePredictor
    )
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False

__all__ = [
    'ScoringEngine',
    'DataFetcher',
    'SmartMoneyTracker',
    'ThemeManager',
    'analyze_compression',
    'TickerScore',
    'CompressionData',
    'SmartMoneyData',
    'ThemeData',
    'MarketData',
    'NewsItem',
    'ScanResult',
]

# Add AI classes if available
if AI_AVAILABLE:
    __all__.extend([
        'AIPredictionEngine',
        'AIPredictionData',
        'NewsSentimentAnalyzer',
        'SocialSentimentAnalyzer',
        'PricePredictor'
    ])
