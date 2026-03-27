"""
Reporting and Analytics Module for Enhanced Leveraged ETF Strategy v2.0
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend to avoid GUI issues
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import os
from config import *


class PerformanceAnalyzer:
    """
    Calculate performance metrics and generate reports
    """
    
    def __init__(self, ledger_df, trades_df, initial_capital):
        self.ledger = ledger_df
        self.trades = trades_df
        self.initial_capital = initial_capital
        self.metrics = {}
    
    def calculate_returns(self):
        """Calculate returns metrics"""
        if len(self.ledger) == 0:
            return
        
        final_value = self.ledger['Portfolio_Value'].iloc[-1]
        total_return = (final_value - self.initial_capital) / self.initial_capital * 100
        
        # Calculate daily returns
        self.ledger['Daily_Return'] = self.ledger['Portfolio_Value'].pct_change()
        
        # Calculate CAGR
        days = len(self.ledger)
        years = days / 252  # Trading days per year
        if years > 0:
            cagr = (pow(final_value / self.initial_capital, 1/years) - 1) * 100
        else:
            cagr = 0
        
        self.metrics['Total Return (%)'] = round(total_return, 2)
        self.metrics['CAGR (%)'] = round(cagr, 2)
        self.metrics['Final Portfolio Value'] = round(final_value, 2)
        self.metrics['Initial Capital'] = round(self.initial_capital, 2)
    
    def calculate_drawdown(self):
        """Calculate maximum drawdown"""
        if len(self.ledger) == 0:
            return
        
        cumulative_max = self.ledger['Portfolio_Value'].cummax()
        drawdown = (self.ledger['Portfolio_Value'] - cumulative_max) / cumulative_max * 100
        
        self.ledger['Drawdown'] = drawdown
        max_drawdown = drawdown.min()
        
        # Find max drawdown period
        max_dd_idx = drawdown.idxmin()
        max_dd_date = self.ledger.loc[max_dd_idx, 'Date']
        
        self.metrics['Max Drawdown (%)'] = round(max_drawdown, 2)
        self.metrics['Max Drawdown Date'] = max_dd_date
    
    def calculate_risk_metrics(self):
        """Calculate risk-adjusted metrics"""
        if len(self.ledger) < 2:
            return
        
        daily_returns = self.ledger['Daily_Return'].dropna()
        
        if len(daily_returns) == 0:
            return
        
        # Sharpe Ratio (assuming 0% risk-free rate)
        avg_return = daily_returns.mean()
        std_return = daily_returns.std()
        
        if std_return > 0:
            sharpe_ratio = (avg_return / std_return) * np.sqrt(252)  # Annualized
        else:
            sharpe_ratio = 0
        
        # Sortino Ratio (downside deviation)
        downside_returns = daily_returns[daily_returns < 0]
        if len(downside_returns) > 0:
            downside_std = downside_returns.std()
            if downside_std > 0:
                sortino_ratio = (avg_return / downside_std) * np.sqrt(252)
            else:
                sortino_ratio = 0
        else:
            sortino_ratio = 0
        
        # Volatility
        annual_volatility = std_return * np.sqrt(252) * 100
        
        self.metrics['Sharpe Ratio'] = round(sharpe_ratio, 2)
        self.metrics['Sortino Ratio'] = round(sortino_ratio, 2)
        self.metrics['Annual Volatility (%)'] = round(annual_volatility, 2)
    
    def calculate_trade_statistics(self):
        """Calculate trade-related statistics"""
        if len(self.trades) == 0:
            self.metrics['Total Trades'] = 0
            return
        
        # Count buy trades only
        buy_trades = self.trades[self.trades['Action'] == 'BUY']
        sell_trades = self.trades[self.trades['Action'] == 'SELL']
        
        self.metrics['Total Trades'] = len(buy_trades)
        self.metrics['Total Buy Trades'] = len(buy_trades)
        self.metrics['Total Sell Trades'] = len(sell_trades)
        
        # Calculate win rate (requires matching buy/sell pairs)
        tqqq_buys = buy_trades[buy_trades['Ticker'] == 'TQQQ']
        tqqq_sells = sell_trades[sell_trades['Ticker'] == 'TQQQ']
        sqqq_buys = buy_trades[buy_trades['Ticker'] == 'SQQQ']
        sqqq_sells = sell_trades[sell_trades['Ticker'] == 'SQQQ']
        
        self.metrics['TQQQ Trades'] = len(tqqq_buys)
        self.metrics['SQQQ Trades'] = len(sqqq_buys)
        
        # Calculate profit/loss per trade (simplified)
        if len(sell_trades) > 0:
            avg_sell_value = sell_trades['Value'].mean()
            avg_buy_value = buy_trades['Value'].mean()
            
            self.metrics['Avg Trade Size ($)'] = round(avg_buy_value, 2)
    
    def calculate_position_statistics(self):
        """Calculate position distribution statistics"""
        if len(self.ledger) == 0:
            return
        
        # Count days in each position
        position_counts = self.ledger['Position'].value_counts()
        total_days = len(self.ledger)
        
        for position, count in position_counts.items():
            pct = (count / total_days) * 100
            self.metrics[f'Days in {position} (%)'] = round(pct, 2)
    
    def calculate_all_metrics(self):
        """Calculate all performance metrics"""
        self.calculate_returns()
        self.calculate_drawdown()
        self.calculate_risk_metrics()
        self.calculate_trade_statistics()
        self.calculate_position_statistics()
        
        return self.metrics
    
    def generate_summary_report(self):
        """Generate text summary report"""
        report_lines = []
        report_lines.append("=" * 70)
        report_lines.append("ENHANCED LEVERAGED ETF STRATEGY v2.0 - PERFORMANCE REPORT")
        report_lines.append("=" * 70)
        report_lines.append("")
        
        # Trading period
        if len(self.ledger) > 0:
            start_date = self.ledger['Date'].iloc[0]
            end_date = self.ledger['Date'].iloc[-1]
            report_lines.append(f"Trading Period: {start_date} to {end_date}")
            report_lines.append(f"Total Trading Days: {len(self.ledger)}")
            report_lines.append("")
        
        # Performance metrics
        report_lines.append("-" * 70)
        report_lines.append("PERFORMANCE METRICS")
        report_lines.append("-" * 70)
        
        key_metrics = [
            'Initial Capital',
            'Final Portfolio Value',
            'Total Return (%)',
            'CAGR (%)',
            'Max Drawdown (%)',
            'Sharpe Ratio',
            'Sortino Ratio',
            'Annual Volatility (%)'
        ]
        
        for metric in key_metrics:
            if metric in self.metrics:
                report_lines.append(f"{metric:.<40} {self.metrics[metric]:>20}")
        
        report_lines.append("")
        
        # Trade statistics
        report_lines.append("-" * 70)
        report_lines.append("TRADE STATISTICS")
        report_lines.append("-" * 70)
        
        trade_metrics = [
            'Total Trades',
            'TQQQ Trades',
            'SQQQ Trades',
            'Avg Trade Size ($)'
        ]
        
        for metric in trade_metrics:
            if metric in self.metrics:
                report_lines.append(f"{metric:.<40} {self.metrics[metric]:>20}")
        
        report_lines.append("")
        
        # Position distribution
        report_lines.append("-" * 70)
        report_lines.append("POSITION DISTRIBUTION")
        report_lines.append("-" * 70)
        
        for key in self.metrics:
            if 'Days in' in key:
                report_lines.append(f"{key:.<40} {self.metrics[key]:>20}")
        
        report_lines.append("")
        report_lines.append("=" * 70)
        
        return "\n".join(report_lines)
    
    def plot_portfolio_value(self, output_path):
        """Generate portfolio value chart"""
        if len(self.ledger) == 0:
            return
        
        plt.figure(figsize=(14, 7))
        plt.plot(self.ledger['Date'].values, self.ledger['Portfolio_Value'].values, 
                linewidth=2, color='#2E86AB', label='Portfolio Value')
        
        # Add initial capital line
        plt.axhline(y=self.initial_capital, color='gray', linestyle='--', 
                   linewidth=1, alpha=0.7, label='Initial Capital')
        
        plt.title('Portfolio Value Over Time', fontsize=16, fontweight='bold')
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Portfolio Value ($)', fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.legend(fontsize=10)
        
        # Format x-axis
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=3))
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_drawdown(self, output_path):
        """Generate drawdown chart"""
        if len(self.ledger) == 0 or 'Drawdown' not in self.ledger.columns:
            return
        
        plt.figure(figsize=(14, 7))
        plt.fill_between(self.ledger['Date'].values, self.ledger['Drawdown'].values, 0, 
                        color='#A23B72', alpha=0.6, label='Drawdown')
        plt.plot(self.ledger['Date'].values, self.ledger['Drawdown'].values, 
                color='#A23B72', linewidth=1.5)
        
        plt.title('Portfolio Drawdown Over Time', fontsize=16, fontweight='bold')
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Drawdown (%)', fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.legend(fontsize=10)
        
        # Format x-axis
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=3))
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_positions(self, output_path):
        """Generate position distribution chart"""
        if len(self.ledger) == 0:
            return
        
        # Create position timeline
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
        
        # Plot 1: QQQ Price with positions
        ax1_twin = ax1.twinx()
        
        # Plot QQQ price
        ax1.plot(self.ledger['Date'], self.ledger['QQQ_Price'], 
                color='black', linewidth=1.5, label='QQQ Price', alpha=0.7)
        
        # Highlight positions with background colors
        position_colors = {
            'TQQQ': '#28A745',  # Green
            'SQQQ': '#DC3545',  # Red
            'CASH': '#FFC107'   # Yellow
        }
        
        for i in range(len(self.ledger) - 1):
            pos = self.ledger.iloc[i]['Position']
            date_start = self.ledger.iloc[i]['Date']
            date_end = self.ledger.iloc[i + 1]['Date']
            
            if pos in position_colors:
                ax1.axvspan(date_start, date_end, alpha=0.2, 
                           color=position_colors[pos])
        
        ax1.set_xlabel('Date', fontsize=12)
        ax1.set_ylabel('QQQ Price ($)', fontsize=12)
        ax1.set_title('QQQ Price with Position Indicators', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.legend(loc='upper left')
        
        # Format x-axis
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
        plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
        
        # Plot 2: Position percentages
        positions_numeric = []
        for i, row in self.ledger.iterrows():
            if row['Position'] == 'TQQQ':
                positions_numeric.append(row['Position_Pct'] * 100)
            elif row['Position'] == 'SQQQ':
                positions_numeric.append(-row['Position_Pct'] * 100)
            else:
                positions_numeric.append(0)
        
        colors = ['#28A745' if x > 0 else '#DC3545' if x < 0 else '#FFC107' 
                 for x in positions_numeric]
        
        ax2.bar(self.ledger['Date'], positions_numeric, color=colors, alpha=0.6, width=1)
        ax2.axhline(y=0, color='black', linewidth=1, alpha=0.5)
        ax2.set_xlabel('Date', fontsize=12)
        ax2.set_ylabel('Position Size (%)', fontsize=12)
        ax2.set_title('Position Sizing Over Time (+ TQQQ, - SQQQ)', 
                     fontsize=14, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        
        # Format x-axis
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax2.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
        plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_momentum_indicators(self, output_path):
        """Generate momentum and indicators chart"""
        if len(self.ledger) == 0:
            return
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 10))
        
        # Plot 1: QQQ with SMAs
        ax1.plot(self.ledger['Date'], self.ledger['QQQ_Price'], 
                label='QQQ Price', color='black', linewidth=1.5)
        ax1.plot(self.ledger['Date'], self.ledger['SMA_50'], 
                label='50-SMA', color='blue', linewidth=1, alpha=0.7)
        ax1.plot(self.ledger['Date'], self.ledger['SMA_200'], 
                label='200-SMA', color='red', linewidth=1, alpha=0.7)
        ax1.set_title('QQQ Price with Moving Averages', fontweight='bold')
        ax1.set_ylabel('Price ($)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Combined Momentum
        ax2.plot(self.ledger['Date'], self.ledger['Combined_Momentum'], 
                color='purple', linewidth=1.5)
        ax2.axhline(y=0, color='black', linestyle='--', alpha=0.5)
        ax2.axhline(y=0.5, color='green', linestyle='--', alpha=0.3)
        ax2.axhline(y=-0.5, color='red', linestyle='--', alpha=0.3)
        ax2.set_title('Combined Momentum Score', fontweight='bold')
        ax2.set_ylabel('Momentum')
        ax2.grid(True, alpha=0.3)
        
        # Plot 3: Volume Ratio
        ax3.bar(self.ledger['Date'], self.ledger['Volume_Ratio'], 
               color='orange', alpha=0.6, width=1)
        ax3.axhline(y=1.0, color='black', linestyle='--', alpha=0.5)
        ax3.set_title('Volume Ratio', fontweight='bold')
        ax3.set_ylabel('Ratio')
        ax3.set_xlabel('Date')
        ax3.grid(True, alpha=0.3)
        
        # Plot 4: ATR Percentage
        ax4.plot(self.ledger['Date'], self.ledger['ATR_PCT'], 
                color='brown', linewidth=1.5)
        ax4.axhline(y=2.5, color='orange', linestyle='--', alpha=0.5, label='Normal Threshold')
        ax4.set_title('ATR Percentage', fontweight='bold')
        ax4.set_ylabel('ATR %')
        ax4.set_xlabel('Date')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        # Format all x-axes
        for ax in [ax1, ax2, ax3, ax4]:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
            ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()


def generate_all_reports(ledger_df, trades_df, initial_capital, output_dir):
    """
    Generate all reports and save to output directory
    
    Args:
        ledger_df: daily ledger DataFrame
        trades_df: trades DataFrame
        initial_capital: starting capital
        output_dir: directory to save outputs
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize analyzer
    analyzer = PerformanceAnalyzer(ledger_df, trades_df, initial_capital)
    
    # Calculate metrics
    metrics = analyzer.calculate_all_metrics()
    
    # Generate summary report
    summary_text = analyzer.generate_summary_report()
    with open(os.path.join(output_dir, 'summary_report.txt'), 'w') as f:
        f.write(summary_text)
    
    print("Summary Report Generated")
    print(summary_text)
    
    # Save ledger to CSV
    ledger_path = os.path.join(output_dir, 'daily_ledger.csv')
    ledger_df.to_csv(ledger_path, index=False)
    print(f"\nDaily Ledger saved to: {ledger_path}")
    
    # Save trades to CSV
    trades_path = os.path.join(output_dir, 'transactions.csv')
    trades_df.to_csv(trades_path, index=False)
    print(f"Transactions saved to: {trades_path}")
    
    # Generate charts
    print("\nGenerating Charts...")
    
    chart_path = os.path.join(output_dir, 'portfolio_value_chart.png')
    analyzer.plot_portfolio_value(chart_path)
    print(f"Portfolio Value Chart saved to: {chart_path}")
    
    chart_path = os.path.join(output_dir, 'drawdown_chart.png')
    analyzer.plot_drawdown(chart_path)
    print(f"Drawdown Chart saved to: {chart_path}")
    
    chart_path = os.path.join(output_dir, 'position_distribution_chart.png')
    analyzer.plot_positions(chart_path)
    print(f"Position Distribution Chart saved to: {chart_path}")
    
    chart_path = os.path.join(output_dir, 'momentum_indicators_chart.png')
    analyzer.plot_momentum_indicators(chart_path)
    print(f"Momentum Indicators Chart saved to: {chart_path}")
    
    print("\n" + "=" * 70)
    print("ALL REPORTS GENERATED SUCCESSFULLY")
    print("=" * 70)
    
    return metrics

