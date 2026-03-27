"""
QQQ Stock Price Visualization
This script reads QQQ stock data from an Excel file and creates a line graph
showing the closing price over time.
"""

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

def plot_qqq_data():
    """
    Read QQQ.xlsx and create a graph of Date vs Close price.
    """
    # Get the path to the data file
    project_root = Path(__file__).parent.parent
    data_path = project_root / "data" / "QQQ.xlsx"
    
    # Read the Excel file
    print(f"Reading data from {data_path}...")
    df = pd.read_excel(data_path)
    
    # Display basic information about the data
    print(f"\nData shape: {df.shape}")
    print(f"\nColumn names: {df.columns.tolist()}")
    print(f"\nFirst few rows:")
    print(df.head())
    
    # Create the plot
    plt.figure(figsize=(12, 6))
    plt.plot(df['Date'].values, df['Close'].values, linewidth=2, color='blue')
    
    # Customize the plot
    plt.title('QQQ Closing Price Over Time', fontsize=16, fontweight='bold')
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Close Price ($)', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # Save the plot
    output_path = project_root / "data" / "qqq_price_chart.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\nChart saved to: {output_path}")
    
    # Display the plot
    plt.show()

if __name__ == "__main__":
    plot_qqq_data()

