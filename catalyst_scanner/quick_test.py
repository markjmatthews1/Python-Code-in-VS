from gui.live_dashboard_panel import LiveDashboardPanel
import tkinter as tk

print("🎯 Testing Live Dashboard TreeView Fix")
print("="*50)

try:
    print("✅ Import successful")
    
    root = tk.Tk()
    root.withdraw()  # Hide window for testing
    
    dashboard = LiveDashboardPanel(root)
    print("✅ Dashboard created")
    
    dashboard.setup_gui()
    print("✅ GUI setup completed")
    
    if hasattr(dashboard, 'scores_tree'):
        print("✅ scores_tree TreeView exists")
        
        children = dashboard.scores_tree.get_children()
        print(f"✅ TreeView has {len(children)} data items")
        
        if len(children) > 0:
            # Show first item
            first_item = children[0]
            values = dashboard.scores_tree.item(first_item)['values']
            print(f"📊 First item: {values[0]} - {values[1]}")
            print("🎉 SUCCESS! TreeView fix is working!")
        else:
            print("❌ TreeView has no data")
    else:
        print("❌ scores_tree not found")
        
    root.destroy()
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()