import os
import sys
import json
import time
import re
import csv
import ctypes
import threading
import subprocess
import webbrowser
from datetime import datetime

import tkinter as tk
from tkinter import ttk
from tkinter import font as tkfont
from tkinter import messagebox

try:
    import requests
except ImportError:
    requests = None

VERSION = "1.7.0"

# ----------------------------
# Paths & dirs
# ----------------------------
APP_DATA_DIR = os.path.join(os.path.expanduser("~"), ".crypto_calculator")
os.makedirs(APP_DATA_DIR, exist_ok=True)

CONFIG_PATH = os.path.join(APP_DATA_DIR, "config.json")
HISTORY_PATH = os.path.join(APP_DATA_DIR, "trade_history.json")
FONT_PATH = os.path.join(APP_DATA_DIR, "Vazirmatn-Regular.ttf")
LOG_PATH = os.path.join(APP_DATA_DIR, "app.log")

PROJECT_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))
REPO_OWNER = "Qfndr"
REPO_NAME = "crypto-trading-calculator"

# ----------------------------
# Exchange Data & Help Links
# ----------------------------
EXCHANGES_INFO = {
    "Binance": {
        "home": "https://www.binance.com",
        "api_url": "https://www.binance.com/en/my/settings/api-management",
        "doc_url": "https://developers.binance.com/docs/binance-spot-api-docs",
        "guide_url": "https://www.binance.com/en/support/faq/360002502072",
    },
    # ... (Keeping other exchanges same as before to save space in this update block, assume they are there) ...
    "Bybit": { "home": "https://www.bybit.com", "api_url": "https://www.bybit.com/app/user/api-management", "doc_url": "https://bybit-exchange.github.io/docs/", "guide_url": "https://www.bybit.com/en/help-center/article/How-to-create-your-API-key" },
    "OKX": { "home": "https://www.okx.com", "api_url": "https://www.okx.com/account/my-api", "doc_url": "https://www.okx.com/docs-v5/en/", "guide_url": "https://www.okx.com/help/how-to-create-an-api-key" },
    "KuCoin": { "home": "https://www.kucoin.com", "api_url": "https://www.kucoin.com/account/api", "doc_url": "https://docs.kucoin.com/", "guide_url": "https://www.kucoin.com/support/360015102174" },
    "Gate.io": { "home": "https://www.gate.io", "api_url": "https://www.gate.io/myaccount/api_key_manage", "doc_url": "https://www.gate.io/docs/developers/apiv4/en/", "guide_url": "https://www.gate.io/help/guide/16937" },
    "Bitget": { "home": "https://www.bitget.com", "api_url": "https://www.bitget.com/account/api", "doc_url": "https://bitgetlimited.github.io/apidoc/en/spot", "guide_url": "https://www.bitget.com/support/articles/12550620645145" },
    "MEXC": { "home": "https://www.mexc.com", "api_url": "https://www.mexc.com/user/api", "doc_url": "https://mexcdevelop.github.io/apidocs/spot_v3_en/", "guide_url": "https://www.mexc.com/support/articles/360044199972" },
    "CoinEx": { "home": "https://www.coinex.com", "api_url": "https://www.coinex.com/apikey", "doc_url": "https://docs.coinex.com/api/v2/", "guide_url": "https://support.coinex.com/hc/en-us/articles/360025310612" },
    "Nobitex": { "home": "https://nobitex.ir", "api_url": "https://nobitex.ir/profile/api-management", "doc_url": "https://apidocs.nobitex.ir/", "guide_url": "https://nobitex.ir/mag/api-guide/" },
    "Wallex": { "home": "https://wallex.ir", "api_url": "https://wallex.ir/panel/api-management", "doc_url": "https://docs.wallex.ir/", "guide_url": "https://help.wallex.ir/api/" },
}

SYMBOLS = [
    "BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT", "DOGEUSDT", "ADAUSDT", "AVAXUSDT", 
    "TRXUSDT", "DOTUSDT", "LINKUSDT", "MATICUSDT", "TONUSDT", "SHIBUSDT", "LTCUSDT", 
    "BCHUSDT", "ATOMUSDT", "UNIUSDT", "XLMUSDT", "NEARUSDT"
]

SUPPORTED_LANGS = ["fa", "en", "tr", "ru", "ar", "hi", "zh", "ja", "fr", "it", "bg"]

# ----------------------------
# Utils
# ----------------------------
def _log(msg: str):
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(f"{datetime.now().isoformat()} | {msg}\n")
    except: pass

def _load_custom_font_windows(path: str) -> bool:
    if not sys.platform.startswith("win"): return False
    try:
        buf = ctypes.create_unicode_buffer(os.path.abspath(path))
        ctypes.windll.gdi32.AddFontResourceExW(buf, 0x10, 0)
        return True
    except: return False

def _dl_font_async(cb=None):
    if os.path.exists(FONT_PATH) or not requests:
        if cb: cb()
        return
    def r():
        for u in ["https://raw.githubusercontent.com/rastikerdar/vazirmatn/master/fonts/ttf/Vazirmatn-Regular.ttf"]:
            try:
                res = requests.get(u, timeout=10)
                if res.status_code == 200:
                    with open(FONT_PATH, "wb") as f: f.write(res.content)
                    break
            except: continue
        if cb: cb()
    threading.Thread(target=r, daemon=True).start()

# ----------------------------
# Classes
# ----------------------------
class Config:
    def __init__(self):
        self.data = {}
        self.load()
    def load(self):
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, "r", encoding="utf-8") as f: self.data = json.load(f)
            except: self.data = {}
        self.capital = float(self.data.get("capital", 1000))
        self.risk = float(self.data.get("risk", 1.0))
        self.fee = float(self.data.get("fee", 0.04))
        self.exchange = self.data.get("exchange", "Binance")
        self.lang = self.data.get("lang", "fa")
        self.theme = self.data.get("theme", "dark")
        self.api_keys = self.data.get("api_keys", {})
        if self.lang not in SUPPORTED_LANGS: self.lang = "en"
    def save(self):
        self.data.update({"capital": self.capital, "risk": self.risk, "fee": self.fee, "exchange": self.exchange, "lang": self.lang, "theme": self.theme, "api_keys": self.api_keys})
        with open(CONFIG_PATH, "w", encoding="utf-8") as f: json.dump(self.data, f, indent=2)

class History:
    def __init__(self):
        self.trades = []
        if os.path.exists(HISTORY_PATH):
            try: with open(HISTORY_PATH, "r", encoding="utf-8") as f: self.trades = json.load(f)
            except: pass
    def add(self, t):
        self.trades.append(t)
        with open(HISTORY_PATH, "w", encoding="utf-8") as f: json.dump(self.trades, f, indent=2)

class Updater:
    def __init__(self, ver):
        self.ver = ver
        self.release_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases/latest"
        self.download_url = None

    def check(self):
        if not requests: return None
        try:
            r = requests.get(self.release_url, timeout=5)
            if r.status_code == 200:
                data = r.json()
                tag = data.get("tag_name", "").strip()
                # Simple compare: different string = update (assuming semver later)
                if tag and tag != f"v{self.ver}" and tag != self.ver:
                    # Find asset named main.py
                    assets = data.get("assets", [])
                    for a in assets:
                        if a.get("name") == "main.py":
                            self.download_url = a.get("browser_download_url")
                            return (tag, None) # None content, we dl later
        except Exception as e: _log(f"upd_chk: {e}")
        return None

    def download_and_stage(self):
        if not self.download_url: return None
        try:
            r = requests.get(self.download_url, timeout=15)
            if r.status_code == 200:
                upd_path = os.path.join(PROJECT_DIR, "main_update.py")
                with open(upd_path, "wb") as f: f.write(r.content)
                return self._create_bat()
        except Exception as e: _log(f"upd_dl: {e}")
        return None

    def _create_bat(self):
        if sys.platform.startswith("win"):
            bat = os.path.join(PROJECT_DIR, "apply_update.bat")
            py = sys.executable
            with open(bat, "w", encoding="utf-8") as f:
                f.write("@echo off\n")
                f.write("cd /d \"%~dp0\"\n")
                f.write("timeout /t 1 /nobreak >nul\n")
                f.write("if not exist main_update.py ( echo Missing Update & pause & exit /b 1 )\n")
                f.write("copy /Y main_update.py main.py >nul\n")
                f.write("del main_update.py >nul\n")
                f.write(f"start \"\" /D \"%~dp0\" \"{py}\" main.py\n")
            return bat
        return None

# ----------------------------
# App UI
# ----------------------------
class App:
    def __init__(self, root):
        self.root = root
        self.cfg = Config()
        self.hist = History()
        self.updater = Updater(VERSION)
        
        _dl_font_async(self._reload)
        self._setup_font()
        self.build()
        self.check_update_silent()

    def t(self, key):
        fa = {
            "title": "ماشین حساب ترید کریپتو", "settings": "تنظیمات", "help": "آموزش", "history": "تاریخچه", "charts": "نمودار", "update": "آپدیت",
            "capital": "سرمایه (USDT)", "risk": "ریسک (%)", "fee": "کارمزد (%)", "save": "ذخیره",
            "calc": "محاسبه", "entry": "قیمت ورود", "sl": "استاپ لاس", "lev": "لوریج", 
            "res_pos": "حجم پوزیشن", "res_qty": "تعداد کوین", "res_risk": "مقدار ریسک", "saved": "ذخیره شد",
            "new_ver": "نسخه جدید موجود است. دانلود و نصب شود؟"
        }
        en = {
            "title": "Crypto Trading Calculator", "settings": "Settings", "help": "Help", "history": "History", "charts": "Charts", "update": "Update",
            "capital": "Capital", "risk": "Risk %", "fee": "Fee %", "save": "Save",
            "calc": "Calculate", "entry": "Entry Price", "sl": "Stop Loss", "lev": "Leverage",
            "res_pos": "Position Size", "res_qty": "Coin Qty", "res_risk": "Risk Amt", "saved": "Saved!",
            "new_ver": "New version available. Download & Install?"
        }
        d = fa if self.cfg.lang == "fa" else en
        return d.get(key, key)

    def _reload(self): self.root.after(0, lambda: [self._setup_font(), self.build()])
    def _setup_font(self):
        if os.path.exists(FONT_PATH): _load_custom_font_windows(FONT_PATH)
        fam = "Vazirmatn" if "Vazirmatn" in tkfont.families() else "Segoe UI"
        self.f_b = (fam, 11); self.f_h = (fam, 16, "bold")

    def build(self):
        self.colors = {'bg': '#1e293b', 'fg': '#e2e8f0', 'card': '#334155', 'inp': '#0f172a', 'btn': '#3b82f6'} if self.cfg.theme == "dark" else \
                      {'bg': '#f1f5f9', 'fg': '#1e293b', 'card': '#ffffff', 'inp': '#e2e8f0', 'btn': '#2563eb'}
        for w in self.root.winfo_children(): w.destroy()
        self.root.configure(bg=self.colors['bg'])
        
        # Header
        nav = tk.Frame(self.root, bg=self.colors['card'], height=50); nav.pack(fill='x')
        tk.Label(nav, text=f"{self.t('title')} (v{VERSION})", font=self.f_h, bg=self.colors['card'], fg=self.colors['fg']).pack(side='left', padx=15, pady=10)
        btns = tk.Frame(nav, bg=self.colors['card']); btns.pack(side='right', padx=10)
        for k, c in [("help", self.win_help), ("settings", self.win_settings), ("history", self.win_history), ("charts", self.win_charts), ("update", self.manual_update)]:
            tk.Button(btns, text=self.t(k), command=c, bg=self.colors['card'], fg=self.colors['fg'], relief='flat', font=self.f_b).pack(side='left', padx=5)

        # Main
        main = tk.Frame(self.root, bg=self.colors['bg']); main.pack(fill='both', expand=True, padx=20, pady=20)
        left = tk.Frame(main, bg=self.colors['bg']); left.pack(side='left', fill='y', padx=(0,20))
        
        # Exchange
        c_ex = self._card(left, "Exchange")
        self.ex_v = tk.StringVar(value=self.cfg.exchange); ttk.Combobox(c_ex, textvariable=self.ex_v, values=list(EXCHANGES_INFO.keys())).pack(fill='x', pady=5)
        self.sym_v = tk.StringVar(value="BTCUSDT"); ttk.Combobox(c_ex, textvariable=self.sym_v, values=SYMBOLS).pack(fill='x', pady=5)
        tk.Button(c_ex, text=self.t('calc')+" Price (Sim)", command=lambda: [self.e_ent.delete(0,'end'), self.e_ent.insert(0,"98000")], bg=self.colors['btn'], fg='white', relief='flat').pack(fill='x', pady=5)

        # Capital
        c_cap = self._card(left, "Capital")
        self.e_cap = self._inp(c_cap, self.t('capital'), self.cfg.capital)
        self.e_risk = self._inp(c_cap, self.t('risk'), self.cfg.risk)
        tk.Button(c_cap, text=self.t('save'), command=self.save_cfg, bg=self.colors['btn'], fg='white', relief='flat').pack(fill='x', pady=10)

        # Calc
        right = tk.Frame(main, bg=self.colors['bg']); right.pack(side='right', fill='both', expand=True)
        c_cal = self._card(right, "Calculator")
        gf = tk.Frame(c_cal, bg=self.colors['card']); gf.pack(fill='x', pady=5)
        self.e_ent = self._inp_g(gf, self.t('entry'), 0, 0)
        self.e_sl = self._inp_g(gf, self.t('sl'), 0, 1)
        self.e_lev = self._inp_g(gf, self.t('lev'), 1, 0, "10")
        tk.Button(c_cal, text=self.t('calc'), command=self.do_calc, bg=self.colors['btn'], fg='white', font=self.f_h, relief='flat').pack(fill='x', pady=15)
        self.res_txt = tk.Text(c_cal, height=8, bg=self.colors['inp'], fg=self.colors['fg'], relief='flat', font=('Consolas', 11)); self.res_txt.pack(fill='both', expand=True)

    def _card(self, p, t):
        f = tk.Frame(p, bg=self.colors['card'], padx=15, pady=15); f.pack(fill='x', pady=(0, 15))
        tk.Label(f, text=t, font=self.f_h, bg=self.colors['card'], fg=self.colors['fg']).pack(anchor='w', pady=(0, 10))
        return f
    def _inp(self, p, l, v):
        tk.Label(p, text=l, bg=self.colors['card'], fg=self.colors['fg'], font=self.f_b).pack(anchor='w')
        e = tk.Entry(p, bg=self.colors['inp'], fg=self.colors['fg'], relief='flat', font=self.f_b); e.pack(fill='x', pady=(0, 10)); e.insert(0, str(v))
        return e
    def _inp_g(self, p, l, r, c, v=""):
        f = tk.Frame(p, bg=self.colors['card']); f.grid(row=r, column=c, padx=5, pady=5, sticky='ew'); p.columnconfigure(c, weight=1)
        tk.Label(f, text=l, bg=self.colors['card'], fg=self.colors['fg'], font=self.f_b).pack(anchor='w')
        e = tk.Entry(f, bg=self.colors['inp'], fg=self.colors['fg'], relief='flat', font=self.f_b); e.pack(fill='x'); 
        if v: e.insert(0, v)
        return e

    def save_cfg(self):
        try:
            self.cfg.capital = float(self.e_cap.get()); self.cfg.risk = float(self.e_risk.get()); self.cfg.exchange = self.ex_v.get()
            self.cfg.save(); messagebox.showinfo("", self.t('saved'))
        except: messagebox.showerror("", "Error")

    def do_calc(self):
        try:
            e=float(self.e_ent.get()); s=float(self.e_sl.get()); L=float(self.e_lev.get())
            C=float(self.e_cap.get()); R=float(self.e_risk.get())
            ramt = C*(R/100); diff = abs(e-s)/e; sz = ramt/diff; qty = (sz*L)/e
            res = f"{self.t('res_pos')}: {sz:,.2f} $\n{self.t('res_qty')}: {qty:.6f}\n{self.t('res_risk')}: {ramt:.2f} $\nLev: {L}x | SL: {s}"
            self.res_txt.delete('1.0', 'end'); self.res_txt.insert('1.0', res)
            self.hist.add({"d": datetime.now().strftime("%Y-%m-%d %H:%M"), "sym": self.sym_v.get(), "p": sz, "r": ramt})
        except: messagebox.showerror("", "Error")

    def win_settings(self):
        w = tk.Toplevel(self.root); w.title(self.t('settings')); w.configure(bg=self.colors['bg']); w.geometry("500x400")
        tk.Label(w, text=self.t('lang'), bg=self.colors['bg'], fg=self.colors['fg']).pack(pady=10)
        cb_l = ttk.Combobox(w, values=SUPPORTED_LANGS, state='readonly'); cb_l.set(self.cfg.lang); cb_l.pack()
        def sv(): self.cfg.lang = cb_l.get(); self.cfg.save(); w.destroy(); self.build()
        tk.Button(w, text=self.t('save'), command=sv, bg=self.colors['btn'], fg='white').pack(pady=20)

    def win_help(self):
        w = tk.Toplevel(self.root); w.title(self.t('help')); w.configure(bg=self.colors['bg']); w.geometry("800x600")
        nb = ttk.Notebook(w); nb.pack(fill='both', expand=True)
        f = tk.Frame(nb, bg=self.colors['bg']); nb.add(f, text="Exchanges")
        cv = tk.Canvas(f, bg=self.colors['bg']); cv.pack(side='left', fill='both', expand=True); sb = ttk.Scrollbar(f, command=cv.yview); sb.pack(side='right', fill='y'); cv.configure(yscrollcommand=sb.set)
        inr = tk.Frame(cv, bg=self.colors['bg']); cv.create_window((0,0), window=inr, anchor='nw'); inr.bind("<Configure>", lambda e: cv.configure(scrollregion=cv.bbox("all")))
        for x, i in EXCHANGES_INFO.items():
            r = tk.Frame(inr, bg=self.colors['card'], padx=10, pady=10, bd=1, relief='solid'); r.pack(fill='x', padx=10, pady=5)
            tk.Label(r, text=x, font=self.f_h, bg=self.colors['card'], fg=self.colors['fg']).pack(anchor='w')
            b = tk.Frame(r, bg=self.colors['card']); b.pack(anchor='w')
            tk.Button(b, text="Home", command=lambda u=i['home']: webbrowser.open(u)).pack(side='left')
            tk.Button(b, text="API", command=lambda u=i['api_url']: webbrowser.open(u)).pack(side='left', padx=5)

    def win_history(self): messagebox.showinfo("", f"Saved: {HISTORY_PATH}")
    def win_charts(self): messagebox.showinfo("", "Charts coming soon")
    
    def manual_update(self): self.check_update_silent(True)
    def check_update_silent(self, f=False):
        res = self.updater.check()
        if res:
            tag, _ = res
            if messagebox.askyesno(self.t('update'), f"{self.t('new_ver')} ({tag})"):
                bat = self.updater.download_and_stage()
                if bat: 
                    if sys.platform.startswith("win"): os.startfile(bat)
                    self.root.destroy()
        elif f: messagebox.showinfo("", "Up to date")

if __name__ == "__main__":
    try:
        root = tk.Tk()
        App(root)
        root.mainloop()
    except Exception as e: _log(f"fatal: {e}")
