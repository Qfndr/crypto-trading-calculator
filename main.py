import tkinter as tk
from tkinter import ttk, messagebox, filedialog, font as tkfont
import json
import os
from datetime import datetime
from config import Config
from trade_history import TradeHistory
from api_manager import APIManager
from chart_generator import ChartGenerator
from language import Language
from updater import Updater
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading

VERSION = "1.4.0"

class ModernButton(tk.Button):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.config(
            relief=tk.FLAT,
            bd=0,
            padx=15,
            pady=8,
            cursor='hand2'
        )

class CryptoTradingCalculator:
    def __init__(self, root):
        self.root = root
        
        # Initialize language system
        self.language = Language()
        self.updater = Updater()
        
        # Load saved language
        saved_lang = self.load_language_preference()
        if saved_lang:
            self.language.set_language(saved_lang)
        
        self.root.title(f"{self.language.get('app_title')} v{VERSION}")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # Load IranSans font
        self.setup_fonts()
        
        # Load configuration
        self.config = Config()
        self.history = TradeHistory()
        self.api_manager = APIManager()
        self.chart_generator = ChartGenerator()
        
        # Exchange presets
        self.exchanges = {
            "Binance": {"maker": 0.02, "taker": 0.04, "default": 0.04},
            "CoinEx": {"maker": 0.16, "taker": 0.26, "default": 0.26},
            "Bybit": {"maker": 0.02, "taker": 0.055, "default": 0.055},
            "OKX": {"maker": 0.02, "taker": 0.05, "default": 0.05},
            "KuCoin": {"maker": 0.02, "taker": 0.06, "default": 0.06},
            "Gate.io": {"maker": 0.015, "taker": 0.05, "default": 0.05},
            "Bitget": {"maker": 0.02, "taker": 0.06, "default": 0.06},
            "MEXC": {"maker": 0.0, "taker": 0.02, "default": 0.02},
            "Nobitex": {"maker": 0.35, "taker": 0.35, "default": 0.35},
            "Wallex": {"maker": 0.2, "taker": 0.2, "default": 0.2},
            "Exir": {"maker": 0.35, "taker": 0.35, "default": 0.35},
            "دستی (Custom)": {"maker": 0.15, "taker": 0.15, "default": 0.15}
        }
        
        # Theme configuration
        self.themes = {
            'light': {
                'bg': '#f5f5f5',
                'fg': '#1a1a1a',
                'card_bg': '#ffffff',
                'input_bg': '#ffffff',
                'input_fg': '#1a1a1a',
                'button_bg': '#4a90e2',
                'button_fg': '#ffffff',
                'button_hover': '#357abd',
                'accent': '#4a90e2',
                'border': '#e0e0e0',
                'success': '#4caf50',
                'error': '#f44336',
                'text_bg': '#ffffff',
                'text_fg': '#1a1a1a',
                'label_bg': '#ffffff'
            },
            'dark': {
                'bg': '#1a1a1a',
                'fg': '#e0e0e0',
                'card_bg': '#2d2d2d',
                'input_bg': '#3a3a3a',
                'input_fg': '#e0e0e0',
                'button_bg': '#4a90e2',
                'button_fg': '#ffffff',
                'button_hover': '#357abd',
                'accent': '#64b5f6',
                'border': '#404040',
                'success': '#66bb6a',
                'error': '#ef5350',
                'text_bg': '#2d2d2d',
                'text_fg': '#e0e0e0',
                'label_bg': '#2d2d2d'
            }
        }
        
        self.current_theme = self.config.theme
        self.tp_entries = []
        self.chart_window = None
        
        self.create_widgets()
        self.apply_theme()
        self.update_ui_language()
        
    def load_language_preference(self):
        """Load saved language preference"""
        try:
            if os.path.exists('config.json'):
                with open('config.json', 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    return config.get('language', 'fa')
        except:
            pass
        return 'fa'
    
    def save_language_preference(self):
        """Save language preference"""
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
        """Switch between Persian and English"""
        new_lang = 'en' if self.language.current == 'fa' else 'fa'
        self.language.set_language(new_lang)
        self.save_language_preference()
        self.update_ui_language()
        self.root.title(f"{self.language.get('app_title')} v{VERSION}")
    
    def update_ui_language(self):
        """Update all UI text with current language"""
        try:
            # Update theme button
            if self.current_theme == 'dark':
                self.theme_btn.configure(text=f"☀️ {self.language.get('light_mode')}")
            else:
                self.theme_btn.configure(text=f"🌙 {self.language.get('dark_mode')}")
            
            # Update language button
            if self.language.current == 'fa':
                self.lang_btn.configure(text="🌍 English")
            else:
                self.lang_btn.configure(text="🌍 فارسی")
            
            # Update other buttons
            self.settings_btn.configure(text=f"⚙️ {self.language.get('settings')}")
            self.history_btn.configure(text=f"📊 {self.language.get('history')}")
            self.charts_btn.configure(text=f"📈 {self.language.get('charts')}")
            self.update_btn.configure(text=f"🔄 {self.language.get('update')}")
            
            # Update live price button
            self.live_price_btn.configure(text=f"💹 {self.language.get('live_price')}")
            
            # Update calculate button
            self.calc_btn.configure(text=f"🔢 {self.language.get('calculate')}")
            
            # Update result buttons
            self.export_btn.configure(text=f"💾 {self.language.get('export_csv')}")
            self.clear_btn.configure(text=f"🗑️ {self.language.get('clear_results')}")
            
        except:
            pass
        
    def setup_fonts(self):
        """Setup IranSans font"""
        try:
            font_path = os.path.join(os.path.dirname(__file__), 'IRANSans.ttf')
            if os.path.exists(font_path):
                self.persian_font = ('IRANSans', 10)
                self.persian_font_bold = ('IRANSans', 10, 'bold')
                self.persian_font_title = ('IRANSans', 18, 'bold')
                self.persian_font_header = ('IRANSans', 13, 'bold')
            else:
                self.persian_font = ('Tahoma', 10)
                self.persian_font_bold = ('Tahoma', 10, 'bold')
                self.persian_font_title = ('Tahoma', 18, 'bold')
                self.persian_font_header = ('Tahoma', 13, 'bold')
        except:
            self.persian_font = ('Tahoma', 10)
            self.persian_font_bold = ('Tahoma', 10, 'bold')
            self.persian_font_title = ('Tahoma', 18, 'bold')
            self.persian_font_header = ('Tahoma', 13, 'bold')
    
    def create_widgets(self):
        # Main container
        self.main_container = tk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Top bar
        self.top_bar = tk.Frame(self.main_container, height=60)
        self.top_bar.pack(fill=tk.X, side=tk.TOP)
        self.top_bar.pack_propagate(False)
        
        # Title
        title_label = tk.Label(self.top_bar, text=f"💰 {self.language.get('app_title')}", 
                              font=self.persian_font_title)
        title_label.pack(side=tk.LEFT, padx=20, pady=10)
        
        version_label = tk.Label(self.top_bar, text=f"v{VERSION}", 
                                font=self.persian_font, fg='gray')
        version_label.pack(side=tk.LEFT, pady=10)
        
        # Top buttons
        btn_frame = tk.Frame(self.top_bar)
        btn_frame.pack(side=tk.RIGHT, padx=20, pady=10)
        
        self.theme_btn = ModernButton(btn_frame, text="🌙 دارک مود", 
                                      command=self.toggle_theme, width=12, font=self.persian_font)
        self.theme_btn.pack(side=tk.LEFT, padx=5)
        
        self.settings_btn = ModernButton(btn_frame, text="⚙️ تنظیمات", 
                                   command=self.show_settings, width=12, font=self.persian_font)
        self.settings_btn.pack(side=tk.LEFT, padx=5)
        
        self.history_btn = ModernButton(btn_frame, text="📊 تاریخچه", 
                                  command=self.show_history, width=12, font=self.persian_font)
        self.history_btn.pack(side=tk.LEFT, padx=5)
        
        self.charts_btn = ModernButton(btn_frame, text="📈 نمودارها", 
                                 command=self.show_charts, width=12, font=self.persian_font)
        self.charts_btn.pack(side=tk.LEFT, padx=5)
        
        self.lang_btn = ModernButton(btn_frame, text="🌍 English", 
                                     command=self.toggle_language, width=12, font=self.persian_font)
        self.lang_btn.pack(side=tk.LEFT, padx=5)
        
        self.update_btn = ModernButton(btn_frame, text="🔄 آپدیت", 
                                      command=self.show_update_manager, width=12, font=self.persian_font)
        self.update_btn.pack(side=tk.LEFT, padx=5)
        
        # Content area with scrollbar
        content_frame = tk.Frame(self.main_container)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        canvas = tk.Canvas(content_frame, highlightthickness=0)
        scrollbar = tk.Scrollbar(content_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.main_canvas = canvas
        
        # Create cards
        self.create_exchange_card()
        self.create_capital_card()
        self.create_trade_card()
        self.create_results_card()
        
    def create_card(self, title, icon=""):
        """Create a styled card container"""
        card = tk.Frame(self.scrollable_frame, relief=tk.FLAT, bd=1)
        card.pack(fill=tk.X, padx=10, pady=8)
        
        # Card header
        header = tk.Frame(card, height=40)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        header_label = tk.Label(header, text=f"{icon} {title}", 
                               font=self.persian_font_header)
        header_label.pack(side=tk.LEFT, padx=15, pady=10)
        
        # Card body
        body = tk.Frame(card)
        body.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        return card, body
    
    def create_exchange_card(self):
        card, body = self.create_card(self.language.get('exchange_symbol'), "🏦")
        self.exchange_card = card
        
        # Row 1: Exchange and Order Type
        row1 = tk.Frame(body)
        row1.pack(fill=tk.X, pady=5)
        
        tk.Label(row1, text=f"{self.language.get('exchange')}:", font=self.persian_font).pack(side=tk.LEFT, padx=(0, 10))
        self.exchange_combo = ttk.Combobox(row1, values=list(self.exchanges.keys()), 
                                          width=20, state="readonly", font=self.persian_font)
        self.exchange_combo.set(self.config.selected_exchange)
        self.exchange_combo.pack(side=tk.LEFT, padx=5)
        self.exchange_combo.bind('<<ComboboxSelected>>', self.on_exchange_change)
        
        tk.Label(row1, text=f"{self.language.get('order_type')}:", font=self.persian_font).pack(side=tk.LEFT, padx=(20, 10))
        self.order_type_combo = ttk.Combobox(row1, values=["Maker", "Taker"], 
                                             width=15, state="readonly", font=self.persian_font)
        self.order_type_combo.set("Taker" if self.config.order_type == "taker" else "Maker")
        self.order_type_combo.pack(side=tk.LEFT, padx=5)
        self.order_type_combo.bind('<<ComboboxSelected>>', self.on_order_type_change)
        
        # Row 2: Symbol and Live Price
        row2 = tk.Frame(body)
        row2.pack(fill=tk.X, pady=5)
        
        tk.Label(row2, text=f"{self.language.get('symbol')}:", font=self.persian_font).pack(side=tk.LEFT, padx=(0, 10))
        self.symbol_combo = ttk.Combobox(row2, values=self.api_manager.get_available_symbols(), 
                                        width=20, state="readonly", font=self.persian_font)
        self.symbol_combo.set('BTCUSDT')
        self.symbol_combo.pack(side=tk.LEFT, padx=5)
        
        self.live_price_btn = ModernButton(row2, text=f"💹 {self.language.get('live_price')}", 
                                          command=self.get_live_price, width=15, font=self.persian_font)
        self.live_price_btn.pack(side=tk.LEFT, padx=20)
        
        self.live_price_label = tk.Label(row2, text="-", font=self.persian_font_bold)
        self.live_price_label.pack(side=tk.LEFT, padx=10)
        
    def create_capital_card(self):
        card, body = self.create_card(self.language.get('capital_risk'), "💰")
        self.capital_card = card
        
        # Grid layout
        for i in range(3):
            body.columnconfigure(i, weight=1)
        
        # Row 1
        tk.Label(body, text=f"{self.language.get('total_capital')}:", font=self.persian_font).grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.capital_entry = tk.Entry(body, font=self.persian_font, width=20)
        self.capital_entry.insert(0, str(self.config.capital))
        self.capital_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        tk.Label(body, text=f"{self.language.get('risk_percent')}:", font=self.persian_font).grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.risk_entry = tk.Entry(body, font=self.persian_font, width=20)
        self.risk_entry.insert(0, str(self.config.risk_percent))
        self.risk_entry.grid(row=0, column=3, sticky=tk.W, padx=5, pady=5)
        
        # Row 2
        tk.Label(body, text=f"{self.language.get('fee_percent')}:", font=self.persian_font).grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.fee_entry = tk.Entry(body, font=self.persian_font, width=20)
        self.fee_entry.insert(0, str(self.config.fee_percent))
        self.fee_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        save_btn = ModernButton(body, text=f"💾 {self.language.get('save_settings')}", command=self.save_settings_clicked, font=self.persian_font)
        save_btn.grid(row=1, column=2, columnspan=2, padx=5, pady=5, sticky=tk.W)
        
    def create_trade_card(self):
        card, body = self.create_card(self.language.get('trade_info'), "📊")
        self.trade_card = card
        
        # Grid layout
        for i in range(4):
            body.columnconfigure(i, weight=1)
        
        # Row 1
        tk.Label(body, text=f"{self.language.get('entry_price')}:", font=self.persian_font).grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.entry_price = tk.Entry(body, font=self.persian_font, width=18)
        self.entry_price.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        tk.Label(body, text=f"{self.language.get('stop_loss')}:", font=self.persian_font).grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.stop_loss = tk.Entry(body, font=self.persian_font, width=18)
        self.stop_loss.grid(row=0, column=3, sticky=tk.W, padx=5, pady=5)
        
        # Row 2
        tk.Label(body, text=f"{self.language.get('take_profit')} 1:", font=self.persian_font).grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.tp1_entry = tk.Entry(body, font=self.persian_font, width=18)
        self.tp1_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        self.tp_entries.append(self.tp1_entry)
        
        tk.Label(body, text=f"{self.language.get('take_profit')} 2:", font=self.persian_font).grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        self.tp2_entry = tk.Entry(body, font=self.persian_font, width=18)
        self.tp2_entry.grid(row=1, column=3, sticky=tk.W, padx=5, pady=5)
        self.tp_entries.append(self.tp2_entry)
        
        # Row 3
        tk.Label(body, text=f"{self.language.get('take_profit')} 3:", font=self.persian_font).grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.tp3_entry = tk.Entry(body, font=self.persian_font, width=18)
        self.tp3_entry.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        self.tp_entries.append(self.tp3_entry)
        
        tk.Label(body, text=f"{self.language.get('position_type')}:", font=self.persian_font).grid(row=2, column=2, sticky=tk.W, padx=5, pady=5)
        self.position_type = ttk.Combobox(body, values=["LONG", "SHORT"], width=16, state="readonly", font=self.persian_font)
        self.position_type.set("LONG")
        self.position_type.grid(row=2, column=3, sticky=tk.W, padx=5, pady=5)
        
        # Row 4
        tk.Label(body, text=f"{self.language.get('leverage')}:", font=self.persian_font).grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.leverage = tk.Entry(body, font=self.persian_font, width=18)
        self.leverage.insert(0, "10")
        self.leverage.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        
        tk.Label(body, text=f"{self.language.get('notes')}:", font=self.persian_font).grid(row=3, column=2, sticky=tk.W, padx=5, pady=5)
        self.notes_entry = tk.Entry(body, font=self.persian_font, width=18)
        self.notes_entry.grid(row=3, column=3, sticky=tk.W, padx=5, pady=5)
        
        # Calculate button
        calc_frame = tk.Frame(body)
        calc_frame.grid(row=4, column=0, columnspan=4, pady=20)
        
        self.calc_btn = ModernButton(calc_frame, text=f"🔢 {self.language.get('calculate')}", 
                                     command=self.calculate, width=20, 
                                     font=self.persian_font_bold)
        self.calc_btn.pack()
        
    def create_results_card(self):
        card, body = self.create_card(self.language.get('results'), "📋")
        self.results_card = card
        
        # Results text widget
        text_frame = tk.Frame(body)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.results_text = tk.Text(text_frame, height=15, font=('Consolas', 10), 
                                    wrap=tk.WORD, relief=tk.FLAT, padx=10, pady=10)
        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(text_frame, orient="vertical", command=self.results_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.results_text.config(yscrollcommand=scrollbar.set)
        
        # Export buttons
        btn_frame = tk.Frame(body)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.export_btn = ModernButton(btn_frame, text=f"💾 {self.language.get('export_csv')}", 
                                 command=self.export_csv, width=15, font=self.persian_font)
        self.export_btn.pack(side=tk.LEFT, padx=5)
        
        self.clear_btn = ModernButton(btn_frame, text=f"🗑️ {self.language.get('clear_results')}", 
                                command=self.clear_results, width=18, font=self.persian_font)
        self.clear_btn.pack(side=tk.LEFT, padx=5)
        
    def show_update_manager(self):
        """Show update manager window"""
        update_window = tk.Toplevel(self.root)
        update_window.title(self.language.get('update_manager'))
        update_window.geometry("600x700")
        update_window.resizable(False, False)
        
        theme = self.themes[self.current_theme]
        update_window.configure(bg=theme['card_bg'])
        
        # Main frame
        main_frame = tk.Frame(update_window, bg=theme['card_bg'], padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title = tk.Label(main_frame, text=f"🔄 {self.language.get('update_manager')}", 
                        font=self.persian_font_title, bg=theme['card_bg'], fg=theme['fg'])
        title.pack(pady=(0, 20))
        
        # Current version
        current_frame = tk.Frame(main_frame, bg=theme['card_bg'])
        current_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(current_frame, text=f"{self.language.get('current_version')}: v{VERSION}", 
                font=self.persian_font_bold, bg=theme['card_bg'], fg=theme['accent']).pack(anchor=tk.W)
        
        # Check update button and status
        check_frame = tk.Frame(main_frame, bg=theme['card_bg'])
        check_frame.pack(fill=tk.X, pady=10)
        
        status_label = tk.Label(check_frame, text=self.language.get('checking_update'), 
                               font=self.persian_font, bg=theme['card_bg'], fg=theme['fg'])
        status_label.pack(anchor=tk.W, pady=5)
        
        # Check for update
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
        
        # Update button
        update_btn = ModernButton(check_frame, text=f"⬆️ {self.language.get('update_now')}", 
                                 command=lambda: self.perform_update(status_label), 
                                 width=20, font=self.persian_font_bold, state=tk.DISABLED)
        update_btn.pack(pady=10)
        
        # Separator
        ttk.Separator(main_frame, orient='horizontal').pack(fill=tk.X, pady=20)
        
        # Version selector
        selector_label = tk.Label(main_frame, text=self.language.get('select_version'), 
                                 font=self.persian_font_header, bg=theme['card_bg'], fg=theme['fg'])
        selector_label.pack(anchor=tk.W, pady=(0, 10))
        
        # List of versions
        list_frame = tk.Frame(main_frame, bg=theme['card_bg'])
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        versions_list = tk.Listbox(list_frame, height=10, font=self.persian_font,
                                   bg=theme['input_bg'], fg=theme['input_fg'])
        versions_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        versions_scroll = tk.Scrollbar(list_frame, orient="vertical", command=versions_list.yview)
        versions_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        versions_list.config(yscrollcommand=versions_scroll.set)
        
        # Load versions
        def load_versions():
            versions = self.updater.get_all_versions()
            for v in versions:
                versions_list.insert(tk.END, f"v{v['version']} - {v['name']}")
        
        # Install selected version
        def install_selected():
            selection = versions_list.curselection()
            if not selection:
                messagebox.showwarning(self.language.get('info'), "Please select a version")
                return
            
            selected_text = versions_list.get(selection[0])
            version = selected_text.split(' ')[0].replace('v', '')
            
            if messagebox.askyesno(self.language.get('confirm'), 
                                  f"Install version {version}?"):
                self.perform_update(status_label, version)
        
        install_btn = ModernButton(main_frame, text=f"📥 {self.language.get('install_version')}", 
                                  command=install_selected, width=20, font=self.persian_font_bold)
        install_btn.pack(pady=10)
        
        # Start checking for update
        update_window.after(500, check_update)
        update_window.after(1000, load_versions)
    
    def perform_update(self, status_label, version=None):
        """Perform update"""
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
                status_label.config(text=f"❌ {self.language.get('update_error')}: {', '.join(result['failed'])}")
                messagebox.showerror(self.language.get('error'), 
                                    f"{self.language.get('update_error')}\n\nFailed files: {', '.join(result['failed'])}")
        except Exception as e:
            status_label.config(text=f"❌ {self.language.get('update_error')}: {str(e)}")
            messagebox.showerror(self.language.get('error'), str(e))
        
    def toggle_theme(self):
        self.current_theme = 'dark' if self.current_theme == 'light' else 'light'
        self.apply_theme()
        self.update_ui_language()
        self.save_settings_clicked(show_message=False)
        
    def apply_theme(self):
        theme = self.themes[self.current_theme]
        
        # Apply to root
        self.root.configure(bg=theme['bg'])
        
        # Apply to main containers
        self.main_container.configure(bg=theme['bg'])
        self.top_bar.configure(bg=theme['card_bg'])
        self.scrollable_frame.configure(bg=theme['bg'])
        self.main_canvas.configure(bg=theme['bg'])
        
        # Apply to all widgets recursively
        self._apply_theme_recursive(self.root, theme)
        
        # Specifically update cards
        for card in [self.exchange_card, self.capital_card, self.trade_card, self.results_card]:
            card.configure(bg=theme['card_bg'], highlightbackground=theme['border'], highlightthickness=1)
            self._apply_theme_recursive(card, theme)
        
        # Apply to results text
        self.results_text.configure(bg=theme['text_bg'], fg=theme['text_fg'], 
                                   insertbackground=theme['text_fg'])
        
    def _apply_theme_recursive(self, widget, theme):
        """Recursively apply theme to all widgets"""
        try:
            widget_type = widget.winfo_class()
            
            if widget_type == 'Frame':
                widget.configure(bg=theme['card_bg'])
            elif widget_type == 'Label':
                widget.configure(bg=theme['label_bg'], fg=theme['fg'])
            elif widget_type == 'Entry':
                widget.configure(bg=theme['input_bg'], fg=theme['input_fg'], 
                               insertbackground=theme['input_fg'], 
                               disabledbackground=theme['input_bg'],
                               disabledforeground=theme['input_fg'],
                               relief=tk.FLAT, bd=2, highlightthickness=1,
                               highlightbackground=theme['border'],
                               highlightcolor=theme['accent'])
            elif widget_type == 'Text':
                widget.configure(bg=theme['text_bg'], fg=theme['text_fg'], 
                               insertbackground=theme['text_fg'],
                               selectbackground=theme['accent'],
                               selectforeground=theme['button_fg'])
            elif widget_type == 'Button':
                if isinstance(widget, ModernButton):
                    widget.configure(bg=theme['button_bg'], fg=theme['button_fg'],
                                   activebackground=theme['button_hover'], 
                                   activeforeground=theme['button_fg'])
            elif widget_type == 'Canvas':
                widget.configure(bg=theme['bg'], highlightthickness=0)
            elif widget_type == 'Scrollbar':
                widget.configure(bg=theme['card_bg'], troughcolor=theme['bg'])
            
            # Recursively apply to children
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
            
            if exchange != "دستی (Custom)":
                self.fee_entry.config(state='readonly')
    
    def on_order_type_change(self, event=None):
        self.on_exchange_change()
    
    def get_live_price(self):
        """Get live price from API"""
        exchange = self.exchange_combo.get()
        symbol = self.symbol_combo.get()
        
        if exchange == "دستی (Custom)":
            messagebox.showinfo(self.language.get('info'), self.language.get('no_api_price'))
            return
        
        self.live_price_label.config(text=self.language.get('fetching_price'))
        self.root.update()
        
        def fetch_price():
            price = self.api_manager.get_price(exchange, symbol)
            if price:
                self.live_price_label.config(text=f"{price:,.2f} USDT")
                # Auto-fill entry price
                self.entry_price.delete(0, tk.END)
                self.entry_price.insert(0, str(price))
            else:
                self.live_price_label.config(text=self.language.get('price_error'))
                messagebox.showerror(self.language.get('error'), self.language.get('api_error'))
        
        # Run in thread to prevent UI freeze
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
            exchange = self.exchange_combo.get()
            order_type = self.order_type_combo.get()
            notes = self.notes_entry.get()
            
            # Get TPs
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
            
            # Calculate for SL
            if position == "LONG":
                loss_at_sl = (quantity * stop_loss) - position_value - total_fees
            else:
                loss_at_sl = position_value - (quantity * stop_loss) - total_fees
            
            # Calculate liquidation
            if position == "LONG":
                liquidation_price = entry_price * (1 - (1 / leverage) + (fee_percent / 100))
            else:
                liquidation_price = entry_price * (1 + (1 / leverage) + (fee_percent / 100))
            
            results = f"""
{'='*90}
                             نتایج محاسبات
{'='*90}

⏰ تاریخ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🏦 صرافی: {exchange} | 📊 نوع: {position} | 💱 سفارش: {order_type} | 💰 کارمزد: {fee_percent}%
📈 ورود: {entry_price:,.4f} | 🛑 SL: {stop_loss:,.4f} | ⚡ لوریج: {leverage}x

💼 مدیریت سرمایه:
{'─'*90}
💵 سرمایه: {capital:,.2f} USDT | 🎯 ریسک: {risk_percent}% ({risk_amount:,.2f} USDT)

📊 محاسبات پوزیشن:
{'─'*90}
💎 حجم مارجین: {position_size_usdt:,.2f} USDT
💰 ارزش با لوریج: {position_value:,.2f} USDT
🪙 تعداد کوین: {quantity:,.6f}

💸 کارمزدها:
{'─'*90}
↗️ ورود: {entry_fee:,.2f} | ↙️ خروج: {exit_fee:,.2f} | 💵 جمع: {total_fees:,.2f} USDT

🛑 زیان در SL:
{'─'*90}
❌ {loss_at_sl:,.2f} USDT ({(loss_at_sl/capital)*100:+.2f}%)

🎯 تیک پرافیت‌ها:
{'─'*90}
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
            
            results += f"\n⚠️ قیمت لیکوییدیشن:\n{'─'*90}\n🔴 {liquidation_price:,.4f} USDT\n"
            
            # Recommendations
            results += f"\n💡 توصیه‌ها:\n{'─'*90}\n"
            best_rr = max(tp_results, key=lambda x: x['rr'])
            if best_rr['rr'] >= 2:
                results += f"✅ عالی! بهترین R/R: {best_rr['rr']:.2f}:1 در قیمت {best_rr['tp']:,.4f}\n"
            elif best_rr['rr'] >= 1.5:
                results += f"⚠️ قابل قبول. بهترین R/R: {best_rr['rr']:.2f}:1\n"
            else:
                results += "❌ نسبت R/R پایین است! معامله توصیه نمی‌شود.\n"
            
            if notes:
                results += f"\n📝 یادداشت: {notes}\n"
            
            results += f"\n{'='*90}\n"
            
            self.results_text.delete('1.0', tk.END)
            self.results_text.insert('1.0', results)
            
            # Save to history
            trade_data = {
                'exchange': exchange,
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
                'tp_results': tp_results,
                'notes': notes
            }
            self.history.add_trade(trade_data)
            
            messagebox.showinfo(self.language.get('success'), self.language.get('calc_success'))
            
        except ValueError:
            messagebox.showerror(self.language.get('error'), self.language.get('enter_valid'))
        except Exception as e:
            messagebox.showerror(self.language.get('error'), f"{self.language.get('error')}: {str(e)}")
    
    def show_settings(self):
        """Show comprehensive settings window"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title(f"⚙️ {self.language.get('advanced_settings')}")
        settings_window.geometry("700x600")
        settings_window.resizable(False, False)
        
        theme = self.themes[self.current_theme]
        settings_window.configure(bg=theme['bg'])
        
        # Main frame with scrollbar
        main_frame = tk.Frame(settings_window, bg=theme['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        canvas = tk.Canvas(main_frame, bg=theme['bg'], highlightthickness=0)
        scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=theme['card_bg'], padx=20, pady=20)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y")
        
        # Title
        title = tk.Label(scrollable_frame, text=f"⚙️ {self.language.get('advanced_settings')}", 
                        font=self.persian_font_title, bg=theme['card_bg'], fg=theme['fg'])
        title.pack(pady=(0, 20))
        
        # API Keys section for all exchanges
        api_keys = {}
        
        exchanges_with_api = [
            ("Binance", "binance"),
            ("CoinEx", "coinex"),
            ("Bybit", "bybit"),
            ("OKX", "okx"),
            ("KuCoin", "kucoin"),
            ("Gate.io", "gateio"),
            ("Bitget", "bitget"),
            ("MEXC", "mexc")
        ]
        
        for exchange_name, exchange_key in exchanges_with_api:
            # Frame for each exchange
            exchange_frame = tk.LabelFrame(scrollable_frame, text=f"🔑 {exchange_name} API", 
                                          font=self.persian_font_bold, bg=theme['card_bg'], 
                                          fg=theme['fg'], padx=10, pady=10)
            exchange_frame.pack(fill=tk.X, pady=10)
            
            # API Key
            tk.Label(exchange_frame, text="API Key:", bg=theme['card_bg'], 
                    fg=theme['fg'], font=self.persian_font).pack(anchor=tk.W, pady=2)
            api_key_entry = tk.Entry(exchange_frame, width=60, bg=theme['input_bg'], 
                                    fg=theme['input_fg'], font=self.persian_font)
            api_key_entry.pack(pady=(0, 5), fill=tk.X)
            
            # Secret Key
            tk.Label(exchange_frame, text="Secret Key:", bg=theme['card_bg'], 
                    fg=theme['fg'], font=self.persian_font).pack(anchor=tk.W, pady=2)
            secret_key_entry = tk.Entry(exchange_frame, width=60, show='*', bg=theme['input_bg'], 
                                       fg=theme['input_fg'], font=self.persian_font)
            secret_key_entry.pack(pady=(0, 5), fill=tk.X)
            
            # Load from config if exists
            saved_api = self.config.data.get('api_keys', {}).get(exchange_key, {})
            if saved_api:
                api_key_entry.insert(0, saved_api.get('key', ''))
                secret_key_entry.insert(0, saved_api.get('secret', ''))
            
            api_keys[exchange_key] = {
                'key': api_key_entry,
                'secret': secret_key_entry
            }
        
        # Other settings
        other_frame = tk.LabelFrame(scrollable_frame, text=f"🔧 {self.language.get('other_settings')}", 
                                   font=self.persian_font_bold, bg=theme['card_bg'], 
                                   fg=theme['fg'], padx=10, pady=10)
        other_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(other_frame, text=f"{self.language.get('refresh_rate')}:", bg=theme['card_bg'], 
                fg=theme['fg'], font=self.persian_font).pack(anchor=tk.W, pady=5)
        refresh_rate = tk.Entry(other_frame, width=20, bg=theme['input_bg'], 
                               fg=theme['input_fg'], font=self.persian_font)
        refresh_rate.insert(0, str(self.config.data.get('refresh_rate', 10)))
        refresh_rate.pack(anchor=tk.W, pady=(0, 10))
        
        # Save button
        save_btn = ModernButton(scrollable_frame, text=f"💾 {self.language.get('save_all')}", 
                               command=lambda: self._save_advanced_settings(
                                   settings_window, api_keys, refresh_rate.get()), 
                               width=25, font=self.persian_font_bold)
        save_btn.pack(pady=20)
        
    def _save_advanced_settings(self, window, api_keys, refresh_rate):
        """Save all API keys and settings"""
        try:
            # Save API keys
            saved_keys = {}
            for exchange_key, entries in api_keys.items():
                api_key = entries['key'].get().strip()
                secret_key = entries['secret'].get().strip()
                if api_key or secret_key:
                    saved_keys[exchange_key] = {
                        'key': api_key,
                        'secret': secret_key
                    }
            
            # Update config
            self.config.data['api_keys'] = saved_keys
            self.config.data['refresh_rate'] = int(refresh_rate)
            
            # Save to file
            with open('config.json', 'w', encoding='utf-8') as f:
                json.dump(self.config.data, f, indent=4, ensure_ascii=False)
            
            messagebox.showinfo(self.language.get('success'), f"{len(saved_keys)} {self.language.get('keys_saved')}")
            window.destroy()
        except Exception as e:
            messagebox.showerror(self.language.get('error'), f"{self.language.get('error')}: {str(e)}")
    
    def show_history(self):
        """Show trade history"""
        history_window = tk.Toplevel(self.root)
        history_window.title(f"📊 {self.language.get('trade_history')}")
        history_window.geometry("900x600")
        
        theme = self.themes[self.current_theme]
        history_window.configure(bg=theme['bg'])
        
        # Main frame
        main_frame = tk.Frame(history_window, bg=theme['card_bg'], padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title and buttons
        header = tk.Frame(main_frame, bg=theme['card_bg'])
        header.pack(fill=tk.X, pady=(0, 10))
        
        title = tk.Label(header, text=f"📊 {self.language.get('trade_history')}", 
                        font=self.persian_font_header, bg=theme['card_bg'], fg=theme['fg'])
        title.pack(side=tk.LEFT)
        
        export_btn = ModernButton(header, text=f"💾 {self.language.get('export')}", command=self.export_csv, 
                                 width=12, font=self.persian_font)
        export_btn.pack(side=tk.RIGHT, padx=5)
        
        clear_btn = ModernButton(header, text=f"🗑️ {self.language.get('clear')}", command=self.clear_history, 
                                width=12, font=self.persian_font)
        clear_btn.pack(side=tk.RIGHT, padx=5)
        
        # Text widget
        text_frame = tk.Frame(main_frame, bg=theme['card_bg'])
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        text = tk.Text(text_frame, wrap=tk.WORD, font=('Consolas', 9), 
                      bg=theme['text_bg'], fg=theme['text_fg'])
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(text_frame, orient="vertical", command=text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text.config(yscrollcommand=scrollbar.set)
        
        trades = self.history.get_trades()
        if not trades:
            text.insert('1.0', self.language.get('no_trades'))
        else:
            for i, trade in enumerate(reversed(trades), 1):
                trade_text = f"""
{'='*80}
📊 {self.language.get('trade_num')} #{i} - {trade.get('timestamp', 'N/A')}
{'='*80}
🏦 {self.language.get('exchange')}: {trade.get('exchange', 'N/A')} | 📈 {self.language.get('position_type')}: {trade.get('position', 'N/A')}
💱 {self.language.get('symbol')}: {trade.get('symbol', 'N/A')}
💰 {self.language.get('entry_price')}: {trade.get('entry_price', 0):,.4f} | 🛑 {self.language.get('stop_loss')}: {trade.get('stop_loss', 0):,.4f}
⚡ {self.language.get('leverage')}: {trade.get('leverage', 0)}x | 📦 Size: {trade.get('position_size', 0):,.2f} USDT
❌ Loss SL: {trade.get('loss_at_sl', 0):,.2f} USDT
"""
                if 'notes' in trade and trade['notes']:
                    trade_text += f"📝 {self.language.get('notes')}: {trade['notes']}\n"
                trade_text += "\n"
                text.insert(tk.END, trade_text)
        
        text.config(state=tk.DISABLED)
    
    def show_charts(self):
        """Show charts window"""
        if self.chart_window and tk.Toplevel.winfo_exists(self.chart_window):
            self.chart_window.lift()
            return
        
        self.chart_window = tk.Toplevel(self.root)
        self.chart_window.title(f"📈 {self.language.get('charts_analysis')}")
        self.chart_window.geometry("1000x700")
        
        theme = self.themes[self.current_theme]
        self.chart_window.configure(bg=theme['bg'])
        
        # Notebook for tabs
        notebook = ttk.Notebook(self.chart_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab 1: P&L Chart
        pnl_frame = tk.Frame(notebook, bg=theme['card_bg'])
        notebook.add(pnl_frame, text=f"📊 {self.language.get('pnl_chart')}")
        
        # Get current trade data
        try:
            entry_price = float(self.entry_price.get()) if self.entry_price.get() else 50000
            stop_loss = float(self.stop_loss.get()) if self.stop_loss.get() else 48000
            tps = [float(e.get()) for e in self.tp_entries if e.get()]
            if not tps:
                tps = [52000, 54000, 56000]
            position = self.position_type.get()
            
            fig = self.chart_generator.create_pnl_chart(entry_price, stop_loss, tps, position, self.current_theme)
            canvas = FigureCanvasTkAgg(fig, master=pnl_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        except:
            tk.Label(pnl_frame, text=f"⚠️ {self.language.get('enter_trade_first')}", 
                    font=self.persian_font_header, bg=theme['card_bg'], fg=theme['fg']).pack(expand=True)
        
        # Tab 2: History Chart
        history_frame = tk.Frame(notebook, bg=theme['card_bg'])
        notebook.add(history_frame, text=f"📈 {self.language.get('history_analysis')}")
        
        trades = self.history.get_trades()
        if trades and len(trades) > 0:
            try:
                fig = self.chart_generator.create_trade_history_chart(trades, self.current_theme)
                if fig:
                    canvas = FigureCanvasTkAgg(fig, master=history_frame)
                    canvas.draw()
                    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            except:
                tk.Label(history_frame, text=f"⚠️ {self.language.get('chart_error')}", 
                        font=self.persian_font_header, bg=theme['card_bg'], fg=theme['fg']).pack(expand=True)
        else:
            tk.Label(history_frame, text=f"⚠️ {self.language.get('no_history')}", 
                    font=self.persian_font_header, bg=theme['card_bg'], fg=theme['fg']).pack(expand=True)
    
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
                messagebox.showinfo(self.language.get('success'), f"{self.language.get('file_saved')}:\n{filename}")
            else:
                messagebox.showerror(self.language.get('error'), self.language.get('save_error'))
    
    def clear_history(self):
        if messagebox.askyesno(self.language.get('confirm'), self.language.get('clear_history_confirm')):
            self.history.clear_history()
            messagebox.showinfo(self.language.get('success'), self.language.get('history_cleared'))
    
    def clear_results(self):
        self.results_text.delete('1.0', tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = CryptoTradingCalculator(root)
    root.mainloop()
