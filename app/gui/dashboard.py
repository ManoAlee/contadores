import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from ..db import get_monthly_summary, get_printer_list

class DashboardFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color="transparent") # Transparent to blend with container
        self._create_widgets()

    def _create_widgets(self):
        # Refresh logic can be separate, but for now we build on init
        self._build_header()
        
        # Data Fetching
        summary = get_monthly_summary()
        printers = get_printer_list()
        
        if not summary and not printers:
            self._build_empty_state()
        else:
            self._build_kpis(summary, printers)
            self._build_charts(summary)

    def _build_header(self):
        title = ctk.CTkLabel(self, text="Dashboard Geral", font=ctk.CTkFont(size=28, weight="bold"))
        title.pack(anchor="w", pady=(20, 10), padx=20)
        
        sub = ctk.CTkLabel(self, text="Visão geral do parque de impressão", font=ctk.CTkFont(size=14), text_color="gray")
        sub.pack(anchor="w", pady=(0, 20), padx=20)

    def _build_empty_state(self):
        # Container
        empty_frame = ctk.CTkFrame(self, fg_color="#2B2B2B", corner_radius=12)
        empty_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Center content using a inner frame
        center = ctk.CTkFrame(empty_frame, fg_color="transparent")
        center.place(relx=0.5, rely=0.5, anchor="center")
        
        icon = ctk.CTkLabel(center, text="📊", font=("Arial", 64))
        icon.pack(pady=10)
        
        lbl = ctk.CTkLabel(center, text="Sem dados para exibir", font=ctk.CTkFont(size=20, weight="bold"))
        lbl.pack(pady=5)
        
        desc = ctk.CTkLabel(center, text="Para começar, clique em 'Configurações' no menu lateral\ne configure as credenciais de e-mail para sincronização.", 
                            text_color="gray", justify="center")
        desc.pack(pady=10)
        
        # Tip
        tip = ctk.CTkFrame(center, fg_color="#3A3A3A", corner_radius=6)
        tip.pack(pady=20, padx=20)
        ctk.CTkLabel(tip, text="💡 Dica: Após configurar, clique em 'Sincronizar Agora'.", text_color="#DDD").pack(padx=15, pady=8)

    def _build_kpis(self, summary, printers):
        kpi_container = ctk.CTkFrame(self, fg_color="transparent")
        kpi_container.pack(fill="x", padx=20, pady=10)
        
        # Calculate Metrics
        total_printers = len(printers)
        
        # Last month volume
        sorted_months = sorted(summary.keys())
        last_month = sorted_months[-1] if sorted_months else "-"
        last_vol = summary[last_month] if sorted_months else 0
        
        # Total Volume (All time in DB)
        total_vol = sum(summary.values())
        
        # Create Cards
        self._create_kpi_card(kpi_container, "Impressoras Ativas", str(total_printers), "💻")
        self._create_kpi_card(kpi_container, "Volume (Último Mês)", f"{last_vol:,}", "📄")
        self._create_kpi_card(kpi_container, "Volume Total", f"{total_vol:,}", "📈")

    def _create_kpi_card(self, parent, title, value, icon):
        card = ctk.CTkFrame(parent, fg_color="#1E1E1E", corner_radius=10, width=250)
        card.pack(side="left", padx=(0, 15), fill="y")
        card.pack_propagate(False) # Enforce width
        
        # Icon
        ctk.CTkLabel(card, text=icon, font=("Arial", 30)).pack(anchor="nw", padx=15, pady=(15, 5))
        
        # Value
        ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=24, weight="bold")).pack(anchor="w", padx=15)
        
        # Title
        ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=12), text_color="gray").pack(anchor="w", padx=15, pady=(0, 15))

    def _build_charts(self, summary):
        # Sort months
        sorted_months = sorted(summary.keys())[-6:] # Last 6 months
        months = [m[5:] for m in sorted_months] # Show MM part
        total_counts = [summary[m] for m in sorted_months]
        
        # Frame for Chart
        chart_frame = ctk.CTkFrame(self, fg_color="#1E1E1E", corner_radius=12)
        chart_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        if not sorted_months:
             return

        # Matplotlib Figure
        # Using dark theme colors
        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=(6, 4), dpi=100)
        fig.patch.set_facecolor('#1E1E1E') # Match card bg
        ax.set_facecolor('#1E1E1E')
        
        # Plot
        ax.plot(months, total_counts, label="Total Impressões", marker="o", color="#00E5FF", linewidth=2)
        ax.fill_between(months, total_counts, color="#00E5FF", alpha=0.1) # Area effect
        
        # Customize Grid/Ticks
        ax.grid(True, linestyle='--', alpha=0.2, color="gray")
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#555')
        ax.spines['bottom'].set_color('#555')
        ax.tick_params(colors='#AAA')
        
        ax.set_title("Evolução Mensal", color="white", pad=20, loc='left', fontsize=12)
        ax.legend(frameon=False, labelcolor='#AAA')

        # Embed
        canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
