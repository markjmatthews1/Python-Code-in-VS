"""
RecoveryApp Main Entry Point
Uses existing auth renewal apps from parent directory
"""
import tkinter as tk
from gui.recovery_gui import RecoveryAppGUI

def main():
    """Main entry point for RecoveryApp"""
    root = tk.Tk()
    app = RecoveryAppGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()