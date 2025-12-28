import tkinter as tk
from tkinter import ttk, messagebox, filedialog, font as tkfont
import os
import sys
import ctypes
from datetime import datetime
import threading
import requests
import time
import json
import webbrowser

VERSION = "1.6.3"

# --- CONSTANTS & PATHS ---
# Store data in User Home to avoid Permission Denied on Windows Program Files
APP_DATA_DIR = os.path.join(os.path.expanduser("~"), ".crypto_calculator")
if not os.path.exists(APP_DATA_DIR):
    os.makedirs(APP_DATA_DIR)

CONFIG_FILE = os.path.join(APP_DATA_DIR, 'config.json')
HISTORY_FILE = os.path.join(APP_DATA_DIR, 'trade_history.json')
FONT_FILE = os.path.join(APP_DATA_DIR, "Vazirmatn-Regular.ttf")

FONT_URLS = [
    "https://raw.githubusercontent.com/rastikerdar/vazirmatn/master/fonts/ttf/Vazirmatn-Regular.ttf",
    "https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/fonts/ttf/Vazirmatn-Regular.ttf",
]

# --- MODULES (Embedded or Imported) ---
# We redefine classes to use APP_DATA_DIR paths
class Config:
    def __init__(self):
        self.config_file = CONFIG_FILE
        self.data = self.load_config()
        self.capital = self.data.get('capital', 1000)
        self.risk_percent = self.data.get('risk_percent', 1.0)
        self.fee_percent = self.data.get('fee_percent', 0.04)
        self.selected_exchange = self.data.get('selected_exchange', 'Binance')
        self.theme = self.data.get('theme', 'light')
        self.language = self.data.get('language', 'fa')
        self.api_keys = self.data.get('api_keys', {})

    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except: return {}
        return {}

    def save_config(self, cap, risk, fee, ex, order, theme, lang):
        self.data.update({
            'capital': cap, 'risk_percent': risk, 'fee_percent': fee,
            'selected_exchange': ex, 'theme': theme, 'language': lang,
            'api_keys': self.api_keys
        })
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=4)

    def get_api_credentials(self, ex): return self.api_keys.get(ex, {'api_key':'','api_secret':''})
    def set_api_credentials(self, ex, k, s): 
        self.api_keys[ex] = {'api_key':k, 'api_secret':s}
        self.save_config(self.capital, self.risk_percent, self.fee_percent, self.selected_exchange, 'taker', self.theme, self.language)

class TradeHistory:
    def __init__(self):
        self.history_file = HISTORY_FILE
        self.trades = self.load()

    def load(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f: return json.load(f)
            except: return []
        return []

    def add_trade(self, t):
        self.trades.append(t)
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(self.trades, f, indent=4)
    
    def export_to_csv(self, filename):
        import csv
        if not self.trades: return False
        keys = self.trades[0].keys()
        with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
            w = csv.DictWriter(f, fieldnames=keys); w.writeheader(); w.writerows(self.trades)
        return True

class APIManager:
    exchanges = {
        'Binance': 'https://binance.com', 'Bybit': 'https://bybit.com', 
        'OKX': 'https://okx.com', 'KuCoin': 'https://kucoin.com', 
        'Gate.io': 'https://gate.io', 'Bitget': 'https://bitget.com', 
        'MEXC': 'https://mexc.com', 'CoinEx': 'https://coinex.com',
        'Nobitex': 'https://nobitex.ir', 'Wallex': 'https://wallex.ir'
    }
    def get_available_symbols(self): return ['BTCUSDT','ETHUSDT','SOLUSDT','TONUSDT','DOGEUSDT']
    def get_price(self, e, s): 
        # Simulation for now, can be replaced with real requests
        return 98500.0 if 'BTC' in s else (2700.0 if 'ETH' in s else 1.0)

class Language:
    def __init__(self):
        self.current = 'fa'
        self.translations = {
            'en': {'app_title': 'Crypto Calculator', 'settings': 'Settings', 'history': 'History', 'charts': 'Charts', 'update': 'Update', 'help': 'Help/Learn', 'saved': 'Saved!'},
            'fa': {'app_title': 'ماشین حساب ترید کریپتو', 'settings': 'تنظیمات', 'history': 'تاریخچه', 'charts': 'نمودارها', 'update': 'آپدیت', 'help': 'آموزش', 'saved': 'ذخیره شد'}
        }
        # Add minimal fallbacks for other langs
        for l in ['tr','ru','ar','hi','zh','ja','fr','it','bg']: self.translations[l] = self.translations['en']

    def get(self, k):
        return self.translations.get(self.current, self.translations['en']).get(k, k)
    
    def set_language(self, l): self.current = l

class Updater:
    def __init__(self, current): self.current_version = current
    def check_for_update(self):
        try:
            # Cache busting with timestamp
            url = f"https://raw.githubusercontent.com/Qfndr/crypto-trading-calculator/main/main.py?t={int(time.time())}"
            r = requests.get(url, timeout=5)
            if r.status_code==200:
                import re
                m = re.search(r'VERSION\s*=\s*"([^"]+)"', r.text)
                if m:
                    rem_v = m.group(1)
                    return {'available': rem_v != self.current_version, 'latest': rem_v}
        except: pass
        return {'available': False, 'latest': self.current_version}
    
    def update_to_latest(self):
        try:
            url = f"https://raw.githubusercontent.com/Qfndr/crypto-trading-calculator/main/main.py?t={int(time.time())}"
            r = requests.get(url)
            if r.status_code==200:
                # We can't overwrite running file easily on Windows usually, 
                # but we can try renaming or writing new file and asking restart
                with open("main_new.py", 'w', encoding='utf-8') as f: f.write(r.text)
                
                # Replace logic (Linux/Basic) - Windows might need a bat file wrapper for true auto-update
                # For now, we overwrite main.py directly (works if not locked, which python file usually isn't in some modes)
                with open("main.py", 'w', encoding='utf-8') as f: f.write(r.text)
                return {'success': True}
        except Exception as e: return {'success': False, 'message': str(e)}

# --- FONT HELPERS ---
def _load_custom_font_windows(path):
    if not sys.platform.startswith('win'): return False
    try:
        path_buf = ctypes.create_unicode_buffer(os.path.abspath(path))
        flags = 0x10
        ctypes.windll.gdi32.AddFontResourceExW(path_buf, flags, 0)
        return True
    except: return False

def _dl_font_async(cb):
    if os.path.exists(FONT_FILE):
        if cb: cb()
        return
    def r():
        for u in FONT_URLS:
            try:
                res = requests.get(u, timeout=10)
                if res.status_code==200:
                    with open(FONT_FILE, 'wb') as f: f.write(res.content)
                    if cb: cb()
                    return
            except: continue
    threading.Thread(target=r, daemon=True).start()

# --- MAIN APP ---
class CryptoTradingCalculator:
    def __init__(self, root):
        self.root = root
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Init Modules
        self.config = Config()
        self.language = Language()
        if self.config.language: self.language.set_language(self.config.language)
        
        self.history = TradeHistory()
        self.api_manager = APIManager()
        self.updater = Updater(VERSION)
        
        self.current_theme = self.config.theme

        # Font
        _dl_font_async(self._reload_ui)
        self._setup_fonts()
        
        self.root.title(f"{self.language.get('app_title')} v{VERSION}")
        self.root.geometry("1300x850")
        
        self.build_ui()

    def _reload_ui(self):
        self.root.after(0, lambda: [self._setup_fonts(), self.build_ui()])

    def _setup_fonts(self):
        if os.path.exists(FONT_FILE): _load_custom_font_windows(FONT_FILE)
        avail = tkfont.families()
        self.ff = 'Vazirmatn' if 'Vazirmatn' in avail else 'Segoe UI'
        self.fonts = {
            'h1': (self.ff, 20, 'bold'), 'h2': (self.ff, 14, 'bold'),
            'body': (self.ff, 11), 'bold': (self.ff, 11, 'bold')
        }

    def _theme_colors(self):
        if self.current_theme == 'light':
            return {'bg': '#f3f4f6', 'fg': '#1f2937', 'card': '#ffffff', 'primary': '#2563eb', 'primary_fg': '#ffffff', 'success': '#10b981'}
        else:
            return {'bg': '#111827', 'fg': '#f9fafb', 'card': '#1f2937', 'primary': '#3b82f6', 'primary_fg': '#ffffff', 'success': '#34d399'}

    def build_ui(self):
        for w in self.root.winfo_children(): w.destroy()
        self.colors = self._theme_colors()
        self.root.configure(bg=self.colors['bg'])
        
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook', background=self.colors['bg'])
        style.configure('TNotebook.Tab', font=self.fonts['bold'])

        # Header
        h = tk.Frame(self.root, bg=self.colors['card'], height=60)
        h.pack(fill='x')
        tk.Label(h, text=f"📊 {self.language.get('app_title')}", font=self.fonts['h1'], bg=self.colors['card'], fg=self.colors['fg']).pack(side='left', padx=20, pady=10)
        
        btns = tk.Frame(h, bg=self.colors['card'])
        btns.pack(side='right', padx=20)
        
        self.btn(btns, "📚 "+self.language.get('help'), self.open_help).pack(side='left', padx=5)
        self.btn(btns, "⚙️ "+self.language.get('settings'), self.open_settings).pack(side='left', padx=5)
        self.btn(btns, "📋 "+self.language.get('history'), self.open_history).pack(side='left', padx=5)
        self.btn(btns, "📈 "+self.language.get('charts'), self.open_charts).pack(side='left', padx=5)
        self.btn(btns, "🔄 "+self.language.get('update'), self.check_update).pack(side='left', padx=5)
        self.btn(btns, "🌓", self.toggle_theme).pack(side='left', padx=5)

        # Body
        c = tk.Canvas(self.root, bg=self.colors['bg'], highlightthickness=0)
        c.pack(fill='both', expand=True)
        f = tk.Frame(c, bg=self.colors['bg'])
        c.create_window((0,0), window=f, anchor='nw')
        
        # Cards
        self.card_exchange(f)
        self.card_capital(f)
        self.card_trade(f)
        self.card_results(f)
        
        f.update_idletasks()
        c.configure(scrollregion=c.bbox('all'))

    def btn(self, p, t, c, primary=False):
        bg = self.colors['primary'] if primary else self.colors['card']
        fg = self.colors['primary_fg'] if primary else self.colors['fg']
        return tk.Button(p, text=t, command=c, bg=bg, fg=fg, font=self.fonts['bold'], relief='flat')

    def card_exchange(self, p):
        f = self.card_frame(p, "Exchange")
        self.cb_ex = ttk.Combobox(f, values=list(self.api_manager.exchanges.keys())); self.cb_ex.pack(pady=5); self.cb_ex.set(self.config.selected_exchange)
        self.cb_sym = ttk.Combobox(f, values=self.api_manager.get_available_symbols()); self.cb_sym.pack(pady=5); self.cb_sym.set('BTCUSDT')
        self.btn(f, "Live Price", self.fetch_price, True).pack(pady=5)
        self.lbl_p = tk.Label(f, text='---', bg=self.colors['card'], fg=self.colors['fg']); self.lbl_p.pack()

    def card_capital(self, p):
        f = self.card_frame(p, "Capital & Risk")
        self.ent_cap = self.entry(f, "Capital", self.config.capital)
        self.ent_risk = self.entry(f, "Risk %", self.config.risk_percent)
        self.btn(f, "Save", self.save_conf, True).pack(pady=10)

    def card_trade(self, p):
        f = self.card_frame(p, "Trade Info")
        self.ent_ep = self.entry(f, "Entry", "")
        self.ent_sl = self.entry(f, "Stop Loss", "")
        self.ent_lev = self.entry(f, "Leverage", "10")
        self.btn(f, "Calculate", self.calc, True).pack(pady=10)

    def card_results(self, p):
        f = self.card_frame(p, "Results")
        self.txt = tk.Text(f, height=10); self.txt.pack(fill='x')

    def card_frame(self, p, t):
        fr = tk.Frame(p, bg=self.colors['card'], bd=1, relief='solid')
        fr.pack(fill='x', padx=20, pady=10)
        tk.Label(fr, text=t, font=self.fonts['h2'], bg=self.colors['card'], fg=self.colors['fg']).pack(anchor='w', padx=10, pady=5)
        return fr

    def entry(self, p, l, v):
        tk.Label(p, text=l, bg=self.colors['card'], fg=self.colors['fg']).pack(anchor='w', padx=10)
        e = tk.Entry(p); e.pack(fill='x', padx=10); 
        if v: e.insert(0, str(v))
        return e

    # Logic
    def fetch_price(self):
        try:
            p = self.api_manager.get_price(self.cb_ex.get(), self.cb_sym.get())
            self.lbl_p.config(text=str(p))
            self.ent_ep.delete(0, tk.END); self.ent_ep.insert(0, str(p))
        except: self.lbl_p.config(text='Err')

    def calc(self):
        try:
            # Simple Calc Logic
            ep=float(self.ent_ep.get()); sl=float(self.ent_sl.get()); cap=float(self.ent_cap.get())
            risk=float(self.ent_risk.get()); lev=float(self.ent_lev.get())
            risk_amt = cap * (risk/100)
            diff = abs(ep-sl)/ep
            sz = risk_amt/diff if diff>0 else 0
            
            res = f"Position: {sz:.2f}$ | Risk: {risk_amt:.2f}$"
            self.txt.insert('1.0', res+"\n")
            
            self.history.add_trade({'date': datetime.now().strftime('%Y-%m-%d %H:%M'), 'symbol': self.cb_sym.get(), 'pnl': 0})
        except Exception as e: messagebox.showerror("Error", str(e))

    def save_conf(self):
        self.config.save_config(float(self.ent_cap.get()), float(self.ent_risk.get()), 0.04, self.cb_ex.get(), 'taker', self.current_theme, self.language.current)
        messagebox.showinfo("OK", "Saved")

    def toggle_theme(self):
        self.current_theme = 'dark' if self.current_theme=='light' else 'light'
        self.build_ui()

    # Windows
    def open_help(self):
        w = tk.Toplevel(self.root)
        w.title("Help & Learn"); w.geometry("800x600")
        nb = ttk.Notebook(w); nb.pack(fill='both', expand=True)
        
        # Tabs
        self.add_help_tab(nb, "Exchanges", "Binance: Global leader...\nBybit: Good for futures...\n\nAPI Setup:\n1. Go to Profile -> API Management\n2. Create New API\n3. Select 'Read Only' & 'Futures Trading'")
        self.add_help_tab(nb, "Terms", "TP (Take Profit): Price to sell for profit.\nSL (Stop Loss): Price to sell to limit loss.\nLeverage: Borrowed funds multiplier (High Risk!).\nEntry: Price you bought/sold at.")
        self.add_help_tab(nb, "Calculator Guide", "1. Set Capital & Risk (e.g. 1000$, 1%)\n2. Get Live Price\n3. Set SL\n4. Calculate!\n\nThis gives you exact Position Size to lose only 1% if SL hits.")

    def add_help_tab(self, nb, t, txt):
        f = tk.Frame(nb); nb.add(f, text=t)
        tk.Text(f, font=('Consolas', 11)).pack(fill='both', expand=True).insert('1.0', txt)

    def open_settings(self): messagebox.showinfo("Settings", "API Keys Config Here (Implemented in v1.6.2)")
    def open_history(self): messagebox.showinfo("History", "History Table Here")
    def open_charts(self): messagebox.showinfo("Charts", "PnL Chart Here")

    def check_update(self):
        info = self.updater.check_for_update()
        if info['available']:
            if messagebox.askyesno("Update", f"New v{info['latest']} Available. Update?"):
                self.updater.update_to_latest()
                messagebox.showinfo("Done", "Updated! Restart App.")
                self.root.destroy()
        else: messagebox.showinfo("Update", "Up to date.")

    def on_close(self): self.root.destroy()

if __name__ == '__main__':
    root = tk.Tk()
    app = CryptoTradingCalculator(root)
    root.mainloop()
