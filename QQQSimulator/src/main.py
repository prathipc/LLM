"""
Main Program - QQQ Trading Simulator
Entry point for running the automated trading simulation
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from pathlib import Path

from . import config
from .indicators import calculate_all_indicators
from .trade_engine import TradingEngine


def get_start_date_from_user() -> datetime:
    """
    Prompt user for simulation start date
    
    Returns:
        datetime object for start date
    """
    while True:
        try:
            date_str = input("\nEnter simulation start date (format: MM-YYYY, e.g., 01-2020): ").strip()
            month, year = date_str.split('-')
            start_date = datetime(int(year), int(month), 1)
            return start_date
        except (ValueError, IndexError):
            print("Invalid format. Please use MM-YYYY format (e.g., 01-2020)")


def load_and_validate_data(file_path: Path) -> pd.DataFrame:
    """
    Load QQQ data from Excel and validate required columns
    
    Args:
        file_path: Path to QQQ.xlsx file
        
    Returns:
        DataFrame with validated data
        
    Raises:
        FileNotFoundError: If data file doesn't exist
        ValueError: If required columns are missing
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Data file not found: {file_path}")
    
    print(f"\nLoading data from {file_path}...")
    df = pd.read_excel(file_path)
    
    # Rename columns to standardize naming
    column_mapping = {
        'QQQ Open Price': 'Open',
        'QQQ High Price': 'High',
        'QQQ Low Price': 'Low',
        'QQQ Close Price': 'Close',
        'TQQQ Price': 'TQQQ_Price',
        'SQQQ Price': 'SQQQ_Price'
    }
    df = df.rename(columns=column_mapping)
    
    # Validate required columns
    missing_cols = []
    for col in config.REQUIRED_COLUMNS:
        if col not in df.columns:
            missing_cols.append(col)
    
    if missing_cols:
        print(f"Available columns: {df.columns.tolist()}")
        raise ValueError(f"Missing required columns: {missing_cols}")
    
    # Ensure Date column is datetime
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Sort by date
    df = df.sort_values('Date').reset_index(drop=True)
    
    print(f"Loaded {len(df)} rows of data")
    print(f"Date range: {df['Date'].min().date()} to {df['Date'].max().date()}")
    
    return df


def filter_data_by_start_date(df: pd.DataFrame, start_date: datetime) -> pd.DataFrame:
    """
    Filter data to start from specified date
    
    Args:
        df: Full DataFrame
        start_date: Starting date for simulation
        
    Returns:
        Filtered DataFrame
    """
    # Need enough data before start_date for indicator calculation
    min_date = start_date - pd.Timedelta(days=config.MIN_DATA_DAYS)
    
    filtered = df[df['Date'] >= min_date].copy()
    
    if len(filtered) == 0:
        raise ValueError(f"No data available from {start_date.date()}")
    
    print(f"\nFiltered to {len(filtered)} rows starting from {filtered['Date'].min().date()}")
    print(f"(includes {config.MIN_DATA_DAYS} days for indicator calculation)")
    
    return filtered


def calculate_performance_metrics(daily_ledger: pd.DataFrame, initial_balance: float) -> dict:
    """
    Calculate performance metrics from daily ledger
    
    Args:
        daily_ledger: DataFrame with daily portfolio values
        initial_balance: Starting portfolio value
        
    Returns:
        Dictionary with performance metrics
    """
    if len(daily_ledger) == 0:
        return {}
    
    final_value = daily_ledger['Portfolio_Value'].iloc[-1]
    total_return = (final_value - initial_balance) / initial_balance * 100
    
    # Calculate CAGR
    start_date = daily_ledger['Date'].iloc[0]
    end_date = daily_ledger['Date'].iloc[-1]
    years = (end_date - start_date).days / 365.25
    
    if years > 0:
        cagr = (pow(final_value / initial_balance, 1 / years) - 1) * 100
    else:
        cagr = 0
    
    # Calculate maximum drawdown
    portfolio_values = daily_ledger['Portfolio_Value'].values
    running_max = np.maximum.accumulate(portfolio_values)
    drawdown = (portfolio_values - running_max) / running_max * 100
    max_drawdown = drawdown.min()
    
    return {
        'initial_value': initial_balance,
        'final_value': final_value,
        'total_return': total_return,
        'cagr': cagr,
        'max_drawdown': max_drawdown,
        'years': years,
        'start_date': start_date,
        'end_date': end_date
    }


def generate_performance_summary(metrics: dict, transaction_ledger: pd.DataFrame, 
                                output_file: Path):
    """
    Generate and save performance summary report
    
    Args:
        metrics: Performance metrics dictionary
        transaction_ledger: DataFrame with all transactions
        output_file: Path to save summary report
    """
    num_trades = len(transaction_ledger)
    
    with open(output_file, 'w') as f:
        f.write("=" * 70 + "\n")
        f.write("QQQ LEVERAGED ETF TRADING SIMULATOR - PERFORMANCE SUMMARY\n")
        f.write("=" * 70 + "\n\n")
        
        f.write(f"Simulation Period: {metrics['start_date'].date()} to {metrics['end_date'].date()}\n")
        f.write(f"Duration: {metrics['years']:.2f} years\n\n")
        
        f.write("-" * 70 + "\n")
        f.write("PORTFOLIO PERFORMANCE\n")
        f.write("-" * 70 + "\n")
        f.write(f"Initial Portfolio Value:  ${metrics['initial_value']:,.2f}\n")
        f.write(f"Final Portfolio Value:    ${metrics['final_value']:,.2f}\n")
        f.write(f"Total Return:             {metrics['total_return']:,.2f}%\n")
        f.write(f"CAGR:                     {metrics['cagr']:,.2f}%\n")
        f.write(f"Maximum Drawdown:         {metrics['max_drawdown']:,.2f}%\n\n")
        
        f.write("-" * 70 + "\n")
        f.write("TRADING ACTIVITY\n")
        f.write("-" * 70 + "\n")
        f.write(f"Total Number of Trades:   {num_trades}\n")
        
        if num_trades > 0:
            # Count buys and sells
            buys = transaction_ledger[transaction_ledger['Action'] == 'Buy']
            sells = transaction_ledger[transaction_ledger['Action'] == 'Sell']
            
            f.write(f"Number of Buy Orders:     {len(buys)}\n")
            f.write(f"Number of Sell Orders:    {len(sells)}\n\n")
            
            # Asset breakdown
            tqqq_trades = transaction_ledger[transaction_ledger['Asset'] == 'TQQQ']
            sqqq_trades = transaction_ledger[transaction_ledger['Asset'] == 'SQQQ']
            
            f.write(f"TQQQ Trades:              {len(tqqq_trades)}\n")
            f.write(f"SQQQ Trades:              {len(sqqq_trades)}\n")
        
        f.write("\n" + "=" * 70 + "\n")
    
    print(f"\nPerformance summary saved to: {output_file}")


def generate_performance_charts(daily_ledger: pd.DataFrame):
    """
    Generate performance charts
    
    Args:
        daily_ledger: DataFrame with daily portfolio values
    """
    # Portfolio Value Chart
    plt.figure(figsize=(14, 7))
    plt.plot(daily_ledger['Date'].values, daily_ledger['Portfolio_Value'].values, linewidth=2, color='blue')
    plt.title('Portfolio Value Over Time', fontsize=16, fontweight='bold')
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Portfolio Value ($)', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(config.PORTFOLIO_CHART_FILE, dpi=300, bbox_inches='tight')
    print(f"Portfolio chart saved to: {config.PORTFOLIO_CHART_FILE}")
    plt.close()
    
    # Drawdown Chart
    portfolio_values = daily_ledger['Portfolio_Value'].values
    running_max = np.maximum.accumulate(portfolio_values)
    drawdown = (portfolio_values - running_max) / running_max * 100
    
    plt.figure(figsize=(14, 7))
    plt.fill_between(daily_ledger['Date'].values, drawdown, 0, alpha=0.5, color='red')
    plt.plot(daily_ledger['Date'].values, drawdown, linewidth=1, color='darkred')
    plt.title('Portfolio Drawdown from Peak', fontsize=16, fontweight='bold')
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Drawdown (%)', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(config.DRAWDOWN_CHART_FILE, dpi=300, bbox_inches='tight')
    print(f"Drawdown chart saved to: {config.DRAWDOWN_CHART_FILE}")
    plt.close()


def run_simulation():
    """
    Main simulation orchestration
    """
    print("=" * 70)
    print("QQQ LEVERAGED ETF AUTOMATED TRADING SIMULATOR")
    print("=" * 70)
    
    # Get start date from user
    start_date = get_start_date_from_user()
    
    # Load and validate data
    try:
        df = load_and_validate_data(config.DATA_FILE)
    except Exception as e:
        print(f"\nError loading data: {e}")
        return
    
    # Filter data by start date
    try:
        df = filter_data_by_start_date(df, start_date)
    except ValueError as e:
        print(f"\nError: {e}")
        return
    
    # Calculate technical indicators
    print("\nCalculating technical indicators...")
    df = calculate_all_indicators(
        df,
        sma_short_period=config.SMA_SHORT_PERIOD,
        sma_long_period=config.SMA_LONG_PERIOD,
        atr_period=config.ATR_PERIOD,
        trend_lookback=config.SMA_TREND_LOOKBACK,
        trend_tolerance=config.SMA_TREND_TOLERANCE
    )
    
    # Initialize trading engine
    print(f"\nInitializing trading engine with ${config.INITIAL_BALANCE:,.2f}...")
    engine = TradingEngine(config.INITIAL_BALANCE)
    
    # Run simulation
    print("\nRunning simulation...")
    simulation_start_idx = df[df['Date'] >= start_date].index[0]
    
    trade_count = 0
    for idx in range(simulation_start_idx, len(df)):
        row = df.iloc[idx]
        
        # Skip if insufficient data for indicators
        if pd.isna(row['SMA_50']) or pd.isna(row['SMA_200']) or pd.isna(row['ATR']):
            continue
        
        # Evaluate signal
        signal = engine.evaluate_signal(
            qqq_close=row['Close'],
            sma_50=row['SMA_50'],
            sma_200=row['SMA_200'],
            sma_50_trend=row['SMA_50_Trend'],
            sma_200_trend=row['SMA_200_Trend'],
            atr=row['ATR'],
            atr_threshold=config.ATR_THRESHOLD
        )
        
        # Execute trade if signal changed
        action = engine.execute_trade(
            date=row['Date'],
            signal=signal,
            tqqq_price=row['TQQQ_Price'],
            sqqq_price=row['SQQQ_Price']
        )
        
        if action != "Hold":
            trade_count += 1
        
        # Record daily state
        engine.record_daily_state(
            date=row['Date'],
            qqq_close=row['Close'],
            sma_50=row['SMA_50'],
            sma_200=row['SMA_200'],
            atr=row['ATR'],
            signal=signal,
            action=action,
            tqqq_price=row['TQQQ_Price'],
            sqqq_price=row['SQQQ_Price']
        )
    
    print(f"Simulation complete! Processed {len(engine.daily_records)} trading days")
    print(f"Executed {trade_count} signal changes")
    
    # Generate outputs
    print("\n" + "=" * 70)
    print("GENERATING OUTPUTS")
    print("=" * 70)
    
    # Save daily ledger
    daily_ledger = engine.get_daily_ledger()
    daily_ledger.to_csv(config.DAILY_LEDGER_FILE, index=False)
    print(f"\nDaily ledger saved to: {config.DAILY_LEDGER_FILE}")
    
    # Save transaction ledger
    transaction_ledger = engine.get_transaction_ledger()
    transaction_ledger.to_csv(config.TRANSACTION_LEDGER_FILE, index=False)
    print(f"Transaction ledger saved to: {config.TRANSACTION_LEDGER_FILE}")
    
    # Calculate and save performance metrics
    metrics = calculate_performance_metrics(daily_ledger, config.INITIAL_BALANCE)
    generate_performance_summary(metrics, transaction_ledger, config.SUMMARY_REPORT_FILE)
    
    # Generate charts
    generate_performance_charts(daily_ledger)
    
    # Display summary
    print("\n" + "=" * 70)
    print("SIMULATION RESULTS")
    print("=" * 70)
    print(f"Initial Value:    ${metrics['initial_value']:,.2f}")
    print(f"Final Value:      ${metrics['final_value']:,.2f}")
    print(f"Total Return:     {metrics['total_return']:,.2f}%")
    print(f"CAGR:             {metrics['cagr']:,.2f}%")
    print(f"Max Drawdown:     {metrics['max_drawdown']:,.2f}%")
    print(f"Number of Trades: {len(transaction_ledger)}")
    print("=" * 70)


if __name__ == "__main__":
    run_simulation()

