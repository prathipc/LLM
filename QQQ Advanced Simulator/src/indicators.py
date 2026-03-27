"""
Technical Indicator Calculations for Enhanced Leveraged ETF Strategy v2.0
"""

import pandas as pd
import numpy as np
from config import *


def calculate_sma(prices, period):
    """
    Calculate Simple Moving Average
    
    Args:
        prices: pandas Series of prices
        period: int, number of periods for SMA
    
    Returns:
        pandas Series of SMA values
    """
    return prices.rolling(window=period, min_periods=period).mean()


def calculate_sma_slope(sma_series, lookback=SMA_SLOPE_LOOKBACK):
    """
    Calculate annualized slope percentage for SMA
    Formula: ((SMA_today - SMA_N_days_ago) / SMA_N_days_ago) / N * 100
    Then convert to weekly rate
    
    Args:
        sma_series: pandas Series of SMA values
        lookback: number of days to calculate slope (default 5)
    
    Returns:
        pandas Series of slope as percentage per week
    """
    sma_n_days_ago = sma_series.shift(lookback)
    # Avoid division by zero
    slope_pct_per_week = pd.Series(0.0, index=sma_series.index)
    mask = (sma_n_days_ago > 0) & (~sma_n_days_ago.isna())
    slope_pct_per_day = ((sma_series[mask] - sma_n_days_ago[mask]) / sma_n_days_ago[mask]) / lookback * 100
    slope_pct_per_week[mask] = slope_pct_per_day * 5  # Convert to weekly rate
    return slope_pct_per_week


def calculate_atr(high, low, close, period=ATR_PERIOD):
    """
    Calculate Average True Range (ATR)
    
    Args:
        high: pandas Series of high prices
        low: pandas Series of low prices
        close: pandas Series of close prices
        period: int, number of periods for ATR (default 14)
    
    Returns:
        pandas Series of ATR values
    """
    prev_close = close.shift(1)
    
    # True Range is the maximum of:
    # 1. High - Low
    # 2. abs(High - Previous Close)
    # 3. abs(Low - Previous Close)
    tr1 = high - low
    tr2 = np.abs(high - prev_close)
    tr3 = np.abs(low - prev_close)
    
    true_range = pd.DataFrame({'tr1': tr1, 'tr2': tr2, 'tr3': tr3}).max(axis=1)
    
    # ATR is the rolling average of True Range
    atr = true_range.rolling(window=period, min_periods=period).mean()
    
    return atr


def calculate_atr_percentage(atr, close):
    """
    Calculate ATR as percentage of close price
    
    Args:
        atr: pandas Series of ATR values
        close: pandas Series of close prices
    
    Returns:
        pandas Series of ATR percentage
    """
    # Avoid division by zero
    result = pd.Series(0.0, index=atr.index)
    mask = close > 0
    result[mask] = (atr[mask] / close[mask]) * 100
    return result


def calculate_volume_ratio(volume, period=VOLUME_PERIOD):
    """
    Calculate Volume Ratio (current volume / average volume)
    
    Args:
        volume: pandas Series of volume data
        period: int, number of periods for average volume (default 20)
    
    Returns:
        pandas Series of volume ratios
    """
    avg_volume = volume.rolling(window=period, min_periods=period).mean()
    # Avoid division by zero
    volume_ratio = pd.Series(1.0, index=volume.index)
    mask = avg_volume > 0
    volume_ratio[mask] = volume[mask] / avg_volume[mask]
    return volume_ratio


def calculate_combined_momentum(slope_50, slope_200, price, sma_50, sma_200):
    """
    Calculate Combined Momentum Score
    
    Formula from FD:
    Combined Momentum = (Slope_50 * 0.6 + Slope_200 * 0.3 + Price_Position * 0.1)
    
    Where Price_Position = ((Price - SMA_200) / SMA_200) * 100
    
    Args:
        slope_50: pandas Series of 50-SMA slope
        slope_200: pandas Series of 200-SMA slope
        price: pandas Series of current prices
        sma_50: pandas Series of 50-SMA values
        sma_200: pandas Series of 200-SMA values
    
    Returns:
        pandas Series of combined momentum scores
    """
    # Avoid division by zero
    price_position = pd.Series(0.0, index=price.index)
    mask = (sma_200 > 0) & (~sma_200.isna())
    price_position[mask] = ((price[mask] - sma_200[mask]) / sma_200[mask]) * 100
    
    combined_momentum = (slope_50 * 0.6) + (slope_200 * 0.3) + (price_position * 0.1)
    return combined_momentum


def detect_death_cross(sma_50, sma_200):
    """
    Detect Death Cross (50-SMA crosses below 200-SMA)
    
    Args:
        sma_50: pandas Series of 50-SMA values
        sma_200: pandas Series of 200-SMA values
    
    Returns:
        pandas Series of boolean values (True when death cross occurs)
    """
    prev_50 = sma_50.shift(1)
    prev_200 = sma_200.shift(1)
    
    # Death cross: 50-SMA was above 200-SMA, now below
    death_cross = (prev_50 > prev_200) & (sma_50 < sma_200)
    
    return death_cross


def detect_golden_cross(sma_50, sma_200):
    """
    Detect Golden Cross (50-SMA crosses above 200-SMA)
    
    Args:
        sma_50: pandas Series of 50-SMA values
        sma_200: pandas Series of 200-SMA values
    
    Returns:
        pandas Series of boolean values (True when golden cross occurs)
    """
    prev_50 = sma_50.shift(1)
    prev_200 = sma_200.shift(1)
    
    # Golden cross: 50-SMA was below 200-SMA, now above
    golden_cross = (prev_50 < prev_200) & (sma_50 > sma_200)
    
    return golden_cross


def determine_market_regime(sma_50, sma_200, slope_50, slope_200):
    """
    Determine market regime based on SMA positions and slopes
    
    Returns: 'bull', 'bear', 'transition', or 'choppy'
    
    Args:
        sma_50: pandas Series of 50-SMA values
        sma_200: pandas Series of 200-SMA values
        slope_50: pandas Series of 50-SMA slope
        slope_200: pandas Series of 200-SMA slope
    
    Returns:
        pandas Series of regime strings
    """
    regime = pd.Series('choppy', index=sma_50.index)
    
    # Bull regime: 50 > 200 and both slopes positive
    bull_condition = (sma_50 > sma_200) & (slope_50 > SLOPE_BULL_THRESHOLD) & (slope_200 > 0)
    regime[bull_condition] = 'bull'
    
    # Bear regime: 50 < 200 and both slopes negative
    bear_condition = (sma_50 < sma_200) & (slope_50 < SLOPE_BEAR_THRESHOLD) & (slope_200 < 0)
    regime[bear_condition] = 'bear'
    
    # Transition: 50 near 200 or slopes diverging
    transition_condition = (
        (np.abs(sma_50 - sma_200) / sma_200 < 0.02) |  # SMAs within 2%
        ((slope_50 > 0) & (slope_200 < 0)) |  # Diverging slopes
        ((slope_50 < 0) & (slope_200 > 0))
    )
    regime[transition_condition] = 'transition'
    
    return regime


def calculate_all_indicators(df):
    """
    Calculate all technical indicators for the strategy
    
    Args:
        df: pandas DataFrame with columns: Date, Close, High, Low, Volume
    
    Returns:
        pandas DataFrame with all indicators added
    """
    # Make a copy to avoid modifying original
    data = df.copy()
    
    # Calculate SMAs
    data['SMA_50'] = calculate_sma(data[COL_QQQ_CLOSE], SMA_SHORT_PERIOD)
    data['SMA_200'] = calculate_sma(data[COL_QQQ_CLOSE], SMA_LONG_PERIOD)
    
    # Calculate SMA Slopes
    data['Slope_50'] = calculate_sma_slope(data['SMA_50'], SMA_SLOPE_LOOKBACK)
    data['Slope_200'] = calculate_sma_slope(data['SMA_200'], SMA_SLOPE_LOOKBACK)
    
    # Calculate ATR
    data['ATR'] = calculate_atr(data[COL_QQQ_HIGH], data[COL_QQQ_LOW], data[COL_QQQ_CLOSE], ATR_PERIOD)
    data['ATR_PCT'] = calculate_atr_percentage(data['ATR'], data[COL_QQQ_CLOSE])
    
    # Calculate Volume Ratio
    data['Volume_Ratio'] = calculate_volume_ratio(data[COL_QQQ_VOLUME], VOLUME_PERIOD)
    
    # Calculate Combined Momentum
    data['Combined_Momentum'] = calculate_combined_momentum(
        data['Slope_50'], 
        data['Slope_200'],
        data[COL_QQQ_CLOSE],
        data['SMA_50'],
        data['SMA_200']
    )
    
    # Detect Crosses
    data['Death_Cross'] = detect_death_cross(data['SMA_50'], data['SMA_200'])
    data['Golden_Cross'] = detect_golden_cross(data['SMA_50'], data['SMA_200'])
    
    # Determine Market Regime
    data['Market_Regime'] = determine_market_regime(
        data['SMA_50'],
        data['SMA_200'],
        data['Slope_50'],
        data['Slope_200']
    )
    
    return data

