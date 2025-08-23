"""
Test script for Instrument model
Run this file to verify Instrument functionality.
"""

# Add project root to sys.path for import
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from wishlist_tracker.models.instrument import Instrument

# Test 1: Basic instantiation
inst = Instrument(symbol='AAPL', name='Apple Inc.', high_52wk=200.0, current_price=175.5)
print('Test 1:', inst)

# Test 2: to_dict output
print('Test 2:', inst.to_dict())

# Test 3: is_valid (should be True)
print('Test 3:', inst.is_valid())

# Test 4: Blank/invalid instrument
inst2 = Instrument(symbol='', current_price=None)
print('Test 4:', inst2)
print('Test 4 valid?:', inst2.is_valid())

# Test 5: No NaN or 0.0 in output
inst3 = Instrument(symbol='TSLA', name='Tesla', high_52wk=None, current_price=0.0)
print('Test 5:', inst3.to_dict())
print('Test 5 valid?:', inst3.is_valid())
