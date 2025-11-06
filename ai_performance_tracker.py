#!/usr/bin/env python3
"""
AI Performance Tracking and Improvement Monitor
==============================================
Tracks AI recommendation quality over time as training data grows.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import json
import os

class AIPerformanceTracker:
    def __init__(self, trade_log_path="trade_log.xlsx"):
        self.trade_log_path = trade_log_path
        self.performance_history = []
        
    def analyze_current_ai_performance(self):
        """Analyze current AI performance with available training data"""
        
        # Load current trades
        df = pd.read_excel(self.trade_log_path, header=0)
        df = df.dropna(subset=['Ticker'])
        
        # Convert datetime columns safely
        df["Open Datetime"] = pd.to_datetime(df["Open Datetime"], format='mixed', errors='coerce')
        df["Close Datetime"] = pd.to_datetime(df["Close Datetime"], format='mixed', errors='coerce')
        
        # Basic performance metrics
        total_trades = len(df)
        winning_trades = len(df[df['Profit/Loss'] > 0])
        losing_trades = len(df[df['Profit/Loss'] < 0])
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        total_pnl = df['Profit/Loss'].sum()
        avg_win = df[df['Profit/Loss'] > 0]['Profit/Loss'].mean() if winning_trades > 0 else 0
        avg_loss = df[df['Profit/Loss'] < 0]['Profit/Loss'].mean() if losing_trades > 0 else 0
        
        # Risk metrics
        profit_factor = abs(avg_win * winning_trades / (avg_loss * losing_trades)) if losing_trades > 0 and avg_loss != 0 else float('inf')
        
        # Data quality assessment
        paper_trades = len(df[df.get('Type', '') == 'Paper'])
        real_trades = len(df[df.get('Type', '') == 'Real'])
        
        return {
            'date': datetime.now(),
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'total_pnl': total_pnl,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'paper_trades': paper_trades,
            'real_trades': real_trades,
            'training_data_quality': self._assess_training_quality(total_trades)
        }
    
    def _assess_training_quality(self, total_trades):
        """Assess quality of training data"""
        if total_trades < 10:
            return "INSUFFICIENT - Need 50+ trades for reliable AI"
        elif total_trades < 30:
            return "MINIMAL - AI learning but needs more data"
        elif total_trades < 50:
            return "DEVELOPING - AI should start showing improvement"
        elif total_trades < 100:
            return "GOOD - AI has decent training foundation"
        else:
            return "EXCELLENT - Rich training dataset"
    
    def generate_performance_report(self):
        """Generate comprehensive AI performance report"""
        
        performance = self.analyze_current_ai_performance()
        
        print("="*70)
        print("🤖 AI PERFORMANCE ANALYSIS REPORT")
        print("="*70)
        print(f"📅 Analysis Date: {performance['date'].strftime('%Y-%m-%d %H:%M')}")
        print(f"📊 Training Data Quality: {performance['training_data_quality']}")
        print()
        
        print("📈 CURRENT PERFORMANCE METRICS:")
        print(f"   Total Trades: {performance['total_trades']}")
        print(f"   Paper Trades: {performance['paper_trades']}")
        print(f"   Real Trades: {performance['real_trades']}")
        print(f"   Win Rate: {performance['win_rate']:.1f}%")
        print(f"   Total P&L: ${performance['total_pnl']:.2f}")
        print(f"   Average Win: ${performance['avg_win']:.2f}")
        print(f"   Average Loss: ${performance['avg_loss']:.2f}")
        print(f"   Profit Factor: {performance['profit_factor']:.2f}")
        print()
        
        # AI Improvement Recommendations
        self._print_improvement_recommendations(performance)
        
        return performance
    
    def _print_improvement_recommendations(self, performance):
        """Print specific recommendations for AI improvement"""
        
        print("🎯 AI IMPROVEMENT RECOMMENDATIONS:")
        print()
        
        if performance['total_trades'] < 50:
            print("   🔹 PRIORITY: Continue systematic paper trading")
            print("   🔹 TARGET: Build to 50+ trades for AI reliability")
            print("   🔹 FOCUS: Maintain 100-share consistency")
            print()
        
        if performance['win_rate'] < 40:
            print("   🔹 Low win rate detected - this is normal early on")
            print("   🔹 AI needs more diverse market conditions in training")
            print("   🔹 Consider trading different market volatility periods")
            print()
        
        if performance['profit_factor'] < 1.0:
            print("   🔹 Profit factor below 1.0 - losses > wins")
            print("   🔹 AI may be overfitting to limited data")
            print("   🔹 More training data should improve this")
            print()
        
        if performance['paper_trades'] < 10:
            print("   🔹 Need more paper trades for safe AI validation")
            print("   🔹 Recommend 20+ paper trades before considering real money")
            print()
        
        print("   💡 REMEMBER: AI performance typically improves significantly")
        print("      after 30-50 trades as it learns market patterns!")
    
    def track_improvement_over_time(self):
        """Track AI performance over time (call weekly/monthly)"""
        
        performance = self.analyze_current_ai_performance()
        
        # Load historical performance
        history_file = "ai_performance_history.json"
        if os.path.exists(history_file):
            with open(history_file, 'r') as f:
                history = json.load(f)
        else:
            history = []
        
        # Add current performance (convert datetime to string for JSON)
        perf_record = performance.copy()
        perf_record['date'] = performance['date'].isoformat()
        history.append(perf_record)
        
        # Save updated history
        with open(history_file, 'w') as f:
            json.dump(history, f, indent=2)
        
        print(f"📊 Performance tracked! History now contains {len(history)} data points.")
        
        # Show improvement trend if we have multiple data points
        if len(history) >= 2:
            self._show_improvement_trend(history)
    
    def _show_improvement_trend(self, history):
        """Show AI improvement trends"""
        
        if len(history) < 2:
            return
            
        latest = history[-1]
        previous = history[-2]
        
        print("\n📈 AI IMPROVEMENT TRENDS:")
        
        win_rate_change = latest['win_rate'] - previous['win_rate']
        pnl_change = latest['total_pnl'] - previous['total_pnl']
        trades_added = latest['total_trades'] - previous['total_trades']
        
        print(f"   Trades Added: +{trades_added}")
        print(f"   Win Rate Change: {win_rate_change:+.1f}%")
        print(f"   P&L Change: ${pnl_change:+.2f}")
        
        if win_rate_change > 0:
            print("   🟢 Win rate improving!")
        elif win_rate_change < -5:
            print("   🟡 Win rate declining - may need more diverse training data")
        
        if trades_added >= 5:
            print("   🟢 Good progress on building training dataset!")

def main():
    """Run AI performance analysis"""
    
    tracker = AIPerformanceTracker()
    
    print("🤖 Analyzing Current AI Performance...")
    print()
    
    # Generate current performance report
    performance = tracker.generate_performance_report()
    
    # Track improvement over time
    tracker.track_improvement_over_time()
    
    print("\n" + "="*70)
    print("💡 NEXT STEPS:")
    print("   1. Continue your systematic 100-share paper trading")
    print("   2. Run this analysis weekly to track AI improvement")
    print("   3. Consider real money after 20+ successful paper trades")
    print("   4. AI recommendations should improve significantly with more data")
    print("="*70)

if __name__ == "__main__":
    main()