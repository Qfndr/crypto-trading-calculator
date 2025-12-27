class Language:
    def __init__(self):
        self.current = 'fa'  # Default to Persian
        self.translations = {
            'fa': {
                # Main Window
                'app_title': 'ماشین حساب ترید کریپتو',
                'dark_mode': 'دارک مود',
                'light_mode': 'لایت مود',
                'settings': 'تنظیمات',
                'history': 'تاریخچه',
                'charts': 'نمودارها',
                'language': 'زبان',
                'update': 'آپدیت',
                
                # Exchange Card
                'exchange_symbol': 'انتخاب صرافی و سمبل',
                'exchange': 'صرافی',
                'order_type': 'نوع سفارش',
                'symbol': 'سمبل',
                'live_price': 'قیمت لحظه‌ای',
                
                # Capital Card
                'capital_risk': 'تنظیمات سرمایه و ریسک',
                'total_capital': 'سرمایه کل (USDT)',
                'risk_percent': 'درصد ریسک (%)',
                'fee_percent': 'کارمزد (%)',
                'save_settings': 'ذخیره تنظیمات',
                
                # Trade Card
                'trade_info': 'اطلاعات معامله',
                'entry_price': 'قیمت ورود',
                'stop_loss': 'استاپ لاس (SL)',
                'take_profit': 'تیک پرافیت',
                'position_type': 'نوع معامله',
                'leverage': 'لوریج',
                'notes': 'یادداشت',
                'calculate': 'محاسبه',
                
                # Results Card
                'results': 'نتایج محاسبات',
                'export_csv': 'Export CSV',
                'clear_results': 'پاک کردن نتایج',
                
                # Messages
                'success': 'موفق',
                'error': 'خطا',
                'info': 'اطلاعات',
                'confirm': 'تأیید',
                'cancel': 'لغو',
                'save_success': 'تنظیمات با موفقیت ذخیره شد!',
                'calc_success': 'محاسبات با موفقیت انجام شد!\n\nمعامله در تاریخچه ذخیره شد.',
                'enter_valid': 'لطفا اعداد معتبر وارد کنید!',
                'enter_tp': 'لطفا حداقل یک Take Profit وارد کنید!',
                'no_api_price': 'برای صرافی دستی، قیمت API در دسترس نیست.',
                'fetching_price': 'در حال دریافت...',
                'price_error': 'خطا در دریافت قیمت',
                'api_error': 'نتوانستیم قیمت را از API دریافت کنیم.\nلطفا دستی وارد کنید.',
                
                # Settings Window
                'advanced_settings': 'تنظیمات پیشرفته',
                'api_keys': 'کلیدهای API',
                'other_settings': 'سایر تنظیمات',
                'refresh_rate': 'زمان به‌روزرسانی قیمت (ثانیه)',
                'save_all': 'ذخیره تمام تنظیمات',
                'keys_saved': 'صرافی API Key ذخیره شد',
                
                # History Window
                'trade_history': 'تاریخچه معاملات',
                'export': 'Export',
                'clear': 'پاک کردن',
                'no_trades': 'هیچ معامله‌ای ثبت نشده است.',
                'trade_num': 'معامله',
                'clear_history_confirm': 'آیا مطمئن هستید که می‌خواهید تاریخچه را پاک کنید؟',
                'history_cleared': 'تاریخچه با موفقیت پاک شد!',
                'no_export_data': 'هیچ معامله‌ای برای Export وجود ندارد!',
                'file_saved': 'فایل با موفقیت ذخیره شد',
                'save_error': 'خطا در ذخیره فایل!',
                
                # Charts Window
                'charts_analysis': 'نمودارها و تحلیل',
                'pnl_chart': 'نمودار سود/زیان',
                'history_analysis': 'تحلیل تاریخچه',
                'enter_trade_first': 'لطفا ابتدا اطلاعات معامله را وارد کنید',
                'chart_error': 'خطا در نمایش نمودار تاریخچه',
                'no_history': 'تاریخچه معاملاتی وجود ندارد',
                
                # Update Window
                'update_manager': 'مدیریت آپدیت',
                'current_version': 'نسخه فعلی',
                'latest_version': 'آخرین نسخه',
                'checking_update': 'در حال بررسی آپدیت...',
                'update_available': 'آپدیت جدید موجود است!',
                'up_to_date': 'شما از آخرین نسخه استفاده می‌کنید',
                'update_now': 'آپدیت کن',
                'select_version': 'انتخاب نسخه',
                'available_versions': 'نسخه‌های موجود',
                'install_version': 'نصب نسخه',
                'updating': 'در حال آپدیت...',
                'update_success': 'آپدیت با موفقیت انجام شد!\nلطفا برنامه را مجددا اجرا کنید.',
                'update_error': 'خطا در آپدیت',
                'restart_required': 'برنامه نیاز به راه‌اندازی مجدد دارد',
            },
            'en': {
                # Main Window
                'app_title': 'Crypto Trading Calculator',
                'dark_mode': 'Dark Mode',
                'light_mode': 'Light Mode',
                'settings': 'Settings',
                'history': 'History',
                'charts': 'Charts',
                'language': 'Language',
                'update': 'Update',
                
                # Exchange Card
                'exchange_symbol': 'Exchange & Symbol Selection',
                'exchange': 'Exchange',
                'order_type': 'Order Type',
                'symbol': 'Symbol',
                'live_price': 'Live Price',
                
                # Capital Card
                'capital_risk': 'Capital & Risk Settings',
                'total_capital': 'Total Capital (USDT)',
                'risk_percent': 'Risk Percent (%)',
                'fee_percent': 'Fee (%)',
                'save_settings': 'Save Settings',
                
                # Trade Card
                'trade_info': 'Trade Information',
                'entry_price': 'Entry Price',
                'stop_loss': 'Stop Loss (SL)',
                'take_profit': 'Take Profit',
                'position_type': 'Position Type',
                'leverage': 'Leverage',
                'notes': 'Notes',
                'calculate': 'Calculate',
                
                # Results Card
                'results': 'Calculation Results',
                'export_csv': 'Export CSV',
                'clear_results': 'Clear Results',
                
                # Messages
                'success': 'Success',
                'error': 'Error',
                'info': 'Information',
                'confirm': 'Confirm',
                'cancel': 'Cancel',
                'save_success': 'Settings saved successfully!',
                'calc_success': 'Calculation completed successfully!\n\nTrade saved to history.',
                'enter_valid': 'Please enter valid numbers!',
                'enter_tp': 'Please enter at least one Take Profit!',
                'no_api_price': 'API price not available for custom exchange.',
                'fetching_price': 'Fetching...',
                'price_error': 'Price fetch error',
                'api_error': 'Could not fetch price from API.\nPlease enter manually.',
                
                # Settings Window
                'advanced_settings': 'Advanced Settings',
                'api_keys': 'API Keys',
                'other_settings': 'Other Settings',
                'refresh_rate': 'Price Refresh Rate (seconds)',
                'save_all': 'Save All Settings',
                'keys_saved': 'exchange API Keys saved',
                
                # History Window
                'trade_history': 'Trade History',
                'export': 'Export',
                'clear': 'Clear',
                'no_trades': 'No trades recorded.',
                'trade_num': 'Trade',
                'clear_history_confirm': 'Are you sure you want to clear the history?',
                'history_cleared': 'History cleared successfully!',
                'no_export_data': 'No trades available for export!',
                'file_saved': 'File saved successfully',
                'save_error': 'Error saving file!',
                
                # Charts Window
                'charts_analysis': 'Charts & Analysis',
                'pnl_chart': 'P&L Chart',
                'history_analysis': 'History Analysis',
                'enter_trade_first': 'Please enter trade information first',
                'chart_error': 'Error displaying history chart',
                'no_history': 'No trade history available',
                
                # Update Window
                'update_manager': 'Update Manager',
                'current_version': 'Current Version',
                'latest_version': 'Latest Version',
                'checking_update': 'Checking for updates...',
                'update_available': 'New update available!',
                'up_to_date': 'You are using the latest version',
                'update_now': 'Update Now',
                'select_version': 'Select Version',
                'available_versions': 'Available Versions',
                'install_version': 'Install Version',
                'updating': 'Updating...',
                'update_success': 'Update completed successfully!\nPlease restart the application.',
                'update_error': 'Update error',
                'restart_required': 'Application restart required',
            }
        }
    
    def set_language(self, lang):
        """Set current language"""
        if lang in self.translations:
            self.current = lang
            return True
        return False
    
    def get(self, key):
        """Get translation for key"""
        return self.translations[self.current].get(key, key)
    
    def get_all(self):
        """Get all translations for current language"""
        return self.translations[self.current]
