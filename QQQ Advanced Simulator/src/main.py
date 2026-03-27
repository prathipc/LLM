"""
Main Orchestration Script for Enhanced Leveraged ETF Strategy v2.0

This script:
1. Loads QQQ, TQQQ, and SQQQ price data from Excel
2. Calculates all technical indicators
3. Simulates trading using the rule-based engine
4. Generates comprehensive reports and charts
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
    """
    Load price data from Excel file
    
    Args:
        file_path: path to Excel file
    
    Returns:
        pandas DataFrame with required columns
    """
    print("=" * 70)
    print("LOADING DATA")
    print("=" * 70)
    
    # Try to read Excel file
    try:
        # Read QQQ sheet
        df_qqq = pd.read_excel(file_path, sheet_name='QQQ', engine='openpyxl')
        print(f"Loaded QQQ data: {len(df_qqq)} rows")
        
        # Read TQQQ sheet
        df_tqqq = pd.read_excel(file_path, sheet_name='TQQQ', engine='openpyxl')
        print(f"Loaded TQQQ data: {len(df_tqqq)} rows")
        
        # Read SQQQ sheet
        df_sqqq = pd.read_excel(file_path, sheet_name='SQQQ', engine='openpyxl')
        print(f"Loaded SQQQ data: {len(df_sqqq)} rows")
        
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        print("Attempting alternative column names...")
        
        # Try reading with default sheet
        df = pd.read_excel(file_path, engine='openpyxl')
        print(f"Loaded data: {len(df)} rows")
        print(f"Columns: {df.columns.tolist()}")
        return df
    
    # Merge dataframes on Date
    df = df_qqq.copy()
    
    # Merge TQQQ data
    if 'Date' in df_tqqq.columns and 'Close' in df_tqqq.columns:
        df_tqqq_subset = df_tqqq[['Date', 'Close']].rename(columns={'Close': 'TQQQ_Close'})
        df = df.merge(df_tqqq_subset, on='Date', how='left')
    
    # Merge SQQQ data
    if 'Date' in df_sqqq.columns and 'Close' in df_sqqq.columns:
        df_sqqq_subset = df_sqqq[['Date', 'Close']].rename(columns={'Close': 'SQQQ_Close'})
        df = df.merge(df_sqqq_subset, on='Date', how='left')
    
    print(f"Merged data: {len(df)} rows")
    print(f"Columns: {df.columns.tolist()}")
    
    return df


def prepare_data(df):
    """
    Prepare and validate data
    
    Args:
        df: raw DataFrame
    
    Returns:
        cleaned and validated DataFrame
    """
    print("\n" + "=" * 70)
    print("PREPARING DATA")
    print("=" * 70)
    
    # Make a copy
    data = df.copy()
    
    # Ensure Date column is datetime
    if 'Date' in data.columns:
        data['Date'] = pd.to_datetime(data['Date'])
    
    # Sort by date
    data = data.sort_values('Date').reset_index(drop=True)
    
    # Check for required columns
    required_cols = [COL_DATE, COL_QQQ_CLOSE, COL_QQQ_HIGH, COL_QQQ_LOW, COL_QQQ_VOLUME]
    missing_cols = [col for col in required_cols if col not in data.columns]
    
    if missing_cols:
        print(f"WARNING: Missing columns: {missing_cols}")
        print(f"Available columns: {data.columns.tolist()}")
    
    # Fill forward any missing TQQQ/SQQQ prices
    if COL_TQQQ_CLOSE in data.columns:
        data[COL_TQQQ_CLOSE] = data[COL_TQQQ_CLOSE].ffill()
    
    if COL_SQQQ_CLOSE in data.columns:
        data[COL_SQQQ_CLOSE] = data[COL_SQQQ_CLOSE].ffill()
    
    # Remove rows with missing QQQ data
    data = data.dropna(subset=[COL_QQQ_CLOSE])
    
    print(f"Data prepared: {len(data)} rows")
    print(f"Date range: {data['Date'].min()} to {data['Date'].max()}")
    print(f"QQQ price range: ${data[COL_QQQ_CLOSE].min():.2f} to ${data[COL_QQQ_CLOSE].max():.2f}")
    
    return data


def run_backtest(data, initial_capital=INITIAL_CAPITAL):
    """
    Run the backtest simulation
    
    Args:
        data: DataFrame with all indicators
        initial_capital: starting capital
    
    Returns:
        TradeEngine instance with results
    """
    print("\n" + "=" * 70)
    print("RUNNING BACKTEST")
    print("=" * 70)
    print(f"Initial Capital: ${initial_capital:,.2f}")
    print(f"Trading Period: {data['Date'].min()} to {data['Date'].max()}")
    print(f"Total Days: {len(data)}")
    
    # Initialize trade engine
    engine = TradeEngine(initial_capital)
    
    # Process each day
    print("\nProcessing trades...")
    for idx, row in data.iterrows():
        date = row['Date']
        engine.process_day(date, row)
        
        # Print progress every 50 days
        if (idx + 1) % 50 == 0:
            print(f"Processed {idx + 1}/{len(data)} days...", end='\r')
    
    print(f"\nProcessed {len(data)}/{len(data)} days - Complete!          ")
    
    # Get final results
    ledger_df = engine.get_ledger_df()
    trades_df = engine.get_trades_df()
    
    final_value = ledger_df['Portfolio_Value'].iloc[-1] if len(ledger_df) > 0 else initial_capital
    total_return = ((final_value - initial_capital) / initial_capital) * 100
    
    print(f"\nFinal Portfolio Value: ${final_value:,.2f}")
    print(f"Total Return: {total_return:.2f}%")
    print(f"Total Trades Executed: {len(trades_df)}")
    
    return engine


def main():
    """
    Main execution function
    """
    print("\n")
    print("=" * 70)
    print("ENHANCED LEVERAGED ETF STRATEGY v2.0 - BACKTESTING SYSTEM")
    print("=" * 70)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Get paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(script_dir, INPUT_FILE_PATH)
    output_dir = os.path.join(script_dir, OUTPUT_DIR)
    
    print(f"\nInput File: {input_file}")
    print(f"Output Directory: {output_dir}")
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"\nERROR: Input file not found: {input_file}")
        print("Please ensure the Excel file exists in the correct location.")
        sys.exit(1)
    
    try:
        # Step 1: Load data
        raw_data = load_data(input_file)
        
        # Step 2: Prepare data
        clean_data = prepare_data(raw_data)
        
        # Step 3: Calculate indicators
        print("\n" + "=" * 70)
        print("CALCULATING TECHNICAL INDICATORS")
        print("=" * 70)
        data_with_indicators = calculate_all_indicators(clean_data)
        print("All indicators calculated successfully")
        
        # Remove rows where indicators can't be calculated (first 200 days)
        min_required_days = max(SMA_LONG_PERIOD, ATR_PERIOD, VOLUME_PERIOD) + SMA_SLOPE_LOOKBACK
        data_ready = data_with_indicators.iloc[min_required_days:].reset_index(drop=True)
        print(f"Data ready for trading: {len(data_ready)} rows")
        
        # Step 4: Run backtest
        engine = run_backtest(data_ready, INITIAL_CAPITAL)
        
        # Step 5: Generate reports
        print("\n" + "=" * 70)
        print("GENERATING REPORTS")
        print("=" * 70)
        
        ledger_df = engine.get_ledger_df()
        trades_df = engine.get_trades_df()
        
        metrics = generate_all_reports(ledger_df, trades_df, INITIAL_CAPITAL, output_dir)
        
        print("\n" + "=" * 70)
        print("BACKTEST COMPLETED SUCCESSFULLY")
        print("=" * 70)
        print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"\nAll outputs saved to: {output_dir}")
        
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

