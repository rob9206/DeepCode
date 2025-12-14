"""
Main scoring engine for the Slingshot scanner - AI-FIRST ARCHITECTURE.

Orchestrates AI prediction, smart money tracking, and technical confirmation
to identify high-probability setup candidates.

NEW WEIGHTS (AI-First):
- AI Prediction: 50% (was 0%)
- Smart Money: 30% (was 35%)
- Technical: 20% (was 40% compression + 25% theme)
"""
from typing import List, Optional
from datetime import datetime

from .models import TickerScore, ScanResult
from .data_fetcher import DataFetcher
from .compression import analyze_compression
from .smart_money import SmartMoneyTracker
from .theme_manager import ThemeManager

# AI prediction module (new!)
try:
    from .ai_prediction import AIPredictionEngine
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    print("Warning: AI prediction module not available. Using fallback scoring.")


class ScoringEngine:
    """
    AI-FIRST scoring engine for Slingshot.

    Primary signal: AI prediction (50%)
    - News sentiment (FinBERT)
    - Social media sentiment (VADER)
    - ML price prediction (ensemble)
    - Alternative data signals

    Supporting signals:
    - Smart Money (30%): Institutional/insider/options
    - Technical (20%): Compression confirmation
    """

    def __init__(self,
                 ai_weight: float = 0.50,
                 smart_money_weight: float = 0.30,
                 technical_weight: float = 0.20):
        """
        Initialize AI-first scoring engine.

        Args:
            ai_weight: Weight for AI prediction (default 50%)
            smart_money_weight: Weight for smart money score (default 30%)
            technical_weight: Weight for technical confirmation (default 20%)
        """
        self.ai_weight = ai_weight
        self.smart_money_weight = smart_money_weight
        self.technical_weight = technical_weight

        # Backwards compatibility (old names)
        self.compression_weight = technical_weight  # For old code
        self.theme_weight = 0  # Theme is now part of AI prediction

        # Initialize modules
        self.data_fetcher = DataFetcher()
        self.smart_money_tracker = SmartMoneyTracker()
        self.theme_manager = ThemeManager()

        # Initialize AI prediction engine
        if AI_AVAILABLE:
            self.ai_engine = AIPredictionEngine()
        else:
            self.ai_engine = None

    def score_ticker(self, ticker: str) -> Optional[TickerScore]:
        """
        Score a single ticker using AI-FIRST architecture.

        Args:
            ticker: Stock ticker symbol

        Returns:
            TickerScore object or None if scoring fails
        """
        # Fetch market data
        market_data = self.data_fetcher.fetch_market_data(ticker)
        if not market_data:
            print(f"Failed to fetch data for {ticker}")
            return None

        # Get news for AI sentiment analysis
        news_items = self.theme_manager.fetch_news(ticker)

        # NEW: AI Prediction (50% weight)
        ai_prediction = None
        if self.ai_engine and AI_AVAILABLE:
            try:
                ai_prediction = self.ai_engine.predict(
                    ticker=ticker,
                    market_data=market_data,
                    news_items=news_items,
                    social_posts=[]  # TODO: Add Reddit/Twitter scraping
                )
            except Exception as e:
                print(f"AI prediction failed for {ticker}: {e}")
                ai_prediction = None

        # Smart money analysis (30% weight)
        smart_money = self.smart_money_tracker.analyze_smart_money(ticker)

        # Technical compression (20% weight - reduced from 40%)
        compression = analyze_compression(market_data)

        # Theme/narrative (now part of AI prediction)
        theme = self.theme_manager.analyze_theme(ticker)

        # Calculate AI-FIRST total score
        if ai_prediction:
            # AI-first scoring: 50% AI, 30% smart money, 20% technical
            total_score = (
                ai_prediction.overall_ai_score * self.ai_weight +
                smart_money.overall_smart_money_score * self.smart_money_weight +
                compression.overall_compression_score * self.technical_weight
            )
        else:
            # Fallback to old scoring if AI not available
            total_score = (
                compression.overall_compression_score * 0.40 +
                smart_money.overall_smart_money_score * 0.35 +
                theme.overall_theme_score * 0.25
            )

        return TickerScore(
            ticker=ticker,
            timestamp=datetime.now(),
            ai_prediction=ai_prediction,  # NEW: AI prediction data
            smart_money=smart_money,
            compression=compression,
            theme=theme,
            total_score=total_score
        )

    def scan_tickers(self, tickers: List[str]) -> ScanResult:
        """
        Scan multiple tickers and return sorted results.

        Args:
            tickers: List of ticker symbols to scan

        Returns:
            ScanResult with all scores and top candidates
        """
        scores = []

        print(f"Scanning {len(tickers)} tickers...")

        for i, ticker in enumerate(tickers, 1):
            print(f"  [{i}/{len(tickers)}] Analyzing {ticker}...")

            score = self.score_ticker(ticker)
            if score:
                scores.append(score)

        # Sort by total score
        sorted_scores = sorted(scores, key=lambda x: x.total_score, reverse=True)

        # Filter for slingshot candidates
        candidates = [s for s in sorted_scores if s.is_slingshot_candidate]

        return ScanResult(
            timestamp=datetime.now(),
            tickers_scanned=tickers,
            scores=sorted_scores,
            top_candidates=candidates
        )

    def scan_popular(self, limit: Optional[int] = None) -> ScanResult:
        """
        Scan popular/liquid tickers.

        Args:
            limit: Max number of tickers to scan (None = scan all)

        Returns:
            ScanResult with scores
        """
        tickers = self.data_fetcher.get_popular_tickers()
        if limit:
            tickers = tickers[:limit]

        return self.scan_tickers(tickers)

    def scan_theme(self, theme: str, limit: Optional[int] = None) -> ScanResult:
        """
        Scan all tickers in a specific theme.

        Args:
            theme: Theme name (e.g., 'AI', 'Semiconductors')
            limit: Max number of tickers to scan

        Returns:
            ScanResult with scores for theme tickers
        """
        tickers = list(self.theme_manager.get_theme_tickers(theme))
        if limit:
            tickers = tickers[:limit]

        return self.scan_tickers(tickers)

    def deep_dive(self, ticker: str) -> dict:
        """
        Perform deep analysis on a single ticker.

        Returns detailed breakdown of all scoring components.
        """
        score = self.score_ticker(ticker)
        if not score:
            return {'error': f'Failed to analyze {ticker}'}

        # Get additional context
        info = self.data_fetcher.get_ticker_info(ticker)
        institutional = self.smart_money_tracker.get_institutional_holders(ticker)
        insider_trades = self.smart_money_tracker.get_recent_insider_trades(ticker)
        options_flow = self.smart_money_tracker.get_unusual_options_activity(ticker)
        news = self.theme_manager.fetch_news(ticker)

        return {
            'ticker': ticker,
            'info': info,
            'score': score.to_dict(),
            'breakdown': {
                'compression': {
                    'bb_squeeze': score.compression.bb_squeeze,
                    'atr_compression': score.compression.atr_compression,
                    'volume_dryup': score.compression.volume_dryup,
                    'price_range_compression': score.compression.price_range_compression,
                    'overall': score.compression.overall_compression_score,
                    'is_compressed': score.compression.is_compressed
                },
                'smart_money': {
                    'institutional_buying': score.smart_money.institutional_buying,
                    'insider_buying': score.smart_money.insider_buying,
                    'options_flow': score.smart_money.options_flow,
                    'overall': score.smart_money.overall_smart_money_score,
                    'is_accumulating': score.smart_money.is_accumulating
                },
                'theme': {
                    'themes': score.theme.themes,
                    'narrative_score': score.theme.narrative_score,
                    'theme_momentum': score.theme.theme_momentum,
                    'overall': score.theme.overall_theme_score,
                    'is_trending': score.theme.is_trending
                }
            },
            'context': {
                'institutional_holders': institutional[:5],  # Top 5
                'recent_insider_trades': insider_trades[:5],
                'unusual_options': options_flow[:5],
                'recent_news': [
                    {
                        'headline': n.headline,
                        'published': n.published.isoformat(),
                        'source': n.source,
                        'sentiment': n.sentiment
                    }
                    for n in news[:10]
                ]
            }
        }

    def get_weights(self) -> dict:
        """Get current scoring weights.

        Returns weights using old API names for backwards compatibility.
        In AI-first architecture:
        - 'compression' = technical analysis (20%)
        - 'smart_money' = smart money tracking (30%)
        - 'theme' = AI prediction (50%, includes theme analysis)
        """
        return {
            'compression': self.technical_weight,
            'smart_money': self.smart_money_weight,
            'theme': self.ai_weight  # Theme is now part of AI prediction
        }

    def set_weights(self,
                   ai: Optional[float] = None,
                   smart_money: Optional[float] = None,
                   technical: Optional[float] = None,
                   # Backwards compatibility (old API)
                   compression: Optional[float] = None,
                   theme: Optional[float] = None):
        """
        Update scoring weights.

        Weights must sum to 1.0.

        New API:
            ai: AI prediction weight (default 50%)
            smart_money: Smart money weight (default 30%)
            technical: Technical confirmation weight (default 20%)

        Old API (backwards compatible):
            compression: Maps to 'technical' (technical analysis)
            smart_money: Smart money tracking
            theme: Maps to 'ai' (theme is now part of AI prediction)
        """
        # New API parameters
        if ai is not None:
            self.ai_weight = ai
        if smart_money is not None:
            self.smart_money_weight = smart_money
        if technical is not None:
            self.technical_weight = technical
            self.compression_weight = technical  # Backwards compat

        # Old API parameters (for backwards compatibility)
        if compression is not None:
            self.technical_weight = compression
            self.compression_weight = compression
        if theme is not None:
            # Theme is now part of AI prediction
            self.ai_weight = theme
            self.theme_weight = theme  # Keep old attribute for compatibility

        # Validate weights sum to 1.0
        total = self.ai_weight + self.smart_money_weight + self.technical_weight
        if abs(total - 1.0) > 0.01:
            raise ValueError(f"Weights must sum to 1.0 (got {total})")
