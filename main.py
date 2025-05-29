"""
RLC Circuit Simulator - Main Entry Point
Educational tool for analyzing RLC circuit time-domain responses
"""

import sys
import tkinter as tk
from gui_interface import RLCSimulatorGUI

def main():
    """Main entry point for the RLC Circuit Simulator"""
    try:
        # Create the main window
        root = tk.Tk()
        root.title("RLC Circuit Simulator - Educational Tool")
        root.geometry("1200x800")
        
        # Set minimum window size
        root.minsize(800, 600)
        
        # Create the main application
        app = RLCSimulatorGUI(root)
        
        # Start the GUI event loop
        root.mainloop()
        
    except Exception as e:
        print(f"Error starting RLC Circuit Simulator: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
