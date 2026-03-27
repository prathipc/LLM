"""
Configuration module for QQQ Trading Simulator
Contains all parameters, constants, and file paths
"""
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = DATA_DIR

# Input data file
DATA_FILE = DATA_DIR / "QQQ.xlsx"

# Output files
DAILY_LEDGER_FILE = OUTPUT_DIR / "daily_ledger.csv"
TRANSACTION_LEDGER_FILE = OUTPUT_DIR / "transactions.csv"
SUMMARY_REPORT_FILE = OUTPUT_DIR / "summary_report.txt"
PORTFOLIO_CHART_FILE = OUTPUT_DIR / "portfolio_value_chart.png"
DRAWDOWN_CHART_FILE = OUTPUT_DIR / "drawdown_chart.png"

# Trading parameters
INITIAL_BALANCE = 10000.0  # Starting portfolio value in dollars

# Technical indicator periods
SMA_SHORT_PERIOD = 50   # 50-day simple moving average
SMA_LONG_PERIOD = 200   # 200-day simple moving average
ATR_PERIOD = 14         # 14-day Average True Range

# SMA trend detection
SMA_TREND_LOOKBACK = 5  # Days to look back for trend detection
SMA_TREND_TOLERANCE = 0.001  # Tolerance for flat trend (0.1%)

# Volatility override (optional)
ENABLE_VOLATILITY_OVERRIDE = False  # Set to True to enable ATR-based cash override
ATR_THRESHOLD = None  # Set a threshold (e.g., 25.0) to trigger cash position on high volatility

# Transaction costs
TRANSACTION_COST_PER_TRADE = 0.0  # Commission per trade in dollars

# Trading signals
SIGNAL_100_TQQQ = "100% TQQQ"
SIGNAL_50_TQQQ = "50% TQQQ / 50% Cash"
SIGNAL_100_SQQQ = "100% SQQQ"
SIGNAL_100_CASH = "100% Cash"

# Asset names
ASSET_TQQQ = "TQQQ"
ASSET_SQQQ = "SQQQ"
ASSET_CASH = "Cash"

# Required columns in QQQ.xlsx
REQUIRED_COLUMNS = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'TQQQ_Price', 'SQQQ_Price']

# Minimum data requirements
MIN_DATA_DAYS = SMA_LONG_PERIOD + 1  # Need at least 200+ days for indicators


