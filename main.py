import os
import sys
import json
import time
import re
import csv
import ctypes
import threading
import subprocess
from datetime import datetime

import tkinter as tk
from tkinter import ttk
from tkinter import font as tkfont

try:
    import requests
except Exception:
    requests = None

VERSION = "1.6.4"

# ----------------------------
# Paths (avoid PermissionError)
# ----------------------------
APP_DATA_DIR = os.path.join(os.path.expanduser("~"), ".crypto_calculator")
os.makedirs(APP_DATA_DIR, exist_ok=True)

CONFIG_PATH = os.path.join(APP_DATA_DIR, "config.json")
HISTORY_PATH = os.path.join(APP_DATA_DIR, "trade_history.json")
FONT_PATH = os.path.join(APP_DATA_DIR, "Vazirmatn-Regular.ttf")

PROJECT_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))

# ----------------------------
# Font download + Windows load
# ----------------------------
FONT_URLS = [
    "https://raw.githubusercontent.com/rastikerdar/vazirmatn/master/fonts/ttf/Vazirmatn-Regular.ttf",
    "https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/fonts/ttf/Vazirmatn-Regular.ttf",
]


def _load_custom_font_windows(font_path: str) -> bool:
    if not sys.platform.startswith("win"):
        return False
    try:
        buf = ctypes.create_unicode_buffer(os.path.abspath(font_path))
        # FR_PRIVATE = 0x10
        added = ctypes.windll.gdi32.AddFontResourceExW(buf, 0x10, 0)
        return added > 0
    except Exception:
        return False


def _download_font_async(on_done=None):
    if os.path.exists(FONT_PATH) or not requests:
        if on_done:
            on_done()
        return

    def run():
        for url in FONT_URLS:
            try:
                r = requests.get(url, timeout=15, stream=True)
                if r.status_code != 200:
                    continue
                with open(FONT_PATH, "wb") as f:
                    for chunk in r.iter_content(chunk_size=64 * 1024):
                        if chunk:
                            f.write(chunk)
                break
            except Exception:
                continue
        if on_done:
            on_done()

    threading.Thread(target=run, daemon=True).start()


# ----------------------------
# Config + History
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
        self.risk_percent = float(self.data.get("risk_percent", 1.0))
        self.fee_percent = float(self.data.get("fee_percent", 0.04))
        self.selected_exchange = self.data.get("selected_exchange", "Binance")
        self.order_type = self.data.get("order_type", "taker")
        self.theme = self.data.get("theme", "dark")
        self.language = self.data.get("language", "fa")
        self.api_keys = self.data.get("api_keys", {})

    def save(self):
        self.data.update(
            {
                "capital": self.capital,
                "risk_percent": self.risk_percent,
                "fee_percent": self.fee_percent,
                "selected_exchange": self.selected_exchange,
                "order_type": self.order_type,
                "theme": self.theme,
                "language": self.language,
                "api_keys": self.api_keys,
                "last_updated": datetime.now().isoformat(),
            }
        )
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def get_api_credentials(self, ex: str):
        return self.api_keys.get(ex, {"api_key": "", "api_secret": ""})

    def set_api_credentials(self, ex: str, api_key: str, api_secret: str):
        self.api_keys[ex] = {"api_key": api_key or "", "api_secret": api_secret or ""}
        self.save()


class TradeHistory:
    def __init__(self):
        self.trades = []
        self.load()

    def load(self):
        if os.path.exists(HISTORY_PATH):
            try:
                with open(HISTORY_PATH, "r", encoding="utf-8") as f:
                    self.trades = json.load(f) or []
            except Exception:
                self.trades = []

    def add_trade(self, trade: dict):
        self.trades.append(trade)
        with open(HISTORY_PATH, "w", encoding="utf-8") as f:
            json.dump(self.trades, f, ensure_ascii=False, indent=2)

    def export_csv(self, filename: str) -> bool:
        if not self.trades:
            return False
        keys = sorted({k for t in self.trades for k in t.keys()})
        with open(filename, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=keys)
            w.writeheader()
            w.writerows(self.trades)
        return True


# ----------------------------
# Exchange info + Help content
# ----------------------------
EXCHANGES = {
    "Binance": {
        "home": "https://www.binance.com/",
        "api_help": "https://www.binance.com/en/support/faq/detail/360002502072",
        "api_docs": "https://www.binance.com/en/binance-api",
    },
    "Bybit": {
        "home": "https://www.bybit.com/",
        "api_help": "https://www.bybit.com/en/help-center/article/How-to-create-your-API-key",
        "api_mgmt": "https://www.bybit.com/app/user/api-management",
        "testnet_api_mgmt": "https://testnet.bybit.com/app/user/api-management",
    },
    "OKX": {
        "home": "https://www.okx.com/",
        "api_docs": "https://www.okx.com/docs-v5/en/",
    },
    "KuCoin": {"home": "https://www.kucoin.com/"},
    "Gate.io": {"home": "https://www.gate.io/"},
    "Bitget": {"home": "https://www.bitget.com/"},
    "MEXC": {"home": "https://www.mexc.com/"},
    "CoinEx": {"home": "https://www.coinex.com/"},
}

TERMS_FA = {
    "TP (Take Profit)": "هدف سود؛ قیمتی که می‌خواهی در آن بخشی/کل پوزیشن را با سود ببندی.",
    "SL (Stop Loss)": "حد ضرر؛ قیمتی که اگر بازار بر خلاف تو رفت، برای محدود کردن ضرر از معامله خارج می‌شوی.",
    "Leverage (لوریج)": "اهرم؛ چند برابر کردن ارزش پوزیشن نسبت به سرمایه. لوریج بالا ریسک لیکویید شدن را زیاد می‌کند.",
    "Position Size": "اندازه پوزیشن (USDT) بر اساس ریسک؛ یعنی با خوردن SL دقیقاً همان مقدار ریسک تعیین‌شده را از دست بدهی.",
    "R/R": "نسبت ریسک به ریوارد؛ یعنی سود احتمالی چند برابر ریسک است.",
}


# ----------------------------
# Updater (cache-bust + safe replace)
# ----------------------------
class Updater:
    RAW_MAIN = "https://raw.githubusercontent.com/Qfndr/crypto-trading-calculator/main/main.py"

    def __init__(self, current_version: str):
        self.current_version = current_version

    def _fetch_remote_main(self) -> str:
        if not requests:
            raise RuntimeError("requests is not installed")
        url = f"{self.RAW_MAIN}?t={int(time.time())}"
        headers = {"Cache-Control": "no-cache", "Pragma": "no-cache"}
        r = requests.get(url, timeout=10, headers=headers)
        if r.status_code != 200:
            raise RuntimeError(f"HTTP {r.status_code}")
        return r.text

    def check_for_update(self):
        try:
            text = self._fetch_remote_main()
            m = re.search(r'^VERSION\s*=\s*"([^"]+)"', text, flags=re.MULTILINE)
            if not m:
                return {"available": False, "latest": self.current_version, "error": "VERSION not found"}
            latest = m.group(1).strip()
            available = latest != self.current_version
            return {"available": available, "latest": latest}
        except Exception as e:
            return {"available": False, "latest": self.current_version, "error": str(e)}

    def stage_update(self):
        """Download main.py as main_update.py and create an update script to swap after exit."""
        text = self._fetch_remote_main()
        update_py = os.path.join(PROJECT_DIR, "main_update.py")
        with open(update_py, "w", encoding="utf-8") as f:
            f.write(text)

        # Create a windows-friendly update script
        if sys.platform.startswith("win"):
            bat_path = os.path.join(PROJECT_DIR, "apply_update.bat")
            py_exe = sys.executable
            with open(bat_path, "w", encoding="utf-8") as f:
                f.write("@echo off\n")
                f.write("timeout /t 1 /nobreak >nul\n")
                f.write("copy /Y main_update.py main.py >nul\n")
                f.write("del main_update.py >nul\n")
                f.write(f"\"{py_exe}\" \"{os.path.join(PROJECT_DIR,'main.py')}\"\n")
            return {"success": True, "runner": bat_path}

        # Linux/macOS
        sh_path = os.path.join(PROJECT_DIR, "apply_update.sh")
        with open(sh_path, "w", encoding="utf-8") as f:
            f.write("#!/bin/sh\n")
            f.write("sleep 1\n")
            f.write("cp -f main_update.py main.py\n")
            f.write("rm -f main_update.py\n")
            f.write(f"\"{sys.executable}\" \"{os.path.join(PROJECT_DIR,'main.py')}\"\n")
        try:
            os.chmod(sh_path, 0o755)
        except Exception:
            pass
        return {"success": True, "runner": sh_path}


# ----------------------------
# UI
# ----------------------------
class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.cfg = Config()
        self.hist = TradeHistory()
        self.lang = self.cfg.language
        self.theme_name = self.cfg.theme
        self.updater = Updater(VERSION)

        _download_font_async(self._on_font_ready)
        self._setup_fonts()
        self._setup_theme()

        self.root.title(f"{self.t('app_title')} v{VERSION}")
        self.root.geometry("1300x850")
        self.root.minsize(1000, 700)

        self.build_ui()

    # ---- i18n ----
    def t(self, key: str) -> str:
        fa = {
            "app_title": "ماشین حساب ترید کریپتو",
            "help": "آموزش",
            "settings": "تنظیمات",
            "history": "تاریخچه",
            "charts": "نمودارها",
            "update": "آپدیت",
            "theme": "تم",
            "language": "زبان",
            "exchange": "صرافی",
            "symbol": "سمبل",
            "live_price": "قیمت لحظه‌ای",
            "capital": "سرمایه (USDT)",
            "risk": "درصد ریسک (%)",
            "fee": "کارمزد (%)",
            "save": "ذخیره",
            "entry": "قیمت ورود",
            "sl": "استاپ لاس (SL)",
            "pos_type": "نوع معامله",
            "lev": "لوریج",
            "calculate": "محاسبه",
            "results": "نتایج",
            "api_keys": "API Keys",
            "general": "عمومی",
            "export_csv": "خروجی CSV",
            "close": "بستن",
        }
        en = {
            "app_title": "Crypto Trading Calculator",
            "help": "Help/Learn",
            "settings": "Settings",
            "history": "History",
            "charts": "Charts",
            "update": "Update",
            "theme": "Theme",
            "language": "Language",
            "exchange": "Exchange",
            "symbol": "Symbol",
            "live_price": "Live Price",
            "capital": "Capital (USDT)",
            "risk": "Risk %",
            "fee": "Fee %",
            "save": "Save",
            "entry": "Entry",
            "sl": "Stop Loss",
            "pos_type": "Position",
            "lev": "Leverage",
            "calculate": "Calculate",
            "results": "Results",
            "api_keys": "API Keys",
            "general": "General",
            "export_csv": "Export CSV",
            "close": "Close",
        }
        table = fa if self.lang == "fa" else en
        return table.get(key, key)

    # ---- theme/fonts ----
    def _on_font_ready(self):
        try:
            self.root.after(0, lambda: (self._setup_fonts(), self.build_ui()))
        except Exception:
            pass

    def _setup_fonts(self):
        if os.path.exists(FONT_PATH):
            _load_custom_font_windows(FONT_PATH)
        fams = tkfont.families()
        self.ff = "Vazirmatn" if "Vazirmatn" in fams else ("Segoe UI" if "Segoe UI" in fams else "Arial")
        self.f_h1 = (self.ff, 18, "bold")
        self.f_h2 = (self.ff, 13, "bold")
        self.f_b = (self.ff, 11)
        self.f_bb = (self.ff, 11, "bold")

    def _setup_theme(self):
        if self.theme_name == "light":
            self.theme = {
                "bg": "#f3f4f6",
                "fg": "#111827",
                "card": "#ffffff",
                "input": "#ffffff",
                "border": "#e5e7eb",
                "primary": "#2563eb",
                "primary_fg": "#ffffff",
            }
        else:
            self.theme = {
                "bg": "#0b1220",
                "fg": "#e5e7eb",
                "card": "#152033",
                "input": "#1f2a44",
                "border": "#25324d",
                "primary": "#3b82f6",
                "primary_fg": "#ffffff",
            }

    def _apply_ttk_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TLabel", font=self.f_b)
        style.configure(
            "Treeview",
            background=self.theme["input"],
            foreground=self.theme["fg"],
            fieldbackground=self.theme["input"],
            rowheight=24,
        )
        style.configure("Treeview.Heading", font=self.f_bb)
        style.map("Treeview", background=[("selected", self.theme["primary"])])

    # ---- build UI ----
    def build_ui(self):
        for w in self.root.winfo_children():
            w.destroy()

        self._setup_theme()
        self.root.configure(bg=self.theme["bg"])
        self._apply_ttk_styles()

        header = tk.Frame(self.root, bg=self.theme["card"], height=56)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header,
            text=f"📊 {self.t('app_title')}",
            bg=self.theme["card"],
            fg=self.theme["fg"],
            font=self.f_h1,
        ).pack(side="left", padx=16)

        right = tk.Frame(header, bg=self.theme["card"])
        right.pack(side="right", padx=12)

        # Language selector (restored)
        tk.Label(right, text=self.t("language"), bg=self.theme["card"], fg=self.theme["fg"], font=self.f_b).pack(side="left", padx=(0, 6))
        self.var_lang = tk.StringVar(value=self.lang)
        cb_lang = ttk.Combobox(right, values=["fa", "en"], textvariable=self.var_lang, state="readonly", width=4)
        cb_lang.pack(side="left", padx=6)
        cb_lang.bind("<<ComboboxSelected>>", lambda e: self.set_language(self.var_lang.get()))

        self._hbtn(right, f"📚 {self.t('help')}", self.open_help)
        self._hbtn(right, f"⚙️ {self.t('settings')}", self.open_settings)
        self._hbtn(right, f"📋 {self.t('history')}", self.open_history)
        self._hbtn(right, f"📈 {self.t('charts')}", self.open_charts)
        self._hbtn(right, f"🔄 {self.t('update')}", self.check_update)
        self._hbtn(right, "🌓", self.toggle_theme)

        body = tk.Frame(self.root, bg=self.theme["bg"])
        body.pack(fill="both", expand=True)

        canvas = tk.Canvas(body, bg=self.theme["bg"], highlightthickness=0)
        vscroll = ttk.Scrollbar(body, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vscroll.set)
        vscroll.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        self.content = tk.Frame(canvas, bg=self.theme["bg"])
        canvas.create_window((0, 0), window=self.content, anchor="nw")
        self.content.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        self._card_main()

    def _hbtn(self, parent, text, cmd):
        tk.Button(
            parent,
            text=text,
            command=cmd,
            bg=self.theme["card"],
            fg=self.theme["fg"],
            font=self.f_bb,
            relief="flat",
            activebackground=self.theme["bg"],
            activeforeground=self.theme["fg"],
        ).pack(side="left", padx=6)

    def _card(self, title):
        outer = tk.Frame(self.content, bg=self.theme["card"], bd=1, relief="solid")
        outer.pack(fill="x", padx=18, pady=10)
        tk.Label(outer, text=title, bg=self.theme["card"], fg=self.theme["fg"], font=self.f_h2).pack(anchor="w", padx=12, pady=10)
        inner = tk.Frame(outer, bg=self.theme["card"])
        inner.pack(fill="x", padx=12, pady=(0, 12))
        return inner

    def _entry_row(self, parent, label, default):
        row = tk.Frame(parent, bg=self.theme["card"])
        row.pack(fill="x", pady=6)
        tk.Label(row, text=label, bg=self.theme["card"], fg=self.theme["fg"], font=self.f_b, width=16, anchor="w").pack(side="left")
        e = tk.Entry(row, bg=self.theme["input"], fg=self.theme["fg"], insertbackground=self.theme["fg"], relief="flat", font=self.f_b)
        e.pack(side="left", fill="x", expand=True)
        if default != "":
            e.insert(0, str(default))
        return e

    def _card_main(self):
        # Exchange
        c1 = self._card("Exchange")
        self.var_ex = tk.StringVar(value=self.cfg.selected_exchange)
        cb_ex = ttk.Combobox(c1, values=list(EXCHANGES.keys()), textvariable=self.var_ex, state="readonly")
        cb_ex.pack(anchor="w")

        self.var_symbol = tk.StringVar(value="BTCUSDT")
        cb_sym = ttk.Combobox(c1, values=["BTCUSDT", "ETHUSDT", "SOLUSDT", "TONUSDT", "DOGEUSDT"], textvariable=self.var_symbol, state="readonly")
        cb_sym.pack(anchor="w", pady=6)

        self.lbl_price = tk.Label(c1, text="---", bg=self.theme["card"], fg=self.theme["fg"], font=self.f_bb)
        self.lbl_price.pack(anchor="w")
        tk.Button(c1, text=self.t("live_price"), command=self.fetch_price, bg=self.theme["primary"], fg=self.theme["primary_fg"], relief="flat", font=self.f_bb).pack(anchor="w", pady=6)

        # Capital/Risk
        c2 = self._card("Capital & Risk")
        self.e_cap = self._entry_row(c2, self.t("capital"), self.cfg.capital)
        self.e_risk = self._entry_row(c2, self.t("risk"), self.cfg.risk_percent)
        self.e_fee = self._entry_row(c2, self.t("fee"), self.cfg.fee_percent)
        tk.Button(c2, text=self.t("save"), command=self.save_main_settings, bg=self.theme["primary"], fg=self.theme["primary_fg"], relief="flat", font=self.f_bb).pack(anchor="w", pady=8)

        # Trade
        c3 = self._card("Trade")
        self.e_entry = self._entry_row(c3, self.t("entry"), "")
        self.e_sl = self._entry_row(c3, self.t("sl"), "")

        row = tk.Frame(c3, bg=self.theme["card"])
        row.pack(fill="x", pady=6)
        tk.Label(row, text=self.t("pos_type"), bg=self.theme["card"], fg=self.theme["fg"], font=self.f_b, width=16, anchor="w").pack(side="left")
        self.var_side = tk.StringVar(value="LONG")
        cb_side = ttk.Combobox(row, values=["LONG", "SHORT"], state="readonly", textvariable=self.var_side, width=8)
        cb_side.pack(side="left")

        self.e_lev = self._entry_row(c3, self.t("lev"), "10")
        self.e_tp1 = self._entry_row(c3, "TP1", "")
        self.e_tp2 = self._entry_row(c3, "TP2", "")
        self.e_tp3 = self._entry_row(c3, "TP3", "")

        tk.Button(c3, text=self.t("calculate"), command=self.calculate, bg=self.theme["primary"], fg=self.theme["primary_fg"], relief="flat", font=self.f_bb).pack(anchor="w", pady=10)

        # Results
        c4 = self._card(self.t("results"))
        self.txt = tk.Text(c4, height=10, bg=self.theme["input"], fg=self.theme["fg"], insertbackground=self.theme["fg"], relief="flat", font=("Consolas", 10))
        self.txt.pack(fill="x")

    # ---- actions ----
    def set_language(self, lang: str):
        self.lang = lang
        self.cfg.language = lang
        self.cfg.save()
        self.root.title(f"{self.t('app_title')} v{VERSION}")
        self.build_ui()

    def toggle_theme(self):
        self.theme_name = "light" if self.theme_name == "dark" else "dark"
        self.cfg.theme = self.theme_name
        self.cfg.save()
        self.build_ui()

    def save_main_settings(self):
        try:
            self.cfg.capital = float(self.e_cap.get())
            self.cfg.risk_percent = float(self.e_risk.get())
            self.cfg.fee_percent = float(self.e_fee.get())
            self.cfg.selected_exchange = self.var_ex.get()
            self.cfg.save()
        except Exception:
            self._toast(self.content, "Invalid settings")

    def fetch_price(self):
        # Placeholder (kept stable)
        sym = self.var_symbol.get()
        price = 98500.0 if sym.startswith("BTC") else (2700.0 if sym.startswith("ETH") else 1.0)
        self.lbl_price.config(text=str(price))
        self.e_entry.delete(0, tk.END)
        self.e_entry.insert(0, str(price))

    def calculate(self):
        try:
            entry = float(self.e_entry.get())
            sl = float(self.e_sl.get())
            cap = float(self.e_cap.get())
            risk_pct = float(self.e_risk.get())
            fee_pct = float(self.e_fee.get())
            lev = float(self.e_lev.get())
            side = self.var_side.get()
            sym = self.var_symbol.get()

            risk_amt = cap * (risk_pct / 100.0)
            sl_diff = abs(entry - sl) / entry
            if sl_diff <= 0:
                raise ValueError("SL diff is 0")

            pos_size = risk_amt / sl_diff  # USDT size without leverage
            qty = (pos_size * lev) / entry

            tps = []
            for e in [self.e_tp1, self.e_tp2, self.e_tp3]:
                if e.get().strip():
                    tps.append(float(e.get()))

            out = []
            out.append(f"{datetime.now().strftime('%Y-%m-%d %H:%M')} | {sym} {side}")
            out.append(f"Entry: {entry} | SL: {sl} | Lev: {lev}x")
            out.append(f"Position Size: {pos_size:.2f} USDT | Qty: {qty:.6f}")
            out.append(f"Risk: {risk_amt:.2f} USDT | Fee%: {fee_pct}")

            last_pnl = 0.0
            for i, tp in enumerate(tps, start=1):
                pnl_gross = abs(tp - entry) * qty
                # Simple fee model: entry+exit taker fee on notional (approx)
                fee = (pos_size * lev) * (fee_pct / 100.0) * 2
                pnl = pnl_gross - fee
                last_pnl = pnl
                out.append(f"TP{i}: {tp} -> PnL: {pnl:+.2f} USDT")

            self.txt.insert("1.0", "\n".join(out) + "\n\n")

            self.hist.add_trade(
                {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "exchange": self.var_ex.get(),
                    "symbol": sym,
                    "side": side,
                    "entry": entry,
                    "sl": sl,
                    "leverage": lev,
                    "risk_percent": risk_pct,
                    "position_size": round(pos_size, 4),
                    "qty": round(qty, 8),
                    "last_tp_pnl": round(last_pnl, 4),
                }
            )

        except Exception as e:
            self._toast(self.content, f"Calc error: {e}")

    def _toast(self, parent, text: str):
        # themed non-blocking toast instead of messagebox
        top = tk.Toplevel(self.root)
        top.configure(bg=self.theme["card"])
        top.overrideredirect(True)
        top.attributes("-topmost", True)
        tk.Label(top, text=text, bg=self.theme["card"], fg=self.theme["fg"], font=self.f_bb).pack(padx=12, pady=10)
        x = self.root.winfo_rootx() + 40
        y = self.root.winfo_rooty() + 80
        top.geometry(f"+{x}+{y}")
        top.after(1800, top.destroy)

    # ---- windows (themed) ----
    def open_settings(self):
        w = tk.Toplevel(self.root)
        w.title(self.t("settings"))
        w.configure(bg=self.theme["bg"])
        w.geometry("900x600")

        nb = ttk.Notebook(w)
        nb.pack(fill="both", expand=True, padx=10, pady=10)

        tab_general = tk.Frame(nb, bg=self.theme["bg"])
        tab_api = tk.Frame(nb, bg=self.theme["bg"])
        nb.add(tab_general, text=self.t("general"))
        nb.add(tab_api, text=self.t("api_keys"))

        # General (restored language setting)
        tk.Label(tab_general, text=self.t("language"), bg=self.theme["bg"], fg=self.theme["fg"], font=self.f_bb).pack(anchor="w", padx=10, pady=(10, 6))
        var = tk.StringVar(value=self.lang)
        cb = ttk.Combobox(tab_general, values=["fa", "en"], textvariable=var, state="readonly", width=6)
        cb.pack(anchor="w", padx=10)

        tk.Label(tab_general, text=self.t("theme"), bg=self.theme["bg"], fg=self.theme["fg"], font=self.f_bb).pack(anchor="w", padx=10, pady=(16, 6))
        var_theme = tk.StringVar(value=self.theme_name)
        cb_t = ttk.Combobox(tab_general, values=["dark", "light"], textvariable=var_theme, state="readonly", width=8)
        cb_t.pack(anchor="w", padx=10)

        def save_general():
            self.set_language(var.get())
            self.theme_name = var_theme.get()
            self.cfg.theme = self.theme_name
            self.cfg.save()
            self.build_ui()

        tk.Button(tab_general, text=self.t("save"), command=save_general, bg=self.theme["primary"], fg=self.theme["primary_fg"], relief="flat", font=self.f_bb).pack(anchor="w", padx=10, pady=20)

        # API keys
        tk.Label(tab_api, text="API Key / Secret per exchange", bg=self.theme["bg"], fg=self.theme["fg"], font=self.f_bb).pack(anchor="w", padx=10, pady=10)

        holder = tk.Frame(tab_api, bg=self.theme["bg"])
        holder.pack(fill="both", expand=True, padx=10, pady=10)

        cvs = tk.Canvas(holder, bg=self.theme["bg"], highlightthickness=0)
        sb = ttk.Scrollbar(holder, orient="vertical", command=cvs.yview)
        cvs.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        cvs.pack(side="left", fill="both", expand=True)

        inner = tk.Frame(cvs, bg=self.theme["bg"])
        cvs.create_window((0, 0), window=inner, anchor="nw")
        inner.bind("<Configure>", lambda e: cvs.configure(scrollregion=cvs.bbox("all")))

        tk.Label(inner, text="Exchange", bg=self.theme["bg"], fg=self.theme["fg"], font=self.f_bb, width=12, anchor="w").grid(row=0, column=0, padx=6, pady=6)
        tk.Label(inner, text="API Key", bg=self.theme["bg"], fg=self.theme["fg"], font=self.f_bb, width=36, anchor="w").grid(row=0, column=1, padx=6, pady=6)
        tk.Label(inner, text="Secret", bg=self.theme["bg"], fg=self.theme["fg"], font=self.f_bb, width=36, anchor="w").grid(row=0, column=2, padx=6, pady=6)

        self._api_rows = {}
        for i, ex in enumerate(EXCHANGES.keys(), start=1):
            cred = self.cfg.get_api_credentials(ex)
            tk.Label(inner, text=ex, bg=self.theme["bg"], fg=self.theme["fg"], font=self.f_b, anchor="w").grid(row=i, column=0, padx=6, pady=4, sticky="w")

            e1 = tk.Entry(inner, bg=self.theme["input"], fg=self.theme["fg"], insertbackground=self.theme["fg"], relief="flat", width=40)
            e1.grid(row=i, column=1, padx=6, pady=4, sticky="ew")
            e1.insert(0, cred.get("api_key", ""))

            e2 = tk.Entry(inner, bg=self.theme["input"], fg=self.theme["fg"], insertbackground=self.theme["fg"], relief="flat", width=40, show="*")
            e2.grid(row=i, column=2, padx=6, pady=4, sticky="ew")
            e2.insert(0, cred.get("api_secret", ""))

            self._api_rows[ex] = (e1, e2)

        def save_api():
            for ex, (k, s) in self._api_rows.items():
                self.cfg.set_api_credentials(ex, k.get().strip(), s.get().strip())
            self._toast(self.content, "API keys saved")

        tk.Button(tab_api, text=self.t("save"), command=save_api, bg=self.theme["primary"], fg=self.theme["primary_fg"], relief="flat", font=self.f_bb).pack(anchor="w", padx=10, pady=10)

    def open_history(self):
        w = tk.Toplevel(self.root)
        w.title(self.t("history"))
        w.configure(bg=self.theme["bg"])
        w.geometry("950x520")

        cols = ("timestamp", "exchange", "symbol", "side", "entry", "sl", "leverage", "risk_percent", "position_size", "qty", "last_tp_pnl")
        tv = ttk.Treeview(w, columns=cols, show="headings")
        for c in cols:
            tv.heading(c, text=c)
            tv.column(c, width=120, anchor="w")
        tv.pack(fill="both", expand=True, padx=10, pady=10)

        for t in self.hist.trades:
            tv.insert("", "end", values=tuple(t.get(c, "") for c in cols))

        bar = tk.Frame(w, bg=self.theme["bg"])
        bar.pack(fill="x", padx=10, pady=(0, 10))

        def export():
            fn = os.path.join(APP_DATA_DIR, "history_export.csv")
            ok = self.hist.export_csv(fn)
            self._toast(self.content, f"Exported: {fn}" if ok else "No data")

        tk.Button(bar, text=self.t("export_csv"), command=export, bg=self.theme["primary"], fg=self.theme["primary_fg"], relief="flat", font=self.f_bb).pack(side="left")

    def open_charts(self):
        w = tk.Toplevel(self.root)
        w.title(self.t("charts"))
        w.configure(bg=self.theme["bg"])
        w.geometry("900x520")

        cv = tk.Canvas(w, bg=self.theme["card"], highlightthickness=0)
        cv.pack(fill="both", expand=True, padx=10, pady=10)

        # Simple equity curve from last_tp_pnl
        vals = [float(t.get("last_tp_pnl", 0) or 0) for t in self.hist.trades]
        if not vals:
            cv.create_text(450, 250, text="No data", fill=self.theme["fg"], font=self.f_h2)
            return

        eq = []
        s = 0.0
        for v in vals:
            s += v
            eq.append(s)

        w_can = 860
        h_can = 460
        pad = 30
        mx = max(eq)
        mn = min(eq)
        rng = (mx - mn) if mx != mn else 1.0

        # axes
        cv.create_rectangle(pad, pad, w_can, h_can, outline=self.theme["border"], width=1)

        def xy(i, val):
            x = pad + (i / max(1, len(eq) - 1)) * (w_can - pad * 2)
            y = h_can - pad - ((val - mn) / rng) * (h_can - pad * 2)
            return x, y

        prev = None
        for i, v in enumerate(eq):
            x, y = xy(i, v)
            if prev:
                cv.create_line(prev[0], prev[1], x, y, fill=self.theme["primary"], width=2)
            prev = (x, y)

        cv.create_text(pad + 10, pad + 10, text=f"Equity: {eq[-1]:+.2f}", fill=self.theme["fg"], anchor="nw", font=self.f_bb)

    def open_help(self):
        w = tk.Toplevel(self.root)
        w.title(self.t("help"))
        w.configure(bg=self.theme["bg"])
        w.geometry("980x650")

        nb = ttk.Notebook(w)
        nb.pack(fill="both", expand=True, padx=10, pady=10)

        tab_terms = tk.Frame(nb, bg=self.theme["bg"])
        tab_ex = tk.Frame(nb, bg=self.theme["bg"])
        tab_api = tk.Frame(nb, bg=self.theme["bg"])
        nb.add(tab_terms, text="Terms")
        nb.add(tab_ex, text="Exchanges")
        nb.add(tab_api, text="API Keys")

        # Terms
        txt = tk.Text(tab_terms, bg=self.theme["input"], fg=self.theme["fg"], insertbackground=self.theme["fg"], relief="flat", font=(self.ff, 11))
        txt.pack(fill="both", expand=True, padx=10, pady=10)
        if self.lang == "fa":
            for k, v in TERMS_FA.items():
                txt.insert("end", f"{k}\n{v}\n\n")
        else:
            txt.insert("end", "TP/SL/Leverage glossary will be expanded.\n")
        txt.configure(state="disabled")

        # Exchanges
        wrap = tk.Frame(tab_ex, bg=self.theme["bg"])
        wrap.pack(fill="both", expand=True, padx=10, pady=10)
        for ex, info in EXCHANGES.items():
            row = tk.Frame(wrap, bg=self.theme["card"], bd=1, relief="solid")
            row.pack(fill="x", pady=6)
            tk.Label(row, text=ex, bg=self.theme["card"], fg=self.theme["fg"], font=self.f_bb, width=12, anchor="w").pack(side="left", padx=10, pady=10)
            tk.Label(row, text=info.get("home", ""), bg=self.theme["card"], fg=self.theme["fg"], font=self.f_b, anchor="w").pack(side="left", padx=10)
            tk.Button(row, text="Open", command=lambda u=info.get("home", ""): self._open_url(u), bg=self.theme["primary"], fg=self.theme["primary_fg"], relief="flat", font=self.f_bb).pack(side="right", padx=10)

        # API Keys
        api_txt = tk.Text(tab_api, bg=self.theme["input"], fg=self.theme["fg"], insertbackground=self.theme["fg"], relief="flat", font=(self.ff, 11))
        api_txt.pack(fill="both", expand=True, padx=10, pady=10)
        api_txt.insert("end", "Security tip: for price/tracking use Read-Only permissions (no trading/withdraw).\n\n")
        api_txt.insert("end", "Binance: create keys via API Management (guide link)\n")
        api_txt.insert("end", f"- Guide: {EXCHANGES['Binance']['api_help']}\n- Docs: {EXCHANGES['Binance']['api_docs']}\n\n")
        api_txt.insert("end", "Bybit: API Management URLs\n")
        api_txt.insert("end", f"- Mainnet: {EXCHANGES['Bybit']['api_mgmt']}\n- Testnet: {EXCHANGES['Bybit']['testnet_api_mgmt']}\n- Guide: {EXCHANGES['Bybit']['api_help']}\n\n")
        api_txt.insert("end", "OKX: API docs (see API key creation section)\n")
        api_txt.insert("end", f"- Docs: {EXCHANGES['OKX']['api_docs']}\n\n")
        api_txt.insert("end", "Other exchanges: open your profile/security section and look for API / API Management.\n")
        api_txt.configure(state="disabled")

    def _open_url(self, url: str):
        if not url:
            return
        try:
            import webbrowser
            webbrowser.open(url)
        except Exception:
            pass

    # ---- update ----
    def check_update(self):
        info = self.updater.check_for_update()
        if info.get("error"):
            self._toast(self.content, f"Update check failed: {info['error']}")
            return
        if not info.get("available"):
            self._toast(self.content, "Up to date")
            return

        # themed confirm dialog
        dlg = tk.Toplevel(self.root)
        dlg.title(self.t("update"))
        dlg.configure(bg=self.theme["bg"])
        dlg.geometry("420x180")
        tk.Label(dlg, text=f"New version: {info.get('latest')}\nInstall now?", bg=self.theme["bg"], fg=self.theme["fg"], font=self.f_bb).pack(pady=20)

        btns = tk.Frame(dlg, bg=self.theme["bg"])
        btns.pack(pady=10)

        def do():
            try:
                st = self.updater.stage_update()
                runner = st.get("runner")
                dlg.destroy()
                # Start runner then quit
                if runner and sys.platform.startswith("win"):
                    os.startfile(runner)
                elif runner:
                    subprocess.Popen([runner], cwd=PROJECT_DIR)
                self.root.after(200, self.root.destroy)
            except Exception as e:
                dlg.destroy()
                self._toast(self.content, f"Update failed: {e}")

        tk.Button(btns, text="Yes", command=do, bg=self.theme["primary"], fg=self.theme["primary_fg"], relief="flat", font=self.f_bb, width=10).pack(side="left", padx=8)
        tk.Button(btns, text="No", command=dlg.destroy, bg=self.theme["card"], fg=self.theme["fg"], relief="flat", font=self.f_bb, width=10).pack(side="left", padx=8)


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
