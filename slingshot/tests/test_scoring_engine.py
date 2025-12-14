"""Tests for scoring engine."""
import unittest
from unittest.mock import Mock, patch

from slingshot.scoring_engine import ScoringEngine
from slingshot.models import MarketData, CompressionData, SmartMoneyData, ThemeData
from datetime import datetime


class TestScoringEngine(unittest.TestCase):
    """Test main scoring engine."""

    def setUp(self):
        """Set up test engine."""
        self.engine = ScoringEngine()

    def test_initialization(self):
        """Test engine initialization."""
        self.assertIsNotNone(self.engine.data_fetcher)
        self.assertIsNotNone(self.engine.smart_money_tracker)
        self.assertIsNotNone(self.engine.theme_manager)

    def test_get_weights(self):
        """Test getting current weights."""
        weights = self.engine.get_weights()

        self.assertIn('compression', weights)
        self.assertIn('smart_money', weights)
        self.assertIn('theme', weights)

        # Weights should sum to 1.0
        total = sum(weights.values())
        self.assertAlmostEqual(total, 1.0, places=2)

    def test_set_weights(self):
        """Test setting custom weights."""
        self.engine.set_weights(compression=0.5, smart_money=0.3, theme=0.2)

        weights = self.engine.get_weights()
        self.assertEqual(weights['compression'], 0.5)
        self.assertEqual(weights['smart_money'], 0.3)
        self.assertEqual(weights['theme'], 0.2)

    def test_set_weights_invalid(self):
        """Test that invalid weights raise error."""
        with self.assertRaises(ValueError):
            self.engine.set_weights(compression=0.5, smart_money=0.3, theme=0.3)

    @patch('slingshot.scoring_engine.analyze_compression')
    @patch('slingshot.scoring_engine.DataFetcher.fetch_market_data')
    def test_score_ticker(self, mock_fetch, mock_compress):
        """Test scoring a single ticker."""
        # Mock market data
        mock_fetch.return_value = MarketData(
            ticker='TEST',
            prices=[100, 101, 102],
            volumes=[1000, 1100, 1200],
            dates=[datetime.now()] * 3
        )

        # Mock compression analysis
        mock_compress.return_value = CompressionData(
            ticker='TEST',
            bb_squeeze=75.0,
            atr_compression=80.0,
            volume_dryup=70.0,
            price_range_compression=65.0,
            overall_compression_score=72.5
        )

        score = self.engine.score_ticker('TEST')

        self.assertIsNotNone(score)
        self.assertEqual(score.ticker, 'TEST')
        self.assertGreaterEqual(score.total_score, 0)
        self.assertLessEqual(score.total_score, 100)

    def test_scan_tickers_empty(self):
        """Test scanning with empty list."""
        result = self.engine.scan_tickers([])

        self.assertEqual(len(result.scores), 0)
        self.assertEqual(len(result.top_candidates), 0)


if __name__ == '__main__':
    unittest.main()
