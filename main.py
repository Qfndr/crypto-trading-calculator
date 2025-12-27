import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
from datetime import datetime
from config import Config
from trade_history import TradeHistory

VERSION = "1.1.0"

class CryptoTradingCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title(f"ماشین حساب ترید کریپتو v{VERSION}")
        self.root.geometry("900x750")
        self.root.minsize(850, 700)
        
        # Load configuration
        self.config = Config()
        self.history = TradeHistory()
        
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
        
        # Theme colors
        self.themes = {
            'light': {
                'bg': '#f0f0f0',
                'fg': '#000000',
                'entry_bg': '#ffffff',
                'button_bg': '#e0e0e0',
                'text_bg': '#ffffff',
                'frame_bg': '#f0f0f0'
            },
            'dark': {
                'bg': '#1e1e1e',
                'fg': '#ffffff',
                'entry_bg': '#2d2d2d',
                'button_bg': '#3d3d3d',
                'text_bg': '#2d2d2d',
                'frame_bg': '#252525'
            }
        }
        
        self.current_theme = self.config.theme
        self.tp_entries = []
        
        self.create_widgets()
        self.apply_theme()
        
    def create_widgets(self):
        # Main container with scrollbar
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Canvas for scrolling
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Title and theme toggle
        header_frame = ttk.Frame(scrollable_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        title = ttk.Label(header_frame, text=f"ماشین حساب ترید کریپتو v{VERSION}", 
                         font=('Arial', 16, 'bold'))
        title.pack(side=tk.LEFT, padx=5)
        
        self.theme_button = ttk.Button(header_frame, text="🌙 دارک مود", 
                                      command=self.toggle_theme, width=15)
        self.theme_button.pack(side=tk.RIGHT, padx=5)
        
        # Menu buttons
        menu_frame = ttk.Frame(scrollable_frame)
        menu_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(menu_frame, text="📊 تاریخچه", command=self.show_history, width=15).pack(side=tk.LEFT, padx=2)
        ttk.Button(menu_frame, text="💾 Export CSV", command=self.export_csv, width=15).pack(side=tk.LEFT, padx=2)
        ttk.Button(menu_frame, text="🗑️ پاک کردن تاریخچه", command=self.clear_history, width=18).pack(side=tk.LEFT, padx=2)
        
        # Exchange Selection
        exchange_frame = ttk.LabelFrame(scrollable_frame, text="انتخاب صرافی", padding="10")
        exchange_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(exchange_frame, text="صرافی:").grid(row=0, column=0, sticky=tk.W, pady=5, padx=5)
        self.exchange_combo = ttk.Combobox(exchange_frame, values=list(self.exchanges.keys()), 
                                          width=18, state="readonly")
        self.exchange_combo.set(self.config.selected_exchange)
        self.exchange_combo.grid(row=0, column=1, pady=5, padx=5, sticky=tk.W)
        self.exchange_combo.bind('<<ComboboxSelected>>', self.on_exchange_change)
        
        ttk.Label(exchange_frame, text="نوع سفارش:").grid(row=0, column=2, sticky=tk.W, pady=5, padx=5)
        self.order_type_combo = ttk.Combobox(exchange_frame, values=["Maker", "Taker"], 
                                             width=18, state="readonly")
        self.order_type_combo.set("Taker" if self.config.order_type == "taker" else "Maker")
        self.order_type_combo.grid(row=0, column=3, pady=5, padx=5, sticky=tk.W)
        self.order_type_combo.bind('<<ComboboxSelected>>', self.on_order_type_change)
        
        # Capital Settings
        settings_frame = ttk.LabelFrame(scrollable_frame, text="تنظیمات سرمایه", padding="10")
        settings_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(settings_frame, text="سرمایه کل (USDT):").grid(row=0, column=0, sticky=tk.W, pady=5, padx=5)
        self.capital_entry = ttk.Entry(settings_frame, width=20)
        self.capital_entry.insert(0, str(self.config.capital))
        self.capital_entry.grid(row=0, column=1, pady=5, padx=5)
        
        ttk.Label(settings_frame, text="درصد ریسک (%):").grid(row=0, column=2, sticky=tk.W, pady=5, padx=5)
        self.risk_entry = ttk.Entry(settings_frame, width=20)
        self.risk_entry.insert(0, str(self.config.risk_percent))
        self.risk_entry.grid(row=0, column=3, pady=5, padx=5)
        
        ttk.Label(settings_frame, text="کارمزد (%):").grid(row=1, column=0, sticky=tk.W, pady=5, padx=5)
        self.fee_entry = ttk.Entry(settings_frame, width=20)
        self.fee_entry.insert(0, str(self.config.fee_percent))
        self.fee_entry.grid(row=1, column=1, pady=5, padx=5)
        
        ttk.Button(settings_frame, text="ذخیره تنظیمات", command=self.save_settings_clicked).grid(
            row=1, column=2, columnspan=2, pady=10, padx=5)
        
        # Trade Input
        trade_frame = ttk.LabelFrame(scrollable_frame, text="اطلاعات معامله", padding="10")
        trade_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(trade_frame, text="قیمت ورود:").grid(row=0, column=0, sticky=tk.W, pady=5, padx=5)
        self.entry_price = ttk.Entry(trade_frame, width=20)
        self.entry_price.grid(row=0, column=1, pady=5, padx=5)
        
        ttk.Label(trade_frame, text="استاپ لاس (SL):").grid(row=0, column=2, sticky=tk.W, pady=5, padx=5)
        self.stop_loss = ttk.Entry(trade_frame, width=20)
        self.stop_loss.grid(row=0, column=3, pady=5, padx=5)
        
        # Multiple Take Profits
        ttk.Label(trade_frame, text="تیک پرافیت 1:").grid(row=1, column=0, sticky=tk.W, pady=5, padx=5)
        self.tp1_entry = ttk.Entry(trade_frame, width=20)
        self.tp1_entry.grid(row=1, column=1, pady=5, padx=5)
        self.tp_entries.append(self.tp1_entry)
        
        ttk.Label(trade_frame, text="تیک پرافیت 2:").grid(row=1, column=2, sticky=tk.W, pady=5, padx=5)
        self.tp2_entry = ttk.Entry(trade_frame, width=20)
        self.tp2_entry.grid(row=1, column=3, pady=5, padx=5)
        self.tp_entries.append(self.tp2_entry)
        
        ttk.Label(trade_frame, text="تیک پرافیت 3:").grid(row=2, column=0, sticky=tk.W, pady=5, padx=5)
        self.tp3_entry = ttk.Entry(trade_frame, width=20)
        self.tp3_entry.grid(row=2, column=1, pady=5, padx=5)
        self.tp_entries.append(self.tp3_entry)
        
        ttk.Label(trade_frame, text="نوع معامله:").grid(row=2, column=2, sticky=tk.W, pady=5, padx=5)
        self.position_type = ttk.Combobox(trade_frame, values=["LONG", "SHORT"], width=18, state="readonly")
        self.position_type.set("LONG")
        self.position_type.grid(row=2, column=3, pady=5, padx=5)
        
        ttk.Label(trade_frame, text="لوریج:").grid(row=3, column=0, sticky=tk.W, pady=5, padx=5)
        self.leverage = ttk.Entry(trade_frame, width=20)
        self.leverage.insert(0, "10")
        self.leverage.grid(row=3, column=1, pady=5, padx=5)
        
        # Notes
        ttk.Label(trade_frame, text="یادداشت:").grid(row=3, column=2, sticky=tk.W, pady=5, padx=5)
        self.notes_entry = ttk.Entry(trade_frame, width=20)
        self.notes_entry.grid(row=3, column=3, pady=5, padx=5)
        
        ttk.Button(trade_frame, text="محاسبه", command=self.calculate).grid(
            row=4, column=0, columnspan=4, pady=15)
        
        # Results
        results_frame = ttk.LabelFrame(scrollable_frame, text="نتایج محاسبات", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.results_text = tk.Text(results_frame, height=18, width=100, font=('Courier', 9))
        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        results_scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=self.results_text.yview)
        results_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.results_text.config(yscrollcommand=results_scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.on_exchange_change()
    
    def toggle_theme(self):
        self.current_theme = 'dark' if self.current_theme == 'light' else 'light'
        self.apply_theme()
        self.save_settings_clicked(show_message=False)
    
    def apply_theme(self):
        theme = self.themes[self.current_theme]
        
        self.root.configure(bg=theme['bg'])
        self.results_text.configure(bg=theme['text_bg'], fg=theme['fg'], insertbackground=theme['fg'])
        
        if self.current_theme == 'dark':
            self.theme_button.configure(text="☀️ لایت مود")
        else:
            self.theme_button.configure(text="🌙 دارک مود")
    
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
    
    def save_settings_clicked(self, show_message=True):
        try:
            capital = float(self.capital_entry.get())
            risk_percent = float(self.risk_entry.get())
            fee_percent = float(self.fee_entry.get())
            exchange = self.exchange_combo.get()
            order_type = 'maker' if self.order_type_combo.get() == 'Maker' else 'taker'
            
            self.config.save_config(capital, risk_percent, fee_percent, exchange, order_type, self.current_theme)
            
            if show_message:
                messagebox.showinfo("موفق", "تنظیمات با موفقیت ذخیره شد!")
        except ValueError:
            if show_message:
                messagebox.showerror("خطا", "لطفا اعداد معتبر وارد کنید!")
    
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
                messagebox.showerror("خطا", "لطفا حداقل یک Take Profit وارد کنید!")
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
{'='*85}
                          نتایج محاسبات
{'='*85}

تاریخ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

صرافی و کارمزد:
{'='*85}
صرافی: {exchange} | نوع سفارش: {order_type} | کارمزد: {fee_percent}%

اطلاعات معامله:
{'='*85}
نوع: {position} | ورود: {entry_price:,.4f} | SL: {stop_loss:,.4f} | لوریج: {leverage}x

محاسبات ریسک:
{'='*85}
سرمایه: {capital:,.2f} USDT | ریسک: {risk_percent}% ({risk_amount:,.2f} USDT)

محاسبات پوزیشن:
{'='*85}
حجم مارجین: {position_size_usdt:,.2f} USDT
ارزش با لوریج: {position_value:,.2f} USDT
تعداد کوین: {quantity:,.6f}

کارمزدها:
{'='*85}
ورود: {entry_fee:,.2f} | خروج: {exit_fee:,.2f} | جمع: {total_fees:,.2f} USDT

زیان در SL:
{'='*85}
{loss_at_sl:,.2f} USDT ({(loss_at_sl/capital)*100:+.2f}%)

تیک پرافیت‌ها:
{'='*85}
"""
            
            tp_results = []
            for i, tp in enumerate(tps, 1):
                if position == "LONG":
                    profit_at_tp = (quantity * tp) - position_value - total_fees
                else:
                    profit_at_tp = position_value - (quantity * tp) - total_fees
                
                rr_ratio = abs(profit_at_tp / loss_at_sl) if loss_at_sl != 0 else 0
                tp_percent = ((tp - entry_price) / entry_price * 100) if position == "LONG" else ((entry_price - tp) / entry_price * 100)
                
                results += f"TP{i}: {tp:,.4f} USDT ({tp_percent:+.2f}%) → سود: {profit_at_tp:,.2f} USDT ({(profit_at_tp/capital)*100:+.2f}%) | R/R: {rr_ratio:.2f}:1\n"
                tp_results.append({'tp': tp, 'profit': profit_at_tp, 'rr': rr_ratio})
            
            results += f"\nقیمت لیکوییدیشن:\n{'='*85}\n{liquidation_price:,.4f} USDT\n"
            
            # Recommendations
            results += f"\nتوصیه‌ها:\n{'='*85}\n"
            best_rr = max(tp_results, key=lambda x: x['rr'])
            if best_rr['rr'] >= 2:
                results += f"✅ بهترین R/R: {best_rr['rr']:.2f}:1 در قیمت {best_rr['tp']:,.4f}\n"
            elif best_rr['rr'] < 1.5:
                results += "⚠️ نسبت R/R پایین است!\n"
            
            if notes:
                results += f"\n📝 یادداشت: {notes}\n"
            
            results += f"\n{'='*85}\n"
            
            self.results_text.delete('1.0', tk.END)
            self.results_text.insert('1.0', results)
            
            # Save to history
            trade_data = {
                'exchange': exchange,
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
            
        except ValueError:
            messagebox.showerror("خطا", "لطفا تمام فیلدها را با مقادیر معتبر پر کنید!")
        except Exception as e:
            messagebox.showerror("خطا", f"خطایی رخ داد: {str(e)}")
    
    def show_history(self):
        history_window = tk.Toplevel(self.root)
        history_window.title("تاریخچه معاملات")
        history_window.geometry("800x600")
        
        frame = ttk.Frame(history_window, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        text = tk.Text(frame, wrap=tk.WORD, font=('Courier', 9))
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text.config(yscrollcommand=scrollbar.set)
        
        trades = self.history.get_trades()
        if not trades:
            text.insert('1.0', "هیچ معامله‌ای ثبت نشده است.")
        else:
            for i, trade in enumerate(reversed(trades), 1):
                trade_text = f"""
{'='*70}
معامله #{i} - {trade.get('timestamp', 'N/A')}
{'='*70}
صرافی: {trade.get('exchange', 'N/A')} | نوع: {trade.get('position', 'N/A')}
ورود: {trade.get('entry_price', 0):,.4f} | SL: {trade.get('stop_loss', 0):,.4f}
لوریج: {trade.get('leverage', 0)}x | حجم: {trade.get('position_size', 0):,.2f} USDT
زیان SL: {trade.get('loss_at_sl', 0):,.2f} USDT
"""
                if 'notes' in trade and trade['notes']:
                    trade_text += f"یادداشت: {trade['notes']}\n"
                trade_text += "\n"
                text.insert(tk.END, trade_text)
        
        text.config(state=tk.DISABLED)
    
    def export_csv(self):
        if not self.history.trades:
            messagebox.showinfo("اطلاعات", "هیچ معامله‌ای برای Export وجود ندارد!")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=f"trades_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        
        if filename:
            if self.history.export_to_csv(filename):
                messagebox.showinfo("موفق", f"فایل با موفقیت ذخیره شد:\n{filename}")
            else:
                messagebox.showerror("خطا", "خطا در ذخیره فایل!")
    
    def clear_history(self):
        if messagebox.askyesno("تأیید", "آیا مطمئن هستید که می‌خواهید تاریخچه را پاک کنید?"):
            self.history.clear_history()
            messagebox.showinfo("موفق", "تاریخچه با موفقیت پاک شد!")

if __name__ == "__main__":
    root = tk.Tk()
    app = CryptoTradingCalculator(root)
    root.mainloop()
