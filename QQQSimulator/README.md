# QQQ Leveraged ETF Automated Trading Simulator

A sophisticated backtesting system for automated trading strategies using QQQ (NASDAQ-100 ETF) and its leveraged counterparts TQQQ (3x bull) and SQQQ (3x bear).

## Overview

This simulator implements a rule-based trading strategy using technical indicators (SMA and ATR) to systematically trade between TQQQ, SQQQ, and cash positions. It provides comprehensive performance tracking, transaction logging, and visualization capabilities.

## Features

- **Technical Analysis**: Calculates 50-day and 200-day Simple Moving Averages (SMA) and 14-day Average True Range (ATR)
- **Automated Trading Rules**: Implements a sophisticated rulebook for position allocation
- **Portfolio Management**: Tracks positions, executes rebalancing, and compounds returns
- **Performance Metrics**: Calculates CAGR, total return, maximum drawdown, and trade statistics
- **Comprehensive Outputs**: Generates CSV ledgers, performance reports, and visual charts
- **Configurable Parameters**: Easy customization of all trading parameters

## Installation

### Prerequisites

- Python 3.8 or higher
- Required packages listed in `requirements.txt`

### Setup

```bash
# Install dependencies
pip install -r requirements.txt
```

## Usage

### Running the Simulator

```bash
cd QQQSimulator
python -m src.main
```

The simulator will prompt you to enter a start date in MM-YYYY format (e.g., 01-2020).

### Input Data

The simulator expects a file `data/QQQ.xlsx` with the following columns:
- Date
- Open (or QQQ Open Price)
- High (or QQQ High Price)
- Low (or QQQ Low Price)
- Close (or QQQ Close Price)
- Volume
- TQQQ_Price (or TQQQ Price)
- SQQQ_Price (or SQQQ Price)

## Trading Rules

The simulator applies the following rules based on technical indicators:

1. **100% TQQQ**: When QQQ > 50d SMA AND QQQ > 200d SMA AND 50d SMA is rising
2. **50% TQQQ / 50% Cash**: When QQQ > both SMAs but 50d SMA is flat/falling
3. **100% SQQQ**: When QQQ < 50d SMA AND QQQ < 200d SMA AND both SMAs are falling
4. **100% Cash**: All other market conditions (default safe position)
5. **Volatility Override** (optional): Force cash position when ATR exceeds threshold

## Configuration

Edit `src/config.py` to customize:

- `INITIAL_BALANCE`: Starting portfolio value (default: $10,000)
- `SMA_SHORT_PERIOD`: Short-term SMA period (default: 50 days)
- `SMA_LONG_PERIOD`: Long-term SMA period (default: 200 days)
- `ATR_PERIOD`: ATR calculation period (default: 14 days)
- `SMA_TREND_LOOKBACK`: Days for trend detection (default: 5 days)
- `ENABLE_VOLATILITY_OVERRIDE`: Enable/disable ATR-based cash override
- `ATR_THRESHOLD`: Threshold for volatility override (if enabled)

## Outputs

The simulator generates the following files in the `data/` directory:

### 1. Daily Ledger (`daily_ledger.csv`)
Complete daily record of:
- Market indicators (QQQ price, SMAs, ATR)
- Trading signals
- Actions taken
- Positions held (TQQQ, SQQQ, Cash)
- Portfolio value

### 2. Transaction Ledger (`transactions.csv`)
Detailed record of every trade:
- Date, asset, action (buy/sell)
- Quantity, price, amount
- Portfolio value before/after

### 3. Performance Summary (`summary_report.txt`)
Comprehensive performance analysis:
- Total return and CAGR
- Maximum drawdown
- Trade statistics
- Asset allocation breakdown

### 4. Performance Charts
- `portfolio_value_chart.png`: Portfolio value over time
- `drawdown_chart.png`: Drawdown from peak analysis

## Example Results

**Sample backtest from January 2020:**
- Duration: 3.63 years
- Initial Value: $10,000
- Final Value: $14,543.56
- Total Return: 45.44%
- CAGR: 10.87%
- Maximum Drawdown: -60.58%
- Number of Trades: 58

## Project Structure

```
QQQSimulator/
├── src/
│   ├── __init__.py
│   ├── config.py           # Configuration parameters
│   ├── indicators.py       # Technical indicator calculations
│   ├── trade_engine.py     # Trading logic and position management
│   └── main.py            # Main program orchestration
├── data/
│   ├── QQQ.xlsx           # Input data file
│   ├── daily_ledger.csv   # Daily position records (output)
│   ├── transactions.csv   # Transaction log (output)
│   ├── summary_report.txt # Performance summary (output)
│   └── *.png             # Performance charts (output)
├── requirements.txt       # Python dependencies
├── README.md             # This file
└── VALIDATION.md         # Validation report

```

## Technical Details

### Indicator Calculations

**Simple Moving Average (SMA)**:
```python
SMA = sum(prices[-n:]) / n
```

**Average True Range (ATR)**:
```python
TR = max(high - low, abs(high - prev_close), abs(low - prev_close))
ATR = moving_average(TR, period)
```

**Trend Detection**:
```python
trend = 'rising' if (current_SMA - SMA_5_days_ago) / SMA_5_days_ago > 0.001
       'falling' if (current_SMA - SMA_5_days_ago) / SMA_5_days_ago < -0.001
       'flat' otherwise
```

### Position Management

- Trades execute at end-of-day closing prices
- Fractional shares supported for precise allocation
- Full position liquidation before reallocation
- No transaction costs (configurable to $0)
- Automatic compounding of returns

## Validation

See `VALIDATION.md` for a comprehensive validation report confirming all functional requirements are met.

## Notes

- The simulator uses end-of-day prices and assumes perfect execution
- No slippage or market impact modeling
- Historical data only - not for live trading
- Past performance does not guarantee future results
- Leveraged ETFs carry significant risk

## License

This project is for educational and research purposes.

## Author

Created as a comprehensive backtesting tool for QQQ leveraged ETF trading strategies.
