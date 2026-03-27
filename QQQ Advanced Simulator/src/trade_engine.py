"""
Trading Engine for Enhanced Leveraged ETF Strategy v2.0
Implements all trading rules with priority hierarchy
"""

import pandas as pd
import numpy as np
from collections import Counter
from config import *


class TradeEngine:
    """
    Main trading engine that processes signals and manages positions
    """
    
    def __init__(self, initial_capital=INITIAL_CAPITAL):
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.tqqq_shares = 0
        self.sqqq_shares = 0
        self.current_position = 'CASH'  # CASH, TQQQ, SQQQ, MIXED
        self.position_pct = 0.0
        self.entry_price = 0.0
        self.stop_loss_price = None
        self.trailing_stop_price = None
        self.trades = []
        self.daily_ledger = []
        self.signal_stats = Counter()
        
    def reset(self):
        """Reset the engine to initial state"""
        self.cash = self.initial_capital
        self.tqqq_shares = 0
        self.sqqq_shares = 0
        self.current_position = 'CASH'
        self.position_pct = 0.0
        self.entry_price = 0.0
        self.stop_loss_price = None
        self.trailing_stop_price = None
        self.trades = []
        self.daily_ledger = []
        self.signal_stats = Counter()
    
    def get_portfolio_value(self, tqqq_price, sqqq_price):
        """Calculate current portfolio value"""
        tqqq_value = self.tqqq_shares * tqqq_price if not pd.isna(tqqq_price) else 0
        sqqq_value = self.sqqq_shares * sqqq_price if not pd.isna(sqqq_price) else 0
        return self.cash + tqqq_value + sqqq_value
    
    def execute_trade(self, date, action, ticker, price, target_pct, reason):
        """
        Execute a trade and record it
        
        Args:
            date: trading date
            action: 'BUY' or 'SELL'
            ticker: 'TQQQ' or 'SQQQ'
            price: execution price
            target_pct: target position percentage (0.0 to 1.0)
            reason: trading rule that triggered this action
        """
        if pd.isna(price) or price <= 0:
            return False
        
        current_value = self.get_portfolio_value(price if ticker == 'TQQQ' else 0, 
                                                  price if ticker == 'SQQQ' else 0)
        
        if action == 'BUY':
            # Calculate how many shares to buy
            target_value = current_value * target_pct
            cost = target_value - TRANSACTION_FEE
            shares_to_buy = int(cost / (price * (1 + SLIPPAGE)))
            
            if shares_to_buy > 0:
                actual_cost = shares_to_buy * price * (1 + SLIPPAGE) + TRANSACTION_FEE
                
                if actual_cost <= self.cash:
                    if ticker == 'TQQQ':
                        self.tqqq_shares += shares_to_buy
                    else:  # SQQQ
                        self.sqqq_shares += shares_to_buy
                    
                    self.cash -= actual_cost
                    
                    self.trades.append({
                        'Date': date,
                        'Action': action,
                        'Ticker': ticker,
                        'Shares': shares_to_buy,
                        'Price': price,
                        'Value': actual_cost,
                        'Reason': reason
                    })
                    return True
        
        elif action == 'SELL':
            # Sell shares
            if ticker == 'TQQQ' and self.tqqq_shares > 0:
                shares_to_sell = self.tqqq_shares
                proceeds = shares_to_sell * price * (1 - SLIPPAGE) - TRANSACTION_FEE
                self.cash += proceeds
                self.tqqq_shares = 0
                
                self.trades.append({
                    'Date': date,
                    'Action': action,
                    'Ticker': ticker,
                    'Shares': shares_to_sell,
                    'Price': price,
                    'Value': proceeds,
                    'Reason': reason
                })
                return True
            
            elif ticker == 'SQQQ' and self.sqqq_shares > 0:
                shares_to_sell = self.sqqq_shares
                proceeds = shares_to_sell * price * (1 - SLIPPAGE) - TRANSACTION_FEE
                self.cash += proceeds
                self.sqqq_shares = 0
                
                self.trades.append({
                    'Date': date,
                    'Action': action,
                    'Ticker': ticker,
                    'Shares': shares_to_sell,
                    'Price': price,
                    'Value': proceeds,
                    'Reason': reason
                })
                return True
        
        return False
    
    def evaluate_rules(self, row):
        """
        Evaluate all trading rules in priority order
        Returns: (action, ticker, target_pct, reason)
        """
        price = row[COL_QQQ_CLOSE]
        sma_50 = row['SMA_50']
        sma_200 = row['SMA_200']
        slope_50 = row['Slope_50']
        slope_200 = row['Slope_200']
        combined_momentum = row['Combined_Momentum']
        volume_ratio = row['Volume_Ratio']
        atr_pct = row['ATR_PCT']
        death_cross = row['Death_Cross']
        market_regime = row['Market_Regime']
        
        # Check for NaN values
        if any(pd.isna([price, sma_50, sma_200, slope_50, slope_200, combined_momentum, volume_ratio, atr_pct])):
            return ('HOLD', None, 0.0, 'Insufficient data')
        
        # ===== PRIORITY 1: EXIT CONDITIONS (Check first) =====
        
        # Death Cross - Immediate exit to cash
        if death_cross or sma_50 < sma_200:
            if self.tqqq_shares > 0:
                return ('SELL', 'TQQQ', 0.0, 'Rule 1: Death Cross - Exit to Cash')
            elif self.sqqq_shares > 0:
                # Keep SQQQ positions during death cross (bearish condition)
                pass
        
        # Exit TQQQ if conditions deteriorate
        if self.tqqq_shares > 0:
            # Hard stop loss
            tqqq_price = row[COL_TQQQ_CLOSE]
            if not pd.isna(tqqq_price) and self.stop_loss_price is not None:
                if tqqq_price <= self.stop_loss_price:
                    return ('SELL', 'TQQQ', 0.0, 'Rule 9: Hard Stop Loss Hit')
            
            # Trailing stop
            if self.trailing_stop_price is not None:
                if tqqq_price <= self.trailing_stop_price:
                    return ('SELL', 'TQQQ', 0.0, 'Rule 9: Trailing Stop Hit')
            
            # SMA exit buffer breach
            if price < sma_50 * (1 - BUFFER_EXIT_50SMA):
                return ('SELL', 'TQQQ', 0.0, 'Rule 9: Exit Buffer Breach (50-SMA)')
            
            # Momentum turned negative
            if combined_momentum < -0.2:
                return ('SELL', 'TQQQ', 0.0, 'Rule 9: Momentum Turned Negative')
        
        # Exit SQQQ if conditions improve
        if self.sqqq_shares > 0:
            sqqq_price = row[COL_SQQQ_CLOSE]
            
            # Hard stop loss (inverse for SQQQ)
            if not pd.isna(sqqq_price) and self.stop_loss_price is not None:
                if sqqq_price >= self.stop_loss_price:
                    return ('SELL', 'SQQQ', 0.0, 'Rule 10: Hard Stop Loss Hit (SQQQ)')
            
            # Exit if momentum improves significantly
            if combined_momentum > 0.2:
                return ('SELL', 'SQQQ', 0.0, 'Rule 10: Momentum Improved - Exit SQQQ')
            
            # Exit if price moves above 50-SMA
            if price > sma_50 * (1 + BUFFER_ENTRY_50SMA):
                return ('SELL', 'SQQQ', 0.0, 'Rule 10: Price Above 50-SMA - Exit SQQQ')
        
        # ===== PRIORITY 2: HIGH VOLATILITY CHECK =====
        
        # Determine ATR threshold based on regime
        if market_regime == 'bull':
            atr_threshold = ATR_THRESHOLD_BULL
        elif market_regime == 'bear':
            atr_threshold = ATR_THRESHOLD_CRISIS
        elif market_regime == 'transition':
            atr_threshold = ATR_THRESHOLD_CHOPPY
        else:
            atr_threshold = ATR_THRESHOLD_NORMAL
        
        suppress_entries = atr_pct > atr_threshold
        entry_signal = self._evaluate_entry_signals(row, diagnostics_only=suppress_entries)

        if suppress_entries:
            # High volatility - reduce or avoid positions
            if self.tqqq_shares > 0 or self.sqqq_shares > 0:
                return ('HOLD', None, 0.0, 'Rule 2: High Volatility - Hold Position')
            else:
                return ('HOLD', None, 0.0, 'Rule 2: High Volatility - Stay in Cash')
        
        if entry_signal:
            return entry_signal
        
        # Rule 6: Default to CASH
        if self.tqqq_shares == 0 and self.sqqq_shares == 0:
            return ('HOLD', None, POSITION_CASH, 'Rule 6: Stay in Cash - Neutral Conditions')
        else:
            return ('HOLD', None, 0.0, 'Hold Current Position')

    def _evaluate_entry_signals(self, row, diagnostics_only=False):
        """Evaluate entry rules; optionally log diagnostics without trading."""
        price = row[COL_QQQ_CLOSE]
        sma_50 = row['SMA_50']
        sma_200 = row['SMA_200']
        slope_50 = row['Slope_50']
        slope_200 = row['Slope_200']
        combined_momentum = row['Combined_Momentum']
        volume_ratio = row['Volume_Ratio']

        # Rule 3
        if self.tqqq_shares == 0:
            rule3_conditions = {
                'price_vs_50': price > sma_50 * (1 + BUFFER_ENTRY_50SMA),
                'price_vs_200': price > sma_200 * (1 + BUFFER_ENTRY_200SMA),
                'golden_cross': sma_50 > sma_200,
                'momentum': combined_momentum > MOMENTUM_VERY_STRONG_POSITIVE,
                'slope_50': slope_50 > SLOPE_BULL_THRESHOLD,
                'slope_200': slope_200 > 0,
                'volume': volume_ratio >= VOLUME_RATIO_HIGH
            }
            self._log_rule_conditions('rule3_tqqq_100', rule3_conditions)
            if not diagnostics_only and all(rule3_conditions.values()):
                return ('BUY', 'TQQQ', POSITION_100_TQQQ, 'Rule 3: 100% TQQQ - Strong Bull Signal')

        # Rule 4
        if self.tqqq_shares == 0:
            rule4_conditions = {
                'price_vs_50': price > sma_50 * (1 + BUFFER_ENTRY_50SMA),
                'price_vs_200': price > sma_200,
                'golden_cross': sma_50 > sma_200,
                'momentum': MOMENTUM_MODERATE_POSITIVE <= combined_momentum <= MOMENTUM_VERY_STRONG_POSITIVE,
                'volume': volume_ratio >= VOLUME_RATIO_LOW
            }
            self._log_rule_conditions('rule4_tqqq_75', rule4_conditions)
            if not diagnostics_only and all(rule4_conditions.values()):
                return ('BUY', 'TQQQ', POSITION_75_TQQQ, 'Rule 4: 75% TQQQ - Moderate Bull')

        # Rule 5
        if self.tqqq_shares == 0:
            rule5_conditions = {
                'price_vs_200': price > sma_200,
                'price_vs_50': price > sma_50 * 0.98,
                'momentum': MOMENTUM_NEUTRAL_LOW <= combined_momentum <= MOMENTUM_MODERATE_POSITIVE
            }
            self._log_rule_conditions('rule5_tqqq_50', rule5_conditions)
            if not diagnostics_only and all(rule5_conditions.values()):
                return ('BUY', 'TQQQ', POSITION_50_TQQQ, 'Rule 5: 50% TQQQ - Conservative Bull')

        # Rule 7
        if self.sqqq_shares == 0:
            rule7_conditions = {
                'price_vs_50': price < sma_50 * (1 - BUFFER_EXIT_50SMA),
                'price_vs_200': price > sma_200,
                'momentum': MOMENTUM_MODERATE_NEGATIVE <= combined_momentum < MOMENTUM_NEUTRAL_LOW,
                'volume': volume_ratio >= VOLUME_RATIO_MODERATE
            }
            self._log_rule_conditions('rule7_sqqq_50', rule7_conditions)
            if not diagnostics_only and all(rule7_conditions.values()):
                return ('BUY', 'SQQQ', POSITION_50_SQQQ, 'Rule 7: 50% SQQQ - Moderate Bear')

        # Rule 8
        if self.sqqq_shares == 0:
            rule8_conditions = {
                'price_vs_50': price < sma_50 * (1 - BUFFER_EXIT_50SMA),
                'price_vs_200': price < sma_200 * (1 - BUFFER_EXIT_200SMA),
                'death_cross': sma_50 < sma_200,
                'momentum': combined_momentum < MOMENTUM_MODERATE_NEGATIVE,
                'volume': volume_ratio >= VOLUME_RATIO_HIGH
            }
            self._log_rule_conditions('rule8_sqqq_100', rule8_conditions)
            if not diagnostics_only and all(rule8_conditions.values()):
                return ('BUY', 'SQQQ', POSITION_100_SQQQ, 'Rule 8: 100% SQQQ - Strong Bear Signal')

        return None
    def _log_rule_conditions(self, rule_name, conditions):
        """Track which conditions are blocking entries for diagnostics."""
        all_met = True
        for cond, satisfied in conditions.items():
            key = f"{rule_name}.{cond}"
            if satisfied:
                self.signal_stats[f"{key}.hit"] += 1
            else:
                self.signal_stats[f"{key}.miss"] += 1
                all_met = False
        if all_met:
            self.signal_stats[f"{rule_name}.all_met"] += 1

    def print_signal_diagnostics(self, top_n=5):
        """Print a summary of which rule conditions rarely fire."""
        if not self.signal_stats:
            print("\nNo signal diagnostics captured.")
            return

        print("\n" + "=" * 70)
        print("SIGNAL DIAGNOSTICS SUMMARY")
        print("=" * 70)

        rule_data = {}
        for key, count in self.signal_stats.items():
            parts = key.split(".")
            if len(parts) < 3:
                continue
            rule, condition, outcome = parts[0], parts[1], parts[2]
            rule_entry = rule_data.setdefault(rule, {})
            cond_entry = rule_entry.setdefault(condition, {'hit': 0, 'miss': 0})
            cond_entry[outcome] = count

        for rule, conditions in sorted(rule_data.items()):
            print(f"\n{rule.upper()}:")
            blockers = []
            for condition, stats in conditions.items():
                hits = stats.get('hit', 0)
                misses = stats.get('miss', 0)
                total = hits + misses
                miss_pct = (misses / total * 100) if total else 0
                blockers.append((miss_pct, condition, hits, misses))
            blockers.sort(reverse=True)
            for miss_pct, condition, hits, misses in blockers[:top_n]:
                print(f"  - {condition}: {misses} misses / {hits} hits ({miss_pct:.1f}% miss)")
    
    def update_stops(self, current_price, ticker):
        """Update stop loss and trailing stop prices"""
        if ticker == 'TQQQ' and self.tqqq_shares > 0:
            # Calculate current gain
            if self.entry_price > 0:
                gain_pct = (current_price - self.entry_price) / self.entry_price
                
                # Activate trailing stop if gain exceeds trigger
                if gain_pct >= TRAILING_STOP_TRIGGER:
                    new_trailing_stop = current_price * (1 - TRAILING_STOP_DISTANCE)
                    if self.trailing_stop_price is None or new_trailing_stop > self.trailing_stop_price:
                        self.trailing_stop_price = new_trailing_stop
        
        elif ticker == 'SQQQ' and self.sqqq_shares > 0:
            # For SQQQ (inverse), trailing stop works in reverse
            if self.entry_price > 0:
                gain_pct = (self.entry_price - current_price) / self.entry_price
                
                if gain_pct >= TRAILING_STOP_TRIGGER:
                    new_trailing_stop = current_price * (1 + TRAILING_STOP_DISTANCE)
                    if self.trailing_stop_price is None or new_trailing_stop < self.trailing_stop_price:
                        self.trailing_stop_price = new_trailing_stop
    
    def process_day(self, date, row):
        """
        Process a single trading day
        
        Args:
            date: trading date
            row: pandas Series with all indicator values
        """
        tqqq_price = row[COL_TQQQ_CLOSE]
        sqqq_price = row[COL_SQQQ_CLOSE]
        qqq_price = row[COL_QQQ_CLOSE]
        
        # Update trailing stops
        if self.tqqq_shares > 0:
            self.update_stops(tqqq_price, 'TQQQ')
        elif self.sqqq_shares > 0:
            self.update_stops(sqqq_price, 'SQQQ')
        
        # Evaluate trading rules
        action, ticker, target_pct, reason = self.evaluate_rules(row)
        
        # Execute trades
        if action == 'BUY' and ticker:
            price = tqqq_price if ticker == 'TQQQ' else sqqq_price
            if self.execute_trade(date, action, ticker, price, target_pct, reason):
                self.entry_price = price
                self.current_position = ticker
                self.position_pct = target_pct
                
                # Set initial stop loss
                if ticker == 'TQQQ':
                    if target_pct >= 1.0:
                        self.stop_loss_price = price * (1 - STOP_LOSS_100_TQQQ)
                    else:
                        self.stop_loss_price = price * (1 - STOP_LOSS_50_TQQQ)
                else:  # SQQQ
                    if target_pct >= 1.0:
                        self.stop_loss_price = price * (1 + STOP_LOSS_100_SQQQ)
                    else:
                        self.stop_loss_price = price * (1 + STOP_LOSS_SQQQ)
        
        elif action == 'SELL' and ticker:
            price = tqqq_price if ticker == 'TQQQ' else sqqq_price
            if self.execute_trade(date, action, ticker, price, 0.0, reason):
                self.current_position = 'CASH'
                self.position_pct = 0.0
                self.entry_price = 0.0
                self.stop_loss_price = None
                self.trailing_stop_price = None
        
        # Record daily state
        portfolio_value = self.get_portfolio_value(tqqq_price, sqqq_price)
        
        self.daily_ledger.append({
            'Date': date,
            'QQQ_Price': qqq_price,
            'TQQQ_Price': tqqq_price,
            'SQQQ_Price': sqqq_price,
            'Action': action,
            'Ticker': ticker if ticker else 'N/A',
            'Reason': reason,
            'Position': self.current_position,
            'Position_Pct': self.position_pct,
            'TQQQ_Shares': self.tqqq_shares,
            'SQQQ_Shares': self.sqqq_shares,
            'Cash': self.cash,
            'Portfolio_Value': portfolio_value,
            'Stop_Loss': self.stop_loss_price,
            'Trailing_Stop': self.trailing_stop_price,
            'SMA_50': row['SMA_50'],
            'SMA_200': row['SMA_200'],
            'Slope_50': row['Slope_50'],
            'Slope_200': row['Slope_200'],
            'Combined_Momentum': row['Combined_Momentum'],
            'Volume_Ratio': row['Volume_Ratio'],
            'ATR_PCT': row['ATR_PCT'],
            'Market_Regime': row['Market_Regime']
        })
    
    def get_ledger_df(self):
        """Return daily ledger as DataFrame"""
        return pd.DataFrame(self.daily_ledger)
    
    def get_trades_df(self):
        """Return trades as DataFrame"""
        return pd.DataFrame(self.trades)

