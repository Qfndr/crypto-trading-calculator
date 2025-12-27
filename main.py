import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

class CryptoTradingCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("ماشین حساب ترید کریپتو")
        self.root.geometry("850x950")
        self.root.resizable(False, False)
        
        # Exchange presets with maker and taker fees
        self.exchanges = {
            "Binance": {
                "maker": 0.02,
                "taker": 0.04,
                "default": 0.04
            },
            "CoinEx": {
                "maker": 0.16,
                "taker": 0.26,
                "default": 0.26
            },
            "Bybit": {
                "maker": 0.02,
                "taker": 0.055,
                "default": 0.055
            },
            "OKX": {
                "maker": 0.02,
                "taker": 0.05,
                "default": 0.05
            },
            "KuCoin": {
                "maker": 0.02,
                "taker": 0.06,
                "default": 0.06
            },
            "Gate.io": {
                "maker": 0.015,
                "taker": 0.05,
                "default": 0.05
            },
            "Bitget": {
                "maker": 0.02,
                "taker": 0.06,
                "default": 0.06
            },
            "MEXC": {
                "maker": 0.0,
                "taker": 0.02,
                "default": 0.02
            },
            "Nobitex": {
                "maker": 0.35,
                "taker": 0.35,
                "default": 0.35
            },
            "Wallex": {
                "maker": 0.2,
                "taker": 0.2,
                "default": 0.2
            },
            "Exir": {
                "maker": 0.35,
                "taker": 0.35,
                "default": 0.35
            },
            "دستی (Custom)": {
                "maker": 0.15,
                "taker": 0.15,
                "default": 0.15
            }
        }
        
        # Load saved data
        self.load_settings()
        
        self.create_widgets()
        
    def load_settings(self):
        """Load saved settings from JSON file"""
        self.settings_file = 'settings.json'
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.capital = data.get('capital', 100)
                    self.risk_percent = data.get('risk_percent', 1)
                    self.fee_percent = data.get('fee_percent', 0.04)
                    self.selected_exchange = data.get('exchange', 'Binance')
                    self.order_type = data.get('order_type', 'taker')
            except:
                self.set_defaults()
        else:
            self.set_defaults()
    
    def set_defaults(self):
        self.capital = 100
        self.risk_percent = 1
        self.fee_percent = 0.04
        self.selected_exchange = 'Binance'
        self.order_type = 'taker'
    
    def save_settings(self):
        """Save settings to JSON file"""
        data = {
            'capital': self.capital,
            'risk_percent': self.risk_percent,
            'fee_percent': self.fee_percent,
            'exchange': self.selected_exchange,
            'order_type': self.order_type
        }
        with open(self.settings_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    
    def on_exchange_change(self, event=None):
        """Update fee when exchange is changed"""
        exchange = self.exchange_combo.get()
        if exchange in self.exchanges:
            order_type = self.order_type_combo.get()
            if order_type == "Maker":
                fee = self.exchanges[exchange]['maker']
            else:
                fee = self.exchanges[exchange]['taker']
            
            self.fee_entry.config(state='normal')
            self.fee_entry.delete(0, tk.END)
            self.fee_entry.insert(0, str(fee))
            
            # Disable manual edit for preset exchanges
            if exchange != "دستی (Custom)":
                self.fee_entry.config(state='readonly')
            else:
                self.fee_entry.config(state='normal')
    
    def on_order_type_change(self, event=None):
        """Update fee when order type is changed"""
        self.on_exchange_change()
    
    def create_widgets(self):
        # Main container with scrollbar
        main_canvas = tk.Canvas(self.root)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=main_canvas.yview)
        scrollable_frame = ttk.Frame(main_canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
        main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)
        
        main_frame = ttk.Frame(scrollable_frame, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title = ttk.Label(main_frame, text="ماشین حساب ترید کریپتو", 
                         font=('Arial', 16, 'bold'))
        title.grid(row=0, column=0, columnspan=2, pady=10)
        
        # Exchange Selection Frame
        exchange_frame = ttk.LabelFrame(main_frame, text="انتخاب صرافی", padding="10")
        exchange_frame.grid(row=1, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E))
        
        ttk.Label(exchange_frame, text="صرافی:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.exchange_combo = ttk.Combobox(exchange_frame, 
                                          values=list(self.exchanges.keys()), 
                                          width=18, 
                                          state="readonly")
        self.exchange_combo.set(self.selected_exchange)
        self.exchange_combo.grid(row=0, column=1, pady=5, sticky=tk.W)
        self.exchange_combo.bind('<<ComboboxSelected>>', self.on_exchange_change)
        
        ttk.Label(exchange_frame, text="نوع سفارش:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.order_type_combo = ttk.Combobox(exchange_frame, 
                                             values=["Maker", "Taker"], 
                                             width=18, 
                                             state="readonly")
        self.order_type_combo.set("Taker" if self.order_type == "taker" else "Maker")
        self.order_type_combo.grid(row=1, column=1, pady=5, sticky=tk.W)
        self.order_type_combo.bind('<<ComboboxSelected>>', self.on_order_type_change)
        
        # Info label for maker/taker
        info_text = "ℹ️ Maker: لیمیت اردر | Taker: مارکت اردر"
        ttk.Label(exchange_frame, text=info_text, font=('Arial', 8), foreground='gray').grid(
            row=2, column=0, columnspan=2, pady=5)
        
        # Capital Settings Frame
        settings_frame = ttk.LabelFrame(main_frame, text="تنظیمات سرمایه", padding="10")
        settings_frame.grid(row=2, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E))
        
        ttk.Label(settings_frame, text="سرمایه کل (USDT):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.capital_entry = ttk.Entry(settings_frame, width=20)
        self.capital_entry.insert(0, str(self.capital))
        self.capital_entry.grid(row=0, column=1, pady=5)
        
        ttk.Label(settings_frame, text="درصد ریسک هر معامله (%):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.risk_entry = ttk.Entry(settings_frame, width=20)
        self.risk_entry.insert(0, str(self.risk_percent))
        self.risk_entry.grid(row=1, column=1, pady=5)
        
        ttk.Label(settings_frame, text="کارمزد صرافی (%):").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.fee_entry = ttk.Entry(settings_frame, width=20)
        self.fee_entry.insert(0, str(self.fee_percent))
        self.fee_entry.grid(row=2, column=1, pady=5)
        
        save_btn = ttk.Button(settings_frame, text="ذخیره تنظیمات", command=self.save_settings_clicked)
        save_btn.grid(row=3, column=0, columnspan=2, pady=10)
        
        # Trade Input Frame
        trade_frame = ttk.LabelFrame(main_frame, text="اطلاعات معامله", padding="10")
        trade_frame.grid(row=3, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E))
        
        ttk.Label(trade_frame, text="قیمت ورود:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.entry_price = ttk.Entry(trade_frame, width=20)
        self.entry_price.grid(row=0, column=1, pady=5)
        
        ttk.Label(trade_frame, text="قیمت استاپ لاس (SL):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.stop_loss = ttk.Entry(trade_frame, width=20)
        self.stop_loss.grid(row=1, column=1, pady=5)
        
        ttk.Label(trade_frame, text="قیمت تیک پرافیت (TP):").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.take_profit = ttk.Entry(trade_frame, width=20)
        self.take_profit.grid(row=2, column=1, pady=5)
        
        ttk.Label(trade_frame, text="نوع معامله:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.position_type = ttk.Combobox(trade_frame, values=["LONG", "SHORT"], width=18, state="readonly")
        self.position_type.set("LONG")
        self.position_type.grid(row=3, column=1, pady=5)
        
        ttk.Label(trade_frame, text="لوریج (Leverage):").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.leverage = ttk.Entry(trade_frame, width=20)
        self.leverage.insert(0, "10")
        self.leverage.grid(row=4, column=1, pady=5)
        
        # Calculate Button
        calc_btn = ttk.Button(trade_frame, text="محاسبه", command=self.calculate)
        calc_btn.grid(row=5, column=0, columnspan=2, pady=15)
        
        # Results Frame
        results_frame = ttk.LabelFrame(main_frame, text="نتایج محاسبات", padding="10")
        results_frame.grid(row=4, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E))
        
        self.results_text = tk.Text(results_frame, height=22, width=75, font=('Courier', 9))
        self.results_text.grid(row=0, column=0, pady=5)
        
        # Scrollbar for results
        results_scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=self.results_text.yview)
        results_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.results_text.config(yscrollcommand=results_scrollbar.set)
        
        # Pack canvas and scrollbar
        main_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Set initial fee based on saved exchange
        self.on_exchange_change()
        
    def save_settings_clicked(self):
        try:
            self.capital = float(self.capital_entry.get())
            self.risk_percent = float(self.risk_entry.get())
            self.fee_percent = float(self.fee_entry.get())
            self.selected_exchange = self.exchange_combo.get()
            order_type = self.order_type_combo.get()
            self.order_type = 'maker' if order_type == 'Maker' else 'taker'
            self.save_settings()
            messagebox.showinfo("موفق", "تنظیمات با موفقیت ذخیره شد!")
        except ValueError:
            messagebox.showerror("خطا", "لطفا اعداد معتبر وارد کنید!")
    
    def calculate(self):
        try:
            # Get inputs
            entry_price = float(self.entry_price.get())
            stop_loss = float(self.stop_loss.get())
            take_profit = float(self.take_profit.get())
            leverage = float(self.leverage.get())
            position = self.position_type.get()
            
            # Update capital from entry
            capital = float(self.capital_entry.get())
            risk_percent = float(self.risk_entry.get())
            fee_percent = float(self.fee_entry.get())
            exchange = self.exchange_combo.get()
            order_type = self.order_type_combo.get()
            
            # Calculate risk amount
            risk_amount = capital * (risk_percent / 100)
            
            # Calculate price difference percentages
            if position == "LONG":
                sl_diff_percent = ((entry_price - stop_loss) / entry_price) * 100
                tp_diff_percent = ((take_profit - entry_price) / entry_price) * 100
            else:  # SHORT
                sl_diff_percent = ((stop_loss - entry_price) / entry_price) * 100
                tp_diff_percent = ((entry_price - take_profit) / entry_price) * 100
            
            # Calculate position size
            position_size_usdt = risk_amount / (sl_diff_percent / 100)
            
            # Calculate actual position value with leverage
            position_value = position_size_usdt * leverage
            
            # Calculate quantity
            quantity = position_value / entry_price
            
            # Calculate fees
            entry_fee = position_value * (fee_percent / 100)
            exit_fee = position_value * (fee_percent / 100)
            total_fees = entry_fee + exit_fee
            
            # Calculate potential profit/loss
            if position == "LONG":
                profit_at_tp = (quantity * take_profit) - position_value - total_fees
                loss_at_sl = (quantity * stop_loss) - position_value - total_fees
            else:  # SHORT
                profit_at_tp = position_value - (quantity * take_profit) - total_fees
                loss_at_sl = position_value - (quantity * stop_loss) - total_fees
            
            # Calculate Risk/Reward Ratio
            rr_ratio = abs(profit_at_tp / loss_at_sl) if loss_at_sl != 0 else 0
            
            # Calculate liquidation price
            if position == "LONG":
                liquidation_price = entry_price * (1 - (1 / leverage) + (fee_percent / 100))
            else:  # SHORT
                liquidation_price = entry_price * (1 + (1 / leverage) + (fee_percent / 100))
            
            # Display results
            results = f"""
{'='*75}
                    نتایج محاسبات
{'='*75}

تاریخ و زمان: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

صرافی و کارمزد:
{'='*75}
صرافی:                      {exchange}
نوع سفارش:                 {order_type}
کارمزد:                      {fee_percent}%

اطلاعات معامله:
{'='*75}
نوع پوزیشن:                {position}
قیمت ورود:                 {entry_price:,.4f} USDT
قیمت استاپ لاس:              {stop_loss:,.4f} USDT
قیمت تیک پرافیت:           {take_profit:,.4f} USDT
لوریج:                     {leverage}x

محاسبات ریسک:
{'='*75}
سرمایه کل:                  {capital:,.2f} USDT
درصد ریسک:                {risk_percent}%
میزان ریسک:                {risk_amount:,.2f} USDT

محاسبات پوزیشن:
{'='*75}
حجم پوزیشن (مارجین):         {position_size_usdt:,.2f} USDT
ارزش پوزیشن (با لوریج):     {position_value:,.2f} USDT
تعداد کوین:                {quantity:,.6f}

محاسبات کارمزد:
{'='*75}
کارمزد ورود:               {entry_fee:,.2f} USDT
کارمزد خروج:               {exit_fee:,.2f} USDT
جمع کارمزدها:             {total_fees:,.2f} USDT

نتایج سود و زیان:
{'='*75}
سود در تیک پرافیت:         {profit_at_tp:,.2f} USDT ({(profit_at_tp/capital)*100:+.2f}%)
زیان در استاپ لاس:         {loss_at_sl:,.2f} USDT ({(loss_at_sl/capital)*100:+.2f}%)

نسبت ریسک/ریوارد:           {rr_ratio:.2f}:1

قیمت لیکوییدیشن:
{'='*75}
قیمت لیکوییدیشن:          {liquidation_price:,.4f} USDT

توصیه‌ها:
{'='*75}
"""
            
            # Add recommendations
            if rr_ratio < 1.5:
                results += "⚠️  نسبت R/R پایین است! معامله توصیه نمی‌شود.\n"
            elif rr_ratio >= 2:
                results += "✅  نسبت R/R عالی است! معامله مناسب است.\n"
            else:
                results += "ℹ️  نسبت R/R قابل قبول است.\n"
            
            if abs(loss_at_sl / capital * 100) > risk_percent * 1.2:
                results += f"⚠️  هشدار: ضرر بالقوه بیش از ریسک تعیین شده است!\n"
            
            # Calculate distance to liquidation
            if position == "LONG":
                liq_distance = ((entry_price - liquidation_price) / entry_price) * 100
            else:
                liq_distance = ((liquidation_price - entry_price) / entry_price) * 100
            
            if liq_distance < 10:
                results += f"⚠️  خطر لیکوییدیشن بالاست! فاصله: {liq_distance:.2f}%\n"
            
            results += f"\n{'='*75}\n"
            
            self.results_text.delete('1.0', tk.END)
            self.results_text.insert('1.0', results)
            
        except ValueError as e:
            messagebox.showerror("خطا", "لطفا تمام فیلدها را با مقادیر معتبر پر کنید!")
        except Exception as e:
            messagebox.showerror("خطا", f"خطایی رخ داد: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CryptoTradingCalculator(root)
    root.mainloop()
