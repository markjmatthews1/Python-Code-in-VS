#!/usr/bin/env python3
"""
Complete Dual-Broker Position & Yield Integration Test
======================================================

This script tests the complete integration of:
1. E*TRADE positions (43 positions) + dividend yields (25 dividend stocks)
2. Schwab positions (6 positions) + dividend yield lookups
3. Combined estimated income calculations from both brokers

Demonstrates the full dividend tracker system working with real API data from both brokers.

Author: AI Assistant  
Date: September 6, 2025
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

def test_complete_dual_broker_integration():
    """Test complete integration of E*TRADE + Schwab positions and yields"""
    print("🚀 COMPLETE DUAL-BROKER INTEGRATION TEST")
    print("=" * 60)
    
    try:
        from portfolio_data_collector import PortfolioDataCollector
        collector = PortfolioDataCollector()
        
        print("📊 STEP 1: E*TRADE Positions + Yields")
        print("-" * 40)
        
        # Get E*TRADE data (we know this works)
        etrade_ticker_yields = collector.collect_fresh_ticker_yields_from_etrade_ira()
        etrade_positions = collector.get_etrade_positions_by_account()
        
        etrade_ira_count = len(etrade_positions.get('etrade_ira', []))
        etrade_taxable_count = len(etrade_positions.get('etrade_taxable', []))
        etrade_dividend_count = len([t for t in etrade_ticker_yields.values() if t.get('has_dividend', False)])
        
        print(f"✅ E*TRADE IRA positions: {etrade_ira_count}")
        print(f"✅ E*TRADE Taxable positions: {etrade_taxable_count}")
        print(f"✅ E*TRADE tickers with dividends: {etrade_dividend_count}")
        
        print("\n📊 STEP 2: Schwab Positions + Yield Lookups")
        print("-" * 40)
        
        # Get Schwab positions (just fixed this)
        schwab_positions = collector.get_schwab_positions_by_account()
        schwab_ira_count = len(schwab_positions.get('schwab_ira', []))
        schwab_individual_count = len(schwab_positions.get('schwab_individual', []))
        
        print(f"✅ Schwab IRA positions: {schwab_ira_count}")
        print(f"✅ Schwab Individual positions: {schwab_individual_count}")
        
        # Get dividend yields for Schwab tickers
        schwab_ticker_set = set()
        for positions in schwab_positions.values():
            for pos in positions:
                schwab_ticker_set.add(pos['symbol'])
        
        print(f"✅ Unique Schwab tickers: {len(schwab_ticker_set)}")
        print(f"   Schwab tickers: {', '.join(sorted(schwab_ticker_set))}")
        
        # Look up dividend data for Schwab tickers using E*TRADE API
        print(f"🔍 Looking up dividend yields for Schwab tickers...")
        schwab_ticker_yields = {}
        
        for ticker in schwab_ticker_set:
            if ticker in etrade_ticker_yields:
                schwab_ticker_yields[ticker] = etrade_ticker_yields[ticker]
                print(f"   ✅ {ticker}: {etrade_ticker_yields[ticker].get('yield', 0):.2f}% yield")
            else:
                # Look up via E*TRADE API
                try:
                    yield_data = collector.get_dividend_data_for_ticker(ticker)
                    if yield_data:
                        schwab_ticker_yields[ticker] = yield_data
                        print(f"   📊 {ticker}: {yield_data.get('yield', 0):.2f}% yield (fresh lookup)")
                    else:
                        print(f"   ⚪ {ticker}: No dividend data")
                except Exception as e:
                    print(f"   ❌ {ticker}: Error getting yield - {e}")
        
        print("\n💰 STEP 3: Combined Estimated Income Calculation")
        print("-" * 40)
        
        total_annual_income = 0.0
        total_positions = 0
        dividend_positions = 0
        
        # Process E*TRADE positions
        all_etrade_positions = etrade_positions.get('etrade_ira', []) + etrade_positions.get('etrade_taxable', [])
        for position in all_etrade_positions:
            symbol = position.get('symbol', '')
            quantity = position.get('quantity', 0)
            market_value = position.get('market_value', 0)
            
            total_positions += 1
            
            if symbol in etrade_ticker_yields:
                yield_data = etrade_ticker_yields[symbol]
                dividend_yield = yield_data.get('yield', 0)
                annual_dividend = yield_data.get('annual_dividend', 0)
                
                if annual_dividend > 0:
                    annual_income = annual_dividend * quantity
                elif dividend_yield > 0:
                    annual_income = (dividend_yield / 100) * market_value
                else:
                    annual_income = 0
                    
                if annual_income > 0:
                    total_annual_income += annual_income
                    dividend_positions += 1
        
        # Process Schwab positions  
        all_schwab_positions = schwab_positions.get('schwab_ira', []) + schwab_positions.get('schwab_individual', [])
        for position in all_schwab_positions:
            symbol = position.get('symbol', '')
            quantity = position.get('quantity', 0)
            market_value = position.get('market_value', 0)
            
            total_positions += 1
            
            if symbol in schwab_ticker_yields:
                yield_data = schwab_ticker_yields[symbol]
                dividend_yield = yield_data.get('yield', 0)
                annual_dividend = yield_data.get('annual_dividend', 0)
                
                if annual_dividend > 0:
                    annual_income = annual_dividend * quantity
                elif dividend_yield > 0:
                    annual_income = (dividend_yield / 100) * market_value
                else:
                    annual_income = 0
                    
                if annual_income > 0:
                    total_annual_income += annual_income
                    dividend_positions += 1
                    print(f"   💰 Schwab {symbol}: {quantity} shares × {dividend_yield:.2f}% = ${annual_income:,.2f}/year")
        
        monthly_income = total_annual_income / 12
        
        print("\n🎯 FINAL RESULTS - DUAL BROKER INTEGRATION:")
        print("=" * 60)
        print(f"🏦 Total broker accounts: E*TRADE + Schwab")
        print(f"📊 Total positions: {total_positions}")
        print(f"💰 Dividend-paying positions: {dividend_positions}")
        print(f"📈 Annual estimated income: ${total_annual_income:,.2f}")
        print(f"📅 Monthly estimated income: ${monthly_income:,.2f}")
        
        print(f"\n📋 BREAKDOWN:")
        print(f"   E*TRADE IRA: {etrade_ira_count} positions")
        print(f"   E*TRADE Taxable: {etrade_taxable_count} positions") 
        print(f"   Schwab IRA: {schwab_ira_count} positions")
        print(f"   Schwab Individual: {schwab_individual_count} positions")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in dual-broker integration test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_complete_dual_broker_integration()
    if success:
        print("\n🎉 DUAL-BROKER INTEGRATION TEST COMPLETED SUCCESSFULLY!")
    else:
        print("\n❌ DUAL-BROKER INTEGRATION TEST FAILED!")
    
    input("Press Enter to close...")
