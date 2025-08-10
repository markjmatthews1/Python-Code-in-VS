"""
Simple configuration test for E*TRADE API
"""

import os
import sys
import configparser

def test_config():
    """Test if config file is readable"""
    print("🔄 Testing configuration file...")
    
    try:
        # Test config file reading
        config_path = os.path.join("modules", "config.ini")
        
        if not os.path.exists(config_path):
            print(f"❌ Config file not found: {config_path}")
            return False
        
        config = configparser.ConfigParser()
        config.read(config_path)
        
        # Check if API section exists
        if "ETRADE_API" not in config:
            print("❌ ETRADE_API section not found in config")
            return False
        
        # Check if keys exist
        consumer_key = config["ETRADE_API"].get("CONSUMER_KEY", "")
        consumer_secret = config["ETRADE_API"].get("CONSUMER_SECRET", "")
        
        if not consumer_key or consumer_key == "your_consumer_key_here":
            print("❌ Consumer key not set in config")
            return False
            
        if not consumer_secret or consumer_secret == "your_consumer_secret_here":
            print("❌ Consumer secret not set in config")
            return False
        
        print("✅ Configuration file loaded successfully")
        print(f"✅ Consumer key: {consumer_key[:8]}...")
        print(f"✅ Consumer secret: {consumer_secret[:8]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing config: {e}")
        return False

if __name__ == "__main__":
    test_config()
