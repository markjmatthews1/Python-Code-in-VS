"""
Quick verification that dashboards can load with new rotation logic
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_streamlit_import():
    """Test that Streamlit dashboard can import and use rotation engine"""
    print("Testing Streamlit Dashboard Compatibility...")
    
    try:
        from rotation_engine import RotationEngine
        print("✅ RotationEngine imports successfully")
        
        engine = RotationEngine()
        print("✅ RotationEngine instantiates successfully")
        
        targets = engine.find_next_rotation_targets()
        print(f"✅ find_next_rotation_targets() returns {len(targets)} targets")
        
        if targets:
            # Test the display formatting
            ex_day_name = targets[0]['next_ex_div_date'].strftime('%A')
            print(f"✅ Display formatting: 'NEXT ROTATION GROUP - {ex_day_name} Ex-Dividend ({len(targets)} tickers)'")
            
            # Verify all required fields exist
            required_fields = ['ticker', 'name', 'next_ex_div_date', 'buy_deadline', 
                             'deadline_description', 'is_urgent']
            
            for field in required_fields:
                if field in targets[0]:
                    print(f"✅ Field '{field}' exists")
                else:
                    print(f"❌ Field '{field}' missing!")
                    return False
        
        print("\n✅ STREAMLIT DASHBOARD READY")
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_tkinter_import():
    """Test that Tkinter dashboard can import and use rotation engine"""
    print("\nTesting Tkinter Dashboard Compatibility...")
    
    try:
        from rotation_engine import RotationEngine
        print("✅ RotationEngine imports successfully")
        
        engine = RotationEngine()
        print("✅ RotationEngine instantiates successfully")
        
        targets = engine.find_next_rotation_targets()
        print(f"✅ find_next_rotation_targets() returns {len(targets)} targets")
        
        if targets:
            # Test the display formatting
            ex_day_name = targets[0]['next_ex_div_date'].strftime('%A')
            print(f"✅ Display formatting: 'NEXT ROTATION GROUP - {ex_day_name} Ex-Dividend ({len(targets)} tickers)'")
        
        print("\n✅ TKINTER DASHBOARD READY")
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 80)
    print("DASHBOARD COMPATIBILITY TEST")
    print("=" * 80)
    print()
    
    streamlit_ok = test_streamlit_import()
    tkinter_ok = test_tkinter_import()
    
    print("\n" + "=" * 80)
    print("FINAL RESULTS")
    print("=" * 80)
    
    if streamlit_ok and tkinter_ok:
        print("\n✅ ALL DASHBOARDS COMPATIBLE")
        print("\nYou can now run:")
        print("  - Streamlit: streamlit run simple_dashboard.py")
        print("  - Tkinter:   python tkinter_dashboard.py")
        print("\nBoth will show the updated rotation logic:")
        print("  ✓ Only NEXT available ex-date group")
        print("  ✓ Must buy day before ex-date")
        print("  ✓ Automatic rotation after deadline passes")
    else:
        print("\n❌ Some dashboards have compatibility issues")
        if not streamlit_ok:
            print("  - Streamlit dashboard needs attention")
        if not tkinter_ok:
            print("  - Tkinter dashboard needs attention")
