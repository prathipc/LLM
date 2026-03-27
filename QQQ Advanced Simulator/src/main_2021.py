"""
TEST VERSION - Starting from Jan 2021
"""

import pandas as pd
import numpy as np
import os
import sys
from datetime import datetime

# Import modules
from config import *
from indicators import calculate_all_indicators
from trade_engine import TradeEngine
from reporting import generate_all_reports


def load_data(file_path):
    """Load price data from Excel file - Starting from Jan 2021"""
    print("=" * 70)
    print("LOADING DATA (FROM JAN 2021)")
    print("=" * 70)
    
    try:
        # Read all three sheets
        print("Reading QQQ sheet...")
        df_qqq = pd.read_excel(file_path, sheet_name='QQQ')
        print(f"  Loaded QQQ data: {len(df_qqq)} rows")
        
        print("Reading TQQQ sheet...")
        df_tqqq = pd.read_excel(file_path, sheet_name='TQQQ')
        print(f"  Loaded TQQQ data: {len(df_tqqq)} rows")
        
        print("Reading SQQQ sheet...")
        df_sqqq = pd.read_excel(file_path, sheet_name='SQQQ')
        print(f"  Loaded SQQQ data: {len(df_sqqq)} rows")
        
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Merge dataframes on Date
    print("\nMerging data...")
    df = df_qqq.copy()
    
    # Ensure Date is datetime
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Merge TQQQ data
    if 'Date' in df_tqqq.columns and 'Close' in df_tqqq.columns:
        df_tqqq['Date'] = pd.to_datetime(df_tqqq['Date'])
        df_tqqq_subset = df_tqqq[['Date', 'Close']].rename(columns={'Close': 'TQQQ_Close'})
        df = df.merge(df_tqqq_subset, on='Date', how='left')
        print(f"  Merged TQQQ data")
    
    # Merge SQQQ data
    if 'Date' in df_sqqq.columns and 'Close' in df_sqqq.columns:
        df_sqqq['Date'] = pd.to_datetime(df_sqqq['Date'])
        df_sqqq_subset = df_sqqq[['Date', 'Close']].rename(columns={'Close': 'SQQQ_Close'})
        df = df.merge(df_sqqq_subset, on='Date', how='left')
        print(f"  Merged SQQQ data")
    
    # Filter to Jan 2021 onwards
    df = df.sort_values('Date').reset_index(drop=True)
    start_date = pd.to_datetime('2021-01-01')
    df = df[df['Date'] >= start_date].reset_index(drop=True)
    
    print(f"\nFiltered to Jan 2021 onwards: {len(df)} rows")
    print(f"Date range: {df['Date'].min()} to {df['Date'].max()}")
    print(f"Columns: {df.columns.tolist()}")
    
    return df


def prepare_data(df):
    """Prepare and validate data"""
    print("\n" + "=" * 70)
    print("PREPARING DATA")
    print("=" * 70)
    
    data = df.copy()
    
    # Fill forward any missing TQQQ/SQQQ prices
    if COL_TQQQ_CLOSE in data.columns:
        missing_tqqq = data[COL_TQQQ_CLOSE].isna().sum()
        if missing_tqqq > 0:
            print(f"Filling {missing_tqqq} missing TQQQ prices...")
            data[COL_TQQQ_CLOSE] = data[COL_TQQQ_CLOSE].ffill()
    
    if COL_SQQQ_CLOSE in data.columns:
        missing_sqqq = data[COL_SQQQ_CLOSE].isna().sum()
        if missing_sqqq > 0:
            print(f"Filling {missing_sqqq} missing SQQQ prices...")
            data[COL_SQQQ_CLOSE] = data[COL_SQQQ_CLOSE].ffill()
    
    # Remove rows with missing QQQ data
    initial_rows = len(data)
    data = data.dropna(subset=[COL_QQQ_CLOSE])
    removed_rows = initial_rows - len(data)
    
    if removed_rows > 0:
        print(f"Removed {removed_rows} rows with missing QQQ data")
    
    print(f"\nData prepared: {len(data)} rows")
    print(f"Date range: {data['Date'].min().date()} to {data['Date'].max().date()}")
    print(f"QQQ price range: ${data[COL_QQQ_CLOSE].min():.2f} to ${data[COL_QQQ_CLOSE].max():.2f}")
    
    return data


def run_backtest(data, initial_capital=INITIAL_CAPITAL):
    """Run the backtest simulation"""
    print("\n" + "=" * 70)
    print("RUNNING BACKTEST")
    print("=" * 70)
    print(f"Initial Capital: ${initial_capital:,.2f}")
    print(f"Trading Period: {data['Date'].min().date()} to {data['Date'].max().date()}")
    print(f"Total Days: {len(data)}")
    
    # Initialize trade engine
    engine = TradeEngine(initial_capital)
    
    # Process each day
    print("\nProcessing trades...")
    for idx, row in data.iterrows():
        date = row['Date']
        engine.process_day(date, row)
        
        # Print progress every 25 days
        if (idx + 1) % 25 == 0 or (idx + 1) == len(data):
            pct_complete = ((idx + 1) / len(data)) * 100
            print(f"  Day {idx + 1}/{len(data)} ({pct_complete:.1f}%) - Portfolio: ${engine.get_portfolio_value(row.get('TQQQ_Close', 0), row.get('SQQQ_Close', 0)):,.2f}", end='\r')
    
    print(f"\n\nBacktest Complete!")
    
    # Get final results
    ledger_df = engine.get_ledger_df()
    trades_df = engine.get_trades_df()
    
    final_value = ledger_df['Portfolio_Value'].iloc[-1] if len(ledger_df) > 0 else initial_capital
    total_return = ((final_value - initial_capital) / initial_capital) * 100
    
    print(f"\nFinal Portfolio Value: ${final_value:,.2f}")
    print(f"Total Return: {total_return:.2f}%")
    print(f"Total Trades: {len(trades_df)}")
    
    return engine


def main():
    """Main execution function"""
    print("\n" + "=" * 70)
    print("ENHANCED LEVERAGED ETF STRATEGY v2.0")
    print("TEST RUN FROM JANUARY 2021")
    print("=" * 70)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Get paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(script_dir, INPUT_FILE_PATH)
    output_dir = os.path.join(script_dir, OUTPUT_DIR)
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"ERROR: Input file not found: {input_file}")
        sys.exit(1)
    
    try:
        # Load data
        raw_data = load_data(input_file)
        
        # Prepare data
        clean_data = prepare_data(raw_data)
        
        # Calculate indicators
        print("\n" + "=" * 70)
        print("CALCULATING TECHNICAL INDICATORS")
        print("=" * 70)
        print("Calculating SMAs, ATR, Volume Ratios, Momentum...")
        data_with_indicators = calculate_all_indicators(clean_data)
        print("✓ All indicators calculated")
        
        # Remove rows where indicators can't be calculated
        min_required_days = max(SMA_LONG_PERIOD, ATR_PERIOD, VOLUME_PERIOD) + SMA_SLOPE_LOOKBACK
        data_ready = data_with_indicators.iloc[min_required_days:].reset_index(drop=True)
        print(f"✓ Data ready for trading: {len(data_ready)} rows (after {min_required_days} day warmup)")
        
        if len(data_ready) == 0:
            print(f"\nERROR: Not enough data. Need at least {min_required_days} days.")
            sys.exit(1)
        
        # Run backtest
        engine = run_backtest(data_ready, INITIAL_CAPITAL)
        
        # Generate reports
        print("\n" + "=" * 70)
        print("GENERATING REPORTS")
        print("=" * 70)
        
        ledger_df = engine.get_ledger_df()
        trades_df = engine.get_trades_df()
        
        metrics = generate_all_reports(ledger_df, trades_df, INITIAL_CAPITAL, output_dir)
        
        print("\n" + "=" * 70)
        print("✓ BACKTEST COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Outputs saved to: {output_dir}\n")
        
    except Exception as e:
        print(f"\n{'=' * 70}")
        print("ERROR OCCURRED")
        print("=" * 70)
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

