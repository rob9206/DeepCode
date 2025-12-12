"""
Slingshot - Stock Scanner for High-Probability Setups

Identifies stocks with:
1. Technical compression (coiled springs)
2. Smart money accumulation
3. Strong themes/narratives

The combination of these factors creates "slingshot" setups -
stocks ready to launch on their next catalyst.
"""

__version__ = '0.1.0'

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
