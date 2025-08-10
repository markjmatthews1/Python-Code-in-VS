#!/usr/bin/env python3
"""
Test script to open just the Trade Log GUI to verify fixes.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from SSO_SDS_Trade_strategy import show_trade_log_gui

if __name__ == "__main__":
    print("Opening Trade Log GUI to test the fixes...")
    show_trade_log_gui()
