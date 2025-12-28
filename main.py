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

VERSION = "1.6.6"

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
    "Bybit": {
        "home": "https://www.bybit.com",
        "api_url": "https://www.bybit.com/app/user/api-management",
        "doc_url": "https://bybit-exchange.github.io/docs/",
        "guide_url": "https://www.bybit.com/en/help-center/article/How-to-create-your-API-key",
    },
    "OKX": {
        "home": "https://www.okx.com",
        "api_url": "https://www.okx.com/account/my-api",
        "doc_url": "https://www.okx.com/docs-v5/en/",
        "guide_url": "https://www.okx.com/help/how-to-create-an-api-key",
    },
    "KuCoin": {
        "home": "https://www.kucoin.com",
        "api_url": "https://www.kucoin.com/account/api",
        "doc_url": "https://docs.kucoin.com/",
        "guide_url": "https://www.kucoin.com/support/360015102174",
    },
    "Gate.io": {
        "home": "https://www.gate.io",
        "api_url": "https://www.gate.io/myaccount/api_key_manage",
        "doc_url": "https://www.gate.io/docs/developers/apiv4/en/",
        "guide_url": "https://www.gate.io/help/guide/16937",
    },
    "Bitget": {
        "home": "https://www.bitget.com",
        "api_url": "https://www.bitget.com/account/api",
        "doc_url": "https://bitgetlimited.github.io/apidoc/en/spot",
        "guide_url": "https://www.bitget.com/support/articles/12550620645145",
    },
    "MEXC": {
        "home": "https://www.mexc.com",
        "api_url": "https://www.mexc.com/user/api",
        "doc_url": "https://mexcdevelop.github.io/apidocs/spot_v3_en/",
        "guide_url": "https://www.mexc.com/support/articles/360044199972",
    },
    "CoinEx": {
        "home": "https://www.coinex.com",
        "api_url": "https://www.coinex.com/apikey",
        "doc_url": "https://docs.coinex.com/api/v2/",
        "guide_url": "https://support.coinex.com/hc/en-us/articles/360025310612",
    },
    "Nobitex": {
        "home": "https://nobitex.ir",
        "api_url": "https://nobitex.ir/profile/api-management",
        "doc_url": "https://apidocs.nobitex.ir/",
        "guide_url": "https://nobitex.ir/mag/api-guide/",
    },
    "Wallex": {
        "home": "https://wallex.ir",
        "api_url": "https://wallex.ir/panel/api-management",
        "doc_url": "https://docs.wallex.ir/",
        "guide_url": "https://help.wallex.ir/api/",
    },
}

SYMBOLS = [
    "BTCUSDT",
    "ETHUSDT",
    "SOLUSDT",
    "BNBUSDT",
    "XRPUSDT",
    "DOGEUSDT",
    "ADAUSDT",
    "AVAXUSDT",
    "TRXUSDT",
    "DOTUSDT",
    "LINKUSDT",
    "MATICUSDT",
    "TONUSDT",
    "SHIBUSDT",
    "LTCUSDT",
    "BCHUSDT",
    "ATOMUSDT",
    "UNIUSDT",
    "XLMUSDT",
    "NEARUSDT",
]

SUPPORTED_LANGS = ["fa", "en", "tr", "ru", "ar", "hi", "zh", "ja", "fr", "it", "bg"]

# ----------------------------
# Font & Utils
# ----------------------------
FONT_URLS = [
    "https://raw.githubusercontent.com/rastikerdar/vazirmatn/master/fonts/ttf/Vazirmatn-Regular.ttf",
    "https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/fonts/ttf/Vazirmatn-Regular.ttf",
]


def _log(msg: str):
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(f"{datetime.now().isoformat()} | {msg}\n")
    except Exception:
        pass


def _load_custom_font_windows(path: str) -> bool:
    if not sys.platform.startswith("win"):
        return False
    try:
        buf = ctypes.create_unicode_buffer(os.path.abspath(path))
        ctypes.windll.gdi32.AddFontResourceExW(buf, 0x10, 0)
        return True
    except Exception:
        return False


def _dl_font_async(cb=None):
    if os.path.exists(FONT_PATH) or not requests:
        if cb:
            cb()
        return

    def r():
        for u in FONT_URLS:
            try:
                res = requests.get(u, timeout=10)
                if res.status_code == 200:
                    with open(FONT_PATH, "wb") as f:
                        f.write(res.content)
                    break
            except Exception:
                continue
        if cb:
            cb()

    threading.Thread(target=r, daemon=True).start()


# ----------------------------
# Data Models
# ----------------------------
class Config:
    def __init__(self):
        self.data = {}
        self.load()

    def load(self):
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            except Exception:
                self.data = {}

        self.capital = float(self.data.get("capital", 1000))
        self.risk = float(self.data.get("risk", 1.0))
        self.fee = float(self.data.get("fee", 0.04))
        self.exchange = self.data.get("exchange", "Binance")
        self.lang = self.data.get("lang", "fa")
        self.theme = self.data.get("theme", "dark")
        self.api_keys = self.data.get("api_keys", {})

        if self.lang not in SUPPORTED_LANGS:
            self.lang = "en"

    def save(self):
        self.data.update(
            {
                "capital": self.capital,
                "risk": self.risk,
                "fee": self.fee,
                "exchange": self.exchange,
                "lang": self.lang,
                "theme": self.theme,
                "api_keys": self.api_keys,
            }
        )
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)


class History:
    def __init__(self):
        self.trades = []
        if os.path.exists(HISTORY_PATH):
            try:
                with open(HISTORY_PATH, "r", encoding="utf-8") as f:
                    self.trades = json.load(f)
            except Exception:
                self.trades = []

    def add(self, t):
        self.trades.append(t)
        with open(HISTORY_PATH, "w", encoding="utf-8") as f:
            json.dump(self.trades, f, ensure_ascii=False, indent=2)

    def export_csv(self, path):
        if not self.trades:
            return False
        try:
            with open(path, "w", newline="", encoding="utf-8-sig") as f:
                w = csv.DictWriter(f, fieldnames=self.trades[0].keys())
                w.writeheader()
                w.writerows(self.trades)
            return True
        except Exception:
            return False


# ----------------------------
# Updater
# ----------------------------
class Updater:
    def __init__(self, ver):
        self.ver = ver

    def check(self):
        if not requests:
            return None
        try:
            url = f"https://raw.githubusercontent.com/Qfndr/crypto-trading-calculator/main/main.py?t={int(time.time())}"
            r = requests.get(url, timeout=8)
            if r.status_code == 200:
                m = re.search(r'VERSION\s*=\s*"([^"]+)"', r.text)
                if m:
                    rem = m.group(1)
                    if rem != self.ver:
                        return (rem, r.text)
        except Exception as e:
            _log(f"update_check_error: {e}")
        return None

    def stage(self, content):
        upd_path = os.path.join(PROJECT_DIR, "main_update.py")
        with open(upd_path, "w", encoding="utf-8") as f:
            f.write(content)

        if sys.platform.startswith("win"):
            bat = os.path.join(PROJECT_DIR, "apply_update.bat")
            py = sys.executable
            with open(bat, "w", encoding="utf-8") as f:
                f.write("@echo off\n")
                f.write("cd /d \"%~dp0\"\n")
                f.write("timeout /t 1 /nobreak >nul\n")
                f.write("if not exist \"%~dp0main_update.py\" (\n")
                f.write("  echo Could Not Find \"%~dp0main_update.py\"\n")
                f.write("  pause\n")
                f.write("  exit /b 1\n")
                f.write(")\n")
                f.write("copy /Y \"%~dp0main_update.py\" \"%~dp0main.py\" >nul\n")
                f.write("del \"%~dp0main_update.py\" >nul\n")
                f.write(f"start \"\" /D \"%~dp0\" \"{py}\" \"%~dp0main.py\"\n")
            return bat

        # Non-windows: keep simple
        sh = os.path.join(PROJECT_DIR, "apply_update.sh")
        with open(sh, "w", encoding="utf-8") as f:
            f.write("#!/bin/sh\n")
            f.write("cd \"$(dirname \"$0\")\"\n")
            f.write("sleep 1\n")
            f.write("[ -f main_update.py ] || exit 1\n")
            f.write("cp -f main_update.py main.py\n")
            f.write("rm -f main_update.py\n")
            f.write(f"\"{sys.executable}\" main.py\n")
        try:
            os.chmod(sh, 0o755)
        except Exception:
            pass
        return sh


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
        self._setup_theme()

        self.root.title(f"{self.t('title')} v{VERSION}")
        self.root.geometry("1200x800")

        self.build()
        self.check_update_silent()

    def t(self, key):
        fa = {
            "title": "ماشین حساب ترید کریپتو",
            "settings": "تنظیمات",
            "help": "آموزش",
            "history": "تاریخچه",
            "charts": "نمودار",
            "update": "آپدیت",
            "capital": "سرمایه (USDT)",
            "risk": "ریسک (%)",
            "fee": "کارمزد (%)",
            "save": "ذخیره",
            "calc": "محاسبه",
            "entry": "قیمت ورود",
            "sl": "استاپ لاس",
            "lev": "لوریج",
            "res_pos": "حجم پوزیشن",
            "res_qty": "تعداد کوین",
            "res_risk": "مقدار ریسک",
            "err_inp": "لطفا همه فیلدها را عدد معتبر وارد کنید",
            "saved": "ذخیره شد",
            "lang": "زبان",
            "theme": "تم",
            "new_ver": "نسخه جدید موجود است. آپدیت شود؟",
        }
        en = {
            "title": "Crypto Trading Calculator",
            "settings": "Settings",
            "help": "Help",
            "history": "History",
            "charts": "Charts",
            "update": "Update",
            "capital": "Capital",
            "risk": "Risk %",
            "fee": "Fee %",
            "save": "Save",
            "calc": "Calculate",
            "entry": "Entry Price",
            "sl": "Stop Loss",
            "lev": "Leverage",
            "res_pos": "Position Size",
            "res_qty": "Coin Qty",
            "res_risk": "Risk Amt",
            "err_inp": "Please enter valid numbers",
            "saved": "Saved!",
            "lang": "Language",
            "theme": "Theme",
            "new_ver": "New version available. Update now?",
        }

        # All other languages fallback to English
        d = fa if self.cfg.lang == "fa" else en
        return d.get(key, key)

    def _reload(self):
        self.root.after(0, lambda: [self._setup_font(), self.build()])

    def _setup_font(self):
        if os.path.exists(FONT_PATH):
            _load_custom_font_windows(FONT_PATH)
        fam = "Vazirmatn" if "Vazirmatn" in tkfont.families() else "Segoe UI"
        self.f_b = (fam, 11)
        self.f_h = (fam, 16, "bold")

    def _setup_theme(self):
        if self.cfg.theme == "dark":
            self.colors = {
                "bg": "#1e293b",
                "fg": "#e2e8f0",
                "card": "#334155",
                "inp": "#0f172a",
                "btn": "#3b82f6",
            }
        else:
            self.colors = {
                "bg": "#f1f5f9",
                "fg": "#1e293b",
                "card": "#ffffff",
                "inp": "#e2e8f0",
                "btn": "#2563eb",
            }

    def build(self):
        self._setup_theme()
        for w in self.root.winfo_children():
            w.destroy()
        self.root.configure(bg=self.colors["bg"])

        nav = tk.Frame(self.root, bg=self.colors["card"], height=50)
        nav.pack(fill="x")
        tk.Label(
            nav,
            text=self.t("title"),
            font=self.f_h,
            bg=self.colors["card"],
            fg=self.colors["fg"],
        ).pack(side="left", padx=15, pady=10)

        btns = tk.Frame(nav, bg=self.colors["card"])
        btns.pack(side="right", padx=10)

        for k, cmd in [
            ("help", self.win_help),
            ("settings", self.win_settings),
            ("history", self.win_history),
            ("charts", self.win_charts),
            ("update", self.manual_update),
        ]:
            tk.Button(
                btns,
                text=self.t(k),
                command=cmd,
                bg=self.colors["card"],
                fg=self.colors["fg"],
                relief="flat",
                font=self.f_b,
            ).pack(side="left", padx=5)

        main = tk.Frame(self.root, bg=self.colors["bg"])
        main.pack(fill="both", expand=True, padx=20, pady=20)

        left = tk.Frame(main, bg=self.colors["bg"])
        left.pack(side="left", fill="y", padx=(0, 20))

        self.card_ex = self._card(left, "Exchange")
        self.ex_var = tk.StringVar(value=self.cfg.exchange)
        ttk.Combobox(self.card_ex, textvariable=self.ex_var, values=list(EXCHANGES_INFO.keys())).pack(
            fill="x", pady=5
        )

        self.sym_var = tk.StringVar(value="BTCUSDT")
        ttk.Combobox(self.card_ex, textvariable=self.sym_var, values=SYMBOLS).pack(fill="x", pady=5)

        tk.Button(
            self.card_ex,
            text=self.t("calc") + " Price (Sim)",
            command=self.sim_price,
            bg=self.colors["btn"],
            fg="white",
            relief="flat",
        ).pack(fill="x", pady=5)

        self.card_cap = self._card(left, "Capital")
        self.e_cap = self._inp(self.card_cap, self.t("capital"), self.cfg.capital)
        self.e_risk = self._inp(self.card_cap, self.t("risk"), self.cfg.risk)

        tk.Button(
            self.card_cap,
            text=self.t("save"),
            command=self.save_cfg,
            bg=self.colors["btn"],
            fg="white",
            relief="flat",
        ).pack(fill="x", pady=10)

        right = tk.Frame(main, bg=self.colors["bg"])
        right.pack(side="right", fill="both", expand=True)

        self.card_calc = self._card(right, "Trade Calculator")

        f_grid = tk.Frame(self.card_calc, bg=self.colors["card"])
        f_grid.pack(fill="x", pady=5)

        self.e_ent = self._inp_g(f_grid, self.t("entry"), 0, 0)
        self.e_sl = self._inp_g(f_grid, self.t("sl"), 0, 1)
        self.e_lev = self._inp_g(f_grid, self.t("lev"), 1, 0, "10")

        tk.Button(
            self.card_calc,
            text=self.t("calc"),
            command=self.do_calc,
            bg=self.colors["btn"],
            fg="white",
            font=self.f_h,
            relief="flat",
        ).pack(fill="x", pady=20)

        self.res_txt = tk.Text(
            self.card_calc,
            height=10,
            bg=self.colors["inp"],
            fg=self.colors["fg"],
            relief="flat",
            font=("Consolas", 11),
        )
        self.res_txt.pack(fill="both", expand=True)

    def _card(self, p, t):
        f = tk.Frame(p, bg=self.colors["card"], padx=15, pady=15)
        f.pack(fill="x", pady=(0, 15))
        tk.Label(f, text=t, font=self.f_h, bg=self.colors["card"], fg=self.colors["fg"]).pack(
            anchor="w", pady=(0, 10)
        )
        return f

    def _inp(self, p, l, v):
        tk.Label(p, text=l, bg=self.colors["card"], fg=self.colors["fg"], font=self.f_b).pack(anchor="w")
        e = tk.Entry(p, bg=self.colors["inp"], fg=self.colors["fg"], relief="flat", font=self.f_b)
        e.pack(fill="x", pady=(0, 10))
        e.insert(0, str(v))
        return e

    def _inp_g(self, p, l, r, c, v=""):
        f = tk.Frame(p, bg=self.colors["card"])
        f.grid(row=r, column=c, padx=5, pady=5, sticky="ew")
        p.columnconfigure(c, weight=1)
        tk.Label(f, text=l, bg=self.colors["card"], fg=self.colors["fg"], font=self.f_b).pack(anchor="w")
        e = tk.Entry(f, bg=self.colors["inp"], fg=self.colors["fg"], relief="flat", font=self.f_b)
        e.pack(fill="x")
        if v:
            e.insert(0, v)
        return e

    # Logic
    def sim_price(self):
        self.e_ent.delete(0, "end")
        self.e_ent.insert(0, "98000" if "BTC" in self.sym_var.get() else "2700")

    def save_cfg(self):
        try:
            self.cfg.capital = float(self.e_cap.get())
            self.cfg.risk = float(self.e_risk.get())
            self.cfg.exchange = self.ex_var.get()
            self.cfg.save()
            messagebox.showinfo("", self.t("saved"))
        except Exception as e:
            _log(f"save_cfg_error: {e}")
            messagebox.showerror("", self.t("err_inp"))

    def do_calc(self):
        try:
            ent = float(self.e_ent.get())
            sl = float(self.e_sl.get())
            lev = float(self.e_lev.get())
            cap = float(self.e_cap.get())
            risk_pct = float(self.e_risk.get())

            risk_amt = cap * (risk_pct / 100)
            diff_pct = abs(ent - sl) / ent

            if diff_pct == 0:
                raise ValueError("SL diff is 0")

            pos_sz = risk_amt / diff_pct
            qty = (pos_sz * lev) / ent

            res = (
                f"{self.t('res_pos')}: {pos_sz:,.2f} USDT\n"
                f"{self.t('res_qty')}: {qty:.6f}\n"
                f"{self.t('res_risk')}: {risk_amt:.2f} USDT\n"
                f"--------------------------------\n"
                f"Lev: {lev}x | Entry: {ent} | SL: {sl}\n"
            )

            self.res_txt.delete("1.0", "end")
            self.res_txt.insert("1.0", res)

            self.hist.add(
                {
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "symbol": self.sym_var.get(),
                    "entry": ent,
                    "sl": sl,
                    "lev": lev,
                    "pos_size": round(pos_sz, 6),
                    "risk_amt": round(risk_amt, 6),
                    "qty": round(qty, 8),
                }
            )

        except Exception as e:
            _log(f"calc_error: {e}")
            messagebox.showerror("", self.t("err_inp"))

    # Windows
    def win_settings(self):
        w = tk.Toplevel(self.root)
        w.title(self.t("settings"))
        w.configure(bg=self.colors["bg"])
        w.geometry("600x520")

        nb = ttk.Notebook(w)
        nb.pack(fill="both", expand=True, padx=10, pady=10)

        g = tk.Frame(nb, bg=self.colors["bg"])
        nb.add(g, text="General")

        tk.Label(g, text=self.t("lang"), bg=self.colors["bg"], fg=self.colors["fg"], font=self.f_b).pack(pady=6)
        lang_cb = ttk.Combobox(g, values=SUPPORTED_LANGS, state="readonly")
        lang_cb.set(self.cfg.lang)
        lang_cb.pack(pady=2)

        tk.Label(g, text=self.t("theme"), bg=self.colors["bg"], fg=self.colors["fg"], font=self.f_b).pack(pady=6)
        theme_cb = ttk.Combobox(g, values=["dark", "light"], state="readonly")
        theme_cb.set(self.cfg.theme)
        theme_cb.pack(pady=2)

        def save():
            self.cfg.lang = lang_cb.get()
            self.cfg.theme = theme_cb.get()
            self.cfg.save()
            w.destroy()
            self.build()

        tk.Button(g, text=self.t("save"), command=save, bg=self.colors["btn"], fg="white").pack(pady=18)

        a = tk.Frame(nb, bg=self.colors["bg"])
        nb.add(a, text="API Keys")

        tk.Label(a, text="API Keys are stored locally in config.json", bg=self.colors["bg"], fg=self.colors["fg"], font=self.f_b).pack(pady=6)

    def win_help(self):
        w = tk.Toplevel(self.root)
        w.title(self.t("help"))
        w.configure(bg=self.colors["bg"])
        w.geometry("900x650")

        nb = ttk.Notebook(w)
        nb.pack(fill="both", expand=True)

        ex_f = tk.Frame(nb, bg=self.colors["bg"])
        nb.add(ex_f, text="Exchanges")

        cv = tk.Canvas(ex_f, bg=self.colors["bg"])
        cv.pack(side="left", fill="both", expand=True)
        sb = ttk.Scrollbar(ex_f, command=cv.yview)
        sb.pack(side="right", fill="y")
        cv.configure(yscrollcommand=sb.set)

        f = tk.Frame(cv, bg=self.colors["bg"])
        cv.create_window((0, 0), window=f, anchor="nw")
        f.bind("<Configure>", lambda e: cv.configure(scrollregion=cv.bbox("all")))

        for ex, info in EXCHANGES_INFO.items():
            fr = tk.Frame(f, bg=self.colors["card"], bd=1, relief="solid", padx=10, pady=10)
            fr.pack(fill="x", padx=10, pady=6)
            tk.Label(fr, text=ex, font=self.f_h, bg=self.colors["card"], fg=self.colors["fg"]).pack(anchor="w")

            btns = tk.Frame(fr, bg=self.colors["card"])
            btns.pack(anchor="w", pady=6)
            tk.Button(btns, text="🏠 Home", command=lambda u=info["home"]: webbrowser.open(u)).pack(side="left", padx=2)
            tk.Button(btns, text="🔑 API Create", command=lambda u=info["api_url"]: webbrowser.open(u)).pack(side="left", padx=2)
            tk.Button(btns, text="📄 API Docs", command=lambda u=info["doc_url"]: webbrowser.open(u)).pack(side="left", padx=2)
            tk.Button(btns, text="❓ Guide", command=lambda u=info["guide_url"]: webbrowser.open(u)).pack(side="left", padx=2)

    def win_history(self):
        messagebox.showinfo("History", f"Saved at: {HISTORY_PATH}")

    def win_charts(self):
        messagebox.showinfo("Charts", "Equity curve view will be improved.")

    def manual_update(self):
        self.check_update_silent(force_msg=True)

    def check_update_silent(self, force_msg=False):
        res = self.updater.check()
        if res:
            ver, content = res
            if messagebox.askyesno(self.t("update"), f"{self.t('new_ver')} (v{ver})"):
                runner = self.updater.stage(content)
                try:
                    if sys.platform.startswith("win"):
                        os.startfile(runner)
                    else:
                        subprocess.Popen([runner], cwd=PROJECT_DIR)
                    self.root.destroy()
                except Exception as e:
                    _log(f"update_run_error: {e}")
        elif force_msg:
            messagebox.showinfo("", "Up to date")


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        _log(f"fatal: {e}")
        raise
