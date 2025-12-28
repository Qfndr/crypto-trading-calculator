import tkinter as tk
from tkinter import ttk, messagebox, filedialog, font as tkfont
import os
import sys
import ctypes
from datetime import datetime
import threading
import requests

VERSION = "1.6.1"

FONT_FILE = "Vazirmatn-Regular.ttf"
FONT_URLS = [
    # Primary (GitHub raw)
    "https://raw.githubusercontent.com/rastikerdar/vazirmatn/master/fonts/ttf/Vazirmatn-Regular.ttf",
    # Mirror (jsDelivr)
    "https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/fonts/ttf/Vazirmatn-Regular.ttf",
]

try:
    from config import Config
    from trade_history import TradeHistory
    from api_manager import APIManager
    from language import Language
    from updater import Updater
except Exception:
    # Minimal fallback so UI opens even if other modules are broken
    class Config:
        def __init__(self):
            self.capital=1000; self.risk_percent=1.0; self.fee_percent=0.04
            self.selected_exchange='Binance'; self.order_type='Taker'
            self.theme='light'; self.language='fa'; self.api_keys={}
        def save_config(self,*a,**k): return True
        def get_api_credentials(self, ex): return {'api_key':'','api_secret':''}
        def set_api_credentials(self, ex, k, s): return True
    class TradeHistory:
        def __init__(self): self.trades=[]
        def add_trade(self, t): self.trades.append(t)
        def export_to_csv(self, filename='trades_export.csv'):
            import csv
            if not self.trades: return False
            keys = self.trades[0].keys()
            with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
                w = csv.DictWriter(f, fieldnames=keys); w.writeheader(); w.writerows(self.trades)
            return True
    class APIManager:
        exchanges = {'Binance': {}, 'Bybit': {}, 'OKX': {}, 'KuCoin': {}, 'Gate.io': {}, 'Bitget': {}, 'MEXC': {}, 'CoinEx': {}}
        def get_available_symbols(self): return ['BTCUSDT','ETHUSDT']
        def get_price(self, e, s): return 0.0
    class Language:
        def __init__(self):
            self.current='fa'
            self.translations={'fa':{},'en':{},'tr':{},'ru':{},'ar':{},'hi':{},'zh':{},'ja':{},'fr':{},'it':{},'bg':{}}
        def get(self, k): return k
        def set_language(self, l): self.current=l
    class Updater:
        def __init__(self, current_version): self.current_version=current_version
        def check_for_update(self): return {'available': False, 'latest': self.current_version}
        def update_to_latest(self): return {'success': False, 'message': 'Updater unavailable'}


def _load_custom_font_windows(font_path: str) -> bool:
    """Load font into Windows font table for current process (FR_PRIVATE)."""
    if not sys.platform.startswith('win'):
        return False
    try:
        path_buf = ctypes.create_unicode_buffer(os.path.abspath(font_path))
        flags = 0x10  # FR_PRIVATE
        added = ctypes.windll.gdi32.AddFontResourceExW(path_buf, flags, 0)
        return added > 0
    except Exception:
        return False


def _download_font_to_root_async(status_callback=None):
    """Download font to project root without blocking UI."""
    if os.path.exists(FONT_FILE):
        return

    def run():
        for url in FONT_URLS:
            try:
                if status_callback:
                    status_callback("font_downloading")
                r = requests.get(url, timeout=15, stream=True)
                if r.status_code != 200:
                    continue
                with open(FONT_FILE, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=64 * 1024):
                        if chunk:
                            f.write(chunk)
                if status_callback:
                    status_callback("font_downloaded")
                return
            except Exception:
                continue
        if status_callback:
            status_callback("font_failed")

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

        # Apply saved language/theme (if supported)
        try:
            if getattr(self.config, 'language', None):
                self.language.set_language(self.config.language)
        except Exception:
            pass
        self.current_theme = getattr(self.config, 'theme', 'light')

        # Start font download (non-blocking) and load if available
        _download_font_to_root_async(self._on_font_status)
        self._setup_fonts()

        self.root.title(f"{self.language.get('app_title')} v{VERSION}")
        self.root.geometry("1300x850")
        self.root.minsize(1000, 700)

        self.build_ui()

    def _on_font_status(self, state: str):
        # Called from background thread; marshal to UI thread
        def ui():
            if state == 'font_downloaded':
                # Load font and rebuild UI for immediate apply
                self._setup_fonts(force_reload=True)
                self.build_ui()
            elif state == 'font_failed':
                # No blocking errors; just keep fallback fonts
                pass
        try:
            self.root.after(0, ui)
        except Exception:
            pass

    def _setup_fonts(self, force_reload=False):
        # If font exists, attempt to load
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
        for w in self.root.winfo_children():
            w.destroy()

        self._define_colors()
        self.root.configure(bg=self.theme['bg'])

        # Header
        header = tk.Frame(self.root, bg=self.theme['card'], height=60)
        header.pack(fill='x')
        header.pack_propagate(False)

        tk.Label(header, text=f"📊 {self.language.get('app_title')}", font=self.fonts['h1'], bg=self.theme['card'], fg=self.theme['fg']).pack(side='left', padx=20)

        controls = tk.Frame(header, bg=self.theme['card'])
        controls.pack(side='right', padx=20)

        self.lang_var = tk.StringVar(value=self.language.current)
        lang_cb = ttk.Combobox(controls, textvariable=self.lang_var, values=list(self.language.translations.keys()), state='readonly', width=6)
        lang_cb.pack(side='left', padx=5)
        lang_cb.bind('<<ComboboxSelected>>', self.change_language)

        self._btn(controls, "⚙️ " + self.language.get('settings'), self.open_settings).pack(side='left', padx=5)
        self._btn(controls, "📋 " + self.language.get('history'), self.open_history).pack(side='left', padx=5)
        self._btn(controls, "📈 " + self.language.get('charts'), self.open_charts).pack(side='left', padx=5)
        self._btn(controls, "🔄 " + self.language.get('update'), self.check_update).pack(side='left', padx=5)
        self._btn(controls, "🌓", self.toggle_theme).pack(side='left', padx=5)

        # Content
        body = tk.Frame(self.root, bg=self.theme['bg'])
        body.pack(fill='both', expand=True)

        self._build_main_cards(body)

    def _build_main_cards(self, parent):
        # Exchange & Symbol
        p = self._card(parent, self.language.get('exchange_symbol'))
        tk.Label(p, text=self.language.get('exchange'), bg=self.theme['card'], fg=self.theme['fg'], font=self.fonts['body']).grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.cb_exchange = ttk.Combobox(p, values=list(getattr(self.api_manager, 'exchanges', {'Binance': {}}).keys()), state='readonly')
        self.cb_exchange.grid(row=0, column=1, sticky='ew', padx=5, pady=5)
        self.cb_exchange.set(getattr(self.config, 'selected_exchange', 'Binance'))

        tk.Label(p, text=self.language.get('symbol'), bg=self.theme['card'], fg=self.theme['fg'], font=self.fonts['body']).grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.cb_symbol = ttk.Combobox(p, values=self.api_manager.get_available_symbols(), state='readonly')
        self.cb_symbol.grid(row=1, column=1, sticky='ew', padx=5, pady=5)
        self.cb_symbol.set('BTCUSDT')

        self.lbl_price = tk.Label(p, text='---', bg=self.theme['card'], fg=self.theme['fg'], font=self.fonts['bold'])
        self.lbl_price.grid(row=1, column=2, sticky='w', padx=5)
        self._btn(p, self.language.get('live_price'), self.fetch_price, primary=True).grid(row=1, column=3, sticky='ew', padx=5)

        # Capital & Risk
        p2 = self._card(parent, self.language.get('capital_risk'))
        self.ent_capital = self._labeled_entry(p2, self.language.get('total_capital'), getattr(self.config, 'capital', 1000), 0)
        self.ent_risk = self._labeled_entry(p2, self.language.get('risk_percent'), getattr(self.config, 'risk_percent', 1.0), 1)
        self.ent_fee = self._labeled_entry(p2, self.language.get('fee_percent'), getattr(self.config, 'fee_percent', 0.04), 2)
        self._btn(p2, self.language.get('save_settings'), self.save_main_config, success=True).grid(row=3, column=0, columnspan=2, sticky='ew', padx=5, pady=10)

        # Trade
        p3 = self._card(parent, self.language.get('trade_info'))
        self.ent_entry = self._labeled_entry(p3, self.language.get('entry_price'), '', 0)
        self.ent_sl = self._labeled_entry(p3, self.language.get('stop_loss'), '', 1)

        tk.Label(p3, text=self.language.get('position_type'), bg=self.theme['card'], fg=self.theme['fg'], font=self.fonts['body']).grid(row=2, column=0, sticky='w', padx=5, pady=5)
        self.cb_pos = ttk.Combobox(p3, values=['LONG', 'SHORT'], state='readonly')
        self.cb_pos.grid(row=2, column=1, sticky='ew', padx=5, pady=5)
        self.cb_pos.set('LONG')

        tk.Label(p3, text=self.language.get('leverage'), bg=self.theme['card'], fg=self.theme['fg'], font=self.fonts['body']).grid(row=3, column=0, sticky='w', padx=5, pady=5)
        self.ent_lev = tk.Entry(p3)
        self.ent_lev.grid(row=3, column=1, sticky='ew', padx=5, pady=5)
        self.ent_lev.insert(0, '10')

        self.tp_entries = []
        for i in range(3):
            tk.Label(p3, text=f"TP{i+1}", bg=self.theme['card'], fg=self.theme['fg'], font=self.fonts['body']).grid(row=4+i, column=0, sticky='w', padx=5, pady=5)
            e = tk.Entry(p3)
            e.grid(row=4+i, column=1, sticky='ew', padx=5, pady=5)
            self.tp_entries.append(e)

        self._btn(p3, self.language.get('calculate'), self.calculate, primary=True).grid(row=7, column=0, columnspan=2, sticky='ew', padx=5, pady=12)

        # Results
        p4 = self._card(parent, self.language.get('results'))
        self.txt_res = tk.Text(p4, height=10, bg=self.theme['input'], fg=self.theme['fg'], font=('Consolas', 10), relief='flat')
        self.txt_res.pack(fill='both', expand=True, padx=10, pady=8)

    def _card(self, parent, title):
        outer = tk.Frame(parent, bg=self.theme['card'], bd=1, relief='solid')
        outer.pack(fill='x', padx=20, pady=10)
        tk.Label(outer, text=title, bg=self.theme['card'], fg=self.theme['fg'], font=self.fonts['h2']).pack(anchor='w', padx=12, pady=10)
        inner = tk.Frame(outer, bg=self.theme['card'])
        inner.pack(fill='x', padx=12, pady=10)
        return inner

    def _labeled_entry(self, parent, label, value, row):
        tk.Label(parent, text=label, bg=self.theme['card'], fg=self.theme['fg'], font=self.fonts['body']).grid(row=row, column=0, sticky='w', padx=5, pady=5)
        e = tk.Entry(parent)
        e.grid(row=row, column=1, sticky='ew', padx=5, pady=5)
        if value != '':
            e.insert(0, str(value))
        return e

    def _btn(self, parent, text, cmd, primary=False, success=False):
        bg = self.theme['primary'] if primary else (self.theme['success'] if success else self.theme['card'])
        fg = self.theme['primary_fg'] if (primary or success) else self.theme['fg']
        return tk.Button(parent, text=text, command=cmd, bg=bg, fg=fg, relief='flat', font=self.fonts['bold'])

    # --- actions ---
    def change_language(self, _=None):
        self.language.set_language(self.lang_var.get())
        try:
            self.config.language = self.language.current
        except Exception:
            pass
        self.save_main_config(silent=True)
        self.build_ui()

    def toggle_theme(self):
        self.current_theme = 'dark' if self.current_theme == 'light' else 'light'
        try:
            self.config.theme = self.current_theme
        except Exception:
            pass
        self.save_main_config(silent=True)
        self.build_ui()

    def save_main_config(self, silent=False):
        try:
            self.config.save_config(
                float(self.ent_capital.get()),
                float(self.ent_risk.get()),
                float(self.ent_fee.get()),
                self.cb_exchange.get(),
                'taker',
                self.current_theme,
                language=getattr(self.language, 'current', 'fa')
            )
            if not silent:
                messagebox.showinfo("OK", self.language.get('saved'))
        except Exception as e:
            if not silent:
                messagebox.showerror("Error", str(e))

    def fetch_price(self):
        def run():
            try:
                self.lbl_price.config(text='...')
                p = self.api_manager.get_price(self.cb_exchange.get(), self.cb_symbol.get())
                self.lbl_price.config(text=str(p) if p else 'Err')
                if p:
                    self.ent_entry.delete(0, tk.END)
                    self.ent_entry.insert(0, str(p))
            except Exception:
                self.lbl_price.config(text='Err')
        threading.Thread(target=run, daemon=True).start()

    def calculate(self):
        try:
            ep = float(self.ent_entry.get())
            sl = float(self.ent_sl.get())
            cap = float(self.ent_capital.get())
            risk = float(self.ent_risk.get())
            lev = float(self.ent_lev.get())
            pos = self.cb_pos.get()
            tps = [float(x.get()) for x in self.tp_entries if x.get().strip()]
            if not tps:
                raise ValueError('No TP')

            risk_amt = cap * (risk/100)
            diff_pct = abs(ep - sl) / ep
            if diff_pct == 0:
                raise ValueError('SL=Entry')

            pos_size = risk_amt / diff_pct
            qty = (pos_size * lev) / ep

            out = f"{datetime.now().strftime('%Y-%m-%d %H:%M')} | {self.cb_symbol.get()} {pos}\n"
            out += f"Entry: {ep} | SL: {sl} | Lev: {lev}x\n"
            out += f"Size: {pos_size:,.2f}$ | Qty: {qty:.4f}\n"

            last_pnl = 0.0
            for i, tp in enumerate(tps):
                pnl = abs(ep - tp)/ep * pos_size * lev
                last_pnl = pnl
                out += f"TP{i+1}: {tp} -> PnL: {pnl:+.2f}$\n"

            out += "\n"
            self.txt_res.insert('1.0', out)

            self.history.add_trade({'date': datetime.now().strftime('%Y-%m-%d %H:%M'), 'symbol': self.cb_symbol.get(), 'type': pos, 'entry': ep, 'sl': sl, 'pnl': last_pnl})

        except Exception as e:
            messagebox.showerror('Error', str(e))

    # --- windows ---
    def open_settings(self):
        w = tk.Toplevel(self.root)
        w.title(self.language.get('settings'))
        w.geometry('780x520')
        w.configure(bg=self.theme['bg'])

        nb = ttk.Notebook(w)
        nb.pack(fill='both', expand=True, padx=10, pady=10)

        tab_api = tk.Frame(nb, bg=self.theme['bg'])
        tab_app = tk.Frame(nb, bg=self.theme['bg'])
        nb.add(tab_api, text='API Keys')
        nb.add(tab_app, text='App')

        # --- API TAB ---
        tk.Label(tab_api, text='API Keys / Secrets (per exchange)', bg=self.theme['bg'], fg=self.theme['fg'], font=self.fonts['h2']).pack(anchor='w', pady=8)

        holder = tk.Frame(tab_api, bg=self.theme['bg'])
        holder.pack(fill='both', expand=True)

        canvas = tk.Canvas(holder, bg=self.theme['bg'], highlightthickness=0)
        sb = ttk.Scrollbar(holder, orient='vertical', command=canvas.yview)
        frm = tk.Frame(canvas, bg=self.theme['bg'])
        frm.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.create_window((0, 0), window=frm, anchor='nw')
        canvas.configure(yscrollcommand=sb.set)
        canvas.pack(side='left', fill='both', expand=True)
        sb.pack(side='right', fill='y')

        tk.Label(frm, text='Exchange', bg=self.theme['bg'], fg=self.theme['fg'], font=self.fonts['bold']).grid(row=0, column=0, sticky='w', padx=5, pady=5)
        tk.Label(frm, text='API Key', bg=self.theme['bg'], fg=self.theme['fg'], font=self.fonts['bold']).grid(row=0, column=1, sticky='w', padx=5, pady=5)
        tk.Label(frm, text='Secret', bg=self.theme['bg'], fg=self.theme['fg'], font=self.fonts['bold']).grid(row=0, column=2, sticky='w', padx=5, pady=5)

        exchanges = list(getattr(self.api_manager, 'exchanges', {'Binance': {}}).keys())
        self._api_entries = {}
        for i, ex in enumerate(exchanges, start=1):
            tk.Label(frm, text=ex, bg=self.theme['bg'], fg=self.theme['fg'], font=self.fonts['body']).grid(row=i, column=0, sticky='w', padx=5, pady=4)

            cred = self.config.get_api_credentials(ex)
            e_key = tk.Entry(frm, width=40)
            e_key.grid(row=i, column=1, sticky='ew', padx=5, pady=4)
            e_key.insert(0, cred.get('api_key', ''))

            e_sec = tk.Entry(frm, width=40, show='*')
            e_sec.grid(row=i, column=2, sticky='ew', padx=5, pady=4)
            e_sec.insert(0, cred.get('api_secret', ''))

            self._api_entries[ex] = (e_key, e_sec)

        def save_api():
            for ex, (ek, es) in self._api_entries.items():
                self.config.set_api_credentials(ex, ek.get().strip(), es.get().strip())
            messagebox.showinfo('OK', 'API Keys saved')

        tk.Button(tab_api, text='Save API Keys', command=save_api, bg=self.theme['primary'], fg=self.theme['primary_fg'], relief='flat', font=self.fonts['bold']).pack(pady=10)

        # --- APP TAB ---
        tk.Label(tab_app, text='General Settings', bg=self.theme['bg'], fg=self.theme['fg'], font=self.fonts['h2']).pack(anchor='w', pady=8)
        tk.Label(tab_app, text='(Theme/Language are available in the top bar and are saved automatically)', bg=self.theme['bg'], fg=self.theme['fg'], font=self.fonts['body']).pack(anchor='w')

    def open_history(self):
        w = tk.Toplevel(self.root)
        w.title(self.language.get('history'))
        w.geometry('850x450')

        cols = ('Date', 'Symbol', 'Type', 'Entry', 'SL', 'PnL')
        tv = ttk.Treeview(w, columns=cols, show='headings')
        for c in cols:
            tv.heading(c, text=c)
            tv.column(c, width=120)
        tv.pack(fill='both', expand=True)

        for t in getattr(self.history, 'trades', []):
            tv.insert('', 'end', values=(t.get('date'), t.get('symbol'), t.get('type'), t.get('entry'), t.get('sl'), t.get('pnl')))

        def export_csv():
            f = filedialog.asksaveasfilename(defaultextension='.csv')
            if f:
                ok = self.history.export_to_csv(f)
                messagebox.showinfo('OK' if ok else 'Error', 'Exported' if ok else 'No data')

        tk.Button(w, text='Export CSV', command=export_csv).pack(pady=8)

    def open_charts(self):
        w = tk.Toplevel(self.root)
        w.title(self.language.get('charts'))
        w.geometry('650x420')
        c = tk.Canvas(w, bg='white')
        c.pack(fill='both', expand=True)
        trades = getattr(self.history, 'trades', [])
        c.create_text(325, 30, text=f"Trades: {len(trades)}", fill='black')

    def check_update(self):
        info = self.updater.check_for_update()
        if info.get('available'):
            if messagebox.askyesno('Update', f"New version {info.get('latest')} available. Update now?"):
                res = self.updater.update_to_latest()
                if res.get('success'):
                    messagebox.showinfo('Done', 'Updated. Please restart the app.')
                    self.root.destroy()
                else:
                    messagebox.showerror('Error', res.get('message', 'Update failed'))
        else:
            if info.get('error'):
                messagebox.showwarning('Update', f"Could not check update: {info.get('error')}")
            else:
                messagebox.showinfo('Update', 'You are up to date.')

    def on_close(self):
        self.root.destroy()


if __name__ == '__main__':
    root = tk.Tk()
    app = CryptoTradingCalculator(root)
    root.mainloop()
