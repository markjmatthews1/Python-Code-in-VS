#!/usr/bin/env python3
"""
Quick test to verify trade type detection and calculations
"""

def test_trade_type_detection():
    """Test trade type string matching"""
    
    print("🔍 TESTING TRADE TYPE DETECTION")
    print("=" * 40)
    
    test_cases = [
        "Sold Put",
        "sold put", 
        "SOLD PUT",
        "Bought Stock",
        "bought stock",
        "BOUGHT STOCK"
    ]
    
    for test_type in test_cases:
        trade_type = test_type.lower().strip()
        
        print(f"\nOriginal: '{test_type}' → Processed: '{trade_type}'")
        
        if "put" in trade_type and "sold" in trade_type:
            print("   ✅ Detected as: Sold Put")
            print("   → Investment should be blank")
            print("   → Put Cash Req should be calculated")
        elif "stock" in trade_type and "bought" in trade_type:
            print("   ✅ Detected as: Bought Stock")
            print("   → Investment should be calculated")
            print("   → Put fields should be blank")
        else:
            print(f"   ⚠️  Not detected as Sold Put or Bought Stock")

def test_calculations():
    """Test actual calculations"""
    
    print("\n\n🧮 TESTING CALCULATIONS")
    print("=" * 30)
    
    def format_currency(val):
        try:
            num = float(str(val).replace("$","").replace(",","").strip())
            return "$" + format(num, ",.2f")
        except Exception:
            return ""
    
    # Test Sold Put
    print("\n📝 Sold Put Test:")
    trade_type = "sold put"
    shares = -1
    cost = 2.50
    strike = 25.00
    
    print(f"   Inputs: Type='{trade_type}', Shares={shares}, Cost={cost}, Strike={strike}")
    
    if "put" in trade_type and "sold" in trade_type:
        investment = ""
        put_value = format_currency(cost * abs(shares)) if cost and shares else ""
        put_cash_req = format_currency(strike * abs(shares)) if strike and shares else ""
        
        print(f"   Results:")
        print(f"   → Investment: '{investment}' (should be blank)")
        print(f"   → Put Value: '{put_value}' (should be $2.50)")
        print(f"   → Put Cash Req: '{put_cash_req}' (should be $25.00)")

def main():
    test_trade_type_detection()
    test_calculations()
    
    print("\n\n💡 If Sold Put is not working:")
    print("   1. Check the exact text entered in Type field")
    print("   2. Make sure it contains both 'put' and 'sold'")
    print("   3. Check debug output in TradeTracker console")

if __name__ == "__main__":
    main()
