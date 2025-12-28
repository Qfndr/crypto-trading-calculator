import tkinter as tk
from tkinter import ttk, messagebox, filedialog, font as tkfont
import json
import os
import sys
import ctypes
from datetime import datetime
import threading
import math
import requests

# --- VERSION ---
VERSION = "1.6.0"

# --- CONSTANTS ---
FONT_FILE = "Vazirmatn-Regular.ttf"
FONT_URL = "https://github.com/rastikerdar/vazirmatn/raw/master/fonts/ttf/Vazirmatn-Regular.ttf"

# --- FONT LOADER (WINDOWS) ---
def load_custom_font(font_path):
    """Loads a font file into Windows font system temporarily for this session."""
    path = os.path.abspath(font_path)
    if not os.path.exists(path):
        print(f"Font file not found at: {path}")
        return False
    if sys.platform.startswith("win"):
        try:
            # GDI32 AddFontResourceExW
            path_buf = ctypes.create_unicode_buffer(path)
            flags = 0x10  # FR_PRIVATE
            num_fonts = ctypes.windll.gdi32.AddFontResourceExW(path_buf, flags, 0)
            print(f"Font loaded: {num_fonts} (Path: {path})")
            return num_fonts > 0
        except Exception as e:
            print(f"Font load error: {e}")
            return False
    return True

# --- MODULES (Embedded for robustness) ---
# ... (Assuming config.py, language.py etc are present or using mock) ...
try:
    from config import Config
    from trade_history import TradeHistory
    from api_manager import APIManager
    from language import Language
    from updater import Updater
except ImportError:
    # Basic fallbacks if files missing
    class Config:
        def __init__(self): self.data={}
        def load_config(self): return {}
        def save_config(self, *args): pass
    class TradeHistory:
        def __init__(self): self.trades=[]
        def add_trade(self, t): self.trades.append(t)
    class APIManager:
        def get_available_symbols(self): return ['BTCUSDT','ETHUSDT']
        def get_price(self, e, s): return 0.0
    class Language:
        def __init__(self): self.current='en'; self.translations={'en':{}}
        def get(self, k): return k
        def set_language(self, l): self.current=l
    class Updater:
        def check_for_update(self): return {'available':False}
        def update_to_latest(self): pass

# --- MAIN APP ---
class CryptoTradingCalculator:
    def __init__(self, root):
        self.root = root
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # 1. Initialize Core Systems
        self.language = Language()
        self.config = Config()
        self.history = TradeHistory()
        self.api_manager = APIManager()
        self.updater = Updater()
        
        # 2. Download/Load Font
        self.ensure_font()
        
        # 3. Load Configs
        self.load_prefs()
        
        # 4. Setup UI
        self.setup_window()
        self.build_ui()

    def ensure_font(self):
        if not os.path.exists(FONT_FILE):
            print("Downloading font...")
            try:
                res = requests.get(FONT_URL, timeout=5)
                if res.status_code == 200:
                    with open(FONT_FILE, 'wb') as f: f.write(res.content)
            except Exception as e: print(f"DL Error: {e}")
            
        self.font_loaded = load_custom_font(FONT_FILE)
        
        # Check available fonts
        available = tkfont.families()
        if 'Vazirmatn' in available:
            self.ff = 'Vazirmatn'
        elif 'Vazirmatn RD' in available:
             self.ff = 'Vazirmatn RD' # Sometimes name varies
        else:
            self.ff = 'Segoe UI' if 'Segoe UI' in available else 'Arial'
        print(f"Selected Font: {self.ff}")
            
        self.update_font_objects()

    def update_font_objects(self):
        self.fonts = {
            'h1': (self.ff, 20, 'bold'),
            'h2': (self.ff, 14, 'bold'),
            'body': (self.ff, 11),
            'bold': (self.ff, 11, 'bold'),
            'small': (self.ff, 9)
        }

    def load_prefs(self):
        if hasattr(self.config, 'theme'): self.current_theme = self.config.theme
        else: self.current_theme = 'light'
        
        # Load saved language if Config supports it, else use Language class default
        # Ideally Language class should load from its own config or passed here.
        # We'll rely on Language class internal state if implemented.
        pass

    def setup_window(self):
        self.root.title(f"{self.language.get('app_title')} v{VERSION}")
        self.root.geometry("1300x850")
        self.root.minsize(1000, 700)

    def define_colors(self):
        self.colors = {
            'light': {
                'bg': '#f3f4f6', 'fg': '#1f2937',
                'card': '#ffffff', 'card_border': '#e5e7eb',
                'primary': '#2563eb', 'primary_fg': '#ffffff',
                'success': '#10b981', 'danger': '#ef4444',
                'input': '#ffffff', 'input_border': '#d1d5db'
            },
            'dark': {
                'bg': '#111827', 'fg': '#f9fafb',
                'card': '#1f2937', 'card_border': '#374151',
                'primary': '#3b82f6', 'primary_fg': '#ffffff',
                'success': '#34d399', 'danger': '#f87171',
                'input': '#374151', 'input_border': '#4b5563'
            }
        }
        self.theme = self.colors[self.current_theme]

    def build_ui(self):
        # Clear existing
        for widget in self.root.winfo_children():
            widget.destroy()
            
        self.define_colors()
        self.root.configure(bg=self.theme['bg'])
        
        # Styles
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background=self.theme['bg'])
        style.configure('TLabel', background=self.theme['bg'], foreground=self.theme['fg'], font=self.fonts['body'])
        style.configure('Card.TFrame', background=self.theme['card'])
        
        # --- HEADER ---
        header = tk.Frame(self.root, bg=self.theme['card'], height=60)
        header.pack(fill='x', side='top')
        header.pack_propagate(False)
        
        tk.Label(header, text=f"📊 {self.language.get('app_title')}", 
                font=self.fonts['h1'], bg=self.theme['card'], fg=self.theme['fg']).pack(side='left', padx=20)
        
        controls = tk.Frame(header, bg=self.theme['card'])
        controls.pack(side='right', padx=20)
        
        # Language
        self.lang_var = tk.StringVar(value=self.language.current)
        lang_cb = ttk.Combobox(controls, textvariable=self.lang_var, 
                              values=list(self.language.translations.keys()), 
                              state='readonly', width=5)
        lang_cb.pack(side='left', padx=5)
        lang_cb.bind('<<ComboboxSelected>>', self.change_language)
        
        self.btn(controls, "⚙️ " + self.language.get('settings'), self.open_settings).pack(side='left', padx=5)
        self.btn(controls, "📋 " + self.language.get('history'), self.open_history).pack(side='left', padx=5)
        self.btn(controls, "📈 " + self.language.get('charts'), self.open_charts).pack(side='left', padx=5)
        self.btn(controls, "🔄 " + self.language.get('update'), self.check_update).pack(side='left', padx=5)
        self.btn(controls, "🌓 Mode", self.toggle_theme).pack(side='left', padx=5)
        
        # --- SCROLLABLE AREA ---
        container = tk.Frame(self.root, bg=self.theme['bg'])
        container.pack(fill='both', expand=True)
        
        canvas = tk.Canvas(container, bg=self.theme['bg'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        self.scroll_frame = tk.Frame(canvas, bg=self.theme['bg'])
        
        self.scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # --- SECTIONS ---
        self.ui_exchange_section()
        self.ui_capital_section()
        self.ui_trade_section()
        self.ui_results_section()

    def ui_exchange_section(self):
        p = self.card(self.language.get('exchange_symbol'))
        
        self.label(p, self.language.get('exchange'), 0, 0)
        self.cb_exchange = self.combo(p, list(self.api_manager.exchanges.keys()) if hasattr(self.api_manager, 'exchanges') else ['Binance'], 0, 1)
        self.cb_exchange.set(getattr(self.config, 'selected_exchange', 'Binance'))
        
        self.label(p, self.language.get('order_type'), 0, 2)
        self.cb_order = self.combo(p, ['Maker', 'Taker'], 0, 3)
        self.cb_order.set(getattr(self.config, 'order_type', 'Taker'))
        
        self.label(p, self.language.get('symbol'), 1, 0)
        self.cb_symbol = self.combo(p, self.api_manager.get_available_symbols(), 1, 1)
        self.cb_symbol.set('BTCUSDT')
        
        self.btn(p, self.language.get('live_price'), self.fetch_price, primary=True).grid(row=1, column=2, padx=5, sticky='ew')
        self.lbl_price = self.label(p, "---", 1, 3)

    def ui_capital_section(self):
        p = self.card(self.language.get('capital_risk'))
        self.label(p, self.language.get('total_capital'), 0, 0)
        self.ent_capital = self.entry(p, getattr(self.config, 'capital', 1000), 0, 1)
        self.label(p, self.language.get('risk_percent'), 0, 2)
        self.ent_risk = self.entry(p, getattr(self.config, 'risk_percent', 1.0), 0, 3)
        self.label(p, self.language.get('fee_percent'), 1, 0)
        self.ent_fee = self.entry(p, getattr(self.config, 'fee_percent', 0.04), 1, 1)
        
        self.btn(p, self.language.get('save_settings'), self.save_main_config, success=True).grid(row=1, column=2, columnspan=2, sticky='ew', padx=5)

    def ui_trade_section(self):
        p = self.card(self.language.get('trade_info'))
        
        self.label(p, self.language.get('entry_price'), 0, 0)
        self.ent_entry = self.entry(p, "", 0, 1)
        self.label(p, self.language.get('stop_loss'), 0, 2)
        self.ent_sl = self.entry(p, "", 0, 3)
        
        self.tp_entries = []
        for i in range(3):
            self.label(p, f"TP {i+1}", 1, i*2 if i<2 else 0)
            e = self.entry(p, "", 1 if i<2 else 2, (i*2)+1 if i<2 else 1)
            self.tp_entries.append(e)
            
        self.label(p, self.language.get('leverage'), 2, 2)
        self.ent_lev = self.entry(p, "10", 2, 3)
        self.label(p, self.language.get('position_type'), 3, 0)
        self.cb_pos = self.combo(p, ['LONG', 'SHORT'], 3, 1)
        self.cb_pos.set('LONG')
        
        self.btn(p, self.language.get('calculate'), self.calculate, primary=True).grid(row=4, column=0, columnspan=4, sticky='ew', pady=15)

    def ui_results_section(self):
        p = self.card(self.language.get('results'))
        self.txt_res = tk.Text(p, height=10, bg=self.theme['input'], fg=self.theme['fg'], font=('Consolas', 10), relief='flat')
        self.txt_res.pack(fill='both', expand=True, padx=10, pady=5)
        
        b = tk.Frame(p, bg=self.theme['card'])
        b.pack(fill='x')
        self.btn(b, self.language.get('export_csv'), self.export_current).pack(side='left', padx=10)
        self.btn(b, self.language.get('clear_results'), lambda: self.txt_res.delete('1.0', tk.END)).pack(side='left')

    # --- HELPERS ---
    def card(self, title):
        f = tk.Frame(self.scroll_frame, bg=self.theme['card'], bd=1, relief='solid')
        f.pack(fill='x', padx=20, pady=10)
        tk.Label(f, text=title, font=self.fonts['h2'], bg=self.theme['card'], fg=self.theme['fg']).pack(anchor='w', padx=15, pady=10)
        inner = tk.Frame(f, bg=self.theme['card'])
        inner.pack(fill='both', expand=True, padx=15, pady=5)
        return inner
    
    def label(self, p, t, r, c):
        l = tk.Label(p, text=t, bg=self.theme['card'], fg=self.theme['fg'], font=self.fonts['body'])
        l.grid(row=r, column=c, sticky='w', padx=5, pady=5)
        return l
    
    def entry(self, p, v, r, c):
        e = tk.Entry(p, bg=self.theme['input'], fg=self.theme['fg'], font=self.fonts['body'], relief='solid', bd=1)
        if v: e.insert(0, str(v))
        e.grid(row=r, column=c, sticky='ew', padx=5, pady=5)
        return e
    
    def combo(self, p, v, r, c):
        cb = ttk.Combobox(p, values=v, state='readonly', font=self.fonts['body'])
        cb.grid(row=r, column=c, sticky='ew', padx=5, pady=5)
        return cb
    
    def btn(self, p, t, c, primary=False, success=False):
        bg = self.theme['primary'] if primary else (self.theme['success'] if success else self.theme['card'])
        fg = self.theme['primary_fg'] if (primary or success) else self.theme['fg']
        b = tk.Button(p, text=t, command=c, bg=bg, fg=fg, font=self.fonts['bold'], relief='flat')
        return b

    # --- ACTIONS ---
    def change_language(self, e):
        self.language.set_language(self.lang_var.get())
        # Immediate refresh by rebuilding UI
        self.build_ui() 
        self.config.save_config(float(self.ent_capital.get()), float(self.ent_risk.get()), float(self.ent_fee.get()), self.cb_exchange.get(), self.cb_order.get(), self.current_theme)

    def toggle_theme(self):
        self.current_theme = 'dark' if self.current_theme == 'light' else 'light'
        self.build_ui()
        self.config.save_config(float(self.ent_capital.get()), float(self.ent_risk.get()), float(self.ent_fee.get()), self.cb_exchange.get(), self.cb_order.get(), self.current_theme)

    def fetch_price(self):
        def run():
            try:
                self.lbl_price.config(text="...")
                p = self.api_manager.get_price(self.cb_exchange.get(), self.cb_symbol.get())
                if p:
                    self.lbl_price.config(text=str(p))
                    self.ent_entry.delete(0, tk.END)
                    self.ent_entry.insert(0, str(p))
                else: self.lbl_price.config(text="Err")
            except: self.lbl_price.config(text="Err")
        threading.Thread(target=run).start()

    def calculate(self):
        try:
            ep = float(self.ent_entry.get())
            sl = float(self.ent_sl.get())
            cap = float(self.ent_capital.get())
            risk = float(self.ent_risk.get())
            fee = float(self.ent_fee.get())
            lev = float(self.ent_lev.get())
            pos = self.cb_pos.get()
            tps = [float(x.get()) for x in self.tp_entries if x.get()]
            
            if not tps: raise ValueError("No TP entered")
            
            risk_amt = cap * (risk/100)
            diff_pct = abs(ep - sl) / ep
            if diff_pct == 0: raise ValueError("SL equals Entry")
            
            pos_size = risk_amt / diff_pct
            qty = (pos_size * lev) / ep
            
            out = f"--- {self.cb_symbol.get()} ({pos}) ---\n"
            out += f"Size: {pos_size:,.2f}$ | Qty: {qty:.4f}\n"
            out += f"Risk: {risk_amt:.2f}$ | Lev: {lev}x\n"
            
            for i, tp in enumerate(tps):
                pnl = abs(ep - tp)/ep * pos_size * lev
                out += f"TP{i+1}: {tp} -> +{pnl:.2f}$\n"
            
            self.txt_res.insert('1.0', out + "\n")
            
            self.history.add_trade({'date': datetime.now().strftime('%Y-%m-%d %H:%M'), 'symbol': self.cb_symbol.get(), 'type': pos, 'entry': ep, 'sl': sl, 'pnl': pnl})
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def save_main_config(self):
        self.config.save_config(float(self.ent_capital.get()), float(self.ent_risk.get()), float(self.ent_fee.get()), self.cb_exchange.get(), self.cb_order.get(), self.current_theme)
        messagebox.showinfo("Saved", "Settings saved!")

    def export_current(self):
        f = filedialog.asksaveasfilename(defaultextension=".txt")
        if f: 
            with open(f, 'w', encoding='utf-8') as file: file.write(self.txt_res.get('1.0', tk.END))

    def check_update(self):
        try:
            info = self.updater.check_for_update()
            if info.get('available'):
                if messagebox.askyesno("Update", f"New version v{info['latest']} available.\nUpdate now?"):
                    res = self.updater.update_to_latest()
                    if res.get('success'):
                        messagebox.showinfo("Success", "Update installed. Please restart application.")
                        self.root.destroy()
                    else:
                        messagebox.showerror("Error", f"Update failed: {res.get('message')}")
            else:
                messagebox.showinfo("Update", "You are up to date.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # --- SUB WINDOWS ---
    def open_settings(self):
        w = tk.Toplevel(self.root)
        w.title(self.language.get('settings'))
        w.geometry("500x400")
        w.configure(bg=self.theme['bg'])
        tk.Label(w, text="API Keys Config", font=self.fonts['h2'], bg=self.theme['bg'], fg=self.theme['fg']).pack(pady=10)
        # Simplified for brevity - full implementation would match style
        
    def open_history(self):
        w = tk.Toplevel(self.root)
        w.title(self.language.get('history'))
        w.geometry("600x400")
        cols = ('Date', 'Symbol', 'Type', 'Entry', 'PnL')
        tv = ttk.Treeview(w, columns=cols, show='headings')
        for c in cols: tv.heading(c, text=c)
        tv.pack(fill='both', expand=True)
        for t in self.history.trades:
            tv.insert('', 'end', values=(t.get('date'), t.get('symbol'), t.get('type'), t.get('entry'), t.get('pnl')))

    def open_charts(self):
        w = tk.Toplevel(self.root)
        w.title(self.language.get('charts'))
        w.geometry("600x400")
        c = tk.Canvas(w, bg='white')
        c.pack(fill='both', expand=True)
        trades = self.history.trades
        if not trades: 
            c.create_text(300, 200, text="No Data")
            return
        # Simple PnL curve
        data = [float(t.get('pnl', 0)) for t in trades]
        # ... drawing logic ...
        c.create_text(300, 200, text=f"PnL Chart: {len(data)} trades")

    def on_close(self):
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = CryptoTradingCalculator(root)
    root.mainloop()
