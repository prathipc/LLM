"""
Technical Indicators Module
Calculates SMA, ATR, and trend detection for trading signals
"""
import pandas as pd
import numpy as np


def calculate_sma(prices: pd.Series, period: int) -> pd.Series:
    """
    Calculate Simple Moving Average
    
    Args:
        prices: Series of closing prices
        period: Number of periods for the moving average
        
    Returns:
        Series with SMA values (NaN for insufficient data)
    """
    return prices.rolling(window=period, min_periods=period).mean()


def calculate_atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    """
    Calculate Average True Range (ATR)
    
    ATR measures volatility using the true range:
    TR = max(high - low, abs(high - prev_close), abs(low - prev_close))
    ATR = moving average of TR over the specified period
    
    Args:
        high: Series of daily high prices
        low: Series of daily low prices
        close: Series of daily close prices
        period: Number of periods for ATR calculation (default 14)
        
    Returns:
        Series with ATR values (NaN for insufficient data)
    """
    # Calculate True Range components
    prev_close = close.shift(1)
    
    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()
    
    # True Range is the maximum of the three
    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    
    # ATR is the moving average of True Range
    atr = true_range.rolling(window=period, min_periods=period).mean()
    
    return atr


def detect_sma_trend(sma_series: pd.Series, lookback: int = 5, tolerance: float = 0.001) -> pd.Series:
    """
    Detect if SMA is rising, falling, or flat
    
    Compares current SMA value to value 'lookback' periods ago
    Uses tolerance threshold to determine if trend is flat
    
    Args:
        sma_series: Series of SMA values
        lookback: Number of days to look back for comparison (default 5)
        tolerance: Percentage tolerance for flat trend (default 0.001 = 0.1%)
        
    Returns:
        Series with trend labels: 'rising', 'falling', or 'flat'
    """
    prev_sma = sma_series.shift(lookback)
    
    # Calculate percentage change
    pct_change = (sma_series - prev_sma) / prev_sma
    
    # Determine trend based on percentage change and tolerance
    def classify_trend(pct_chg):
        if pd.isna(pct_chg):
            return None
        elif pct_chg > tolerance:
            return 'rising'
        elif pct_chg < -tolerance:
            return 'falling'
        else:
            return 'flat'
    
    trend = pct_change.apply(classify_trend)
    
    return trend


def calculate_all_indicators(df: pd.DataFrame, 
                             sma_short_period: int = 50,
                             sma_long_period: int = 200,
                             atr_period: int = 14,
                             trend_lookback: int = 5,
                             trend_tolerance: float = 0.001) -> pd.DataFrame:
    """
    Calculate all technical indicators and add them to the dataframe
    
    Args:
        df: DataFrame with OHLC data (must have columns: High, Low, Close)
        sma_short_period: Period for short-term SMA (default 50)
        sma_long_period: Period for long-term SMA (default 200)
        atr_period: Period for ATR calculation (default 14)
        trend_lookback: Days to look back for trend detection (default 5)
        trend_tolerance: Tolerance for flat trend detection (default 0.001)
        
    Returns:
        DataFrame with added indicator columns
    """
    # Make a copy to avoid modifying original
    result = df.copy()
    
    # Calculate SMAs
    result['SMA_50'] = calculate_sma(result['Close'], sma_short_period)
    result['SMA_200'] = calculate_sma(result['Close'], sma_long_period)
    
    # Calculate ATR
    result['ATR'] = calculate_atr(result['High'], result['Low'], result['Close'], atr_period)
    
    # Detect SMA trends
    result['SMA_50_Trend'] = detect_sma_trend(result['SMA_50'], trend_lookback, trend_tolerance)
    result['SMA_200_Trend'] = detect_sma_trend(result['SMA_200'], trend_lookback, trend_tolerance)
    
    return result


