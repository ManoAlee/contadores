# alerts.py
"""gui/alerts.py
Frame to display maintenance alerts based on printer usage.
"""

import customtkinter as ctk
from ..db import get_printer_list

class AlertsFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color="transparent")
        self._create_widgets()

    def _create_widgets(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(30, 20))
        ctk.CTkLabel(header, text="Alertas e Manutenção", font=ctk.CTkFont(family="Roboto", size=28, weight="bold")).pack(side="left")
        
        ctk.CTkButton(header, text="↻ Atualizar", width=100, fg_color="#333", hover_color="#444", command=self.refresh_alerts).pack(side="right")

        # Container for alerts
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.refresh_alerts()

    def refresh_alerts(self):
        for widget in self.scroll.winfo_children():
            widget.destroy()

        printers = get_printer_list()
        alerts_found = 0
        
        MAINTENANCE_THRESHOLD = 50000 

        for p in printers:
            total = p['last_total']
            if total > MAINTENANCE_THRESHOLD:
                alerts_found += 1
                self._create_alert_card(p, f"Alto volume de impressão ({total:,} págs). Manutenção sugerida.")
        
        if alerts_found == 0:
            self._show_empty_state()

    def _show_empty_state(self):
        container = ctk.CTkFrame(self.scroll, fg_color="#1E1E1E", corner_radius=15)
        container.pack(fill="x", pady=20, padx=10, ipady=40)
        
        ctk.CTkLabel(container, text="✅", font=("Arial", 48)).pack(pady=10)
        ctk.CTkLabel(container, text="Tudo Certo!", font=ctk.CTkFont(size=18, weight="bold")).pack()
        ctk.CTkLabel(container, text="Nenhuma impressora requer manutenção no momento.", text_color="gray").pack(pady=5)

    def _create_alert_card(self, printer, message):
        card = ctk.CTkFrame(self.scroll, fg_color="#2A1A1A", corner_radius=12, border_width=1, border_color="#FF5555")
        card.pack(fill="x", pady=8, padx=10)
        
        # Icon
        icon_bg = ctk.CTkFrame(card, width=50, height=50, fg_color="#3A1010", corner_radius=8)
        icon_bg.pack(side="left", padx=15, pady=15)
        icon_bg.pack_propagate(False)
        ctk.CTkLabel(icon_bg, text="⚠️", font=("Arial", 24)).place(relx=0.5, rely=0.5, anchor="center")
        
        # Content
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(side="left", fill="both", expand=True, pady=10)
        
        ctk.CTkLabel(content, text=f"Impressora {printer['printer_id']} ({printer.get('model', 'N/A')})", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w")
        ctk.CTkLabel(content, text=message, text_color="#FFAAAA").pack(anchor="w")
        
        # Action button
        ctk.CTkButton(card, text="📅 Agendar", width=100, fg_color="#D32F2F", hover_color="#B71C1C").pack(side="right", padx=15)
