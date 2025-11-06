#!/usr/bin/env python3
"""
Test Script: Schwab Integration with Global Token System
=======================================================

Tests the Schwab balance integration with the dividend tracker's
global authentication system. Validates real-time balance retrieval
without GUI dependencies for testing purposes.
"""

import os
import sys
import traceback

# Add modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

# Import the Schwab integrator from our enhanced script
sys.path.append(os.path.dirname(__file__))
from enhanced_portfolio_updater_with_schwab import SchwabBalanceIntegrator

def test_schwab_integration():
    """Test the Schwab balance integration functionality"""
    
    print("🧪 Testing Schwab Integration with Global Token System")
    print("=" * 60)
    
    try:
        # Initialize the Schwab integrator
        integrator = SchwabBalanceIntegrator()
        
        print(f"\n📁 Token file: {integrator.token_file}")
        print(f"🔑 App key: {integrator.app_key[:8]}...")
        print(f"🌐 Accounts URL: {integrator.accounts_url}")
        
        # Test token loading
        print(f"\n1️⃣ Testing token loading...")
        tokens = integrator.load_tokens()
        
        if tokens:
            print(f"✅ Tokens loaded successfully")
            print(f"🕐 Expires at: {tokens.get('expires_at', 'Unknown')}")
        else:
            print(f"❌ Failed to load tokens")
            return False
            
        # Test token expiration check
        print(f"\n2️⃣ Testing token expiration check...")
        is_expired = integrator.is_token_expired(tokens)
        print(f"⏰ Token expired: {is_expired}")
        
        # Test Schwab balance retrieval
        print(f"\n3️⃣ Testing Schwab balance retrieval...")
        balances = integrator.get_schwab_balances()
        
        if balances:
            print(f"\n✅ Schwab balances retrieved successfully:")
            total = 0
            for account, balance in balances.items():
                print(f"   {account}: ${balance:,.2f}")
                total += balance
            print(f"   📊 Total Schwab: ${total:,.2f}")
            
            return True
        else:
            print(f"❌ Failed to retrieve Schwab balances")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return False

def main():
    """Main test execution"""
    success = test_schwab_integration()
    
    if success:
        print(f"\n🎉 Schwab integration test PASSED!")
        print(f"✅ Ready for portfolio updater integration")
    else:
        print(f"\n❌ Schwab integration test FAILED!")
        print(f"🔧 Check token file and authentication setup")

if __name__ == "__main__":
    main()
    try:
        input("\nPress Enter to continue...")
    except (EOFError, KeyboardInterrupt):
        print("\nExiting...")
