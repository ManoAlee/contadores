#!/usr/bin/env python3
"""gui_main.py
Entry point for the Contadores Impressoras management application.
It launches a CustomTkinter based desktop UI with a navigation bar,
Dashboard, Printers view, Alerts and Settings.
"""

import os
import sys
import customtkinter as ctk
from .gui.navbar import NavBar
from .gui.dashboard import DashboardFrame
from .gui.printers import PrintersFrame
from .gui.alerts import AlertsFrame
from .gui.settings import SettingsFrame
# Future imports for other frames can be added here

# Ensure the application can find the package modules when run from the script location
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Contadores Impressoras – Gestão Premium")
        self.geometry("1200x800")
        self.resizable(True, True)
        # Theme configuration – dark mode with custom colors
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")

        # Initialize frames dictionary first
        self.frames = {}
        
        # Create navigation bar on the left
        self.navbar = NavBar(master=self, callback=self.show_frame)
        self.navbar.pack(side="left", fill="y")

        # Container for dynamic frames
        self.container = ctk.CTkFrame(master=self)
        self.container.pack(side="right", fill="both", expand=True)

        self._init_frames()
        # Show default frame (Dashboard)
        self.show_frame("Dashboard")

    def _init_frames(self):
        # Dashboard frame
        dashboard = DashboardFrame(master=self.container)
        self.frames["Dashboard"] = dashboard
        dashboard.grid(row=0, column=0, sticky="nsew")
        # Printers frame
        printers = PrintersFrame(master=self.container)
        self.frames["Printers"] = printers
        printers.grid(row=0, column=0, sticky="nsew")
        # Alerts frame
        alerts = AlertsFrame(master=self.container)
        self.frames["Alerts"] = alerts
        alerts.grid(row=0, column=0, sticky="nsew")
        # Settings frame
        settings = SettingsFrame(master=self.container)
        self.frames["Settings"] = settings
        settings.grid(row=0, column=0, sticky="nsew")

    def show_frame(self, name: str):
        """Raise the requested frame to the front."""
        frame = self.frames.get(name)
        if frame:
            frame.tkraise()
        else:
            print(f"[WARN] Frame '{name}' not found.")

if __name__ == "__main__":
    app = App()
    app.mainloop()
