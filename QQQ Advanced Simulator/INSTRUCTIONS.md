# How to Run the QQQ Advanced Simulator

## Quick Start

Open a terminal and run:

```bash
cd "/Users/prathip_priya/Documents/Cursor/QQQ Advanced Simulator"
python3 src/main_fixed.py
```

## What the Program Does

1. **Loads Data** - Reads QQQ, TQQQ, and SQQQ price data from `data/Input Files/QQQ.xlsx`
2. **Filters Data** - Uses only data from January 2021 onwards
3. **Calculates Indicators** - Computes SMAs, slopes, ATR, volume ratios, momentum, and market regime
4. **Runs Simulation** - Executes trading strategy with all rules from the functional document
5. **Generates Reports** - Creates comprehensive analysis and charts

## Expected Performance

- Data Loading: ~0.1 seconds
- Indicator Calculation: ~0.07 seconds  
- Trading Simulation: ~0.13 seconds
- Report Generation: ~1-2 seconds
- **Total Runtime: ~2-3 seconds**

## Output Files

All outputs are saved to: `data/Output Files/`

### Generated Files:

1. **daily_ledger.csv** - Complete day-by-day portfolio state
   - Date, prices, positions, portfolio value, indicators
   
2. **transactions.csv** - All trades executed
   - Entry/exit dates, prices, shares, P&L
   
3. **summary_report.txt** - Performance metrics summary
   - Returns, Sharpe ratio, max drawdown, win rate, etc.
   
4. **portfolio_value_chart.png** - Portfolio growth over time
   
5. **drawdown_chart.png** - Drawdown analysis
   
6. **positions_chart.png** - Position timeline with QQQ price
   
7. **momentum_indicators_chart.png** - Technical indicators visualization

## Troubleshooting

### If you get "Module not found" errors:

```bash
pip3 install pandas numpy matplotlib openpyxl
```

### If matplotlib hangs:

The program already uses `matplotlib.use('Agg')` to prevent GUI issues.

### If you want to test with different date ranges:

Edit line 62 in `src/main_fixed.py`:
```python
start_date = pd.Timestamp('2021-01-01')  # Change this date
```

## Program Structure

```
src/
├── config.py          - All parameters and settings
├── indicators.py      - Technical indicator calculations
├── trade_engine.py    - Trading logic and rules
├── reporting.py       - Report generation and charts
└── main_fixed.py      - Main orchestration (RUN THIS)
```

## Configuration

All strategy parameters are in `src/config.py`:

- Initial Capital: $10,000
- SMA Periods: 50 and 200 days
- Buffer Percentages: 1.5-3%
- Stop Loss Levels: 6-8%
- Transaction Costs: $0 + 0.1% slippage

## Notes

- The program processes ~1,030 trading days from 2021-2025
- All trading rules from the functional document are implemented
- Progress updates are shown every 50 trading days
- Charts are saved as high-resolution PNG files (300 DPI)

