# Enhanced Leveraged ETF Strategy v2.0

A comprehensive Python-based backtesting system for trading leveraged ETFs (TQQQ and SQQQ) based on QQQ price action, technical indicators, and a sophisticated rule-based trading strategy.

## Overview

This program implements a systematic trading strategy that:
- Analyzes QQQ price movements using technical indicators
- Makes buy/sell decisions for leveraged ETFs (TQQQ and SQQQ)
- Manages positions with stop-loss and trailing stops
- Generates comprehensive performance reports and visualizations

## Features

### Technical Indicators
- 50-day and 200-day Simple Moving Averages (SMA)
- SMA Slopes (momentum analysis)
- 14-day Average True Range (ATR)
- 20-day Volume Ratio
- Combined Momentum Score
- Market Regime Detection (Bull/Bear/Transition/Choppy)

### Trading Rules
1. **Death Cross Protection** - Immediate exit to cash when 50-SMA crosses below 200-SMA
2. **Volatility Management** - Reduces exposure during high volatility periods
3. **Position Sizing** - Dynamic allocation from 0% to 100% based on market conditions
4. **Stop Loss Protection** - Hard stops and trailing stops to protect capital
5. **Volume Confirmation** - Uses volume analysis to validate signals
6. **Multi-timeframe Analysis** - Considers both short and long-term trends

### Position Types
- 100% TQQQ (Strong Bull Signal)
- 75% TQQQ + 25% Cash (Moderate Bull)
- 50% TQQQ + 50% Cash (Conservative Bull)
- 100% Cash (Neutral/Defensive)
- 50% SQQQ + 50% Cash (Moderate Bear)
- 100% SQQQ (Strong Bear Signal)

## Installation

### Requirements
- Python 3.8 or higher
- pip (Python package installer)

### Setup

1. Clone or download this repository

2. Install required packages:
```bash
pip install -r requirements.txt
```

Or install packages individually:
```bash
pip install pandas numpy matplotlib openpyxl
```

## Usage

### Input Data

Place your Excel file with QQQ, TQQQ, and SQQQ price data in:
```
data/Input Files/QQQ.xlsx
```

The Excel file should have three sheets:
- **QQQ** sheet with columns: Date, Close, High, Low, Volume
- **TQQQ** sheet with columns: Date, Close
- **SQQQ** sheet with columns: Date, Close

### Running the Backtest

Navigate to the src directory and run:
```bash
cd src
python main.py
```

### Output

The program will generate the following outputs in `data/Output Files/`:

1. **summary_report.txt** - Comprehensive performance metrics
2. **daily_ledger.csv** - Daily portfolio state and positions
3. **transactions.csv** - All buy/sell transactions
4. **portfolio_value_chart.png** - Portfolio value over time
5. **drawdown_chart.png** - Drawdown analysis
6. **position_distribution_chart.png** - Position allocation over time
7. **momentum_indicators_chart.png** - Technical indicators visualization

## Performance Metrics

The system calculates:
- Total Return (%)
- Compound Annual Growth Rate (CAGR)
- Maximum Drawdown
- Sharpe Ratio
- Sortino Ratio
- Annual Volatility
- Win Rate
- Trade Statistics
- Position Distribution

## Configuration

Edit `src/config.py` to customize:
- Initial capital
- Transaction fees and slippage
- Buffer percentages
- Stop loss thresholds
- ATR thresholds
- Volume ratios
- Momentum thresholds

### Strategy Modes

The configuration now supports two parameter presets:

- **Backtest mode (default):** Relaxed thresholds so signals fire more often (`QQQ_STRATEGY_MODE=backtest`).
- **Strict mode:** Original rulebook values for production (`QQQ_STRATEGY_MODE=strict`).

Set the mode via environment variable before running:

```bash
export QQQ_STRATEGY_MODE=strict   # or backtest
python3 RUN_ME.py
```

### Signal Diagnostics

The trading engine now logs which rule conditions are blocking entries. After each run you’ll see a “Signal Diagnostics Summary” that highlights the highest miss percentages per rule. Use this to tune buffers, momentum, or volume filters without guesswork.

## Project Structure

```
QQQ Advanced Simulator/
├── src/
│   ├── config.py           # Configuration parameters
│   ├── indicators.py       # Technical indicator calculations
│   ├── trade_engine.py     # Trading logic and execution
│   ├── reporting.py        # Report generation and visualization
│   └── main.py            # Main orchestration script
├── data/
│   ├── Input Files/       # Place input Excel files here
│   └── Output Files/      # Generated reports and charts
├── FD/                    # Functional documentation
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Strategy Rules Priority

The trading engine evaluates rules in the following priority order:

1. **Exit Conditions** (highest priority)
   - Death Cross detection
   - Stop loss hits
   - Trailing stop hits
   - Buffer breaches

2. **Volatility Checks**
   - High ATR warnings
   - Regime-based adjustments

3. **Entry Signals**
   - Bullish conditions for TQQQ
   - Bearish conditions for SQQQ
   - Neutral conditions for Cash

## Risk Management

The strategy implements multiple layers of risk management:
- **Hard Stop Losses**: 6-8% stops depending on position size
- **Trailing Stops**: Activated after 15% gain, trails by 10%
- **Position Sizing**: Scales from 50% to 100% based on conviction
- **Volatility Filters**: Reduces exposure during market stress
- **Volume Confirmation**: Requires volume support for entries

## Backtesting Methodology

The system:
1. Loads historical price data
2. Calculates technical indicators for each day
3. Evaluates trading rules in priority order
4. Simulates trade execution with realistic slippage
5. Tracks portfolio value and positions daily
6. Generates comprehensive performance analytics

## Limitations

- Past performance does not guarantee future results
- Simulated results include assumptions about slippage and fees
- Market conditions can change, affecting strategy performance
- Leveraged ETFs have decay and tracking error
- Real-world execution may differ from backtested results

## Support

For questions or issues:
1. Review the Functional Documentation in the FD/ folder
2. Check configuration parameters in config.py
3. Verify input data format matches requirements

## Version History

- **v2.0** - Initial release with comprehensive rule engine

## License

This software is provided for educational and research purposes only. Use at your own risk. The authors are not responsible for any trading losses.

## Disclaimer

This is a backtesting tool for educational purposes. It should not be construed as investment advice. Always conduct your own research and consult with financial professionals before making investment decisions.
