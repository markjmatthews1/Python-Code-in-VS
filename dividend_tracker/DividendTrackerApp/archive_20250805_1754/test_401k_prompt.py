#!/usr/bin/env python3
"""Test script for 401k value prompting functionality"""

from modules.estimated_income_tracker import build_estimated_income_tracker

print("🧪 Testing dividend tracker with 401k prompting...")
print("Note: You'll be prompted to enter the 401k value during execution")

# Test with prompting (k401_value=None)
build_estimated_income_tracker(use_api=True, include_portfolio=True)

print("✅ Test completed successfully!")
