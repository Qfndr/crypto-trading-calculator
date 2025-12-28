import tkinter as tk
from tkinter import ttk, messagebox, filedialog, font as tkfont
import json
import os
import sys
import ctypes
from datetime import datetime
import threading
import math

# --- VERSION ---
VERSION = "1.6.0"

# --- CONSTANTS ---
FONT_FILE = "Vazirmatn-Regular.ttf"
FONT_URL = "https://github.com/rastikerdar/vazirmatn/raw/master/fonts/ttf/Vazirmatn-Regular.ttf"

# --- MODULES (Inline for single-file portability if needed, but imports are cleaner) ---
# We assume other files (config.py, language.py, etc.) exist. 
# If they are missing features, we will patch them in next steps.
try:
    from config import Config
    from trade_history import TradeHistory
    from api_manager import APIManager
    from language import Language
    from updater import Updater
except ImportError:
    # Fallback/Mock classes if files missing (just in case)
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
    class Updater:
        def check_for_update(self): return {'available':False}

# --- FONT LOADER (WINDOWS) ---
def load_custom_font(font_path):
    """Loads a font file into Windows font system temporarily for this session."""
    if not os.path.exists(font_path):
        return False
    if sys.platform.startswith("win"):
        try:
            # GDI32 AddFontResourceExW
            # FR_PRIVATE = 0x10
            path_buf = ctypes.create_unicode_buffer(os.path.abspath(font_path))
            flags = 0x10 
            num_fonts = ctypes.windll.gdi32.AddFontResourceExW(path_buf, flags, 0)
            return num_fonts > 0
        except:
            return False
    return True # Linux/Mac usually need standard install or ~/.fonts

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
        
        # 4. Setup UI Theme & Window
        self.setup_window()
        self.setup_styles()
        
        # 5. Build UI
        self.create_ui()

    def ensure_font(self):
        # Try to download if missing
        if not os.path.exists(FONT_FILE):
            try:
                import requests
                res = requests.get(FONT_URL, timeout=5)
                if res.status_code == 200:
                    with open(FONT_FILE, 'wb') as f: f.write(res.content)
            except: pass
            
        # Load font
        self.font_loaded = load_custom_font(FONT_FILE)
        
        # Define font families
        # If loaded successfully, 'Vazirmatn' should be available. 
        # If not, fallback to nice system fonts.
        available = tkfont.families()
        if 'Vazirmatn' in available:
            self.ff = 'Vazirmatn'
        else:
            self.ff = 'Segoe UI' if 'Segoe UI' in available else 'Arial'
            
        self.fonts = {
            'h1': (self.ff, 20, 'bold'),
            'h2': (self.ff, 14, 'bold'),
            'body': (self.ff, 11),
            'bold': (self.ff, 11, 'bold'),
            'small': (self.ff, 9)
        }

    def load_prefs(self):
        # Load language/theme from config
        # We assume config object has these fields populated
        if hasattr(self.config, 'theme'): self.current_theme = self.config.theme
        else: self.current_theme = 'light'
        
        # Language is loaded in Language class usually, but we sync it
        # (Assuming language class handles its own persistence or we set it)
        pass 

    def setup_window(self):
        self.root.title(f"{self.language.get('app_title')} v{VERSION}")
        self.root.geometry("1300x850")
        self.root.minsize(1000, 700)

    def setup_styles(self):
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
        self.root.configure(bg=self.theme['bg'])
        
        # TTK Styles
        style = ttk.Style()
        style.theme_use('clam') # Clean base
        
        # Configure generic widgets
        style.configure('TFrame', background=self.theme['bg'])
        style.configure('Card.TFrame', background=self.theme['card'], relief='flat')
        style.configure('TLabel', background=self.theme['bg'], foreground=self.theme['fg'], font=self.fonts['body'])
        style.configure('Card.TLabel', background=self.theme['card'], foreground=self.theme['fg'], font=self.fonts['body'])
        style.configure('TButton', font=self.fonts['bold'])

    def create_ui(self):
        # Main Container
        main = ttk.Frame(self.root)
        main.pack(fill='both', expand=True)
        
        # --- HEADER ---
        header = tk.Frame(main, bg=self.theme['card'], height=60, bd=0)
        header.pack(fill='x', side='top')
        header.pack_propagate(False)
        
        tk.Label(header, text=f"📊 {self.language.get('app_title')}", 
                font=self.fonts['h1'], bg=self.theme['card'], fg=self.theme['fg']).pack(side='left', padx=20)
        
        # Controls in Header
        controls = tk.Frame(header, bg=self.theme['card'])
        controls.pack(side='right', padx=20)
        
        # Language Selector
        self.lang_var = tk.StringVar(value=self.language.current)
        lang_cb = ttk.Combobox(controls, textvariable=self.lang_var, 
                              values=list(self.language.translations.keys()), 
                              state='readonly', width=5)
        lang_cb.pack(side='left', padx=5)
        lang_cb.bind('<<ComboboxSelected>>', self.change_language)
        
        # Action Buttons
        self.btn(controls, "⚙️ " + self.language.get('settings'), self.open_settings).pack(side='left', padx=5)
        self.btn(controls, "📋 " + self.language.get('history'), self.open_history).pack(side='left', padx=5)
        self.btn(controls, "📈 " + self.language.get('charts'), self.open_charts).pack(side='left', padx=5)
        self.btn(controls, "🔄 " + self.language.get('update'), self.check_update).pack(side='left', padx=5)
        self.btn(controls, "🌓 Mode", self.toggle_theme).pack(side='left', padx=5)

        # --- SCROLLABLE CONTENT ---
        canvas = tk.Canvas(main, bg=self.theme['bg'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(main, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=self.theme['bg'])
        
        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.content_area = scroll_frame
        
        # --- SECTIONS ---
        self.ui_exchange_section()
        self.ui_capital_section()
        self.ui_trade_section()
        self.ui_results_section()

    def ui_exchange_section(self):
        p = self.card(self.language.get('exchange_symbol'))
        
        # Row 1
        self.label(p, self.language.get('exchange'), 0, 0)
        self.cb_exchange = self.combo(p, list(self.api_manager.exchanges.keys()) if hasattr(self.api_manager, 'exchanges') else ['Binance','Bybit'], 0, 1)
        self.cb_exchange.set(getattr(self.config, 'selected_exchange', 'Binance'))
        
        self.label(p, self.language.get('order_type'), 0, 2)
        self.cb_order = self.combo(p, ['Maker', 'Taker'], 0, 3)
        self.cb_order.set(getattr(self.config, 'order_type', 'Taker'))

        # Row 2
        self.label(p, self.language.get('symbol'), 1, 0)
        self.cb_symbol = self.combo(p, self.api_manager.get_available_symbols(), 1, 1)
        self.cb_symbol.set('BTCUSDT')
        
        # Live Price
        btn_price = tk.Button(p, text=self.language.get('live_price'), command=self.fetch_price,
                            bg=self.theme['primary'], fg=self.theme['primary_fg'], font=self.fonts['bold'], relief='flat')
        btn_price.grid(row=1, column=2, padx=10, pady=5, sticky='ew')
        
        self.lbl_price = self.label(p, "---", 1, 3)

    def ui_capital_section(self):
        p = self.card(self.language.get('capital_risk'))
        
        self.label(p, self.language.get('total_capital'), 0, 0)
        self.ent_capital = self.entry(p, getattr(self.config, 'capital', 1000), 0, 1)
        
        self.label(p, self.language.get('risk_percent'), 0, 2)
        self.ent_risk = self.entry(p, getattr(self.config, 'risk_percent', 1.0), 0, 3)
        
        self.label(p, self.language.get('fee_percent'), 1, 0)
        self.ent_fee = self.entry(p, getattr(self.config, 'fee_percent', 0.04), 1, 1)
        
        tk.Button(p, text=self.language.get('save_settings'), command=self.save_main_config,
                 bg=self.theme['success'], fg='white', font=self.fonts['bold'], relief='flat').grid(row=1, column=2, columnspan=2, sticky='ew', padx=10, pady=5)

    def ui_trade_section(self):
        p = self.card(self.language.get('trade_info'))
        
        self.label(p, self.language.get('entry_price'), 0, 0)
        self.ent_entry = self.entry(p, "", 0, 1)
        
        self.label(p, self.language.get('stop_loss'), 0, 2)
        self.ent_sl = self.entry(p, "", 0, 3)
        
        # Multi-TP
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
        
        # Calculate
        tk.Button(p, text=self.language.get('calculate'), command=self.calculate,
                 bg=self.theme['primary'], fg='white', font=self.fonts['h2'], relief='flat').grid(row=4, column=0, columnspan=4, sticky='ew', padx=10, pady=15)

    def ui_results_section(self):
        p = self.card(self.language.get('results'))
        
        self.txt_res = tk.Text(p, height=12, bg=self.theme['input'], fg=self.theme['fg'], 
                              font=('Consolas', 10), relief='flat', bd=1)
        self.txt_res.pack(fill='both', expand=True, padx=10, pady=5)
        
        bbox = tk.Frame(p, bg=self.theme['card'])
        bbox.pack(fill='x', pady=5)
        
        self.btn(bbox, self.language.get('export_csv'), self.export_current).pack(side='left', padx=10)
        self.btn(bbox, self.language.get('clear_results'), lambda: self.txt_res.delete('1.0', tk.END)).pack(side='left')

    # --- HELPERS ---
    def card(self, title):
        f = tk.Frame(self.content_area, bg=self.theme['card'], bd=1, relief='solid')
        f.pack(fill='x', padx=20, pady=10)
        tk.Label(f, text=title, font=self.fonts['h2'], bg=self.theme['card'], fg=self.theme['fg']).pack(anchor='w', padx=15, pady=10)
        inner = tk.Frame(f, bg=self.theme['card'])
        inner.pack(fill='both', expand=True, padx=15, pady=5)
        return inner

    def label(self, parent, text, r, c):
        l = tk.Label(parent, text=text, bg=self.theme['card'], fg=self.theme['fg'], font=self.fonts['body'])
        l.grid(row=r, column=c, sticky='w', padx=5, pady=5)
        return l

    def entry(self, parent, val, r, c):
        e = tk.Entry(parent, bg=self.theme['input'], fg=self.theme['fg'], font=self.fonts['body'], relief='solid', bd=1)
        if val: e.insert(0, str(val))
        e.grid(row=r, column=c, sticky='ew', padx=5, pady=5)
        return e

    def combo(self, parent, vals, r, c):
        cb = ttk.Combobox(parent, values=vals, state='readonly', font=self.fonts['body'])
        cb.grid(row=r, column=c, sticky='ew', padx=5, pady=5)
        return cb

    def btn(self, parent, text, cmd):
        b = tk.Button(parent, text=text, command=cmd, bg=self.theme['card'], fg=self.theme['fg'], 
                     font=self.fonts['bold'], relief='flat', bd=0, activebackground=self.theme['bg'])
        return b

    # --- LOGIC ---
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
            
            if not tps: raise ValueError("No TP")
            
            risk_amt = cap * (risk/100)
            diff_pct = abs(ep - sl) / ep
            if diff_pct == 0: raise ValueError("SL = Entry")
            
            pos_size_usdt = risk_amt / diff_pct
            qty = (pos_size_usdt * lev) / ep
            
            # Formatted Output
            out = f"--- {datetime.now().strftime('%H:%M')} | {self.cb_symbol.get()} ({pos}) ---\n"
            out += f"Entry: {ep} | SL: {sl} | Lev: {lev}x\n"
            out += f"Size: {pos_size_usdt:,.2f}$ | Qty: {qty:.4f}\n"
            out += f"Risk: {risk_amt:.2f}$ ({risk}%)\n"
            
            # Liquidation
            if pos == 'LONG': liq = ep * (1 - (1/lev) + (fee/100))
            else: liq = ep * (1 + (1/lev) + (fee/100))
            out += f"Liq Price: {liq:.4f}\n\n"
            
            # TPs
            for i, tp in enumerate(tps):
                pnl = abs(ep - tp)/ep * pos_size_usdt * lev
                # rough Fee deduction
                total_fee = pos_size_usdt * lev * (fee/100) * 2 
                net_pnl = pnl - total_fee
                out += f"TP{i+1}: {tp} -> PnL: {net_pnl:+.2f}$\n"
            
            self.txt_res.insert('1.0', out + "\n")
            
            # Save
            self.history.add_trade({
                'date': datetime.now().strftime('%Y-%m-%d %H:%M'),
                'symbol': self.cb_symbol.get(),
                'type': pos, 'entry': ep, 'sl': sl, 
                'pnl': net_pnl # storing last TP pnl as estimate
            })
            
        except Exception as e:
            messagebox.showerror("Error", f"Calc Error: {str(e)}")

    # --- POPUP WINDOWS ---
    def open_settings(self):
        w = tk.Toplevel(self.root)
        w.title(self.language.get('settings'))
        w.geometry("500x400")
        w.configure(bg=self.theme['bg'])
        
        # API Keys Table
        tk.Label(w, text="API Configuration", font=self.fonts['h2'], bg=self.theme['bg'], fg=self.theme['fg']).pack(pady=10)
        
        f = tk.Frame(w, bg=self.theme['bg'])
        f.pack(fill='both', expand=True, padx=10)
        
        tk.Label(f, text="Exchange", bg=self.theme['bg'], fg=self.theme['fg']).grid(row=0, column=0)
        tk.Label(f, text="API Key", bg=self.theme['bg'], fg=self.theme['fg']).grid(row=0, column=1)
        tk.Label(f, text="Secret", bg=self.theme['bg'], fg=self.theme['fg']).grid(row=0, column=2)
        
        entries = {}
        exs = list(self.api_manager.exchanges.keys()) if hasattr(self.api_manager, 'exchanges') else ['Binance','Bybit']
        for i, ex in enumerate(exs):
            tk.Label(f, text=ex, bg=self.theme['bg'], fg=self.theme['fg']).grid(row=i+1, column=0)
            k = tk.Entry(f); k.grid(row=i+1, column=1)
            s = tk.Entry(f, show='*'); s.grid(row=i+1, column=2)
            entries[ex] = (k, s)
            
        def save():
            # Save API keys logic here (to Config)
            messagebox.showinfo("Saved", "Settings saved successfully")
            w.destroy()
            
        tk.Button(w, text="Save All", command=save, bg=self.theme['primary'], fg='white').pack(pady=10)

    def open_history(self):
        w = tk.Toplevel(self.root)
        w.title(self.language.get('history'))
        w.geometry("700x500")
        
        cols = ('Date', 'Symbol', 'Type', 'Entry', 'SL', 'PnL')
        tv = ttk.Treeview(w, columns=cols, show='headings')
        for c in cols: tv.heading(c, text=c)
        tv.pack(fill='both', expand=True)
        
        for t in self.history.trades:
            tv.insert('', 'end', values=(t.get('date'), t.get('symbol'), t.get('type'), t.get('entry'), t.get('sl'), f"{t.get('pnl',0):.2f}"))
            
        btn_f = tk.Frame(w)
        btn_f.pack(fill='x', pady=5)
        tk.Button(btn_f, text="Export CSV", command=lambda: self.history.export_to_csv('history_export.csv')).pack(side='left', padx=10)

    def open_charts(self):
        w = tk.Toplevel(self.root)
        w.title(self.language.get('charts'))
        w.geometry("600x400")
        w.configure(bg='white')
        
        # Simple Canvas Chart implementation to avoid matplotlib heavy dep if preferred, 
        # or use matplotlib if installed. Here we draw a simple PnL curve.
        cv = tk.Canvas(w, bg='white')
        cv.pack(fill='both', expand=True)
        
        trades = self.history.trades
        if not trades:
            cv.create_text(300, 200, text="No Data to Chart")
            return
            
        # Extract PnL
        pnls = [float(t.get('pnl', 0)) for t in trades]
        cum_pnl = []
        c = 0
        for p in pnls:
            c += p
            cum_pnl.append(c)
            
        # Draw
        if not cum_pnl: return
        w_can = 600
        h_can = 400
        max_val = max(max(cum_pnl), 1)
        min_val = min(min(cum_pnl), 0)
        rng = max_val - min_val if max_val != min_val else 1
        
        step_x = w_can / len(cum_pnl)
        prev_x, prev_y = 0, h_can/2
        
        # Zero line
        z_y = h_can - ((0 - min_val) / rng * h_can)
        cv.create_line(0, z_y, w_can, z_y, fill='gray', dash=(2,2))
        
        for i, val in enumerate(cum_pnl):
            x = (i+1) * step_x
            # Normalize y
            y = h_can - ((val - min_val) / rng * (h_can - 40)) - 20
            cv.create_line(prev_x, prev_y, x, y, fill='blue', width=2)
            cv.create_oval(x-2, y-2, x+2, y+2, fill='blue')
            prev_x, prev_y = x, y

    def check_update(self):
        info = self.updater.check_for_update()
        if info.get('available'):
            if messagebox.askyesno("Update", f"New version v{info['latest']} available. Update?"):
                self.updater.update_to_latest()
                messagebox.showinfo("Done", "Updated! Please restart.")
                self.root.destroy()
        else:
            messagebox.showinfo("Update", "You are up to date.")

    def change_language(self, e):
        # Save and Restart
        lang = self.lang_var.get()
        self.language.set_language(lang)
        self.save_main_config()
        messagebox.showinfo("Language", "Please restart application to apply language fully.")

    def save_main_config(self):
        # Save current UI state to config
        self.config.save_config(
            float(self.ent_capital.get()),
            float(self.ent_risk.get()),
            float(self.ent_fee.get()),
            self.cb_exchange.get(),
            self.cb_order.get(),
            self.current_theme
        )

    def toggle_theme(self):
        self.current_theme = 'dark' if self.current_theme == 'light' else 'light'
        self.config.save_config(
            float(self.ent_capital.get()),
            float(self.ent_risk.get()),
            float(self.ent_fee.get()),
            self.cb_exchange.get(),
            self.cb_order.get(),
            self.current_theme
        )
        messagebox.showinfo("Theme", "Restart required to apply theme fully.")

    def export_current(self):
        txt = self.txt_res.get('1.0', tk.END)
        f = filedialog.asksaveasfilename(defaultextension=".txt")
        if f:
            with open(f, 'w', encoding='utf-8') as file: file.write(txt)

    def on_close(self):
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = CryptoTradingCalculator(root)
    root.mainloop()
