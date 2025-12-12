"""
Main scoring engine for the Slingshot scanner.

Orchestrates compression analysis, smart money tracking, and theme scoring
to identify high-probability setup candidates.
"""
from typing import List, Optional
from datetime import datetime

from .models import TickerScore, ScanResult
from .data_fetcher import DataFetcher
from .compression import analyze_compression
from .smart_money import SmartMoneyTracker
from .theme_manager import ThemeManager


class ScoringEngine:
    """
    Main engine that orchestrates all analysis modules.

    Combines technical compression, smart money activity, and
    narrative themes to generate a unified score.
    """

    def __init__(self,
                 compression_weight: float = 0.40,
                 smart_money_weight: float = 0.35,
                 theme_weight: float = 0.25):
        """
        Initialize scoring engine.

        Args:
            compression_weight: Weight for compression score (default 40%)
            smart_money_weight: Weight for smart money score (default 35%)
            theme_weight: Weight for theme/narrative score (default 25%)
        """
        self.compression_weight = compression_weight
        self.smart_money_weight = smart_money_weight
        self.theme_weight = theme_weight

        # Initialize modules
        self.data_fetcher = DataFetcher()
        self.smart_money_tracker = SmartMoneyTracker()
        self.theme_manager = ThemeManager()

    def score_ticker(self, ticker: str) -> Optional[TickerScore]:
        """
        Score a single ticker across all dimensions.

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

        # Analyze compression
        compression = analyze_compression(market_data)

        # Analyze smart money
        smart_money = self.smart_money_tracker.analyze_smart_money(ticker)

        # Analyze theme/narrative
        theme = self.theme_manager.analyze_theme(ticker)

        # Calculate total score
        total_score = (
            compression.overall_compression_score * self.compression_weight +
            smart_money.overall_smart_money_score * self.smart_money_weight +
            theme.overall_theme_score * self.theme_weight
        )

        return TickerScore(
            ticker=ticker,
            timestamp=datetime.now(),
            compression=compression,
            smart_money=smart_money,
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
        """Get current scoring weights."""
        return {
            'compression': self.compression_weight,
            'smart_money': self.smart_money_weight,
            'theme': self.theme_weight
        }

    def set_weights(self,
                   compression: Optional[float] = None,
                   smart_money: Optional[float] = None,
                   theme: Optional[float] = None):
        """
        Update scoring weights.

        Weights must sum to 1.0.
        """
        if compression is not None:
            self.compression_weight = compression
        if smart_money is not None:
            self.smart_money_weight = smart_money
        if theme is not None:
            self.theme_weight = theme

        # Validate
        total = self.compression_weight + self.smart_money_weight + self.theme_weight
        if abs(total - 1.0) > 0.01:
            raise ValueError(f"Weights must sum to 1.0 (got {total})")
