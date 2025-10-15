#!/usr/bin/env python3
"""
Test script to verify improved web scraping parsers
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from apis import *
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_mini_split_search():
    """Test the mini split air conditioner search that was failing"""
    search_term = "12000 BTU 115v mini split air conditioner"
    
    print(f"🔍 Testing Mini Split Search: '{search_term}'")
    print("=" * 60)
    
    # Initialize all retailers
    retailers = {
        "Amazon": AmazonPriceChecker(),
        "Walmart": WalmartPriceChecker(), 
        "Target": TargetPriceChecker(),
        "Best Buy": BestBuyPriceChecker(),
        "Home Depot": HomeDepotAPI(),
        "Lowe's": LowesAPI(),
        "Sam's Club": SamsClubPriceChecker()
    }
    
    results = {}
    
    for name, retailer in retailers.items():
        print(f"\n🛒 Testing {name}...")
        try:
            products = retailer.search_products(search_term, max_results=3)
            results[name] = products
            
            if products:
                print(f"✅ Found {len(products)} products on {name}")
                for i, product in enumerate(products[:2], 1):
                    print(f"  {i}. {product['title'][:60]}... - ${product['price']}")
            else:
                print(f"❌ No products found on {name}")
                
        except Exception as e:
            print(f"❌ Error with {name}: {e}")
            results[name] = []
    
    print(f"\n📊 Summary:")
    print("=" * 60)
    total_found = sum(len(products) for products in results.values())
    working_retailers = sum(1 for products in results.values() if products)
    
    print(f"Total products found: {total_found}")
    print(f"Working retailers: {working_retailers}/7")
    
    for name, products in results.items():
        status = "✅" if products else "❌"
        print(f"{status} {name}: {len(products)} products")
    
    return results

if __name__ == "__main__":
    test_mini_split_search()