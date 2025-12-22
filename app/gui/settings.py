# settings.py
"""gui/settings.py
Frame to configure application settings:
- IMAP credentials for email parser
- Maintenance thresholds
"""

import customtkinter as ctk
import keyring
from ..email_parser import process_emails
import threading

SERVICE_ID = "ContadoresImpressoras"

class SettingsFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color="transparent")
        self._create_widgets()

    def _create_widgets(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(30, 20))
        ctk.CTkLabel(header, text="Configurações", font=ctk.CTkFont(family="Roboto", size=28, weight="bold")).pack(side="left")

        # Container
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20)

        # === IMAP Configuration Card ===
        box = ctk.CTkFrame(content, fg_color="#1E1E1E", corner_radius=12)
        box.pack(fill="x", pady=10)
        
        ctk.CTkLabel(box, text="📧 Sincronização de E-mail (IMAP)", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", padx=20, pady=(20, 10))
        ctk.CTkLabel(box, text="Configure as credenciais para busca automática dos contadores.", text_color="gray").pack(anchor="w", padx=20, pady=(0, 10))
        
        grid = ctk.CTkFrame(box, fg_color="transparent")
        grid.pack(fill="x", padx=20, pady=(0,20))
        
        ctk.CTkLabel(grid, text="Servidor IMAP:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.entry_host = ctk.CTkEntry(grid, width=300, placeholder_text="imap.gmail.com", height=35)
        self.entry_host.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        ctk.CTkLabel(grid, text="E-mail:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.entry_user = ctk.CTkEntry(grid, width=300, height=35)
        self.entry_user.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        ctk.CTkLabel(grid, text="Senha:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.entry_pass = ctk.CTkEntry(grid, width=300, show="*", height=35)
        self.entry_pass.grid(row=2, column=1, sticky="w", padx=5, pady=5)
        
        btn_save = ctk.CTkButton(box, text="💾 Salvar Credenciais", command=self.save_creds, height=40, font=ctk.CTkFont(weight="bold"))
        btn_save.pack(pady=20, padx=20, fill="x")

        # === Actions Card ===
        box2 = ctk.CTkFrame(content, fg_color="#1E1E1E", corner_radius=12)
        box2.pack(fill="x", pady=10)
        
        ctk.CTkLabel(box2, text="⚡ Ações Rápidas", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", padx=20, pady=(20, 10))
        
        self.btn_sync = ctk.CTkButton(box2, text="🔄 Sincronizar Agora (Ler E-mails)", command=self.run_sync, fg_color="#1f77b4", hover_color="#1565C0", height=40, font=ctk.CTkFont(weight="bold"))
        self.btn_sync.pack(pady=(10, 5), padx=20, fill="x")
        
        self.status_lbl = ctk.CTkLabel(box2, text="", text_color="gray")
        self.status_lbl.pack(pady=(0, 20))
        
        self.load_creds()

    def save_creds(self):
        host = self.entry_host.get()
        user = self.entry_user.get()
        pwd = self.entry_pass.get()
        
        if host and user and pwd:
            keyring.set_password(SERVICE_ID, "host", host)
            keyring.set_password(SERVICE_ID, "user", user)
            keyring.set_password(SERVICE_ID, "pass", pwd)
            self.status_lbl.configure(text="Credenciais salvas com sucesso!", text_color="#00FF00")
        else:
            self.status_lbl.configure(text="Preencha todos os campos!", text_color="#FF5555")

    def load_creds(self):
        host = keyring.get_password(SERVICE_ID, "host")
        user = keyring.get_password(SERVICE_ID, "user")
        if host: self.entry_host.insert(0, host)
        if user: self.entry_user.insert(0, user)

    def run_sync(self):
        self.btn_sync.configure(state="disabled", text="⏳ Sincronizando...")
        self.status_lbl.configure(text="Conectando ao e-mail...", text_color="#FFD700") # Gold
        threading.Thread(target=self._sync_thread, daemon=True).start()
        
    def _sync_thread(self):
        try:
            from .. import email_parser
            
            host = keyring.get_password(SERVICE_ID, "host")
            user = keyring.get_password(SERVICE_ID, "user")
            pwd = keyring.get_password(SERVICE_ID, "pass")
            
            if not host or not user or not pwd:
                self.status_lbl.configure(text="Erro: Credenciais não configuradas.", text_color="#FF5555")
                return

            email_parser.IMAP_HOST = host
            email_parser.IMAP_USER = user
            email_parser.IMAP_PASS = pwd
            
            email_parser.process_emails(mark_as_seen=False)
            
            self.status_lbl.configure(text="Sincronização concluída com sucesso!", text_color="#00FF00")
        except Exception as e:
            self.status_lbl.configure(text=f"Erro: {str(e)}", text_color="#FF5555")
        finally:
            self.btn_sync.configure(state="normal", text="🔄 Sincronizar Agora (Ler E-mails)")
