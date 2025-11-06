#!/usr/bin/env python3
"""
Check static headers
"""

# Create headers with corrected structure - removed Current Yield % and Yield Change
static_headers = [
    'Account', 'Ticker', 'Qty # (Historical)', 'Current Qty (API)', 'Price Paid $', 
    'Current Price $', 'Current Value $', 'Original Value $', 'Total Gain $', 'Total Gain %',
    'Payment Cycle', 'Rate/Share', 'Monthly Dividend', 'Annual Dividend',
    'Beginning Yield %'
]

print(f"Static headers count: {len(static_headers)}")
print("Headers:")
for i, header in enumerate(static_headers, 1):
    print(f"  {i:2d}. {header}")
