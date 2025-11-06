#!/usr/bin/env python3
"""
AI Recommendation Confidence Scorer
===================================
Provides confidence scores for AI recommendations based on training data quality.
"""

import pandas as pd
import numpy as np
from datetime import datetime

def calculate_ai_confidence_score():
    """
    Calculate confidence score for current AI recommendations.
    Higher score = more reliable recommendations.
    """
    
    # Load training data
    try:
        df = pd.read_excel("trade_log.xlsx", header=0)
        df = df.dropna(subset=['Ticker'])
        
        # Convert datetime safely
        df['Open Datetime'] = pd.to_datetime(df['Open Datetime'], format='mixed', errors='coerce')
        
        total_trades = len(df)
        paper_trades = len(df[df.get('Type', '') == 'Paper'])
        
        # Count recent trades (last 30 days)
        cutoff_date = datetime.now() - pd.Timedelta(days=30)
        recent_trades = len(df[df['Open Datetime'] > cutoff_date])
        
        # Calculate confidence factors
        data_quantity_score = min(total_trades / 100, 1.0) * 40  # Max 40 points for 100+ trades
        data_recency_score = min(recent_trades / 20, 1.0) * 20   # Max 20 points for 20+ recent trades
        data_diversity_score = min(len(df['Ticker'].unique()) / 15, 1.0) * 20  # Max 20 points for 15+ different tickers
        
        # Performance consistency score
        if total_trades >= 10:
            win_rate = len(df[df['Profit/Loss'] > 0]) / total_trades
            profit_factor = calculate_profit_factor(df)
            consistency_score = min((win_rate * 2 + min(profit_factor/2, 1)) * 10, 20)  # Max 20 points
        else:
            consistency_score = 0
        
        total_confidence = data_quantity_score + data_recency_score + data_diversity_score + consistency_score
        
        return {
            'total_confidence': min(total_confidence, 100),
            'data_quantity_score': data_quantity_score,
            'data_recency_score': data_recency_score, 
            'data_diversity_score': data_diversity_score,
            'consistency_score': consistency_score,
            'total_trades': total_trades,
            'recent_trades': recent_trades,
            'unique_tickers': len(df['Ticker'].unique()),
            'recommendation': get_confidence_recommendation(total_confidence)
        }
        
    except Exception as e:
        import traceback
        return {
            'total_confidence': 0,
            'error': str(e),
            'traceback': traceback.format_exc(),
            'recommendation': "ERROR - Cannot assess AI confidence"
        }

def calculate_profit_factor(df):
    """Calculate profit factor from trade data"""
    wins = df[df['Profit/Loss'] > 0]['Profit/Loss'].sum()
    losses = abs(df[df['Profit/Loss'] < 0]['Profit/Loss'].sum())
    return wins / losses if losses > 0 else float('inf')

def get_confidence_recommendation(confidence_score):
    """Get recommendation based on confidence score"""
    if confidence_score >= 80:
        return "HIGH CONFIDENCE - AI recommendations are reliable"
    elif confidence_score >= 60:
        return "MODERATE CONFIDENCE - AI showing good patterns"
    elif confidence_score >= 40:
        return "DEVELOPING CONFIDENCE - AI learning but use caution"
    elif confidence_score >= 20:
        return "LOW CONFIDENCE - AI still learning, paper trade only"
    else:
        return "VERY LOW CONFIDENCE - Build more training data first"

def display_confidence_dashboard():
    """Display comprehensive AI confidence dashboard"""
    
    confidence = calculate_ai_confidence_score()
    
    if 'error' in confidence:
        print(f"❌ Error calculating confidence: {confidence['error']}")
        return
    
    print("🤖 AI RECOMMENDATION CONFIDENCE DASHBOARD")
    print("="*55)
    print(f"📅 Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print()
    
    # Overall confidence
    total = confidence['total_confidence']
    print(f"🎯 OVERALL AI CONFIDENCE: {total:.1f}/100")
    print(f"   {get_confidence_bar(total)}")
    print(f"   {confidence['recommendation']}")
    print()
    
    # Detailed breakdown
    print("📊 CONFIDENCE BREAKDOWN:")
    print(f"   Data Quantity: {confidence['data_quantity_score']:.1f}/40 points")
    print(f"   Data Recency:  {confidence['data_recency_score']:.1f}/20 points")
    print(f"   Data Diversity: {confidence['data_diversity_score']:.1f}/20 points")
    print(f"   Performance:   {confidence['consistency_score']:.1f}/20 points")
    print()
    
    # Actionable recommendations
    print("💡 IMPROVEMENT ACTIONS:")
    if confidence['data_quantity_score'] < 30:
        print("   🔹 PRIORITY: Add more trades (target 50+ for reliability)")
    if confidence['data_recency_score'] < 15:
        print("   🔹 Add recent trades to keep AI current with market conditions")
    if confidence['data_diversity_score'] < 15:
        print("   🔹 Trade more different tickers for better AI generalization")
    if confidence['consistency_score'] < 15:
        print("   🔹 Focus on improving win rate and profit factor")
    
    if total >= 60:
        print("   ✅ AI confidence is good! Recommendations becoming reliable.")
    elif total >= 40:
        print("   🟡 AI confidence is developing. Continue systematic approach.")
    else:
        print("   🔴 AI confidence is low. Focus on building more training data.")

def get_confidence_bar(score):
    """Create visual confidence bar"""
    filled = int(score / 5)  # 20 bars max (100/5)
    empty = 20 - filled
    return f"[{'█' * filled}{'░' * empty}] {score:.1f}%"

def save_confidence_history():
    """Save confidence scores over time for trend analysis"""
    
    confidence = calculate_ai_confidence_score()
    
    if 'error' in confidence:
        return
    
    # Load existing history
    try:
        history_df = pd.read_excel("ai_confidence_history.xlsx")
    except:
        history_df = pd.DataFrame(columns=['Date', 'Confidence_Score', 'Total_Trades', 'Recommendation'])
    
    # Add current data
    new_row = {
        'Date': datetime.now(),
        'Confidence_Score': confidence['total_confidence'],
        'Total_Trades': confidence['total_trades'],
        'Recommendation': confidence['recommendation']
    }
    
    history_df = pd.concat([history_df, pd.DataFrame([new_row])], ignore_index=True)
    history_df.to_excel("ai_confidence_history.xlsx", index=False)
    
    print(f"📊 Confidence history saved! Tracking {len(history_df)} data points.")

def main():
    """Run AI confidence analysis"""
    
    print("🔍 Analyzing AI Recommendation Confidence...")
    print()
    
    display_confidence_dashboard()
    
    print("\n" + "="*55)
    save_confidence_history()
    
    print("\n💡 TIP: Run this weekly to track AI improvement over time!")
    print("    As confidence score increases, AI recommendations become more reliable.")

if __name__ == "__main__":
    main()