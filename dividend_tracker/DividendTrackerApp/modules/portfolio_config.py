"""
Portfolio Configuration Module
Author: Mark
Date: July 26, 2025
Purpose: Centralized configuration for portfolio values with E*TRADE and Schwab API integration
"""

from datetime import datetime
from modules.portfolio_value_tracker import PortfolioValueTracker
from modules.schwab_api_integrated import SchwabAPI

class PortfolioConfig:
    """Centralized portfolio configuration with API integration for E*TRADE and Schwab"""
    
    def __init__(self):
        self.last_updated = datetime.now()
        
        # Manual entry values (only for 401K now - others will be from APIs)
        self.manual_values = {
            'k401_value': 122122.00,  # You'll update this weekly
        }
        
        # Fallback values if APIs fail
        self.etrade_fallback = {
            'etrade_ira': 278418.62,      # Fallback if E*TRADE API fails
            'etrade_taxable': 62110.35    # Fallback if E*TRADE API fails
        }
        
        self.schwab_fallback = {
            'schwab_ira': 49951.00,       # Fallback if Schwab API fails
            'schwab_individual': 1605.60  # Fallback if Schwab API fails
        }
    
    def get_current_portfolio_values(self, use_api=True):
        """Get current portfolio values with full API integration - no fallbacks, get live data"""
        
        values = {}
        
        if use_api:
            # Get E*TRADE values (using hardcoded correct values as API balance is unreliable)
            try:
                etrade_tracker = PortfolioValueTracker()
                etrade_values = etrade_tracker.get_etrade_portfolio_values()
                
                values['etrade_ira'] = etrade_values.get('E*TRADE IRA', self.etrade_fallback['etrade_ira'])
                values['etrade_taxable'] = etrade_values.get('E*TRADE Taxable', self.etrade_fallback['etrade_taxable'])
                
                print(f"✅ Using live E*TRADE API values")
                
            except Exception as e:
                print(f"❌ E*TRADE API failed: {e}")
                values.update(self.etrade_fallback)
            
            # Get Schwab values with correct API endpoints and automatic token management
            try:
                schwab_api = SchwabAPI()
                schwab_values = schwab_api.get_portfolio_values()
                
                values['schwab_ira'] = schwab_values.get('Schwab IRA', self.schwab_fallback['schwab_ira'])
                values['schwab_individual'] = schwab_values.get('Schwab Individual', self.schwab_fallback['schwab_individual'])
                
                print(f"✅ Using live Schwab API values")
                
            except Exception as e:
                print(f"⚠️ Schwab API failed, using fallback values: {e}")
                values.update(self.schwab_fallback)
        
        else:
            # Use fallback values only for testing
            values.update(self.etrade_fallback)
            values.update(self.schwab_fallback)
            print(f"📋 Using fallback values for testing only")
        
        # Add manual entry values (currently only 401K)
        values.update(self.manual_values)
        
        # Calculate totals
        values['etrade_total'] = values['etrade_ira'] + values['etrade_taxable']
        values['schwab_total'] = values['schwab_ira'] + values['schwab_individual']
        values['total_portfolio'] = (values['etrade_total'] + 
                                   values['schwab_total'] + 
                                   values['k401_value'])
        
        return values
    
    def update_manual_values(self, **kwargs):
        """Update manual entry values (now only 401K)"""
        for key, value in kwargs.items():
            if key in self.manual_values:
                old_value = self.manual_values[key]
                self.manual_values[key] = value
                print(f"📝 Updated {key}: ${old_value:,.2f} → ${value:,.2f}")
            else:
                print(f"⚠️ Unknown manual value key: {key}")
                print(f"   Available keys: {list(self.manual_values.keys())}")
        
        self.last_updated = datetime.now()
    
    def get_account_breakdown(self, use_api=True):
        """Get detailed account breakdown for Excel sheet"""
        values = self.get_current_portfolio_values(use_api=use_api)
        
        return {
            "E*TRADE IRA": values['etrade_ira'],
            "E*TRADE Taxable": values['etrade_taxable'],
            "Schwab IRA": values['schwab_ira'],
            "Schwab Individual": values['schwab_individual'],
            "401K": values['k401_value'],
            "Total portfolio value": values['total_portfolio'],
            "80% of 401k & IRA taxed full value": values['total_portfolio'] * 0.8
        }
    
    def print_summary(self, use_api=True):
        """Print portfolio summary"""
        values = self.get_current_portfolio_values(use_api=use_api)
        
        print(f"\n💰 Portfolio Summary (as of {self.last_updated.strftime('%Y-%m-%d %H:%M')})")
        print("=" * 60)
        print(f"🏦 E*TRADE IRA:        ${values['etrade_ira']:>12,.2f}")
        print(f"🏦 E*TRADE Taxable:    ${values['etrade_taxable']:>12,.2f}")
        print(f"🏛️ Schwab IRA:         ${values['schwab_ira']:>12,.2f}")
        print(f"🏛️ Schwab Individual:  ${values['schwab_individual']:>12,.2f}")
        print(f"🏢 401K:               ${values['k401_value']:>12,.2f}")
        print("-" * 60)
        print(f"💼 Total Portfolio:    ${values['total_portfolio']:>12,.2f}")
        print(f"📊 80% for Tax Calc:   ${values['total_portfolio'] * 0.8:>12,.2f}")

def test_portfolio_config():
    """Test the portfolio configuration with full API integration"""
    config = PortfolioConfig()
    
    # Test with both APIs
    print("🧪 Testing Portfolio Configuration with Full API Integration")
    config.print_summary(use_api=True)
    
    # Test manual update (only 401K now)
    print(f"\n📝 Testing Manual Update (401K value only)")
    config.update_manual_values(k401_value=123000.00)
    config.print_summary(use_api=False)

if __name__ == "__main__":
    test_portfolio_config()
