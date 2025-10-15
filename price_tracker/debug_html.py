#!/usr/bin/env python3
"""
Debug script to examine HTML structure from retailer websites
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import requests
from bs4 import BeautifulSoup
import random
import time
import urllib.parse

def debug_retailer_html(search_term="12000 BTU 115v mini split air conditioner"):
    """Debug HTML structure for retailers"""
    
    retailers_config = {
        "Home Depot": {
            "url": f"https://www.homedepot.com/s/{urllib.parse.quote_plus(search_term)}",
            "headers": {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'DNT': '1'
            }
        },
        "Target": {
            "url": f"https://www.target.com/s?searchTerm={urllib.parse.quote_plus(search_term)}",
            "headers": {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9'
            }
        },
        "Sam's Club": {
            "url": f"https://www.samsclub.com/search?searchTerm={urllib.parse.quote_plus(search_term)}",
            "headers": {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9'
            }
        }
    }
    
    for retailer_name, config in retailers_config.items():
        print(f"\n{'='*60}")
        print(f"🔍 Debugging {retailer_name}")
        print(f"{'='*60}")
        
        try:
            session = requests.Session()
            session.headers.update(config['headers'])
            
            time.sleep(random.uniform(2, 4))
            response = session.get(config['url'], timeout=15)
            
            print(f"Status Code: {response.status_code}")
            print(f"Response Length: {len(response.text)}")
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for common product container patterns
                patterns_to_check = [
                    ('div', {'class': lambda x: x and 'product' in str(x).lower()}),
                    ('div', {'data-testid': True}),
                    ('div', {'data-automation-id': True}),
                    ('article', {}),
                    ('section', {'class': lambda x: x and 'product' in str(x).lower()}),
                    ('li', {'class': lambda x: x and 'product' in str(x).lower()}),
                ]
                
                for tag, attrs in patterns_to_check:
                    elements = soup.find_all(tag, attrs)
                    if elements:
                        print(f"Found {len(elements)} '{tag}' elements with {attrs}")
                        
                        # Show first few class names or attributes
                        for i, elem in enumerate(elements[:3]):
                            classes = elem.get('class', [])
                            test_id = elem.get('data-testid', '')
                            auto_id = elem.get('data-automation-id', '')
                            if classes:
                                print(f"  #{i+1} classes: {' '.join(classes)}")
                            if test_id:
                                print(f"  #{i+1} data-testid: {test_id}")
                            if auto_id:
                                print(f"  #{i+1} data-automation-id: {auto_id}")
                
                # Look for any elements containing price-like text
                price_elements = soup.find_all(text=lambda text: text and '$' in text and any(c.isdigit() for c in text))
                print(f"Found {len(price_elements)} elements with price-like text")
                
                # Sample first few price texts
                for i, price_text in enumerate(price_elements[:3]):
                    print(f"  Price #{i+1}: {price_text.strip()}")
                
                # Look for links
                links = soup.find_all('a', href=True)
                print(f"Found {len(links)} links total")
                
                # Count divs to understand page structure
                all_divs = soup.find_all('div')
                print(f"Total div elements: {len(all_divs)}")
                
                # Check for JavaScript/dynamic content indicators
                scripts = soup.find_all('script')
                print(f"JavaScript scripts: {len(scripts)}")
                
                if 'window.' in response.text or 'JSON.parse' in response.text:
                    print("⚠️  Page likely uses dynamic content loading (JavaScript)")
                
            else:
                print(f"❌ Request failed with status {response.status_code}")
                if response.status_code == 403:
                    print("   This suggests the site is blocking automated requests")
                
        except Exception as e:
            print(f"❌ Error debugging {retailer_name}: {e}")
            continue

if __name__ == "__main__":
    debug_retailer_html()