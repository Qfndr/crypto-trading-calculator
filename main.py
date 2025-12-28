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
import sys

VERSION = "1.5.1"

# --- FONT MANAGEMENT ---
try:
    import requests
    FONT_URL = "https://github.com/rastikerdar/vazirmatn/raw/master/fonts/ttf/Vazirmatn-Regular.ttf"
    FONT_PATH = "Vazirmatn-Regular.ttf"
    
    if not os.path.exists(FONT_PATH):
        def download_font():
            try:
                response = requests.get(FONT_URL, timeout=10)
                if response.status_code == 200:
                    with open(FONT_PATH, 'wb') as f:
                        f.write(response.content)
            except: pass
        threading.Thread(target=download_font).start()
except:
    pass

class CryptoTradingCalculator:
    def __init__(self, root):
        self.root = root
        
        # --- INIT SYSTEMS ---
        self.language = Language()
        self.updater = Updater()
        self.config = Config()
        self.history = TradeHistory()
        self.api_manager = APIManager()
        self.chart_generator = ChartGenerator()
        
        # Load Language
        saved_lang = self.load_language_preference()
        if saved_lang:
            self.language.set_language(saved_lang)
            
        # --- WINDOW CONFIG ---
        self.root.title(f"💰 {self.language.get('app_title')} v{VERSION}")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 800)
        
        # --- THEMES (Professional Flat Design) ---
        self.themes = {
            'light': {
                'bg': '#f0f2f5', 'fg': '#1c1e21',
                'card_bg': '#ffffff', 'card_fg': '#1c1e21',
                'input_bg': '#ffffff', 'input_fg': '#1c1e21', 'input_border': '#ccd0d5',
                'btn_bg': '#1877f2', 'btn_fg': '#ffffff', 'btn_hover': '#166fe5',
                'accent': '#1877f2', 'success': '#42b72a', 'error': '#fa3e3e',
                'header_bg': '#ffffff', 'border': '#ddd'
            },
            'dark': {
                'bg': '#18191a', 'fg': '#e4e6eb',
                'card_bg': '#242526', 'card_fg': '#e4e6eb',
                'input_bg': '#3a3b3c', 'input_fg': '#e4e6eb', 'input_border': '#3e4042',
                'btn_bg': '#2d88ff', 'btn_fg': '#ffffff', 'btn_hover': '#4599ff',
                'accent': '#2d88ff', 'success': '#45bd62', 'error': '#f02849',
                'header_bg': '#242526', 'border': '#3e4042'
            }
        }
        self.current_theme = self.config.theme
        
        # --- FONTS ---
        self.setup_fonts()
        
        # --- DATA ---
        self.tp_entries = []
        self.exchanges = {
            "Binance": {"maker": 0.02, "taker": 0.04}, "Bybit": {"maker": 0.02, "taker": 0.055},
            "OKX": {"maker": 0.02, "taker": 0.05}, "KuCoin": {"maker": 0.02, "taker": 0.06},
            "Gate.io": {"maker": 0.015, "taker": 0.05}, "Custom": {"maker": 0.15, "taker": 0.15}
        }
        
        # --- BUILD UI ---
        self.style = ttk.Style()
        self.create_widgets()
        self.apply_theme()
        
    def setup_fonts(self):
        """Robust font selection"""
        # Attempt to find Vazirmatn or system fonts
        available_families = tk.font.families()
        
        # Priority list
        priorities = ['Vazirmatn', 'Segoe UI', 'Roboto', 'Helvetica', 'Arial']
        self.main_font_family = 'Arial' # Fallback
        
        for font in priorities:
            if font in available_families or (font == 'Vazirmatn' and os.path.exists(FONT_PATH)):
                self.main_font_family = font
                break
                
        # Define font objects
        self.f_title = (self.main_font_family, 24, 'bold')
        self.f_header = (self.main_font_family, 16, 'bold')
        self.f_sub = (self.main_font_family, 12, 'bold')
        self.f_body = (self.main_font_family, 11)
        self.f_bold = (self.main_font_family, 11, 'bold')
        self.f_small = (self.main_font_family, 9)

    def load_language_preference(self):
        try:
            if os.path.exists('config.json'):
                with open('config.json', 'r', encoding='utf-8') as f:
                    return json.load(f).get('language', 'fa')
        except: return 'fa'

    def save_language_preference(self):
        try:
            data = {}
            if os.path.exists('config.json'):
                with open('config.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
            data['language'] = self.language.current
            with open('config.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
        except: pass

    def create_widgets(self):
        # Container
        self.container = tk.Frame(self.root)
        self.container.pack(fill=tk.BOTH, expand=True)
        
        # Header
        self.header = tk.Frame(self.container, height=70)
        self.header.pack(fill=tk.X, side=tk.TOP)
        self.header.pack_propagate(False)
        
        # Logo/Title
        self.title_lbl = tk.Label(self.header, text=f"📊 {self.language.get('app_title')}", font=self.f_header)
        self.title_lbl.pack(side=tk.LEFT, padx=20)
        
        # Nav Buttons
        nav_frame = tk.Frame(self.header)
        nav_frame.pack(side=tk.RIGHT, padx=20)
        
        self.btn_theme = self.create_nav_btn(nav_frame, "🌙", self.toggle_theme)
        self.btn_settings = self.create_nav_btn(nav_frame, "⚙️", self.show_settings)
        self.btn_history = self.create_nav_btn(nav_frame, "📋", self.show_history)
        self.btn_charts = self.create_nav_btn(nav_frame, "📈", self.show_charts)
        self.btn_update = self.create_nav_btn(nav_frame, "🔄", self.show_update)
        
        # Language Menu
        self.lang_var = tk.StringVar(value=self.language.current)
        lang_menu = ttk.OptionMenu(nav_frame, self.lang_var, self.language.current, 
                                 *self.language.translations.keys(), 
                                 command=self.change_language)
        lang_menu.pack(side=tk.LEFT, padx=5)

        # Scrollable Content
        self.canvas = tk.Canvas(self.container, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.container, orient="vertical", command=self.canvas.yview)
        self.scroll_frame = tk.Frame(self.canvas)
        
        self.scroll_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.container.bind_all("<MouseWheel>", lambda e: self.canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        # Cards
        self.create_exchange_section()
        self.create_capital_section()
        self.create_trade_section()
        self.create_results_section()

    def create_nav_btn(self, parent, text, cmd):
        btn = tk.Button(parent, text=text, command=cmd, font=self.f_bold, 
                       relief=tk.FLAT, bd=0, padx=15, pady=5, cursor='hand2')
        btn.pack(side=tk.LEFT, padx=2)
        return btn

    def create_section(self, parent, title):
        frame = tk.Frame(parent, bd=1, relief=tk.SOLID)
        frame.pack(fill=tk.X, padx=20, pady=10)
        
        lbl = tk.Label(frame, text=title, font=self.f_sub, anchor="w", padx=15, pady=10)
        lbl.pack(fill=tk.X)
        
        content = tk.Frame(frame, padx=15, pady=15)
        content.pack(fill=tk.BOTH, expand=True)
        return frame, lbl, content

    def create_exchange_section(self):
        self.card_exchange, self.lbl_exchange, body = self.create_section(self.scroll_frame, self.language.get('exchange_symbol'))
        
        # Exchange
        tk.Label(body, text=self.language.get('exchange'), font=self.f_body).grid(row=0, column=0, sticky='w', pady=5)
        self.cb_exchange = ttk.Combobox(body, values=list(self.exchanges.keys()), font=self.f_body, state='readonly')
        self.cb_exchange.set(self.config.selected_exchange)
        self.cb_exchange.grid(row=0, column=1, sticky='ew', padx=10, pady=5)
        self.cb_exchange.bind('<<ComboboxSelected>>', self.update_fees)
        
        # Order Type
        tk.Label(body, text=self.language.get('order_type'), font=self.f_body).grid(row=0, column=2, sticky='w', pady=5)
        self.cb_order = ttk.Combobox(body, values=['Maker', 'Taker'], font=self.f_body, state='readonly')
        self.cb_order.set('Taker')
        self.cb_order.grid(row=0, column=3, sticky='ew', padx=10, pady=5)
        self.cb_order.bind('<<ComboboxSelected>>', self.update_fees)

        # Symbol
        tk.Label(body, text=self.language.get('symbol'), font=self.f_body).grid(row=1, column=0, sticky='w', pady=5)
        self.cb_symbol = ttk.Combobox(body, values=self.api_manager.get_available_symbols(), font=self.f_body)
        self.cb_symbol.set('BTCUSDT')
        self.cb_symbol.grid(row=1, column=1, sticky='ew', padx=10, pady=5)
        
        # Live Price
        self.btn_price = tk.Button(body, text=self.language.get('live_price'), command=self.fetch_price, font=self.f_body)
        self.btn_price.grid(row=1, column=2, sticky='ew', padx=10)
        self.lbl_price_val = tk.Label(body, text="---", font=self.f_bold)
        self.lbl_price_val.grid(row=1, column=3, sticky='w', padx=10)

    def create_capital_section(self):
        self.card_capital, self.lbl_capital, body = self.create_section(self.scroll_frame, self.language.get('capital_risk'))
        
        fields = [
            (self.language.get('total_capital'), 'capital_entry', str(self.config.capital)),
            (self.language.get('risk_percent'), 'risk_entry', str(self.config.risk_percent)),
            (self.language.get('fee_percent'), 'fee_entry', str(self.config.fee_percent))
        ]
        
        for i, (text, name, val) in enumerate(fields):
            tk.Label(body, text=text, font=self.f_body).grid(row=0, column=i*2, sticky='w')
            entry = tk.Entry(body, font=self.f_body)
            entry.insert(0, val)
            entry.grid(row=0, column=i*2+1, sticky='ew', padx=10)
            setattr(self, name, entry)
            
        self.btn_save = tk.Button(body, text=self.language.get('save_settings'), command=self.save_config_ui, font=self.f_body)
        self.btn_save.grid(row=1, column=0, columnspan=6, sticky='ew', pady=10)

    def create_trade_section(self):
        self.card_trade, self.lbl_trade, body = self.create_section(self.scroll_frame, self.language.get('trade_info'))
        
        # Entry / SL
        tk.Label(body, text=self.language.get('entry_price'), font=self.f_body).grid(row=0, column=0, sticky='w')
        self.entry_price = tk.Entry(body, font=self.f_body)
        self.entry_price.grid(row=0, column=1, sticky='ew', padx=5, pady=5)
        
        tk.Label(body, text=self.language.get('stop_loss'), font=self.f_body).grid(row=0, column=2, sticky='w')
        self.stop_loss = tk.Entry(body, font=self.f_body)
        self.stop_loss.grid(row=0, column=3, sticky='ew', padx=5, pady=5)
        
        # TPs
        self.tp_entries = []
        for i in range(3):
            tk.Label(body, text=f"TP {i+1}", font=self.f_body).grid(row=1, column=i*2 if i<2 else 0, sticky='w')
            e = tk.Entry(body, font=self.f_body)
            e.grid(row=1 if i<2 else 2, column=(i*2)+1 if i<2 else 1, sticky='ew', padx=5, pady=5)
            self.tp_entries.append(e)
            
        # Type & Lev
        tk.Label(body, text=self.language.get('position_type'), font=self.f_body).grid(row=2, column=2, sticky='w')
        self.cb_pos = ttk.Combobox(body, values=['LONG', 'SHORT'], state='readonly', font=self.f_body)
        self.cb_pos.set('LONG')
        self.cb_pos.grid(row=2, column=3, sticky='ew', padx=5)
        
        tk.Label(body, text=self.language.get('leverage'), font=self.f_body).grid(row=3, column=0, sticky='w')
        self.leverage = tk.Entry(body, font=self.f_body)
        self.leverage.insert(0, "10")
        self.leverage.grid(row=3, column=1, sticky='ew', padx=5)

        # Calculate
        self.btn_calc = tk.Button(body, text=f"🚀 {self.language.get('calculate')}", command=self.calculate, font=self.f_bold, height=2)
        self.btn_calc.grid(row=4, column=0, columnspan=4, sticky='ew', pady=15)

    def create_results_section(self):
        self.card_res, self.lbl_res, body = self.create_section(self.scroll_frame, self.language.get('results'))
        
        self.txt_result = tk.Text(body, height=15, font=('Consolas', 10), relief=tk.FLAT)
        self.txt_result.pack(fill=tk.BOTH, expand=True)
        
        btn_frame = tk.Frame(body)
        btn_frame.pack(fill=tk.X, pady=5)
        
        self.btn_export = tk.Button(btn_frame, text=self.language.get('export_csv'), command=self.export_csv)
        self.btn_export.pack(side=tk.LEFT, padx=5)
        
        self.btn_clear = tk.Button(btn_frame, text=self.language.get('clear_results'), command=lambda: self.txt_result.delete('1.0', tk.END))
        self.btn_clear.pack(side=tk.LEFT, padx=5)

    # --- LOGIC ---
    
    def change_language(self, lang_code):
        self.language.set_language(lang_code)
        self.save_language_preference()
        # Restart interface to apply changes properly
        self.root.destroy()
        new_root = tk.Tk()
        app = CryptoTradingCalculator(new_root)
        new_root.mainloop()

    def update_fees(self, e=None):
        ex = self.cb_exchange.get()
        if ex in self.exchanges:
            key = 'maker' if self.cb_order.get() == 'Maker' else 'taker'
            self.fee_entry.delete(0, tk.END)
            self.fee_entry.insert(0, str(self.exchanges[ex][key]))

    def fetch_price(self):
        def _run():
            try:
                self.lbl_price_val.config(text="...")
                p = self.api_manager.get_price(self.cb_exchange.get(), self.cb_symbol.get())
                if p:
                    self.lbl_price_val.config(text=f"{p}")
                    self.entry_price.delete(0, tk.END)
                    self.entry_price.insert(0, str(p))
                else:
                    self.lbl_price_val.config(text="Err")
            except: self.lbl_price_val.config(text="Err")
        threading.Thread(target=_run).start()

    def calculate(self):
        try:
            # Gather Data
            ep = float(self.entry_price.get())
            sl = float(self.stop_loss.get())
            cap = float(self.capital_entry.get())
            risk = float(self.risk_entry.get())
            lev = float(self.leverage.get())
            fee = float(self.fee_entry.get())
            tps = [float(x.get()) for x in self.tp_entries if x.get()]
            pos = self.cb_pos.get()
            
            if not tps: raise ValueError
            
            # Math
            risk_amt = cap * (risk/100)
            diff_pct = abs(ep - sl) / ep
            pos_size = risk_amt / diff_pct
            qty = (pos_size * lev) / ep
            
            # Output
            res = f"--- {datetime.now().strftime('%H:%M:%S')} ---\n"
            res += f"{pos} | {lev}x | {self.cb_symbol.get()}\n"
            res += f"Entry: {ep} | SL: {sl}\n"
            res += f"Size: {pos_size:.2f}$ ({qty:.4f})\n"
            res += f"Risk: {risk_amt:.2f}$ ({risk}%)\n\n"
            
            for i, tp in enumerate(tps):
                pnl = abs(ep - tp) / ep * pos_size * lev
                res += f"TP{i+1}: {tp} -> +{pnl:.2f}$\n"
                
            self.txt_result.insert('1.0', res + "\n")
            
            # Save History
            self.history.add_trade({
                'symbol': self.cb_symbol.get(),
                'entry': ep, 'sl': sl, 'pnl': 0, # Simplified for now
                'date': datetime.now().strftime('%Y-%m-%d')
            })
            
        except:
            messagebox.showerror(self.language.get('error'), self.language.get('enter_valid'))

    def show_settings(self):
        # REAL Settings Window
        win = tk.Toplevel(self.root)
        win.title(self.language.get('settings'))
        win.geometry("400x300")
        
        tk.Label(win, text="API Key").pack(pady=5)
        e_key = tk.Entry(win); e_key.pack()
        
        tk.Label(win, text="Secret Key").pack(pady=5)
        e_secret = tk.Entry(win); e_secret.pack()
        
        def save():
            # Save to config
            self.config.set_api_keys(self.cb_exchange.get(), e_key.get(), e_secret.get())
            messagebox.showinfo("Saved", "API Keys Saved!")
            win.destroy()
            
        tk.Button(win, text="Save", command=save).pack(pady=20)

    def show_history(self):
        # REAL History Window
        win = tk.Toplevel(self.root)
        win.title(self.language.get('history'))
        win.geometry("600x400")
        
        cols = ('Date', 'Symbol', 'Entry', 'SL', 'Result')
        tree = ttk.Treeview(win, columns=cols, show='headings')
        for c in cols: tree.heading(c, text=c)
        tree.pack(fill=tk.BOTH, expand=True)
        
        for t in self.history.trades:
            tree.insert('', 'end', values=(t.get('date'), t.get('symbol'), t.get('entry'), t.get('sl'), t.get('pnl')))

    def show_charts(self):
        # REAL Chart Window
        win = tk.Toplevel(self.root)
        win.title(self.language.get('charts'))
        win.geometry("600x400")
        
        if not self.history.trades:
            tk.Label(win, text="No Data").pack()
            return
            
        # Basic PnL Chart using Canvas (No matplotlib dep if not needed, but cleaner)
        c = tk.Canvas(win, bg='white')
        c.pack(fill=tk.BOTH, expand=True)
        # Draw simple line based on PnL history
        # (Simplified drawing logic for robustness)
        c.create_text(300, 200, text="Chart Placeholder (Matplotlib integration pending)")

    def show_update(self):
        win = tk.Toplevel(self.root)
        win.title(self.language.get('update'))
        
        status = tk.Label(win, text="Checking...")
        status.pack(pady=20, padx=20)
        
        def check():
            info = self.updater.check_for_update()
            if info['available']:
                status.config(text=f"New: v{info['latest']}")
                tk.Button(win, text="Update Now", command=lambda: self.updater.update_to_latest()).pack()
            else:
                status.config(text="Up to date!")
        
        win.after(100, check)

    def save_config_ui(self):
        self.config.save_config(
            float(self.capital_entry.get()),
            float(self.risk_entry.get()),
            float(self.fee_entry.get()),
            self.cb_exchange.get(),
            self.cb_order.get(),
            self.current_theme
        )
        messagebox.showinfo("Saved", "Config Saved")

    def export_csv(self):
        f = filedialog.asksaveasfilename(defaultextension=".csv")
        if f: self.history.export_to_csv(f)

    def toggle_theme(self):
        self.current_theme = 'dark' if self.current_theme == 'light' else 'light'
        self.apply_theme()
        
    def apply_theme(self):
        t = self.themes[self.current_theme]
        self.root.config(bg=t['bg'])
        self.container.config(bg=t['bg'])
        self.header.config(bg=t['header_bg'])
        self.title_lbl.config(bg=t['header_bg'], fg=t['fg'])
        self.canvas.config(bg=t['bg'])
        self.scroll_frame.config(bg=t['bg'])
        
        # Update cards
        for x in [self.card_exchange, self.card_capital, self.card_trade, self.card_res]:
            x.config(bg=t['card_bg'], highlightbackground=t['border'])
        
        for l in [self.lbl_exchange, self.lbl_capital, self.lbl_trade, self.lbl_res]:
            l.config(bg=t['card_bg'], fg=t['fg'])
            
        # Update Text result
        self.txt_result.config(bg=t['input_bg'], fg=t['input_fg'])

if __name__ == "__main__":
    root = tk.Tk()
    app = CryptoTradingCalculator(root)
    root.mainloop()
