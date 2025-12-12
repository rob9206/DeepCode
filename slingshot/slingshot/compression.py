"""
Technical compression analysis module.

Detects when a stock is "coiling" - showing signs of low volatility
and tight price action that often precedes large moves.
"""
import numpy as np
import pandas as pd
from typing import Optional

from .models import CompressionData, MarketData


def calculate_bollinger_bands(prices: pd.Series, window: int = 20, num_std: float = 2.0):
    """Calculate Bollinger Bands."""
    sma = prices.rolling(window=window).mean()
    std = prices.rolling(window=window).std()
    upper = sma + (std * num_std)
    lower = sma - (std * num_std)
    return upper, sma, lower


def calculate_bb_squeeze_score(prices: pd.Series, window: int = 20) -> float:
    """
    Calculate Bollinger Band squeeze score (0-100).

    Higher score = tighter squeeze = more compression.
    Measures bandwidth as percentage of price.
    """
    if len(prices) == 0:
        return 50.0  # Empty data

    upper, sma, lower = calculate_bollinger_bands(prices, window)

    # Calculate bandwidth as percentage of middle band
    bandwidth = ((upper - lower) / sma) * 100

    # Get current bandwidth
    historical_bw = bandwidth.dropna()
    if len(historical_bw) == 0:
        return 50.0  # No valid data

    current_bw = bandwidth.iloc[-1]

    # Compare to historical bandwidth (lower percentile = higher compression)
    if len(historical_bw) < window:
        return 50.0  # Not enough data

    # Calculate percentile (lower percentile = tighter bands = higher score)
    percentile = (historical_bw < current_bw).sum() / len(historical_bw)

    # Invert so tight squeeze = high score
    score = (1 - percentile) * 100

    return min(max(score, 0), 100)


def calculate_atr(high: pd.Series, low: pd.Series, close: pd.Series, window: int = 14) -> pd.Series:
    """Calculate Average True Range."""
    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())

    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(window=window).mean()

    return atr


def calculate_atr_compression_score(high: pd.Series, low: pd.Series, close: pd.Series,
                                   window: int = 14) -> float:
    """
    Calculate ATR compression score (0-100).

    Higher score = lower ATR = more compression.
    """
    if len(close) == 0:
        return 50.0  # Empty data

    atr = calculate_atr(high, low, close, window)
    atr_pct = (atr / close) * 100  # ATR as percentage of price

    historical_atr = atr_pct.dropna()
    if len(historical_atr) == 0:
        return 50.0  # No valid data

    current_atr = atr_pct.iloc[-1]

    if len(historical_atr) < window:
        return 50.0

    # Lower ATR percentile = higher compression score
    percentile = (historical_atr < current_atr).sum() / len(historical_atr)
    score = (1 - percentile) * 100

    return min(max(score, 0), 100)


def calculate_volume_dryup_score(volumes: pd.Series, window: int = 20) -> float:
    """
    Calculate volume dry-up score (0-100).

    Higher score = lower recent volume = more compression.
    """
    if len(volumes) < window:
        return 50.0

    # Calculate average volume
    avg_volume = volumes.rolling(window=window).mean()

    # Recent volume vs historical average
    recent_vol = volumes.iloc[-5:].mean()  # Last 5 days
    historical_avg = avg_volume.iloc[:-5].mean()

    if historical_avg == 0:
        return 50.0

    # Lower ratio = more dry-up = higher score
    ratio = recent_vol / historical_avg

    # Convert to 0-100 scale (ratio < 0.5 = high score, ratio > 1.5 = low score)
    if ratio < 0.5:
        score = 100
    elif ratio > 1.5:
        score = 0
    else:
        score = 100 - ((ratio - 0.5) * 100)

    return min(max(score, 0), 100)


def calculate_price_range_compression(high: pd.Series, low: pd.Series,
                                     close: pd.Series, window: int = 20) -> float:
    """
    Calculate price range compression score (0-100).

    Higher score = tighter recent trading range = more compression.
    """
    if len(close) < window:
        return 50.0

    # Calculate daily range as percentage
    daily_range = ((high - low) / close) * 100

    # Recent range vs historical
    recent_range = daily_range.iloc[-10:].mean()  # Last 10 days
    historical_range = daily_range.iloc[:-10].mean()

    if historical_range == 0:
        return 50.0

    # Lower ratio = more compression = higher score
    ratio = recent_range / historical_range

    if ratio < 0.5:
        score = 100
    elif ratio > 1.5:
        score = 0
    else:
        score = 100 - ((ratio - 0.5) * 100)

    return min(max(score, 0), 100)


def analyze_compression(market_data: MarketData,
                       bb_weight: float = 0.35,
                       atr_weight: float = 0.30,
                       vol_weight: float = 0.20,
                       range_weight: float = 0.15) -> CompressionData:
    """
    Analyze technical compression for a ticker.

    Args:
        market_data: Market data for the ticker
        bb_weight: Weight for BB squeeze score
        atr_weight: Weight for ATR compression score
        vol_weight: Weight for volume dry-up score
        range_weight: Weight for price range compression score

    Returns:
        CompressionData with all compression metrics
    """
    # Convert to pandas for easier calculation
    df = pd.DataFrame({
        'close': market_data.prices,
        'high': market_data.prices,  # Simplified - ideally you'd have actual high/low
        'low': market_data.prices,
        'volume': market_data.volumes
    })

    # Calculate individual scores
    bb_score = calculate_bb_squeeze_score(df['close'])
    atr_score = calculate_atr_compression_score(df['high'], df['low'], df['close'])
    vol_score = calculate_volume_dryup_score(df['volume'])
    range_score = calculate_price_range_compression(df['high'], df['low'], df['close'])

    # Calculate weighted overall score
    overall = (
        bb_score * bb_weight +
        atr_score * atr_weight +
        vol_score * vol_weight +
        range_score * range_weight
    )

    return CompressionData(
        ticker=market_data.ticker,
        bb_squeeze=bb_score,
        atr_compression=atr_score,
        volume_dryup=vol_score,
        price_range_compression=range_score,
        overall_compression_score=overall
    )
