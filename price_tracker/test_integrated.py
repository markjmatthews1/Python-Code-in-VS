#!/usr/bin/env python3
"""
Quick test of the integrated price tracker search functionality
"""

if __name__ == "__main__":
    # Test the unified search
    from apis import search_products_unified
    
    test_searches = [
        "mini split air conditioner",
        "laptop computer",
        "cordless drill"
    ]
    
    print("🧪 Testing Integrated Multi-Retailer Search")
    print("=" * 60)
    
    for search_term in test_searches:
        print(f"\n🔍 Searching for: {search_term}")
        print("-" * 40)
        
        try:
            results = search_products_unified(search_term, max_results=3)
            
            if results:
                print(f"✅ Found {len(results)} products:")
                for i, product in enumerate(results, 1):
                    price_str = f"${product['price']:.2f}" if product['price'] > 0 else "Price not available"
                    print(f"  {i}. [{product['retailer']}] {product['title'][:60]}...")
                    print(f"     Price: {price_str}")
                    print()
            else:
                print("❌ No products found")
                
        except Exception as e:
            print(f"❌ Search failed: {e}")
        
        print("-" * 40)
    
    # Clean up
    try:
        from apis import cleanup_global_scraper
        cleanup_global_scraper()
        print("\n🧹 Browser resources cleaned up")
    except:
        pass
    
    print("\n✅ Test completed!")