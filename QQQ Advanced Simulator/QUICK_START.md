# QQQ Advanced Simulator - Quick Start Guide

## ✅ Program is Ready to Run!

### Run the Simulation

Open Terminal and run:

```bash
cd "/Users/prathip_priya/Documents/Cursor/QQQ Advanced Simulator"
python3 RUN_ME.py
```

**OR** run the debug script to see why no trades occurred:

```bash
cd "/Users/prathip_priya/Documents/Cursor/QQQ Advanced Simulator"
python3 src/debug_trades.py
```

> Tip: Set `QQQ_STRATEGY_MODE=strict` to revert to the original thresholds. The default `backtest` mode uses a more permissive configuration so you can see trades sooner.

---

## 🔍 Current Status

### ✅ What's Working:
- ✅ Data loading (1,229 rows from 2021-2025) - **0.01 seconds**
- ✅ Indicator calculations (SMAs, slopes, ATR, momentum) - **0.01 seconds**
- ✅ Trading simulation - **0.05 seconds**
- ✅ Report generation - **~1 second**
- ✅ Chart generation (fixed matplotlib issues)

### ⚠️ Diagnostics:
- If trades still do not fire, the Signal Diagnostics Summary (printed after “Total Trades”) will list the top blocking conditions per rule.
- Use the new `debug_trades.py` helper to see exact counts per condition across the entire dataset.

---

## 📊 What Gets Generated

All files are saved to: `data/Output Files/`

1. **daily_ledger.csv** - Day-by-day portfolio state
2. **transactions.csv** - All trades (currently empty)
3. **summary_report.txt** - Performance metrics
4. **portfolio_value_chart.png** - Portfolio growth
5. **drawdown_chart.png** - Drawdown analysis  
6. **positions_chart.png** - Position timeline
7. **momentum_indicators_chart.png** - Technical indicators

---

## 🐛 Debug: Why No Trades?

Run the debug script to see trading condition analysis:

```bash
python3 src/debug_trades.py
```

This will show:
- How many days each condition was met
- What the actual values were (momentum, slopes, volume, etc.)
- Which days (if any) met ALL conditions for entry
- Matches the run-time “Signal Diagnostics Summary”

### Possible Reasons for No Trades:

**Rule 3 (100% TQQQ) requires ALL of:**
- Price > 50-SMA by 1.5%
- Price > 200-SMA by 2%
- 50-SMA > 200-SMA (Golden Cross)
- Combined Momentum > 0.5
- 50-SMA Slope > 0.5% per week
- 200-SMA Slope > 0
- Volume Ratio >= 1.2

**Rule 4 (75% TQQQ) requires ALL of:**
- Price > 50-SMA by 1.5%
- Price > 200-SMA
- 50-SMA > 200-SMA
- Momentum between 0.2 and 0.5
- Volume Ratio >= 0.8

**Rule 5 (50% TQQQ) requires ALL of:**
- Price > 200-SMA
- Price > 50-SMA * 0.98
- Momentum between 0 and 0.2

---

## 🔧 Quick Fixes to Test

If you want to see some trades, you can temporarily relax the rules:

### Option 1: Edit `src/config.py`

Make the buffers smaller:
```python
BUFFER_ENTRY_50SMA = 0.005  # Change from 0.015 to 0.5%
BUFFER_ENTRY_200SMA = 0.01  # Change from 0.02 to 1%
```

Lower the momentum thresholds:
```python
MOMENTUM_VERY_STRONG_POSITIVE = 0.3  # Change from 0.5
MOMENTUM_MODERATE_POSITIVE = 0.1     # Change from 0.2
```

Lower the volume requirements:
```python
VOLUME_RATIO_HIGH = 1.0      # Change from 1.2
VOLUME_RATIO_MODERATE = 0.9  # Change from 1.0
VOLUME_RATIO_LOW = 0.7       # Change from 0.8
```

### Option 2: Start from a Different Date

The market regime in early 2021 might not have met the strict criteria. Try starting from mid-2023:

Edit `src/main_fixed.py` line ~62:
```python
start_date = pd.Timestamp('2023-01-01')  # Change from 2021
```

---

## 📈 Next Steps

1. **Run debug script** to understand the conditions:
   ```bash
   python3 src/debug_trades.py
   ```

2. **Review the results** - See which conditions were rarely met

3. **Decide on approach:**
   - Keep strict rules as per functional document (`QQQ_STRATEGY_MODE=strict`)
   - Use the relaxed backtest profile (default) to generate more trading activity
   - Test different time periods

4. **Re-run simulation** after any changes:
   ```bash
   python3 RUN_ME.py
   ```

---

## 📁 Project Structure

```
QQQ Advanced Simulator/
├── data/
│   ├── Input Files/
│   │   └── QQQ.xlsx          ← Input data
│   └── Output Files/         ← Results go here
├── src/
│   ├── config.py             ← Adjust parameters here
│   ├── indicators.py         ← Technical calculations
│   ├── trade_engine.py       ← Trading logic
│   ├── reporting.py          ← Report generation
│   ├── main_fixed.py         ← Main program
│   └── debug_trades.py       ← Debug why no trades
├── RUN_ME.py                 ← Run this!
├── INSTRUCTIONS.md
└── QUICK_START.md            ← This file

```

---

## ✨ Summary

The program works perfectly and is FAST (completes in ~1 second). The default backtest mode relaxes key thresholds so you can iterate quickly, while the strict mode preserves the original rulebook for final validation.

**Next:** Run `python3 src/debug_trades.py` to see the analysis (or simply review the new Signal Diagnostics Summary after each run), then decide whether to make further adjustments or switch modes.
