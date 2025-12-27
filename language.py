"""
Multi-language support for Crypto Trading Calculator
Supports: Persian (fa), English (en)
"""

class Language:
    def __init__(self):
        self.current = 'fa'  # Default language
        self.translations = {
            'fa': {
                # App Info
                'app_title': 'ماشین حساب ترید کریپتو',
                'version': 'نسخه',
                
                # Top Menu Buttons
                'dark_mode': 'دارک مود',
                'light_mode': 'لایت مود',
                'settings': 'تنظیمات',
                'history': 'تاریخچه',
                'charts': 'نمودارها',
                'language': 'زبان',
                'update': 'آپدیت',
                
                # Card Titles
                'exchange_symbol': 'انتخاب صرافی و سمبل',
                'capital_risk': 'تنظیمات سرمایه و ریسک',
                'trade_info': 'اطلاعات معامله',
                'results': 'نتایج محاسبات',
                
                # Exchange & Symbol Card
                'exchange': 'صرافی',
                'order_type': 'نوع سفارش',
                'symbol': 'سمبل',
                'live_price': 'قیمت لحظه‌ای',
                'fetching_price': 'در حال دریافت...',
                'price_error': 'خطا در دریافت قیمت',
                
                # Capital & Risk Card
                'total_capital': 'سرمایه کل (USDT)',
                'risk_percent': 'درصد ریسک (%)',
                'fee_percent': 'کارمزد (%)',
                'save_settings': 'ذخیره تنظیمات',
                
                # Trade Info Card
                'entry_price': 'قیمت ورود',
                'stop_loss': 'استاپ لاس (SL)',
                'take_profit': 'تیک پرافیت',
                'position_type': 'نوع معامله',
                'leverage': 'لوریج',
                'notes': 'یادداشت',
                'calculate': 'محاسبه',
                
                # Results Card
                'export_csv': 'Export CSV',
                'clear_results': 'پاک کردن نتایج',
                
                # Update Manager
                'update_manager': 'مدیریت آپدیت',
                'current_version': 'نسخه فعلی',
                'latest_version': 'آخرین نسخه',
                'checking_update': 'در حال بررسی آپدیت',
                'update_available': 'نسخه جدید موجود است!',
                'up_to_date': 'نسخه شما به‌روز است',
                'update_now': 'آپدیت کن',
                'updating': 'در حال آپدیت',
                'update_success': 'آپدیت موفق بود!',
                'update_error': 'خطا در آپدیت',
                'restart_required': 'لطفاً برنامه را مجدداً اجرا کنید',
                'select_version': 'انتخاب نسخه دلخواه',
                'install_version': 'نصب نسخه انتخابی',
                
                # Advanced Settings
                'advanced_settings': 'تنظیمات پیشرفته',
                'api_keys': 'کلیدهای API',
                'other_settings': 'سایر تنظیمات',
                'refresh_rate': 'نرخ به‌روزرسانی (ثانیه)',
                'save_all': 'ذخیره همه',
                'keys_saved': 'کلید ذخیره شد',
                
                # Trade History
                'trade_history': 'تاریخچه معاملات',
                'trade_num': 'معامله',
                'no_trades': 'هیچ معامله‌ای ثبت نشده است.',
                'export': 'خروجی',
                'clear': 'پاک کردن',
                'clear_history_confirm': 'آیا مطمئن هستید که می‌خواهید تاریخچه را پاک کنید؟',
                'history_cleared': 'تاریخچه پاک شد',
                
                # Charts
                'charts_analysis': 'تحلیل نمودارها',
                'pnl_chart': 'نمودار سود/زیان',
                'history_analysis': 'تحلیل تاریخچه',
                'enter_trade_first': 'ابتدا اطلاعات معامله را وارد کنید',
                'chart_error': 'خطا در ایجاد نمودار',
                'no_history': 'تاریخچه‌ای موجود نیست',
                
                # Messages
                'success': 'موفق',
                'error': 'خطا',
                'info': 'اطلاعات',
                'confirm': 'تأیید',
                'warning': 'هشدار',
                'save_success': 'تنظیمات با موفقیت ذخیره شد',
                'calc_success': 'محاسبات انجام شد',
                'enter_valid': 'لطفاً اعداد معتبر وارد کنید',
                'enter_tp': 'حداقل یک تیک پرافیت وارد کنید',
                'no_api_price': 'برای صرافی دستی نمی‌توان قیمت زنده دریافت کرد',
                'api_error': 'خطا در دریافت داده از API',
                'no_export_data': 'داده‌ای برای خروجی وجود ندارد',
                'file_saved': 'فایل ذخیره شد',
                'save_error': 'خطا در ذخیره فایل',
            },
            'en': {
                # App Info
                'app_title': 'Crypto Trading Calculator',
                'version': 'Version',
                
                # Top Menu Buttons
                'dark_mode': 'Dark Mode',
                'light_mode': 'Light Mode',
                'settings': 'Settings',
                'history': 'History',
                'charts': 'Charts',
                'language': 'Language',
                'update': 'Update',
                
                # Card Titles
                'exchange_symbol': 'Exchange & Symbol Selection',
                'capital_risk': 'Capital & Risk Settings',
                'trade_info': 'Trade Information',
                'results': 'Calculation Results',
                
                # Exchange & Symbol Card
                'exchange': 'Exchange',
                'order_type': 'Order Type',
                'symbol': 'Symbol',
                'live_price': 'Live Price',
                'fetching_price': 'Fetching...',
                'price_error': 'Price Error',
                
                # Capital & Risk Card
                'total_capital': 'Total Capital (USDT)',
                'risk_percent': 'Risk Percent (%)',
                'fee_percent': 'Fee Percent (%)',
                'save_settings': 'Save Settings',
                
                # Trade Info Card
                'entry_price': 'Entry Price',
                'stop_loss': 'Stop Loss (SL)',
                'take_profit': 'Take Profit',
                'position_type': 'Position Type',
                'leverage': 'Leverage',
                'notes': 'Notes',
                'calculate': 'Calculate',
                
                # Results Card
                'export_csv': 'Export CSV',
                'clear_results': 'Clear Results',
                
                # Update Manager
                'update_manager': 'Update Manager',
                'current_version': 'Current Version',
                'latest_version': 'Latest Version',
                'checking_update': 'Checking for updates',
                'update_available': 'New version available!',
                'up_to_date': 'You are up to date',
                'update_now': 'Update Now',
                'updating': 'Updating',
                'update_success': 'Update successful!',
                'update_error': 'Update error',
                'restart_required': 'Please restart the application',
                'select_version': 'Select Version',
                'install_version': 'Install Selected Version',
                
                # Advanced Settings
                'advanced_settings': 'Advanced Settings',
                'api_keys': 'API Keys',
                'other_settings': 'Other Settings',
                'refresh_rate': 'Refresh Rate (seconds)',
                'save_all': 'Save All',
                'keys_saved': 'keys saved',
                
                # Trade History
                'trade_history': 'Trade History',
                'trade_num': 'Trade',
                'no_trades': 'No trades recorded yet.',
                'export': 'Export',
                'clear': 'Clear',
                'clear_history_confirm': 'Are you sure you want to clear the history?',
                'history_cleared': 'History cleared',
                
                # Charts
                'charts_analysis': 'Charts Analysis',
                'pnl_chart': 'P&L Chart',
                'history_analysis': 'History Analysis',
                'enter_trade_first': 'Please enter trade information first',
                'chart_error': 'Error creating chart',
                'no_history': 'No history available',
                
                # Messages
                'success': 'Success',
                'error': 'Error',
                'info': 'Information',
                'confirm': 'Confirm',
                'warning': 'Warning',
                'save_success': 'Settings saved successfully',
                'calc_success': 'Calculation completed',
                'enter_valid': 'Please enter valid numbers',
                'enter_tp': 'Please enter at least one take profit',
                'no_api_price': 'Cannot fetch live price for custom exchange',
                'api_error': 'Error fetching data from API',
                'no_export_data': 'No data to export',
                'file_saved': 'File saved',
                'save_error': 'Error saving file',
            }
        }
    
    def set_language(self, lang_code):
        """Set current language (fa or en)"""
        if lang_code in self.translations:
            self.current = lang_code
            return True
        return False
    
    def get(self, key, default=None):
        """Get translation for a key"""
        if default is None:
            default = key
        return self.translations.get(self.current, {}).get(key, default)
    
    def get_all(self):
        """Get all translations for current language"""
        return self.translations.get(self.current, {})
