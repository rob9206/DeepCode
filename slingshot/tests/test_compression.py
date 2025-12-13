"""Tests for compression analysis module."""
import unittest
from datetime import datetime, timedelta
import numpy as np

from slingshot.models import MarketData
from slingshot.compression import (
    calculate_bb_squeeze_score,
    calculate_atr_compression_score,
    calculate_volume_dryup_score,
    calculate_price_range_compression,
    analyze_compression
)
import pandas as pd


class TestCompression(unittest.TestCase):
    """Test compression detection functions."""

    def setUp(self):
        """Set up test data."""
        # Create sample market data with 100 days
        np.random.seed(42)
        dates = [datetime.now() - timedelta(days=i) for i in range(100, 0, -1)]

        # Simulate a compressing stock (decreasing volatility)
        base_price = 100
        prices = []
        volumes = []

        for i in range(100):
            # Early period: high volatility
            if i < 50:
                volatility = 5.0
                vol_mult = 1.5
            # Later period: low volatility (compression)
            else:
                volatility = 1.0
                vol_mult = 0.5

            price = base_price + np.random.normal(0, volatility)
            volume = int(1000000 + np.random.normal(0, 500000 * vol_mult))

            prices.append(max(price, 1))  # Ensure positive
            volumes.append(max(volume, 0))  # Ensure non-negative

        self.market_data = MarketData(
            ticker='TEST',
            prices=prices,
            volumes=volumes,
            dates=dates
        )

    def test_bb_squeeze_score(self):
        """Test Bollinger Band squeeze calculation."""
        prices = pd.Series(self.market_data.prices)
        score = calculate_bb_squeeze_score(prices)

        self.assertIsInstance(score, float)
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)

    def test_atr_compression_score(self):
        """Test ATR compression calculation."""
        prices = pd.Series(self.market_data.prices)
        # For simplicity, use close as high/low (normally you'd have separate)
        score = calculate_atr_compression_score(prices, prices, prices)

        self.assertIsInstance(score, float)
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)

    def test_volume_dryup_score(self):
        """Test volume dry-up calculation."""
        volumes = pd.Series(self.market_data.volumes)
        score = calculate_volume_dryup_score(volumes)

        self.assertIsInstance(score, float)
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)

    def test_price_range_compression(self):
        """Test price range compression calculation."""
        prices = pd.Series(self.market_data.prices)
        score = calculate_price_range_compression(prices, prices, prices)

        self.assertIsInstance(score, float)
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)

    def test_analyze_compression(self):
        """Test full compression analysis."""
        result = analyze_compression(self.market_data)

        self.assertEqual(result.ticker, 'TEST')
        self.assertGreaterEqual(result.bb_squeeze, 0)
        self.assertLessEqual(result.bb_squeeze, 100)
        self.assertGreaterEqual(result.overall_compression_score, 0)
        self.assertLessEqual(result.overall_compression_score, 100)

    def test_compression_detection(self):
        """Test that compression is detected in compressing stock."""
        result = analyze_compression(self.market_data)

        # With our setup (decreasing volatility), we should see some compression
        # This is a soft assertion - exact value depends on random data
        self.assertGreater(result.overall_compression_score, 30)


if __name__ == '__main__':
    unittest.main()
