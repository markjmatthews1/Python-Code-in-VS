#!/usr/bin/env python3
"""
Test Schwab News Feed Integration

Quick test to verify the Schwab news feed collector works with the
authentication manager and can be integrated into the main application.

Author: Investment Catalyst Team
Date: September 29, 2025
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_auth_manager():
    """Test authentication manager functionality"""
    print("🔐 Testing Authentication Manager...")
    
    try:
        from utils.auth_manager import get_auth_manager
        
        auth_mgr = get_auth_manager()
        auth_status = auth_mgr.get_auth_status()
        
        print(f"Authentication Status:")
        for service, status in auth_status.items():
            print(f"  {service}: {'✅' if status else '❌'}")
        
        # Test Schwab headers
        schwab_headers = auth_mgr.get_schwab_headers()
        schwab_available = bool(schwab_headers)
        
        print(f"Schwab API Headers: {'✅' if schwab_available else '❌'}")
        
        return schwab_available
        
    except Exception as e:
        print(f"❌ Auth Manager Test Failed: {e}")
        return False

def test_news_collector():
    """Test Schwab news collector functionality"""
    print("\n📰 Testing Schwab News Collector...")
    
    try:
        from utils.auth_manager import get_auth_manager
        from data_collectors.schwab_news_feed import SchwabNewsFeedCollector
        
        # Initialize with auth manager
        auth_mgr = get_auth_manager()
        news_collector = SchwabNewsFeedCollector(auth_mgr)
        
        print("✅ News collector initialized successfully")
        
        # Test with sample tickers
        test_tickers = ['AAPL', 'SMCI', 'MARA']
        print(f"Testing news fetch for: {test_tickers}")
        
        # Note: This will likely fail without proper Schwab auth, but should not crash
        news_data = news_collector.get_news_for_portfolio(test_tickers, hours_back=24)
        
        print(f"✅ News fetch completed: {len(news_data)} articles retrieved")
        
        # Test news processing
        if news_data:
            sample_article = news_data[0]
            print(f"Sample article: {sample_article.get('headline', 'No headline')[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ News Collector Test Failed: {e}")
        return False

def test_portfolio_integration():
    """Test portfolio and news integration"""
    print("\n📊 Testing Portfolio Integration...")
    
    try:
        from data_collectors.portfolio_loader import load_user_portfolio
        
        # Load portfolio
        portfolio_loader = load_user_portfolio()
        
        if portfolio_loader.is_portfolio_loaded():
            tickers = portfolio_loader.get_tickers()
            print(f"✅ Portfolio loaded: {len(tickers)} tickers")
            print(f"   Tickers: {tickers[:5]}{'...' if len(tickers) > 5 else ''}")
            
            # Test news collection for actual portfolio
            from utils.auth_manager import get_auth_manager
            from data_collectors.schwab_news_feed import SchwabNewsFeedCollector
            
            auth_mgr = get_auth_manager()
            news_collector = SchwabNewsFeedCollector(auth_mgr)
            
            print(f"Fetching news for portfolio tickers...")
            news_data = news_collector.get_news_for_portfolio(tickers[:3], hours_back=24)  # Limit to first 3 for testing
            
            print(f"✅ Portfolio news integration successful: {len(news_data)} articles")
            
            return True
        else:
            print("❌ Portfolio not loaded")
            return False
            
    except Exception as e:
        print(f"❌ Portfolio Integration Test Failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Schwab News Feed Integration Test")
    print("=" * 50)
    
    test_results = []
    
    # Test authentication manager
    test_results.append(("Auth Manager", test_auth_manager()))
    
    # Test news collector
    test_results.append(("News Collector", test_news_collector()))
    
    # Test portfolio integration
    test_results.append(("Portfolio Integration", test_portfolio_integration()))
    
    # Summary
    print("\n📋 Test Summary:")
    print("=" * 50)
    
    passed = 0
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(test_results)} tests passed")
    
    if passed == len(test_results):
        print("🎉 All tests passed! Schwab news feed integration is ready.")
    else:
        print("⚠️ Some tests failed. Check authentication and dependencies.")

if __name__ == "__main__":
    main()