# navbar.py
"""gui/navbar.py
Navigation bar with premium aesthetic.
"""

import customtkinter as ctk

class NavBar(ctk.CTkFrame):
    def __init__(self, master, callback, **kwargs):
        super().__init__(master, width=220, corner_radius=0, **kwargs)
        self.callback = callback
        self.configure(fg_color="#1a1a1a") # Darker background
        self._create_widgets()

    def _create_widgets(self):
        # Header / Logo Area
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(pady=(30, 40), padx=20, fill="x")
        
        ctk.CTkLabel(header, text="🖨️", font=("Arial", 32)).pack(anchor="center")
        ctk.CTkLabel(header, text="CONTADORES", font=ctk.CTkFont(family="Roboto", size=18, weight="bold"), text_color="white").pack(pady=(10,0))
        ctk.CTkLabel(header, text="Gestão Premium", font=ctk.CTkFont(size=12), text_color="gray").pack()

        # Navigation Buttons
        self.buttons = {}
        sections = [
            ("📊 Dashboard", "Dashboard"),
            ("🖨️ Impressoras", "Printers"),
            ("⚠️ Alertas", "Alerts"),
            ("⚙️ De E-mail", "Settings"),
        ]
        
        for label, frame_name in sections:
            btn = ctk.CTkButton(
                self,
                text=label,
                command=lambda name=frame_name: self.handle_click(name),
                width=180,
                height=40,
                corner_radius=8,
                fg_color="transparent",
                text_color="#AAAAAA",
                hover_color="#333333",
                anchor="w",
                font=ctk.CTkFont(size=14)
            )
            btn.pack(pady=5, padx=20)
            self.buttons[frame_name] = btn
            
        # Select first one visually
        self.handle_click("Dashboard")

        # Footer
        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.pack(side="bottom", pady=20)
        ctk.CTkLabel(footer, text="v1.0.0", text_color="#444", font=("Arial", 10)).pack()

    def handle_click(self, frame_name):
        # Update visual state
        for name, btn in self.buttons.items():
            if name == frame_name:
                btn.configure(fg_color="#1f77b4", text_color="white") # Active state
            else:
                btn.configure(fg_color="transparent", text_color="#AAAAAA")
        
        self.callback(frame_name)
