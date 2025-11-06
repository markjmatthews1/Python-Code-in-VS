#!/usr/bin/env python3
"""
Test Position Data + Ticker Yields Integration
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

def test_estimated_income_calculation():
    """Test if we can calculate estimated income with real position data"""
    print("🧪 TESTING ESTIMATED INCOME CALCULATION")
    print("=" * 50)
    
    try:
        # 1. Test ticker yield collection (we know this works)
        print("\n📊 Step 1: Testing ticker yield collection...")
        from portfolio_data_collector import PortfolioDataCollector
        collector = PortfolioDataCollector()
        
        ticker_yields = collector.collect_fresh_ticker_yields_from_etrade_ira()
        if ticker_yields:
            dividend_count = len([t for t in ticker_yields.values() if t.get('has_dividend', False)])
            print(f"✅ Ticker yields: {len(ticker_yields)} total, {dividend_count} with dividends")
            
            # Show a few examples
            for i, (symbol, data) in enumerate(list(ticker_yields.items())[:5]):
                yield_pct = data.get('yield', 0)
                annual_div = data.get('annual_dividend', 0)
                print(f"   {symbol}: {yield_pct:.2f}% yield, ${annual_div:.4f} annual")
        else:
            print("❌ No ticker yields collected")
            return False
        
        # 2. Test position data collection
        print("\n🏦 Step 2: Testing position data collection...")
        positions = collector.get_etrade_positions_by_account()
        
        ira_positions = positions.get('etrade_ira', [])
        taxable_positions = positions.get('etrade_taxable', [])
        
        print(f"✅ E*TRADE IRA: {len(ira_positions)} positions")
        print(f"✅ E*TRADE Taxable: {len(taxable_positions)} positions")
        
        # Show position examples
        if ira_positions:
            print("\n📋 Sample IRA positions:")
            for pos in ira_positions[:5]:
                symbol = pos.get('symbol', 'N/A')
                quantity = pos.get('quantity', 0)
                market_value = pos.get('market_value', 0)
                print(f"   {symbol}: {quantity} shares, ${market_value:,.2f} value")
        
        # 3. Calculate estimated income
        print("\n💰 Step 3: Calculating estimated income...")
        total_annual_income = 0.0
        position_with_dividends = 0
        
        all_positions = ira_positions + taxable_positions
        
        for position in all_positions:
            symbol = position.get('symbol', '')
            quantity = position.get('quantity', 0)
            
            if symbol in ticker_yields:
                yield_data = ticker_yields[symbol]
                annual_dividend = yield_data.get('annual_dividend', 0)
                dividend_yield = yield_data.get('yield', 0)
                
                if annual_dividend > 0 or dividend_yield > 0:
                    # Calculate annual income for this position
                    if annual_dividend > 0:
                        position_annual_income = annual_dividend * quantity
                    else:
                        # Use yield percentage * market value
                        market_value = position.get('market_value', 0)
                        position_annual_income = (dividend_yield / 100) * market_value
                    
                    total_annual_income += position_annual_income
                    position_with_dividends += 1
                    
                    print(f"   💰 {symbol}: {quantity} × ${annual_dividend:.4f} = ${position_annual_income:.2f}/year")
        
        monthly_income = total_annual_income / 12
        
        print("\n🎯 ESTIMATED INCOME RESULTS:")
        print(f"📊 Total positions analyzed: {len(all_positions)}")
        print(f"💰 Positions with dividends: {position_with_dividends}")
        print(f"📈 Annual estimated income: ${total_annual_income:,.2f}")
        print(f"📅 Monthly estimated income: ${monthly_income:,.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_estimated_income_calculation()
    if success:
        print("\n✅ Test completed successfully!")
    else:
        print("\n❌ Test failed!")
