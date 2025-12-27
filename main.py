import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

class CryptoTradingCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("ماشین حساب ترید کریپتو")
        self.root.geometry("800x900")
        self.root.resizable(False, False)
        
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
                    self.fee_percent = data.get('fee_percent', 0.15)
            except:
                self.set_defaults()
        else:
            self.set_defaults()
    
    def set_defaults(self):
        self.capital = 100
        self.risk_percent = 1
        self.fee_percent = 0.15
    
    def save_settings(self):
        """Save settings to JSON file"""
        data = {
            'capital': self.capital,
            'risk_percent': self.risk_percent,
            'fee_percent': self.fee_percent
        }
        with open(self.settings_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    
    def create_widgets(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title = ttk.Label(main_frame, text="ماشین حساب ترید کریپتو", 
                         font=('Arial', 16, 'bold'))
        title.grid(row=0, column=0, columnspan=2, pady=10)
        
        # Capital Settings Frame
        settings_frame = ttk.LabelFrame(main_frame, text="تنظیمات سرمایه", padding="10")
        settings_frame.grid(row=1, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E))
        
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
        trade_frame.grid(row=2, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E))
        
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
        results_frame.grid(row=3, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E))
        
        self.results_text = tk.Text(results_frame, height=20, width=70, font=('Courier', 10))
        self.results_text.grid(row=0, column=0, pady=5)
        
        # Scrollbar for results
        scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=self.results_text.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.results_text.config(yscrollcommand=scrollbar.set)
        
    def save_settings_clicked(self):
        try:
            self.capital = float(self.capital_entry.get())
            self.risk_percent = float(self.risk_entry.get())
            self.fee_percent = float(self.fee_entry.get())
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
            # Position Size = Risk Amount / (SL% * Leverage)
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
{'='*70}
                    نتایج محاسبات
{'='*70}

تاریخ و زمان: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

اطلاعات معامله:
{'='*70}
نوع پوزیشن:                {position}
قیمت ورود:                 {entry_price:,.4f} USDT
قیمت استاپ لاس:              {stop_loss:,.4f} USDT
قیمت تیک پرافیت:           {take_profit:,.4f} USDT
لوریج:                     {leverage}x

محاسبات ریسک:
{'='*70}
سرمایه کل:                  {capital:,.2f} USDT
درصد ریسک:                {risk_percent}%
میزان ریسک:                {risk_amount:,.2f} USDT

محاسبات پوزیشن:
{'='*70}
حجم پوزیشن (مارجین):         {position_size_usdt:,.2f} USDT
ارزش پوزیشن (با لوریج):     {position_value:,.2f} USDT
تعداد کوین:                {quantity:,.6f}

محاسبات کارمزد:
{'='*70}
کارمزد ورود:               {entry_fee:,.2f} USDT
کارمزد خروج:               {exit_fee:,.2f} USDT
جمع کارمزدها:             {total_fees:,.2f} USDT

نتایج سود و زیان:
{'='*70}
سود در تیک پرافیت:         {profit_at_tp:,.2f} USDT ({(profit_at_tp/capital)*100:+.2f}%)
زیان در استاپ لاس:         {loss_at_sl:,.2f} USDT ({(loss_at_sl/capital)*100:+.2f}%)

نسبت ریسک/ریوارد:           {rr_ratio:.2f}:1

قیمت لیکوییدیشن:
{'='*70}
قیمت لیکوییدیشن:          {liquidation_price:,.4f} USDT

توصیه‌ها:
{'='*70}
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
            
            results += f"\n{'='*70}\n"
            
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
