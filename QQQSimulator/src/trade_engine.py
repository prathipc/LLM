"""
Trading Engine Module
Handles signal generation, position management, and portfolio tracking
"""
import pandas as pd
from datetime import datetime
from typing import Optional, Dict, List, Tuple
from . import config


class TradingEngine:
    """
    Core trading engine that manages positions and executes trades
    based on technical signals
    """
    
    def __init__(self, initial_balance: float = config.INITIAL_BALANCE):
        """
        Initialize the trading engine
        
        Args:
            initial_balance: Starting cash balance
        """
        self.initial_balance = initial_balance
        self.cash = initial_balance
        self.tqqq_shares = 0.0
        self.sqqq_shares = 0.0
        self.current_signal = None
        self.previous_signal = None
        
        # Tracking
        self.daily_records = []
        self.transactions = []
        self.portfolio_values = []
        
    def evaluate_signal(self, 
                       qqq_close: float,
                       sma_50: float,
                       sma_200: float,
                       sma_50_trend: str,
                       sma_200_trend: str,
                       atr: float,
                       atr_threshold: Optional[float] = None) -> str:
        """
        Evaluate trading signal based on technical indicators and rulebook
        
        Rules:
        1. 100% TQQQ: QQQ > 50d SMA & QQQ > 200d SMA & 50d SMA rising
        2. 50% TQQQ / 50% Cash: QQQ > both SMAs & 50d SMA flat/falling
        3. 100% SQQQ: DISABLED - Now defaults to Cash
        4. 100% Cash: All other conditions (including bearish scenarios)
        5. Volatility override: If ATR > threshold, hold Cash
        
        Args:
            qqq_close: Current QQQ closing price
            sma_50: 50-day SMA value
            sma_200: 200-day SMA value
            sma_50_trend: Trend of 50-day SMA ('rising', 'falling', 'flat')
            sma_200_trend: Trend of 200-day SMA
            atr: Current ATR value
            atr_threshold: Optional ATR threshold for volatility override
            
        Returns:
            Signal string indicating position allocation
        """
        # Check if we have valid data
        if pd.isna(qqq_close) or pd.isna(sma_50) or pd.isna(sma_200) or pd.isna(atr):
            return config.SIGNAL_100_CASH
        
        if sma_50_trend is None or sma_200_trend is None:
            return config.SIGNAL_100_CASH
        
        # Volatility override (optional)
        if config.ENABLE_VOLATILITY_OVERRIDE and atr_threshold is not None:
            if atr > atr_threshold:
                return config.SIGNAL_100_CASH
        
        # Rule 1: 100% TQQQ
        # QQQ > 50d SMA & QQQ > 200d SMA & 50d SMA rising
        if qqq_close > sma_50 and qqq_close > sma_200 and sma_50_trend == 'rising':
            return config.SIGNAL_100_TQQQ
        
        # Rule 2: 50% TQQQ / 50% Cash
        # QQQ > both SMAs & 50d SMA flat or falling
        if qqq_close > sma_50 and qqq_close > sma_200 and sma_50_trend in ['flat', 'falling']:
            return config.SIGNAL_50_TQQQ
        
        # Rule 3: 100% SQQQ - DISABLED (Now defaults to Cash)
        # ORIGINAL: QQQ < 50d SMA & QQQ < 200d SMA & both SMAs falling
        # MODIFIED: This rule is commented out - strategy will hold 100% Cash instead
        # if qqq_close < sma_50 and qqq_close < sma_200:
        #     if sma_50_trend == 'falling' and sma_200_trend == 'falling':
        #         return config.SIGNAL_100_SQQQ
        
        # Rule 4: Default to 100% Cash for all other conditions
        # This now includes the former SQQQ scenario (bearish conditions)
        return config.SIGNAL_100_CASH
    
    def calculate_portfolio_value(self, tqqq_price: float, sqqq_price: float) -> float:
        """
        Calculate current portfolio value
        
        Args:
            tqqq_price: Current TQQQ price
            sqqq_price: Current SQQQ price
            
        Returns:
            Total portfolio value
        """
        tqqq_value = self.tqqq_shares * tqqq_price if not pd.isna(tqqq_price) else 0
        sqqq_value = self.sqqq_shares * sqqq_price if not pd.isna(sqqq_price) else 0
        return tqqq_value + sqqq_value + self.cash
    
    def liquidate_position(self, asset: str, price: float, date: datetime) -> float:
        """
        Sell all shares of a given asset
        
        Args:
            asset: Asset to sell ('TQQQ' or 'SQQQ')
            price: Current price of the asset
            date: Transaction date
            
        Returns:
            Amount received from sale
        """
        if asset == config.ASSET_TQQQ:
            if self.tqqq_shares > 0:
                quantity = self.tqqq_shares
                amount = quantity * price - config.TRANSACTION_COST_PER_TRADE
                self.cash += amount
                self.tqqq_shares = 0
                
                # Record transaction
                self.transactions.append({
                    'Date': date,
                    'Asset': asset,
                    'Action': 'Sell',
                    'Quantity': quantity,
                    'Price': price,
                    'Amount': amount,
                    'Portfolio_Value_Before': self.cash - amount,
                    'Portfolio_Value_After': self.cash
                })
                return amount
        
        elif asset == config.ASSET_SQQQ:
            if self.sqqq_shares > 0:
                quantity = self.sqqq_shares
                amount = quantity * price - config.TRANSACTION_COST_PER_TRADE
                self.cash += amount
                self.sqqq_shares = 0
                
                # Record transaction
                self.transactions.append({
                    'Date': date,
                    'Asset': asset,
                    'Action': 'Sell',
                    'Quantity': quantity,
                    'Price': price,
                    'Amount': amount,
                    'Portfolio_Value_Before': self.cash - amount,
                    'Portfolio_Value_After': self.cash
                })
                return amount
        
        return 0.0
    
    def buy_position(self, asset: str, price: float, allocation_pct: float, date: datetime) -> float:
        """
        Buy asset with specified percentage of portfolio
        
        Args:
            asset: Asset to buy ('TQQQ' or 'SQQQ')
            price: Current price of the asset
            allocation_pct: Percentage of cash to allocate (0.0 to 1.0)
            date: Transaction date
            
        Returns:
            Amount invested
        """
        if allocation_pct <= 0 or self.cash <= 0:
            return 0.0
        
        amount_to_invest = self.cash * allocation_pct
        cost = config.TRANSACTION_COST_PER_TRADE
        
        if amount_to_invest <= cost:
            return 0.0
        
        net_investment = amount_to_invest - cost
        quantity = net_investment / price
        
        portfolio_value_before = self.cash
        self.cash -= amount_to_invest
        
        if asset == config.ASSET_TQQQ:
            self.tqqq_shares += quantity
        elif asset == config.ASSET_SQQQ:
            self.sqqq_shares += quantity
        
        # Record transaction
        self.transactions.append({
            'Date': date,
            'Asset': asset,
            'Action': 'Buy',
            'Quantity': quantity,
            'Price': price,
            'Amount': net_investment,
            'Portfolio_Value_Before': portfolio_value_before,
            'Portfolio_Value_After': self.cash + quantity * price
        })
        
        return amount_to_invest
    
    def execute_trade(self, date: datetime, signal: str, tqqq_price: float, sqqq_price: float) -> str:
        """
        Execute trade based on signal change
        
        Args:
            date: Trading date
            signal: Current trading signal
            tqqq_price: Current TQQQ price
            sqqq_price: Current SQQQ price
            
        Returns:
            Description of action taken
        """
        # Check if signal changed
        if signal == self.current_signal:
            return "Hold"
        
        action_description = []
        
        # First, liquidate current positions if switching
        if self.tqqq_shares > 0:
            self.liquidate_position(config.ASSET_TQQQ, tqqq_price, date)
            action_description.append(f"Sell TQQQ")
        
        if self.sqqq_shares > 0:
            self.liquidate_position(config.ASSET_SQQQ, sqqq_price, date)
            action_description.append(f"Sell SQQQ")
        
        # Now execute new position based on signal
        if signal == config.SIGNAL_100_TQQQ:
            self.buy_position(config.ASSET_TQQQ, tqqq_price, 1.0, date)
            action_description.append("Buy TQQQ (100%)")
        
        elif signal == config.SIGNAL_50_TQQQ:
            self.buy_position(config.ASSET_TQQQ, tqqq_price, 0.5, date)
            action_description.append("Buy TQQQ (50%)")
        
        elif signal == config.SIGNAL_100_SQQQ:
            self.buy_position(config.ASSET_SQQQ, sqqq_price, 1.0, date)
            action_description.append("Buy SQQQ (100%)")
        
        elif signal == config.SIGNAL_100_CASH:
            action_description.append("Hold Cash (100%)")
        
        # Update current signal
        self.previous_signal = self.current_signal
        self.current_signal = signal
        
        return ", ".join(action_description) if action_description else "Hold"
    
    def record_daily_state(self, date: datetime, qqq_close: float, sma_50: float, 
                          sma_200: float, atr: float, signal: str, action: str,
                          tqqq_price: float, sqqq_price: float):
        """
        Record daily portfolio state
        
        Args:
            date: Trading date
            qqq_close: QQQ closing price
            sma_50: 50-day SMA
            sma_200: 200-day SMA
            atr: ATR value
            signal: Current signal
            action: Action taken
            tqqq_price: TQQQ price
            sqqq_price: SQQQ price
        """
        portfolio_value = self.calculate_portfolio_value(tqqq_price, sqqq_price)
        
        record = {
            'Date': date,
            'QQQ_Close': qqq_close,
            'SMA_50': sma_50,
            'SMA_200': sma_200,
            'ATR': atr,
            'Signal': signal,
            'Action': action,
            'TQQQ_Shares': self.tqqq_shares,
            'SQQQ_Shares': self.sqqq_shares,
            'Cash': self.cash,
            'Portfolio_Value': portfolio_value
        }
        
        self.daily_records.append(record)
        self.portfolio_values.append(portfolio_value)
    
    def get_daily_ledger(self) -> pd.DataFrame:
        """
        Get daily position ledger as DataFrame
        
        Returns:
            DataFrame with daily records
        """
        return pd.DataFrame(self.daily_records)
    
    def get_transaction_ledger(self) -> pd.DataFrame:
        """
        Get transaction ledger as DataFrame
        
        Returns:
            DataFrame with all transactions
        """
        return pd.DataFrame(self.transactions)


