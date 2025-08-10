#!/usr/bin/env python3
"""
Detailed E*TRADE Account Analysis
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from etrade_account_api import ETRADEAccountAPI

def detailed_account_analysis():
    """Perform detailed analysis of E*TRADE accounts"""
    print("🔍 Detailed E*TRADE Account Analysis")
    print("=" * 60)
    
    try:
        api = ETRADEAccountAPI()
        accounts = api.get_account_list()
        
        if not accounts:
            print("❌ No accounts found")
            return
        
        total_portfolio = 0
        
        for account in accounts:
            account_id_key = account.get('accountIdKey')
            account_name = account.get('accountName', '')
            account_type = account.get('accountType', '')
            
            print(f"\n📊 Account: {account_name} ({account_type})")
            print(f"    Account ID: {account_id_key}")
            
            # Try to get account balance first
            try:
                balance_data = api.session.get(f"/v1/accounts/{account_id_key}/balance")
                if balance_data.status_code == 200:
                    balance_json = balance_data.json()
                    print(f"    💰 Balance API Response: {balance_json}")
                else:
                    print(f"    ⚠️ Balance API Error: {balance_data.status_code}")
            except Exception as e:
                print(f"    ❌ Balance API Error: {e}")
            
            # Get positions
            positions = api.get_account_positions(account_id_key)
            
            if not positions:
                print("    📈 No positions found")
                continue
            
            print(f"    📈 Found {len(positions)} positions")
            
            account_total = 0
            cash_balance = 0
            
            for position in positions:
                try:
                    product = position.get('Product', {})
                    symbol = product.get('symbol', '')
                    quantity = float(position.get('quantity', 0))
                    market_value = position.get('marketValue', 0)
                    
                    if symbol == 'MMDA1':  # Money Market / Cash
                        cash_balance += float(market_value)
                        print(f"        💵 Cash/MMDA: ${market_value:,.2f}")
                    else:
                        account_total += float(market_value)
                        print(f"        📈 {symbol}: {quantity} shares = ${market_value:,.2f}")
                    
                except Exception as e:
                    print(f"        ❌ Error processing position: {e}")
            
            account_total += cash_balance
            total_portfolio += account_total
            
            print(f"    💰 Account Total (including cash): ${account_total:,.2f}")
        
        print(f"\n🏦 Total E*TRADE Portfolio: ${total_portfolio:,.2f}")
        
        # Add expected Schwab values
        schwab_ira = 49951.00
        schwab_individual = 1605.60
        schwab_total = schwab_ira + schwab_individual
        
        grand_total = total_portfolio + schwab_total
        
        print(f"🏛️ Schwab IRA: ${schwab_ira:,.2f}")
        print(f"🏛️ Schwab Individual: ${schwab_individual:,.2f}")
        print(f"🏛️ Schwab Total: ${schwab_total:,.2f}")
        
        print(f"\n🎯 Grand Total (E*TRADE + Schwab): ${grand_total:,.2f}")
        
        # Compare with your stated values
        your_etrade_ira = 278418.00
        your_etrade_taxable = 62110.00
        your_etrade_total = your_etrade_ira + your_etrade_taxable
        your_total = 514206.60
        
        print(f"\n📋 Your Manual Values:")
        print(f"    E*TRADE IRA: ${your_etrade_ira:,.2f}")
        print(f"    E*TRADE Taxable: ${your_etrade_taxable:,.2f}")
        print(f"    E*TRADE Total: ${your_etrade_total:,.2f}")
        print(f"    Overall Total: ${your_total:,.2f}")
        
        etrade_diff = total_portfolio - your_etrade_total
        total_diff = grand_total - your_total
        
        print(f"\n📊 Differences:")
        print(f"    E*TRADE API vs Manual: ${etrade_diff:,.2f}")
        print(f"    Total API vs Manual: ${total_diff:,.2f}")
        
    except Exception as e:
        print(f"❌ Error in analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    detailed_account_analysis()
