import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
from datetime import datetime
from config import Config
from trade_history import TradeHistory
from api_manager import APIManager
from chart_generator import ChartGenerator
from language import Language
from updater import Updater
import threading

VERSION = "1.5.0"

# Download font on startup
try:
    from font_downloader import download_vazirmatn_font
    download_vazirmatn_font()
except:
    pass

class ModernButton(tk.Button):
    """Premium glassmorphism button"""
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.default_bg = kwargs.get('bg', '#4a90e2')
        self.hover_bg = '#357abd'
        
        self.config(
            relief=tk.FLAT,
            bd=0,
            padx=20,
            pady=12,
            cursor='hand2',
            font=('Segoe UI', 10, 'bold')
        )
        
        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)
    
    def on_enter(self, e):
        self.config(bg=self.hover_bg)
    
    def on_leave(self, e):
        self.config(bg=self.default_bg)

class CryptoTradingCalculator:
    def __init__(self, root):
        self.root = root
        
        # Initialize systems
        self.language = Language()
        self.updater = Updater()
        
        # Load language
        saved_lang = self.load_language_preference()
        if saved_lang:
            self.language.set_language(saved_lang)
        
        self.root.title(f"{self.language.get('app_title')} v{VERSION}")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 800)
        
        # Setup fonts
        self.setup_fonts()
        
        # Load config
        self.config = Config()
        self.history = TradeHistory()
        self.api_manager = APIManager()
        self.chart_generator = ChartGenerator()
        
        # Exchanges
        self.exchanges = {
            "Binance": {"maker": 0.02, "taker": 0.04, "default": 0.04},
            "Bybit": {"maker": 0.02, "taker": 0.055, "default": 0.055},
            "OKX": {"maker": 0.02, "taker": 0.05, "default": 0.05},
            "KuCoin": {"maker": 0.02, "taker": 0.06, "default": 0.06},
            "Gate.io": {"maker": 0.015, "taker": 0.05, "default": 0.05},
            "Bitget": {"maker": 0.02, "taker": 0.06, "default": 0.06},
            "MEXC": {"maker": 0.0, "taker": 0.02, "default": 0.02},
            "CoinEx": {"maker": 0.16, "taker": 0.26, "default": 0.26},
            "Nobitex": {"maker": 0.35, "taker": 0.35, "default": 0.35},
            "Wallex": {"maker": 0.2, "taker": 0.2, "default": 0.2},
            "Exir": {"maker": 0.35, "taker": 0.35, "default": 0.35},
            "Custom": {"maker": 0.15, "taker": 0.15, "default": 0.15}
        }
        
        # Premium themes
        self.themes = {
            'light': {
                'bg': '#f0f4f8',
                'fg': '#1a202c',
                'card_bg': '#ffffff',
                'input_bg': '#ffffff',
                'input_fg': '#2d3748',
                'button_bg': '#4a90e2',
                'button_fg': '#ffffff',
                'button_hover': '#357abd',
                'accent': '#4a90e2',
                'border': '#e2e8f0',
                'success': '#48bb78',
                'error': '#f56565',
                'text_bg': '#ffffff',
                'text_fg': '#2d3748',
            },
            'dark': {
                'bg': '#0f172a',
                'fg': '#e2e8f0',
                'card_bg': '#1e293b',
                'input_bg': '#334155',
                'input_fg': '#e2e8f0',
                'button_bg': '#4a90e2',
                'button_fg': '#ffffff',
                'button_hover': '#357abd',
                'accent': '#60a5fa',
                'border': '#475569',
                'success': '#4ade80',
                'error': '#f87171',
                'text_bg': '#1e293b',
                'text_fg': '#e2e8f0',
            }
        }
        
        self.current_theme = self.config.theme
        self.tp_entries = []
        
        self.create_widgets()
        self.apply_theme()
        self.update_ui_language()
        
    def setup_fonts(self):
        """Setup beautiful fonts"""
        # Try Vazirmatn first, then fallback
        font_file = 'Vazirmatn-Regular.ttf'
        if os.path.exists(font_file):
            try:
                self.title_font = ('Vazirmatn', 24, 'bold')
                self.header_font = ('Vazirmatn', 16, 'bold')
                self.body_font = ('Vazirmatn', 11)
                self.body_font_bold = ('Vazirmatn', 11, 'bold')
                return
            except:
                pass
        
        # Fallback fonts
        self.title_font = ('Segoe UI', 24, 'bold')
        self.header_font = ('Segoe UI', 16, 'bold')
        self.body_font = ('Segoe UI', 11)
        self.body_font_bold = ('Segoe UI', 11, 'bold')
    
    def load_language_preference(self):
        try:
            if os.path.exists('config.json'):
                with open('config.json', 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    return config.get('language', 'fa')
        except:
            pass
        return 'fa'
    
    def save_language_preference(self):
        try:
            config_data = {}
            if os.path.exists('config.json'):
                with open('config.json', 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
            
            config_data['language'] = self.language.current
            
            with open('config.json', 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=4, ensure_ascii=False)
        except:
            pass
    
    def toggle_language(self):
        new_lang = 'en' if self.language.current == 'fa' else 'fa'
        self.language.set_language(new_lang)
        self.save_language_preference()
        self.root.title(f"{self.language.get('app_title')} v{VERSION}")
        
        # Rebuild UI
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        self.tp_entries = []
        self.create_exchange_card()
        self.create_capital_card()
        self.create_trade_card()
        self.create_results_card()
        self.apply_theme()
        self.update_ui_language()
    
    def update_ui_language(self):
        try:
            if self.current_theme == 'dark':
                self.theme_btn.configure(text=f"☀️ {self.language.get('light_mode')}")
            else:
                self.theme_btn.configure(text=f"🌙 {self.language.get('dark_mode')}")
            
            if self.language.current == 'fa':
                self.lang_btn.configure(text="🌐 English")
            else:
                self.lang_btn.configure(text="🌐 فارسی")
            
            self.settings_btn.configure(text=f"⚙️ {self.language.get('settings')}")
            self.history_btn.configure(text=f"📊 {self.language.get('history')}")
            self.charts_btn.configure(text=f"📈 {self.language.get('charts')}")
            self.update_btn.configure(text=f"🔄 {self.language.get('update')}")
        except:
            pass
    
    def create_widgets(self):
        # Main container
        self.main_container = tk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Top bar
        self.top_bar = tk.Frame(self.main_container, height=70)
        self.top_bar.pack(fill=tk.X, side=tk.TOP, padx=20, pady=(20, 10))
        self.top_bar.pack_propagate(False)
        
        # Title
        title_frame = tk.Frame(self.top_bar)
        title_frame.pack(side=tk.LEFT, padx=20)
        
        title_label = tk.Label(title_frame, text=f"💎 {self.language.get('app_title')}", 
                              font=self.title_font)
        title_label.pack(anchor=tk.W)
        
        version_label = tk.Label(title_frame, text=f"v{VERSION}", 
                                font=self.body_font)
        version_label.pack(anchor=tk.W)
        
        # Buttons
        btn_frame = tk.Frame(self.top_bar)
        btn_frame.pack(side=tk.RIGHT, padx=20)
        
        self.theme_btn = ModernButton(btn_frame, text="🌙", command=self.toggle_theme, width=12)
        self.theme_btn.pack(side=tk.LEFT, padx=3)
        
        self.settings_btn = ModernButton(btn_frame, text="⚙️", command=self.show_settings, width=12)
        self.settings_btn.pack(side=tk.LEFT, padx=3)
        
        self.history_btn = ModernButton(btn_frame, text="📊", command=self.show_history, width=12)
        self.history_btn.pack(side=tk.LEFT, padx=3)
        
        self.charts_btn = ModernButton(btn_frame, text="📈", command=self.show_charts, width=12)
        self.charts_btn.pack(side=tk.LEFT, padx=3)
        
        self.lang_btn = ModernButton(btn_frame, text="🌐", command=self.toggle_language, width=12)
        self.lang_btn.pack(side=tk.LEFT, padx=3)
        
        self.update_btn = ModernButton(btn_frame, text="🔄", command=self.show_update_manager, width=12)
        self.update_btn.pack(side=tk.LEFT, padx=3)
        
        # Content
        content_frame = tk.Frame(self.main_container)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        canvas = tk.Canvas(content_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.main_canvas = canvas
        
        # Cards
        self.create_exchange_card()
        self.create_capital_card()
        self.create_trade_card()
        self.create_results_card()
    
    def create_card(self, title, icon=""):
        """Create premium card"""
        card = tk.Frame(self.scrollable_frame, relief=tk.RAISED, bd=2)
        card.pack(fill=tk.X, padx=10, pady=12)
        
        # Header
        header = tk.Frame(card, height=50)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        header_label = tk.Label(header, text=f"{icon}  {title}", font=self.header_font)
        header_label.pack(side=tk.LEFT, padx=25, pady=15)
        
        # Body
        body = tk.Frame(card)
        body.pack(fill=tk.BOTH, expand=True, padx=25, pady=20)
        
        return card, body
    
    def create_exchange_card(self):
        card, body = self.create_card(self.language.get('exchange_symbol'), "🏦")
        self.exchange_card = card
        
        for i in range(4):
            body.columnconfigure(i, weight=1)
        
        # Row 1
        tk.Label(body, text=self.language.get('exchange'), font=self.body_font_bold).grid(
            row=0, column=0, sticky=tk.W, padx=10, pady=10)
        
        self.exchange_combo = ttk.Combobox(body, values=list(self.exchanges.keys()), 
                                          width=25, state="readonly", font=self.body_font)
        self.exchange_combo.set(self.config.selected_exchange)
        self.exchange_combo.grid(row=0, column=1, sticky=tk.W, padx=10, pady=10)
        self.exchange_combo.bind('<<ComboboxSelected>>', self.on_exchange_change)
        
        tk.Label(body, text=self.language.get('order_type'), font=self.body_font_bold).grid(
            row=0, column=2, sticky=tk.W, padx=10, pady=10)
        
        self.order_type_combo = ttk.Combobox(body, values=["Maker", "Taker"], 
                                             width=20, state="readonly", font=self.body_font)
        self.order_type_combo.set("Taker")
        self.order_type_combo.grid(row=0, column=3, sticky=tk.W, padx=10, pady=10)
        self.order_type_combo.bind('<<ComboboxSelected>>', self.on_order_type_change)
        
        # Row 2
        tk.Label(body, text=self.language.get('symbol'), font=self.body_font_bold).grid(
            row=1, column=0, sticky=tk.W, padx=10, pady=10)
        
        self.symbol_combo = ttk.Combobox(body, values=self.api_manager.get_available_symbols(), 
                                        width=25, state="readonly", font=self.body_font)
        self.symbol_combo.set('BTCUSDT')
        self.symbol_combo.grid(row=1, column=1, sticky=tk.W, padx=10, pady=10)
        
        self.live_price_btn = ModernButton(body, text=f"💹 {self.language.get('live_price')}", 
                                          command=self.get_live_price, width=18)
        self.live_price_btn.grid(row=1, column=2, padx=10, pady=10, sticky=tk.W)
        
        self.live_price_label = tk.Label(body, text="-", font=self.header_font)
        self.live_price_label.grid(row=1, column=3, sticky=tk.W, padx=10, pady=10)
    
    def create_capital_card(self):
        card, body = self.create_card(self.language.get('capital_risk'), "💰")
        self.capital_card = card
        
        for i in range(4):
            body.columnconfigure(i, weight=1)
        
        tk.Label(body, text=self.language.get('total_capital'), font=self.body_font_bold).grid(
            row=0, column=0, sticky=tk.W, padx=10, pady=10)
        
        self.capital_entry = tk.Entry(body, font=self.body_font, width=25)
        self.capital_entry.insert(0, str(self.config.capital))
        self.capital_entry.grid(row=0, column=1, sticky=tk.W, padx=10, pady=10)
        
        tk.Label(body, text=self.language.get('risk_percent'), font=self.body_font_bold).grid(
            row=0, column=2, sticky=tk.W, padx=10, pady=10)
        
        self.risk_entry = tk.Entry(body, font=self.body_font, width=25)
        self.risk_entry.insert(0, str(self.config.risk_percent))
        self.risk_entry.grid(row=0, column=3, sticky=tk.W, padx=10, pady=10)
        
        tk.Label(body, text=self.language.get('fee_percent'), font=self.body_font_bold).grid(
            row=1, column=0, sticky=tk.W, padx=10, pady=10)
        
        self.fee_entry = tk.Entry(body, font=self.body_font, width=25)
        self.fee_entry.insert(0, str(self.config.fee_percent))
        self.fee_entry.grid(row=1, column=1, sticky=tk.W, padx=10, pady=10)
        
        save_btn = ModernButton(body, text=f"💾 {self.language.get('save_settings')}", 
                               command=self.save_settings_clicked)
        save_btn.grid(row=1, column=2, columnspan=2, padx=10, pady=10, sticky=tk.W)
    
    def create_trade_card(self):
        card, body = self.create_card(self.language.get('trade_info'), "📊")
        self.trade_card = card
        
        for i in range(4):
            body.columnconfigure(i, weight=1)
        
        # Row 1
        tk.Label(body, text=self.language.get('entry_price'), font=self.body_font_bold).grid(
            row=0, column=0, sticky=tk.W, padx=10, pady=10)
        self.entry_price = tk.Entry(body, font=self.body_font, width=23)
        self.entry_price.grid(row=0, column=1, sticky=tk.W, padx=10, pady=10)
        
        tk.Label(body, text=self.language.get('stop_loss'), font=self.body_font_bold).grid(
            row=0, column=2, sticky=tk.W, padx=10, pady=10)
        self.stop_loss = tk.Entry(body, font=self.body_font, width=23)
        self.stop_loss.grid(row=0, column=3, sticky=tk.W, padx=10, pady=10)
        
        # Row 2
        tk.Label(body, text=f"{self.language.get('take_profit')} 1", font=self.body_font_bold).grid(
            row=1, column=0, sticky=tk.W, padx=10, pady=10)
        self.tp1_entry = tk.Entry(body, font=self.body_font, width=23)
        self.tp1_entry.grid(row=1, column=1, sticky=tk.W, padx=10, pady=10)
        self.tp_entries.append(self.tp1_entry)
        
        tk.Label(body, text=f"{self.language.get('take_profit')} 2", font=self.body_font_bold).grid(
            row=1, column=2, sticky=tk.W, padx=10, pady=10)
        self.tp2_entry = tk.Entry(body, font=self.body_font, width=23)
        self.tp2_entry.grid(row=1, column=3, sticky=tk.W, padx=10, pady=10)
        self.tp_entries.append(self.tp2_entry)
        
        # Row 3
        tk.Label(body, text=f"{self.language.get('take_profit')} 3", font=self.body_font_bold).grid(
            row=2, column=0, sticky=tk.W, padx=10, pady=10)
        self.tp3_entry = tk.Entry(body, font=self.body_font, width=23)
        self.tp3_entry.grid(row=2, column=1, sticky=tk.W, padx=10, pady=10)
        self.tp_entries.append(self.tp3_entry)
        
        tk.Label(body, text=self.language.get('position_type'), font=self.body_font_bold).grid(
            row=2, column=2, sticky=tk.W, padx=10, pady=10)
        self.position_type = ttk.Combobox(body, values=["LONG", "SHORT"], width=21, 
                                         state="readonly", font=self.body_font)
        self.position_type.set("LONG")
        self.position_type.grid(row=2, column=3, sticky=tk.W, padx=10, pady=10)
        
        # Row 4
        tk.Label(body, text=self.language.get('leverage'), font=self.body_font_bold).grid(
            row=3, column=0, sticky=tk.W, padx=10, pady=10)
        self.leverage = tk.Entry(body, font=self.body_font, width=23)
        self.leverage.insert(0, "10")
        self.leverage.grid(row=3, column=1, sticky=tk.W, padx=10, pady=10)
        
        tk.Label(body, text=self.language.get('notes'), font=self.body_font_bold).grid(
            row=3, column=2, sticky=tk.W, padx=10, pady=10)
        self.notes_entry = tk.Entry(body, font=self.body_font, width=23)
        self.notes_entry.grid(row=3, column=3, sticky=tk.W, padx=10, pady=10)
        
        # Calculate button
        calc_frame = tk.Frame(body)
        calc_frame.grid(row=4, column=0, columnspan=4, pady=25)
        
        self.calc_btn = ModernButton(calc_frame, text=f"🔢 {self.language.get('calculate')}", 
                                     command=self.calculate, width=30)
        self.calc_btn.pack()
    
    def create_results_card(self):
        card, body = self.create_card(self.language.get('results'), "📋")
        self.results_card = card
        
        text_frame = tk.Frame(body)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.results_text = tk.Text(text_frame, height=18, font=('Consolas', 10), 
                                    wrap=tk.WORD, relief=tk.FLAT, padx=15, pady=15)
        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=self.results_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.results_text.config(yscrollcommand=scrollbar.set)
        
        btn_frame = tk.Frame(body)
        btn_frame.pack(fill=tk.X, pady=(15, 0))
        
        self.export_btn = ModernButton(btn_frame, text=f"💾 {self.language.get('export_csv')}", 
                                 command=self.export_csv, width=18)
        self.export_btn.pack(side=tk.LEFT, padx=5)
        
        self.clear_btn = ModernButton(btn_frame, text=f"🗑️ {self.language.get('clear_results')}", 
                                command=self.clear_results, width=20)
        self.clear_btn.pack(side=tk.LEFT, padx=5)
    
    def show_update_manager(self):
        """Show update manager"""
        update_window = tk.Toplevel(self.root)
        update_window.title(self.language.get('update_manager'))
        update_window.geometry("700x750")
        
        theme = self.themes[self.current_theme]
        update_window.configure(bg=theme['bg'])
        
        main_frame = tk.Frame(update_window, bg=theme['card_bg'], padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        title = tk.Label(main_frame, text=f"🔄 {self.language.get('update_manager')}", 
                        font=self.title_font, bg=theme['card_bg'], fg=theme['fg'])
        title.pack(pady=(0, 20))
        
        # Current version
        current_frame = tk.Frame(main_frame, bg=theme['card_bg'])
        current_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(current_frame, text=f"{self.language.get('current_version')}: v{VERSION}", 
                font=self.body_font_bold, bg=theme['card_bg'], fg=theme['accent']).pack(anchor=tk.W)
        
        # Status
        status_label = tk.Label(main_frame, text=self.language.get('checking_update'), 
                               font=self.body_font, bg=theme['card_bg'], fg=theme['fg'])
        status_label.pack(pady=10)
        
        def check_update():
            status_label.config(text=f"⏳ {self.language.get('checking_update')}")
            update_window.update()
            
            update_info = self.updater.check_for_update()
            
            if update_info['available']:
                status_label.config(text=f"✅ {self.language.get('update_available')}\n{self.language.get('latest_version')}: v{update_info['latest']}")
                update_btn.config(state=tk.NORMAL)
            else:
                status_label.config(text=f"✅ {self.language.get('up_to_date')}")
                update_btn.config(state=tk.DISABLED)
        
        update_btn = ModernButton(main_frame, text=f"⬆️ {self.language.get('update_now')}", 
                                 command=lambda: self.perform_update(status_label), 
                                 width=25, state=tk.DISABLED)
        update_btn.pack(pady=15)
        
        # Version list
        tk.Label(main_frame, text=self.language.get('select_version'), 
                font=self.header_font, bg=theme['card_bg'], fg=theme['fg']).pack(pady=(20, 10))
        
        list_frame = tk.Frame(main_frame, bg=theme['input_bg'])
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        versions_list = tk.Listbox(list_frame, height=12, font=self.body_font,
                                   bg=theme['input_bg'], fg=theme['input_fg'])
        versions_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        versions_scroll = ttk.Scrollbar(list_frame, orient="vertical", command=versions_list.yview)
        versions_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        versions_list.config(yscrollcommand=versions_scroll.set)
        
        def load_versions():
            versions = self.updater.get_all_versions()
            for v in versions:
                versions_list.insert(tk.END, f"v{v['version']} - {v['name']}")
        
        def install_selected():
            selection = versions_list.curselection()
            if not selection:
                messagebox.showwarning(self.language.get('info'), "Please select a version")
                return
            
            selected_text = versions_list.get(selection[0])
            version = selected_text.split(' ')[0].replace('v', '')
            
            if messagebox.askyesno(self.language.get('confirm'), f"Install version {version}?"):
                self.perform_update(status_label, version)
        
        install_btn = ModernButton(main_frame, text=f"📥 {self.language.get('install_version')}", 
                                  command=install_selected, width=25)
        install_btn.pack(pady=15)
        
        update_window.after(500, check_update)
        update_window.after(1000, load_versions)
    
    def perform_update(self, status_label, version=None):
        status_label.config(text=f"⏳ {self.language.get('updating')}...")
        self.root.update()
        
        try:
            if version:
                result = self.updater.update_to_version(version)
            else:
                result = self.updater.update_to_latest()
            
            if result['success']:
                status_label.config(text=f"✅ {self.language.get('update_success')}")
                messagebox.showinfo(self.language.get('success'), 
                                   f"{self.language.get('update_success')}\n\n{self.language.get('restart_required')}")
                self.root.quit()
            else:
                status_label.config(text=f"❌ {self.language.get('update_error')}")
                messagebox.showerror(self.language.get('error'), 
                                    f"{self.language.get('update_error')}\n\nFailed: {', '.join(result['failed'])}")
        except Exception as e:
            status_label.config(text=f"❌ {str(e)}")
            messagebox.showerror(self.language.get('error'), str(e))
        
    def toggle_theme(self):
        self.current_theme = 'dark' if self.current_theme == 'light' else 'light'
        self.apply_theme()
        self.update_ui_language()
        self.save_settings_clicked(show_message=False)
        
    def apply_theme(self):
        """Apply theme"""
        theme = self.themes[self.current_theme]
        
        self.root.configure(bg=theme['bg'])
        self.main_container.configure(bg=theme['bg'])
        self.scrollable_frame.configure(bg=theme['bg'])
        self.main_canvas.configure(bg=theme['bg'])
        
        self._apply_theme_recursive(self.root, theme)
        
        for card in [self.exchange_card, self.capital_card, self.trade_card, self.results_card]:
            card.configure(bg=theme['card_bg'], highlightbackground=theme['border'], 
                         highlightthickness=2, relief=tk.RAISED)
            self._apply_theme_recursive(card, theme)
        
        self.results_text.configure(bg=theme['text_bg'], fg=theme['text_fg'], 
                                   insertbackground=theme['accent'])
    
    def _apply_theme_recursive(self, widget, theme):
        try:
            widget_type = widget.winfo_class()
            
            if widget_type == 'Frame':
                widget.configure(bg=theme['card_bg'])
            elif widget_type == 'Label':
                widget.configure(bg=theme['card_bg'], fg=theme['fg'])
            elif widget_type == 'Entry':
                widget.configure(bg=theme['input_bg'], fg=theme['input_fg'], 
                               insertbackground=theme['accent'], relief=tk.FLAT, bd=2,
                               highlightthickness=1, highlightbackground=theme['border'])
            elif widget_type == 'Button':
                if isinstance(widget, ModernButton):
                    widget.default_bg = theme['button_bg']
                    widget.hover_bg = theme['button_hover']
                    widget.configure(bg=theme['button_bg'], fg=theme['button_fg'],
                                   activebackground=theme['button_hover'])
            elif widget_type == 'Canvas':
                widget.configure(bg=theme['bg'], highlightthickness=0)
            
            for child in widget.winfo_children():
                self._apply_theme_recursive(child, theme)
        except:
            pass
    
    def on_exchange_change(self, event=None):
        exchange = self.exchange_combo.get()
        if exchange in self.exchanges:
            order_type = self.order_type_combo.get()
            fee = self.exchanges[exchange]['maker' if order_type == 'Maker' else 'taker']
            
            self.fee_entry.config(state='normal')
            self.fee_entry.delete(0, tk.END)
            self.fee_entry.insert(0, str(fee))
            
            if exchange != "Custom":
                self.fee_entry.config(state='readonly')
    
    def on_order_type_change(self, event=None):
        self.on_exchange_change()
    
    def get_live_price(self):
        exchange = self.exchange_combo.get()
        symbol = self.symbol_combo.get()
        
        if exchange == "Custom":
            messagebox.showinfo(self.language.get('info'), self.language.get('no_api_price'))
            return
        
        self.live_price_label.config(text=self.language.get('fetching_price'))
        self.root.update()
        
        def fetch_price():
            price = self.api_manager.get_price(exchange, symbol)
            if price:
                self.live_price_label.config(text=f"{price:,.2f} USDT")
                self.entry_price.delete(0, tk.END)
                self.entry_price.insert(0, str(price))
            else:
                self.live_price_label.config(text=self.language.get('price_error'))
                messagebox.showerror(self.language.get('error'), self.language.get('api_error'))
        
        thread = threading.Thread(target=fetch_price)
        thread.daemon = True
        thread.start()
    
    def save_settings_clicked(self, show_message=True):
        try:
            capital = float(self.capital_entry.get())
            risk_percent = float(self.risk_entry.get())
            fee_percent = float(self.fee_entry.get())
            exchange = self.exchange_combo.get()
            order_type = 'maker' if self.order_type_combo.get() == 'Maker' else 'taker'
            
            self.config.save_config(capital, risk_percent, fee_percent, exchange, order_type, self.current_theme)
            
            if show_message:
                messagebox.showinfo(self.language.get('success'), self.language.get('save_success'))
        except ValueError:
            if show_message:
                messagebox.showerror(self.language.get('error'), self.language.get('enter_valid'))
    
    def calculate(self):
        try:
            entry_price = float(self.entry_price.get())
            stop_loss = float(self.stop_loss.get())
            leverage = float(self.leverage.get())
            position = self.position_type.get()
            
            capital = float(self.capital_entry.get())
            risk_percent = float(self.risk_entry.get())
            fee_percent = float(self.fee_entry.get())
            
            tps = []
            for tp_entry in self.tp_entries:
                tp_val = tp_entry.get().strip()
                if tp_val:
                    tps.append(float(tp_val))
            
            if not tps:
                messagebox.showerror(self.language.get('error'), self.language.get('enter_tp'))
                return
            
            risk_amount = capital * (risk_percent / 100)
            
            if position == "LONG":
                sl_diff_percent = ((entry_price - stop_loss) / entry_price) * 100
            else:
                sl_diff_percent = ((stop_loss - entry_price) / entry_price) * 100
            
            position_size_usdt = risk_amount / (sl_diff_percent / 100)
            position_value = position_size_usdt * leverage
            quantity = position_value / entry_price
            
            entry_fee = position_value * (fee_percent / 100)
            exit_fee = position_value * (fee_percent / 100)
            total_fees = entry_fee + exit_fee
            
            if position == "LONG":
                loss_at_sl = (quantity * stop_loss) - position_value - total_fees
            else:
                loss_at_sl = position_value - (quantity * stop_loss) - total_fees
            
            if position == "LONG":
                liquidation_price = entry_price * (1 - (1 / leverage) + (fee_percent / 100))
            else:
                liquidation_price = entry_price * (1 + (1 / leverage) + (fee_percent / 100))
            
            results = f"""
{'='*90}
                     📊 CALCULATION RESULTS
{'='*90}

⏰ Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📊 Position: {position} | ⚡ Leverage: {leverage}x | 💰 Fee: {fee_percent}%
📈 Entry: {entry_price:,.4f} | 🛑 SL: {stop_loss:,.4f}

💼 CAPITAL MANAGEMENT:
{'-'*90}
💵 Capital: {capital:,.2f} USDT | 🎯 Risk: {risk_percent}% ({risk_amount:,.2f} USDT)

📊 POSITION CALCULATION:
{'-'*90}
💎 Margin Size: {position_size_usdt:,.2f} USDT
💰 Leveraged Value: {position_value:,.2f} USDT
🪙 Quantity: {quantity:,.6f}

💸 FEES:
{'-'*90}
↗️ Entry: {entry_fee:,.2f} | ↙️ Exit: {exit_fee:,.2f} | 💵 Total: {total_fees:,.2f} USDT

🛑 LOSS AT SL:
{'-'*90}
❌ {loss_at_sl:,.2f} USDT ({(loss_at_sl/capital)*100:+.2f}%)

🎯 TAKE PROFITS:
{'-'*90}
"""
            
            tp_results = []
            for i, tp in enumerate(tps, 1):
                if position == "LONG":
                    profit_at_tp = (quantity * tp) - position_value - total_fees
                else:
                    profit_at_tp = position_value - (quantity * tp) - total_fees
                
                rr_ratio = abs(profit_at_tp / loss_at_sl) if loss_at_sl != 0 else 0
                tp_percent = ((tp - entry_price) / entry_price * 100) if position == "LONG" else ((entry_price - tp) / entry_price * 100)
                
                status = "✅" if rr_ratio >= 2 else "⚠️" if rr_ratio >= 1.5 else "❌"
                results += f"{status} TP{i}: {tp:,.4f} ({tp_percent:+.2f}%) → 💰 {profit_at_tp:,.2f} USDT ({(profit_at_tp/capital)*100:+.2f}%) | R/R: {rr_ratio:.2f}:1\n"
                tp_results.append({'tp': tp, 'profit': profit_at_tp, 'rr': rr_ratio})
            
            results += f"\n⚠️ LIQUIDATION PRICE:\n{'-'*90}\n🔴 {liquidation_price:,.4f} USDT\n"
            
            results += f"\n💡 RECOMMENDATIONS:\n{'-'*90}\n"
            best_rr = max(tp_results, key=lambda x: x['rr'])
            if best_rr['rr'] >= 2:
                results += f"✅ Excellent! Best R/R: {best_rr['rr']:.2f}:1 at {best_rr['tp']:,.4f}\n"
            elif best_rr['rr'] >= 1.5:
                results += f"⚠️ Acceptable. Best R/R: {best_rr['rr']:.2f}:1\n"
            else:
                results += "❌ Low R/R ratio. Trade not recommended.\n"
            
            results += f"\n{'='*90}\n"
            
            self.results_text.delete('1.0', tk.END)
            self.results_text.insert('1.0', results)
            
            trade_data = {
                'exchange': self.exchange_combo.get(),
                'symbol': self.symbol_combo.get(),
                'position': position,
                'entry_price': entry_price,
                'stop_loss': stop_loss,
                'tps': tps,
                'leverage': leverage,
                'capital': capital,
                'risk_percent': risk_percent,
                'position_size': position_size_usdt,
                'quantity': quantity,
                'loss_at_sl': loss_at_sl,
                'tp_results': tp_results
            }
            self.history.add_trade(trade_data)
            
            messagebox.showinfo(self.language.get('success'), self.language.get('calc_success'))
            
        except ValueError:
            messagebox.showerror(self.language.get('error'), self.language.get('enter_valid'))
        except Exception as e:
            messagebox.showerror(self.language.get('error'), str(e))
    
    def show_settings(self):
        messagebox.showinfo(self.language.get('info'), "Coming soon!")
    
    def show_history(self):
        messagebox.showinfo(self.language.get('info'), "Coming soon!")
    
    def show_charts(self):
        messagebox.showinfo(self.language.get('info'), "Coming soon!")
    
    def export_csv(self):
        if not self.history.trades:
            messagebox.showinfo(self.language.get('info'), self.language.get('no_export_data'))
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=f"trades_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        
        if filename:
            if self.history.export_to_csv(filename):
                messagebox.showinfo(self.language.get('success'), 
                                  f"{self.language.get('file_saved')}:\n{filename}")
            else:
                messagebox.showerror(self.language.get('error'), self.language.get('save_error'))
    
    def clear_results(self):
        self.results_text.delete('1.0', tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = CryptoTradingCalculator(root)
    root.mainloop()
