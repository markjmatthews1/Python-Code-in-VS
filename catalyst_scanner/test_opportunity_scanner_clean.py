#!/usr/bin/env python3
"""
Test Opportunity Scanner with no hardcoded data
Verify it doesn't show fake SMCI earnings
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from analyzers.opportunity_scanner import OpportunityScanner

def test_opportunity_scanner_no_fake_data():
    """Test that OpportunityScanner doesn't show fake SMCI earnings"""
    
    print("=== OPPORTUNITY SCANNER CLEAN TEST ===")
    
    # Initialize scanner
    scanner = OpportunityScanner()
    
    # Empty catalyst events (no hardcoded data)
    catalyst_events = []
    
    # Empty portfolio and technical data
    portfolio_data = {}
    technical_data = {}
    
    # Scan for opportunities
    opportunities = scanner.scan_opportunities(
        portfolio_data=portfolio_data,
        technical_data=technical_data,
        catalyst_events=catalyst_events
    )
    
    print(f"Number of opportunities found: {len(opportunities)}")
    
    # Check for any SMCI references
    smci_opportunities = [opp for opp in opportunities if 'SMCI' in str(opp)]
    
    if smci_opportunities:
        print("❌ ERROR: Found SMCI opportunities with potentially fake data:")
        for opp in smci_opportunities:
            print(f"   {opp}")
    else:
        print("✅ SUCCESS: No SMCI opportunities with fake data found")
    
    print(f"All opportunities: {opportunities}")
    
    return len(smci_opportunities) == 0

if __name__ == "__main__":
    success = test_opportunity_scanner_no_fake_data()
    print(f"\nTest passed: {success}")