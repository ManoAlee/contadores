# printers.py
"""gui/printers.py
Modernized list of printers with card design.
"""

import threading
from tkinter import messagebox
import customtkinter as ctk
from ..db import get_printer_list
import threading
from tkinter import messagebox
import customtkinter as ctk
from ..db import get_printer_list
from ..snmp_client import scan_and_update_db


class PrintersFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color="transparent")
        self._create_widgets()

    def _create_widgets(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(30, 20))
        
        ctk.CTkLabel(header, text="Minhas Impressoras", font=ctk.CTkFont(family="Roboto", size=28, weight="bold")).pack(side="left")
        
        # Buttons Container
        btns = ctk.CTkFrame(header, fg_color="transparent")
        btns.pack(side="right")

        # Sync Button (Renamed to Network Scan)
        self.btn_sync = ctk.CTkButton(btns, text="📡 Scan de Rede (IP)", width=160, fg_color="#1f77b4", hover_color="#1565C0", command=self.run_sync)
        self.btn_sync.pack(side="left", padx=(0, 10))

        # Refresh Button
        refresh_btn = ctk.CTkButton(btns, text="↻ Recarregar Visual", width=120, fg_color="#333", hover_color="#444", command=self.refresh)
        refresh_btn.pack(side="left")

        # Scrollable List
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self.refresh()

    def refresh(self):
        for widget in self.scroll.winfo_children():
            widget.destroy()

        printers = get_printer_list()
        
        if not printers:
            self._show_empty_state()
            return
            
        for p in printers:
            self._create_printer_card(p)

    def _show_empty_state(self):
        container = ctk.CTkFrame(self.scroll, fg_color="#1E1E1E", corner_radius=15)
        container.pack(fill="x", pady=20, padx=10, ipady=40)
        
        ctk.CTkLabel(container, text="📭", font=("Arial", 48)).pack(pady=10)
        ctk.CTkLabel(container, text="Nenhuma impressora encontrada", font=ctk.CTkFont(size=18, weight="bold")).pack()
        ctk.CTkLabel(container, text="Os dados aparecerão aqui após a sincronização de e-mails.", text_color="gray").pack(pady=5)

    def _create_printer_card(self, p):
        card = ctk.CTkFrame(self.scroll, fg_color="#1E1E1E", corner_radius=12, border_width=1, border_color="#333")
        card.pack(fill="x", pady=8, padx=10)
        
        # Grid layout inside card
        card.grid_columnconfigure(1, weight=1)
        
        # Icon
        icon_bg = ctk.CTkFrame(card, width=50, height=50, fg_color="#252525", corner_radius=8)
        icon_bg.grid(row=0, column=0, rowspan=2, padx=15, pady=15)
        icon_bg.pack_propagate(False)
        ctk.CTkLabel(icon_bg, text="🖨️", font=("Arial", 24)).place(relx=0.5, rely=0.5, anchor="center")

        # Info
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.grid(row=0, column=1, rowspan=2, sticky="ns", pady=10)
        # Parse rich model string "Model|Sector|IP"
        raw_model = p.get('model') or "Modelo Desconhecido"
        if "|" in raw_model:
            parts = raw_model.split("|")
            model_text = parts[0]
            sector_text = parts[1] if len(parts) > 1 else ""
            ip_text = parts[2] if len(parts) > 2 else ""
        else:
            model_text = raw_model
            sector_text = ""
            ip_text = ""

        # Model and Sector
        title_text = f"Lexmark {model_text}"
        if sector_text:
            title_text += f"  •  {sector_text}"
            
        ctk.CTkLabel(info_frame, text=title_text, font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w")
        
        # Subtitle with IP and Serial
        subtitle = f"N/S: {p['printer_id']}"
        if ip_text:
            subtitle += f"  |  IP: {ip_text}"
            
        ctk.CTkLabel(info_frame, text=subtitle, text_color="gray", font=ctk.CTkFont(size=13)).pack(anchor="w")

        # Metrics (Right side)
        metrics_frame = ctk.CTkFrame(card, fg_color="transparent")
        metrics_frame.grid(row=0, column=2, padx=20, pady=15, sticky="e")
        
        # Pages Pill
        pages_pill = ctk.CTkFrame(metrics_frame, fg_color="#2b3b4b", corner_radius=15)
        pages_pill.pack(pady=2)
        ctk.CTkLabel(pages_pill, text=f"{p['last_total']:,} págs", text_color="#64B5F6", font=ctk.CTkFont(weight="bold")).pack(padx=10, pady=2)
        
        # Date
        date_str = p['last_timestamp'][:10]
        ctk.CTkLabel(metrics_frame, text=f"Desde {date_str}", font=ctk.CTkFont(size=10), text_color="#666").pack()

        # Hover effects
        card.bind("<Enter>", lambda e, c=card: c.configure(border_color="#1f77b4", border_width=2))
        card.bind("<Leave>", lambda e, c=card: c.configure(border_color="#333", border_width=1))

    def run_sync(self):
        """Trigger SNMP Network Scan."""
        self.btn_sync.configure(state="disabled", text="📡 Escaneando IPs...")
        threading.Thread(target=self._sync_thread, daemon=True).start()

    def _sync_thread(self):
        try:
            # Get current list which contains IPs in the model field
            printers = get_printer_list()
            
            # Run scan
            updated_count, errors = scan_and_update_db(printers)
            
            # Success feedback
            self.after(0, lambda: self._on_sync_success(updated_count, errors))

        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Erro de Scan", f"Falha na comunicação: {str(e)}"))
        finally:
            self.after(0, lambda: self.btn_sync.configure(state="normal", text="📡 Scan de Rede (IP)"))

    def _on_sync_success(self, count, errors):
        self.refresh()
        
        msg = f"Varredura finalizada!\n{count} impressoras responderam com dados atualizados."
        if errors:
            msg += "\n\nErros encontrados:\n" + "\n".join(errors[:5])
            if len(errors) > 5:
                msg += f"\n...e mais {len(errors)-5} erros."
        
        icon = "info" if not errors else "warning"
        messagebox.showinfo("Scan Concluído", msg, icon=icon)
