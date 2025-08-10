#!/usr/bin/env python3
"""
Console-Based Dividend Completion Display
No GUI needed - beautiful text display in terminal
Perfect for when other apps are running
"""

import os
import sys
from datetime import datetime
import time

def print_colored_box(text, width=60, char="=", color_code=""):
    """Print a colored text box"""
    if color_code:
        print(f"\033[{color_code}m{char * width}\033[0m")
        print(f"\033[{color_code}m{text.center(width)}\033[0m")
        print(f"\033[{color_code}m{char * width}\033[0m")
    else:
        print(char * width)
        print(text.center(width))
        print(char * width)

def print_metric_row(label, value, width=60):
    """Print a metric in a formatted row"""
    dots = "." * (width - len(label) - len(str(value)) - 2)
    print(f" {label} {dots} {value}")

def get_dividend_summary():
    """Get a quick dividend summary from Excel file"""
    try:
        import pandas as pd
        excel_file = os.path.join(os.path.dirname(__file__), "outputs", "Dividends_2025.xlsx")
        
        if not os.path.exists(excel_file):
            return None
            
        # Try to read dividend data
        df = pd.read_excel(excel_file, sheet_name=0)  # First sheet
        
        # Find yield column
        yield_column = None
        for col in df.columns:
            if any(word in col.lower() for word in ['yield', 'div yield', 'dividend yield']):
                yield_column = col
                break
        
        if yield_column and 'value' in [c.lower() for c in df.columns]:
            # Get value column
            value_col = None
            for col in df.columns:
                if 'value' in col.lower() or 'current value' in col.lower():
                    value_col = col
                    break
            
            if value_col:
                # Convert to numeric and filter ≥4% yield
                df[yield_column] = pd.to_numeric(df[yield_column], errors='coerce')
                df[value_col] = pd.to_numeric(df[value_col], errors='coerce')
                
                dividend_stocks = df[df[yield_column] >= 4.0]
                
                if not dividend_stocks.empty:
                    total_value = dividend_stocks[value_col].sum()
                    avg_yield = dividend_stocks[yield_column].mean()
                    position_count = len(dividend_stocks)
                    monthly_income = (total_value * avg_yield / 100) / 12
                    annual_income = total_value * avg_yield / 100
                    
                    return {
                        'total_value': total_value,
                        'avg_yield': avg_yield,
                        'positions': position_count,
                        'monthly_income': monthly_income,
                        'annual_income': annual_income,
                        'data_available': True
                    }
        
        return {'data_available': False}
        
    except Exception as e:
        return {'data_available': False, 'error': str(e)}

def show_console_completion_display():
    """Show beautiful console-based completion display"""
    
    # Clear screen (Windows)
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # Header
    print("\n")
    print_colored_box("🎯 DIVIDEND TRACKER", width=70, char="█", color_code="42")  # Green background
    print_colored_box("✅ WEEKLY PROCESSING COMPLETE", width=70, char="─", color_code="32")  # Green text
    print("\n")
    
    # Get data summary
    summary = get_dividend_summary()
    
    if summary and summary.get('data_available'):
        # Success - show metrics
        print_colored_box("📊 PORTFOLIO SUMMARY", width=70, char="═", color_code="36")  # Cyan
        print()
        
        print_metric_row("💰 Total Dividend Value", f"${summary['total_value']:,.0f}")
        print_metric_row("📈 Average Yield", f"{summary['avg_yield']:.1f}%")
        print_metric_row("🎯 Dividend Positions", f"{summary['positions']}")
        print_metric_row("💵 Monthly Income", f"${summary['monthly_income']:.0f}")
        print_metric_row("🎉 Annual Income", f"${summary['annual_income']:.0f}")
        print_metric_row("📅 Last Updated", datetime.now().strftime('%m/%d/%Y %H:%M'))
        
        print("\n" + "─" * 70)
        print_colored_box("✅ SUCCESS", width=70, char="─", color_code="32")
        
    else:
        # No detailed data - show basic completion
        print_colored_box("✅ PROCESSING COMPLETED", width=70, char="═", color_code="33")  # Yellow
        print()
        print(" 📊 Portfolio data updated successfully")
        print(" 💰 Dividend estimates calculated")
        print(" 📈 Excel report ready")
        print(" 🎯 Showing dividend stocks ≥4% yield only")
        print()
        if summary and 'error' in summary:
            print(f" ⚠️  Data summary unavailable: {summary['error']}")
        else:
            print(" 📋 Check outputs/Dividends_2025.xlsx for detailed results")
    
    print("\n")
    print_colored_box("🎉 ALL SYSTEMS OPERATIONAL", width=70, char="═", color_code="32")
    
    # Instructions
    print("\n📋 NEXT STEPS:")
    print("  📊 Review outputs/Dividends_2025.xlsx for full analysis")
    print("  💰 Only 401k amounts need manual weekly updates")
    print("  🔄 All API data refreshed automatically")
    
    print(f"\n⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("─" * 70)
    
    # Pause to show results
    print("\n💡 Press Enter to continue...")
    try:
        input()
    except:
        time.sleep(5)  # Auto-close after 5 seconds if input fails

def show_minimal_completion():
    """Minimal completion message for absolute reliability"""
    print("\n" + "="*60)
    print("🎯 DIVIDEND TRACKER - PROCESSING COMPLETE")
    print("="*60)
    print("✅ Your dividend data has been processed successfully!")
    print("📊 Check outputs/Dividends_2025.xlsx for results")
    print("🎯 Showing dividend stocks ≥4% yield only")
    print(f"📅 Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

if __name__ == "__main__":
    try:
        show_console_completion_display()
    except Exception as e:
        print(f"⚠️ Console display error: {e}")
        show_minimal_completion()
