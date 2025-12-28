import tkinter as tk
from tkinter import ttk, messagebox, filedialog, font as tkfont
import os
import sys
import ctypes
from datetime import datetime
import threading
import requests
import time

VERSION = "1.6.2"

FONT_FILE = "Vazirmatn-Regular.ttf"
FONT_URLS = [
    "https://raw.githubusercontent.com/rastikerdar/vazirmatn/master/fonts/ttf/Vazirmatn-Regular.ttf",
    "https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/fonts/ttf/Vazirmatn-Regular.ttf",
]

# --- MODULES ---
try:
    from config import Config
    from trade_history import TradeHistory
    from api_manager import APIManager
    from language import Language
    from updater import Updater
except Exception:
    class Config:
        def __init__(self): self.data={}
        def load_config(self): return {}
        def save_config(self,*a,**k): return True
        def get_api_credentials(self, ex): return {'api_key':'','api_secret':''}
        def set_api_credentials(self, ex, k, s): return True
    class TradeHistory:
        def __init__(self): self.trades=[]
        def add_trade(self, t): pass
    class APIManager:
        exchanges={}
        def get_available_symbols(self): return []
        def get_price(self, e, s): return 0.0
    class Language:
        def __init__(self): self.current='fa'; self.translations={'fa':{}}
        def get(self, k): return k
        def set_language(self, l): pass
    class Updater:
        def __init__(self, v): self.current_version=v
        def check_for_update(self): return {'available':False}
        def update_to_latest(self): return {'success':False}

def _load_custom_font_windows(font_path: str) -> bool:
    if not sys.platform.startswith('win'): return False
    try:
        path_buf = ctypes.create_unicode_buffer(os.path.abspath(font_path))
        flags = 0x10
        ctypes.windll.gdi32.AddFontResourceExW(path_buf, flags, 0)
        return True
    except: return False

def _download_font_to_root_async(cb=None):
    if os.path.exists(FONT_FILE):
        if cb: cb('font_downloaded')
        return
    def run():
        for url in FONT_URLS:
            try:
                r = requests.get(url, timeout=10, stream=True)
                if r.status_code==200:
                    with open(FONT_FILE, 'wb') as f:
                        for chunk in r.iter_content(64*1024):
                            if chunk: f.write(chunk)
                    if cb: cb('font_downloaded')
                    return
            except: continue
        if cb: cb('font_failed')
    threading.Thread(target=run, daemon=True).start()

class CryptoTradingCalculator:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        self.config = Config()
        self.language = Language()
        self.history = TradeHistory()
        self.api_manager = APIManager()
        self.updater = Updater(VERSION)

        try:
            if getattr(self.config, 'language', None):
                self.language.set_language(self.config.language)
        except: pass
        self.current_theme = getattr(self.config, 'theme', 'light')

        _download_font_to_root_async(self._on_font_status)
        self._setup_fonts()
        
        self.root.title(f"{self.language.get('app_title')} v{VERSION}")
        self.root.geometry("1300x850")
        self.root.minsize(1000, 700)
        
        self.build_ui()

    def _on_font_status(self, st):
        def ui():
            if st=='font_downloaded':
                self._setup_fonts()
                self.build_ui()
        try: self.root.after(0, ui)
        except: pass

    def _setup_fonts(self):
        if os.path.exists(FONT_FILE):
            _load_custom_font_windows(FONT_FILE)
        fams = tkfont.families()
        self.ff = 'Vazirmatn' if 'Vazirmatn' in fams else ('Segoe UI' if 'Segoe UI' in fams else 'Arial')
        self.fonts = {
            'h1': (self.ff, 20, 'bold'),
            'h2': (self.ff, 14, 'bold'),
            'body': (self.ff, 11),
            'bold': (self.ff, 11, 'bold'),
        }

    def _define_colors(self):
        self.colors = {
            'light': {'bg': '#f3f4f6', 'fg': '#1f2937', 'card': '#ffffff', 'primary': '#2563eb', 'primary_fg': '#ffffff', 'success': '#10b981', 'input': '#ffffff'},
            'dark': {'bg': '#111827', 'fg': '#f9fafb', 'card': '#1f2937', 'primary': '#3b82f6', 'primary_fg': '#ffffff', 'success': '#34d399', 'input': '#374151'},
        }
        self.theme = self.colors.get(self.current_theme, self.colors['light'])

    def build_ui(self):
        for w in self.root.winfo_children(): w.destroy()
        self._define_colors()
        self.root.configure(bg=self.theme['bg'])
        
        # Style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background=self.theme['bg'])
        style.configure('TLabel', background=self.theme['bg'], foreground=self.theme['fg'], font=self.fonts['body'])
        style.configure('Card.TFrame', background=self.theme['card'])
        style.configure('Treeview', background=self.theme['input'], foreground=self.theme['fg'], fieldbackground=self.theme['input'])
        style.configure('Treeview.Heading', font=self.fonts['bold'])

        # Header
        h = tk.Frame(self.root, bg=self.theme['card'], height=60)
        h.pack(fill='x'); h.pack_propagate(False)
        tk.Label(h, text=f"📊 {self.language.get('app_title')}", font=self.fonts['h1'], bg=self.theme['card'], fg=self.theme['fg']).pack(side='left', padx=20)
        
        c = tk.Frame(h, bg=self.theme['card'])
        c.pack(side='right', padx=20)
        
        self.lang_var = tk.StringVar(value=self.language.current)
        l = ttk.Combobox(c, textvariable=self.lang_var, values=list(self.language.translations.keys()), state='readonly', width=5)
        l.pack(side='left', padx=5); l.bind('<<ComboboxSelected>>', self.change_language)

        self._btn(c, "⚙️ "+self.language.get('settings'), self.open_settings).pack(side='left', padx=5)
        self._btn(c, "📋 "+self.language.get('history'), self.open_history).pack(side='left', padx=5)
        self._btn(c, "📈 "+self.language.get('charts'), self.open_charts).pack(side='left', padx=5)
        self._btn(c, "🔄 "+self.language.get('update'), self.check_update).pack(side='left', padx=5)
        self._btn(c, "🌓", self.toggle_theme).pack(side='left', padx=5)

        # Body
        body = tk.Frame(self.root, bg=self.theme['bg'])
        body.pack(fill='both', expand=True)
        self._build_cards(body)

    def _build_cards(self, parent):
        # Exch
        p1 = self._card(parent, self.language.get('exchange_symbol'))
        tk.Label(p1, text=self.language.get('exchange'), bg=self.theme['card'], fg=self.theme['fg'], font=self.fonts['body']).grid(row=0,column=0,padx=5,pady=5)
        self.cb_ex = ttk.Combobox(p1, values=list(getattr(self.api_manager,'exchanges',{}).keys()), state='readonly')
        self.cb_ex.grid(row=0,column=1,sticky='ew',padx=5)
        self.cb_ex.set(getattr(self.config,'selected_exchange','Binance'))
        
        tk.Label(p1, text=self.language.get('symbol'), bg=self.theme['card'], fg=self.theme['fg'], font=self.fonts['body']).grid(row=1,column=0,padx=5,pady=5)
        self.cb_sym = ttk.Combobox(p1, values=self.api_manager.get_available_symbols(), state='readonly')
        self.cb_sym.grid(row=1,column=1,sticky='ew',padx=5)
        self.cb_sym.set('BTCUSDT')
        
        self.lbl_pr = tk.Label(p1, text='---', bg=self.theme['card'], fg=self.theme['fg'], font=self.fonts['bold'])
        self.lbl_pr.grid(row=1,column=2,padx=5)
        self._btn(p1, self.language.get('live_price'), self.fetch_price, primary=True).grid(row=1,column=3,padx=5)

        # Cap
        p2 = self._card(parent, self.language.get('capital_risk'))
        self.ent_cap = self._l_entry(p2, self.language.get('total_capital'), getattr(self.config,'capital',1000), 0)
        self.ent_risk = self._l_entry(p2, self.language.get('risk_percent'), getattr(self.config,'risk_percent',1.0), 1)
        self.ent_fee = self._l_entry(p2, self.language.get('fee_percent'), getattr(self.config,'fee_percent',0.04), 2)
        self._btn(p2, self.language.get('save_settings'), self.save_main_config, success=True).grid(row=3,column=0,columnspan=2,sticky='ew',padx=5,pady=10)

        # Trade
        p3 = self._card(parent, self.language.get('trade_info'))
        self.ent_ep = self._l_entry(p3, self.language.get('entry_price'), '', 0)
        self.ent_sl = self._l_entry(p3, self.language.get('stop_loss'), '', 1)
        
        tk.Label(p3, text=self.language.get('position_type'), bg=self.theme['card'], fg=self.theme['fg'], font=self.fonts['body']).grid(row=2,column=0,padx=5)
        self.cb_pos = ttk.Combobox(p3, values=['LONG','SHORT'], state='readonly')
        self.cb_pos.grid(row=2,column=1,sticky='ew',padx=5); self.cb_pos.set('LONG')
        
        tk.Label(p3, text=self.language.get('leverage'), bg=self.theme['card'], fg=self.theme['fg'], font=self.fonts['body']).grid(row=3,column=0,padx=5)
        self.ent_lev = tk.Entry(p3); self.ent_lev.grid(row=3,column=1,sticky='ew',padx=5); self.ent_lev.insert(0,'10')
        
        self.tps = []
        for i in range(3):
            tk.Label(p3, text=f"TP{i+1}", bg=self.theme['card'], fg=self.theme['fg'], font=self.fonts['body']).grid(row=4+i,column=0,padx=5)
            e = tk.Entry(p3); e.grid(row=4+i,column=1,sticky='ew',padx=5); self.tps.append(e)
            
        self._btn(p3, self.language.get('calculate'), self.calc, primary=True).grid(row=7,column=0,columnspan=2,sticky='ew',padx=5,pady=10)

        # Res
        p4 = self._card(parent, self.language.get('results'))
        self.txt = tk.Text(p4, height=10, bg=self.theme['input'], fg=self.theme['fg'], font=('Consolas',10), relief='flat')
        self.txt.pack(fill='both', expand=True, padx=10, pady=5)

    def _card(self, p, t):
        o = tk.Frame(p, bg=self.theme['card'], bd=1, relief='solid')
        o.pack(fill='x', padx=20, pady=10)
        tk.Label(o, text=t, bg=self.theme['card'], fg=self.theme['fg'], font=self.fonts['h2']).pack(anchor='w', padx=10, pady=10)
        i = tk.Frame(o, bg=self.theme['card'])
        i.pack(fill='x', padx=10, pady=5)
        return i
    
    def _l_entry(self, p, l, v, r):
        tk.Label(p, text=l, bg=self.theme['card'], fg=self.theme['fg'], font=self.fonts['body']).grid(row=r,column=0,sticky='w',padx=5,pady=5)
        e = tk.Entry(p)
        e.grid(row=r,column=1,sticky='ew',padx=5,pady=5)
        if v!='': e.insert(0, str(v))
        return e
    
    def _btn(self, p, t, c, primary=False, success=False):
        bg = self.theme['primary'] if primary else (self.theme['success'] if success else self.theme['card'])
        fg = self.theme['primary_fg'] if (primary or success) else self.theme['fg']
        return tk.Button(p, text=t, command=c, bg=bg, fg=fg, relief='flat', font=self.fonts['bold'])

    # Logic
    def change_language(self, _):
        self.language.set_language(self.lang_var.get())
        self.save_main_config(True)
        self.build_ui()
    
    def toggle_theme(self):
        self.current_theme = 'dark' if self.current_theme=='light' else 'light'
        self.save_main_config(True)
        self.build_ui()

    def save_main_config(self, silent=False):
        try:
            self.config.save_config(
                float(self.ent_cap.get()), float(self.ent_risk.get()), float(self.ent_fee.get()),
                self.cb_ex.get(), 'taker', self.current_theme, getattr(self.language,'current','fa')
            )
            if not silent: messagebox.showinfo('OK', self.language.get('saved'))
        except Exception as e:
            if not silent: messagebox.showerror('Error', str(e))

    def fetch_price(self):
        def r():
            try:
                self.lbl_pr.config(text='...')
                p = self.api_manager.get_price(self.cb_ex.get(), self.cb_sym.get())
                self.lbl_pr.config(text=str(p) if p else 'Err')
                if p:
                    self.ent_ep.delete(0, tk.END)
                    self.ent_ep.insert(0, str(p))
            except: self.lbl_pr.config(text='Err')
        threading.Thread(target=r, daemon=True).start()

    def calc(self):
        try:
            ep = float(self.ent_ep.get()); sl = float(self.ent_sl.get())
            cap = float(self.ent_cap.get()); risk = float(self.ent_risk.get())
            lev = float(self.ent_lev.get()); pos = self.cb_pos.get()
            tps = [float(x.get()) for x in self.tps if x.get().strip()]
            
            risk_amt = cap*(risk/100)
            diff = abs(ep-sl)/ep
            if diff==0: raise ValueError
            sz = risk_amt/diff; qty = (sz*lev)/ep
            
            out = f"{datetime.now().strftime('%H:%M')} | {pos}\n"
            out += f"Sz: {sz:.1f}$ | Qty: {qty:.4f}\n"
            for i,tp in enumerate(tps):
                pnl = abs(ep-tp)/ep * sz * lev
                out += f"TP{i+1}: {tp} -> {pnl:+.1f}$\n"
            self.txt.insert('1.0', out+'\n')
            self.history.add_trade({'date':datetime.now().strftime('%Y-%m-%d %H:%M'),'symbol':self.cb_sym.get(),'type':pos,'entry':ep,'sl':sl,'pnl':pnl})
        except Exception as e: messagebox.showerror('Err',str(e))

    # Windows (FIXED COLORS)
    def open_settings(self):
        w = tk.Toplevel(self.root)
        w.configure(bg=self.theme['bg']) # FIX
        w.title(self.language.get('settings')); w.geometry('600x400')
        
        tk.Label(w, text="API Keys", bg=self.theme['bg'], fg=self.theme['fg'], font=self.fonts['h2']).pack(pady=10)
        
        f = tk.Frame(w, bg=self.theme['bg'])
        f.pack(fill='both', expand=True, padx=10)
        
        # Simple list for API keys
        exs = list(getattr(self.api_manager,'exchanges',{}).keys())
        self._apis = {}
        for i, ex in enumerate(exs):
            tk.Label(f, text=ex, bg=self.theme['bg'], fg=self.theme['fg']).grid(row=i, column=0, padx=5, pady=2)
            k = tk.Entry(f); k.grid(row=i, column=1, padx=5); k.insert(0, self.config.get_api_credentials(ex).get('api_key',''))
            s = tk.Entry(f, show='*'); s.grid(row=i, column=2, padx=5); s.insert(0, self.config.get_api_credentials(ex).get('api_secret',''))
            self._apis[ex] = (k,s)
            
        def sv():
            for ex, (k,s) in self._apis.items(): self.config.set_api_credentials(ex, k.get(), s.get())
            messagebox.showinfo('OK', 'Saved')
            
        tk.Button(w, text='Save', command=sv, bg=self.theme['primary'], fg=self.theme['primary_fg']).pack(pady=10)

    def open_history(self):
        w = tk.Toplevel(self.root)
        w.configure(bg=self.theme['bg']) # FIX
        w.title(self.language.get('history')); w.geometry('700x400')
        
        cols=('Date','Symbol','Type','PnL')
        tv = ttk.Treeview(w, columns=cols, show='headings')
        for c in cols: tv.heading(c, text=c)
        tv.pack(fill='both', expand=True)
        for t in getattr(self.history,'trades',[]):
            tv.insert('','end',values=(t.get('date'),t.get('symbol'),t.get('type'),t.get('pnl')))

    def open_charts(self):
        w = tk.Toplevel(self.root)
        w.configure(bg=self.theme['bg']) # FIX
        w.title(self.language.get('charts')); w.geometry('600x400')
        c = tk.Canvas(w, bg='white') # Charts stay white/neutral usually, or match theme input color
        c.pack(fill='both', expand=True)
        c.create_text(300, 200, text="PnL Chart")

    def check_update(self):
        # Force refresh to bypass cache if possible, or assume updater handles it
        info = self.updater.check_for_update()
        if info['available']:
            if messagebox.askyesno('Update', f"New: v{info['latest']}\nUpdate?"):
                res = self.updater.update_to_latest()
                if res['success']: 
                    messagebox.showinfo('OK', 'Updated. Restart app.')
                    self.root.destroy()
                else: messagebox.showerror('Err', res.get('message'))
        else:
            if info.get('error'): messagebox.showwarning('Err', info['error'])
            else: messagebox.showinfo('OK', 'Up to date.')

    def on_close(self): self.root.destroy()

if __name__ == '__main__':
    root = tk.Tk()
    app = CryptoTradingCalculator(root)
    root.mainloop()
