"""Tests for theme manager module."""
import unittest

from slingshot.theme_manager import ThemeManager


class TestThemeManager(unittest.TestCase):
    """Test theme management functions."""

    def setUp(self):
        """Set up test manager."""
        self.manager = ThemeManager()

    def test_get_ticker_themes(self):
        """Test getting themes for a ticker."""
        themes = self.manager.get_ticker_themes('NVDA')

        self.assertIsInstance(themes, list)
        self.assertIn('AI', themes)
        self.assertIn('Semiconductors', themes)

    def test_get_theme_tickers(self):
        """Test getting tickers in a theme."""
        tickers = self.manager.get_theme_tickers('AI')

        self.assertIsInstance(tickers, set)
        self.assertIn('NVDA', tickers)
        self.assertIn('AMD', tickers)

    def test_fetch_news(self):
        """Test news fetching (stub)."""
        news = self.manager.fetch_news('NVDA')

        self.assertIsInstance(news, list)
        if news:
            self.assertIsNotNone(news[0].headline)
            self.assertIsNotNone(news[0].sentiment)
            self.assertGreaterEqual(news[0].sentiment, -1)
            self.assertLessEqual(news[0].sentiment, 1)

    def test_calculate_narrative_score(self):
        """Test narrative score calculation."""
        news = self.manager.fetch_news('NVDA')
        score = self.manager.calculate_narrative_score(news)

        self.assertIsInstance(score, float)
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)

    def test_calculate_theme_momentum(self):
        """Test theme momentum calculation."""
        news = self.manager.fetch_news('NVDA')
        score = self.manager.calculate_theme_momentum(news)

        self.assertIsInstance(score, float)
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)

    def test_analyze_theme(self):
        """Test full theme analysis."""
        result = self.manager.analyze_theme('NVDA')

        self.assertEqual(result.ticker, 'NVDA')
        self.assertIsInstance(result.themes, list)
        self.assertGreater(len(result.themes), 0)
        self.assertGreaterEqual(result.overall_theme_score, 0)
        self.assertLessEqual(result.overall_theme_score, 100)

    def test_list_themes(self):
        """Test theme listing."""
        themes = self.manager.list_themes()

        self.assertIsInstance(themes, list)
        self.assertIn('AI', themes)
        self.assertIn('Semiconductors', themes)

    def test_get_theme_info(self):
        """Test theme info retrieval."""
        info = self.manager.get_theme_info('AI')

        self.assertEqual(info['name'], 'AI')
        self.assertGreater(info['ticker_count'], 0)
        self.assertIsInstance(info['tickers'], list)


if __name__ == '__main__':
    unittest.main()
