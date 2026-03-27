"""
Configuration Parameters for Enhanced Leveraged ETF Strategy v2.0
"""

import os

# File Paths
INPUT_FILE_PATH = "../data/Input Files/QQQ.xlsx"
OUTPUT_DIR = "../data/Output Files/"

# Initial Capital
INITIAL_CAPITAL = 10000.0

# Transaction Costs
TRANSACTION_FEE = 0.00  # Per-trade fee in dollars
SLIPPAGE = 0.001  # 0.1% slippage assumption

# SMA Parameters
SMA_SHORT_PERIOD = 50
SMA_LONG_PERIOD = 200
SMA_SLOPE_LOOKBACK = 5  # Days for slope calculation

# Buffer Percentages (defaults = strict rulebook)
BUFFER_ENTRY_50SMA = 0.015  # 1.5% above 50-SMA for entry
BUFFER_EXIT_50SMA = 0.025   # 2.5% below 50-SMA for exit
BUFFER_ENTRY_200SMA = 0.02  # 2% above 200-SMA
BUFFER_EXIT_200SMA = 0.03   # 3% below 200-SMA

# Stop Loss Parameters
STOP_LOSS_100_TQQQ = 0.08  # 8% hard stop for 100% TQQQ
STOP_LOSS_50_TQQQ = 0.06   # 6% hard stop for 50% TQQQ
STOP_LOSS_SQQQ = 0.06      # 6% stop for SQQQ positions
STOP_LOSS_100_SQQQ = 0.08  # 8% stop for 100% SQQQ

# Trailing Stop Parameters
TRAILING_STOP_TRIGGER = 0.15   # 15% gain to activate trailing
TRAILING_STOP_DISTANCE = 0.10  # 10% trailing stop

# ATR Parameters
ATR_PERIOD = 14
ATR_THRESHOLD_NORMAL = 0.025   # 2.5% in normal markets
ATR_THRESHOLD_BULL = 0.030     # 3.0% in strong trends
ATR_THRESHOLD_CHOPPY = 0.020   # 2.0% in transitions
ATR_THRESHOLD_CRISIS = 0.015   # 1.5% in crisis

# Volume Parameters
VOLUME_PERIOD = 20
VOLUME_RATIO_LOW = 0.90
VOLUME_RATIO_MODERATE = 1.10
VOLUME_RATIO_HIGH = 1.25

# Momentum Thresholds
MOMENTUM_VERY_STRONG_POSITIVE = 0.5
MOMENTUM_MODERATE_POSITIVE = 0.2
MOMENTUM_NEUTRAL_LOW = -0.2
MOMENTUM_MODERATE_NEGATIVE = -0.5

# Position Sizing
POSITION_100_TQQQ = 1.00
POSITION_75_TQQQ = 0.75
POSITION_50_TQQQ = 0.50
POSITION_50_SQQQ = 0.50
POSITION_100_SQQQ = 1.00
POSITION_CASH = 0.00

# Market Regime Thresholds
SLOPE_BULL_THRESHOLD = 0.5      # Weekly slope > 0.5% is bull
SLOPE_BEAR_THRESHOLD = -0.5     # Weekly slope < -0.5% is bear
SLOPE_NEUTRAL_RANGE = 0.2       # Within +/- 0.2% is neutral

# Excel Column Names (matching actual Excel file structure)
COL_DATE = 'Date'
COL_CLOSE = 'QQQ Close Price'
COL_OPEN = 'QQQ Open Price'
COL_HIGH = 'QQQ High Price'
COL_LOW = 'QQQ Low Price'
COL_VOLUME = 'Volume'
COL_TQQQ_CLOSE = 'TQQQ Price'
COL_SQQQ_CLOSE = 'SQQQ Price'

# Aliases for backward compatibility
COL_QQQ_CLOSE = COL_CLOSE
COL_QQQ_OPEN = COL_OPEN
COL_QQQ_HIGH = COL_HIGH
COL_QQQ_LOW = COL_LOW
COL_QQQ_VOLUME = COL_VOLUME

# ------------------------------------------------------------------
# Adaptive Parameter Modes
# ------------------------------------------------------------------
# By default we run in "backtest" mode to make the engine more active.
# Set environment variable QQQ_STRATEGY_MODE=strict to use the
# original rulebook thresholds without overrides.
STRATEGY_MODE = os.getenv("QQQ_STRATEGY_MODE", "backtest").lower()

if STRATEGY_MODE == "backtest":
    # Relax entry buffers so we can participate in more trends
    BUFFER_ENTRY_50SMA = 0.005  # 0.5% above 50-SMA
    BUFFER_ENTRY_200SMA = 0.01  # 1% above 200-SMA

    # Open up the neutral band so Rule 5 can fire more often
    MOMENTUM_VERY_STRONG_POSITIVE = 0.3
    MOMENTUM_MODERATE_POSITIVE = 0.1
    MOMENTUM_NEUTRAL_LOW = -0.3

    # Loosen volume confirmations
    VOLUME_RATIO_LOW = 0.70
    VOLUME_RATIO_MODERATE = 0.90
    VOLUME_RATIO_HIGH = 1.00

    # Reduce ATR-based lock-outs
    ATR_THRESHOLD_NORMAL = 0.030
    ATR_THRESHOLD_BULL = 0.035
    ATR_THRESHOLD_CHOPPY = 0.025
    ATR_THRESHOLD_CRISIS = 0.020

