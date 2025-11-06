from gui.live_dashboard_panel import LiveDashboardPanel
import tkinter as tk

print("🎯 Testing Live Dashboard with Arial 12 Fonts")
print("="*50)

try:
    root = tk.Tk()
    root.title("🎯 Live Dashboard - Arial 12 Font Test")
    root.geometry("1400x900")
    
    dashboard = LiveDashboardPanel(root)
    print("✅ Dashboard created")
    
    dashboard.setup_gui()
    print("✅ GUI setup completed with Arial 12 fonts")
    
    # Verify TreeView font is set
    if hasattr(dashboard, 'scores_tree'):
        style = dashboard.scores_tree['style'] if 'style' in dashboard.scores_tree.keys() else None
        print(f"✅ TreeView style configured: {style}")
        
        children = dashboard.scores_tree.get_children()
        print(f"✅ TreeView has {len(children)} items with improved fonts")
    
    print("\n📖 Opening Live Dashboard with improved Arial 12 fonts...")
    print("   • All labels should now be more readable")
    print("   • TreeView data should be larger and clearer")
    print("   • Control panel text should be consistent")
    print("   Close window when done reviewing")
    
    root.mainloop()
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()