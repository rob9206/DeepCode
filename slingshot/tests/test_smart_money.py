"""Tests for smart money tracking module."""
import unittest

from slingshot.smart_money import SmartMoneyTracker


class TestSmartMoney(unittest.TestCase):
    """Test smart money tracking functions."""

    def setUp(self):
        """Set up test tracker."""
        self.tracker = SmartMoneyTracker()

    def test_institutional_buying_score(self):
        """Test institutional buying score."""
        score = self.tracker.get_institutional_buying_score('NVDA')

        self.assertIsInstance(score, float)
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)

    def test_insider_buying_score(self):
        """Test insider buying score."""
        score = self.tracker.get_insider_buying_score('NVDA')

        self.assertIsInstance(score, float)
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)

    def test_options_flow_score(self):
        """Test options flow score."""
        score = self.tracker.get_options_flow_score('NVDA')

        self.assertIsInstance(score, float)
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)

    def test_analyze_smart_money(self):
        """Test full smart money analysis."""
        result = self.tracker.analyze_smart_money('NVDA')

        self.assertEqual(result.ticker, 'NVDA')
        self.assertGreaterEqual(result.institutional_buying, 0)
        self.assertLessEqual(result.institutional_buying, 100)
        self.assertGreaterEqual(result.overall_smart_money_score, 0)
        self.assertLessEqual(result.overall_smart_money_score, 100)

    def test_caching(self):
        """Test that results are cached."""
        result1 = self.tracker.analyze_smart_money('NVDA')
        result2 = self.tracker.analyze_smart_money('NVDA')

        # Should return same cached object
        self.assertEqual(result1, result2)

    def test_institutional_holders(self):
        """Test institutional holders retrieval."""
        holders = self.tracker.get_institutional_holders('NVDA')

        self.assertIsInstance(holders, list)
        if holders:
            self.assertIn('name', holders[0])
            self.assertIn('shares', holders[0])

    def test_insider_trades(self):
        """Test insider trades retrieval."""
        trades = self.tracker.get_recent_insider_trades('NVDA')

        self.assertIsInstance(trades, list)
        if trades:
            self.assertIn('name', trades[0])
            self.assertIn('type', trades[0])

    def test_unusual_options(self):
        """Test unusual options activity retrieval."""
        options = self.tracker.get_unusual_options_activity('NVDA')

        self.assertIsInstance(options, list)
        if options:
            self.assertIn('type', options[0])
            self.assertIn('sentiment', options[0])


if __name__ == '__main__':
    unittest.main()
