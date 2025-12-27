import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
matplotlib.use('TkAgg')

class ChartGenerator:
    def __init__(self):
        self.fig = None
        self.canvas = None
    
    def create_pnl_chart(self, entry_price, stop_loss, take_profits, position_type='LONG', theme='light'):
        """Create profit/loss chart"""
        # Set style based on theme
        if theme == 'dark':
            plt.style.use('dark_background')
            bg_color = '#2d2d2d'
            text_color = 'white'
        else:
            plt.style.use('default')
            bg_color = 'white'
            text_color = 'black'
        
        self.fig, ax = plt.subplots(figsize=(10, 6), facecolor=bg_color)
        ax.set_facecolor(bg_color)
        
        # Calculate price range
        all_prices = [entry_price, stop_loss] + take_profits
        min_price = min(all_prices) * 0.95
        max_price = max(all_prices) * 1.05
        
        # Create price points
        prices = [min_price, stop_loss, entry_price] + sorted(take_profits) + [max_price]
        
        # Calculate PnL percentages
        pnl_percentages = []
        for price in prices:
            if position_type == 'LONG':
                pnl = ((price - entry_price) / entry_price) * 100
            else:
                pnl = ((entry_price - price) / entry_price) * 100
            pnl_percentages.append(pnl)
        
        # Plot the line
        ax.plot(prices, pnl_percentages, 'b-', linewidth=2, label='P&L')
        
        # Mark important points
        ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5, label='Break Even')
        ax.axvline(x=entry_price, color='yellow', linestyle='--', alpha=0.7, label=f'Entry: {entry_price:,.2f}')
        ax.axvline(x=stop_loss, color='red', linestyle='--', alpha=0.7, label=f'SL: {stop_loss:,.2f}')
        
        # Mark TPs
        colors = ['green', 'lightgreen', 'lime']
        for i, tp in enumerate(take_profits):
            color = colors[i] if i < len(colors) else 'green'
            ax.axvline(x=tp, color=color, linestyle='--', alpha=0.7, label=f'TP{i+1}: {tp:,.2f}')
        
        # Fill areas
        ax.fill_between(prices, pnl_percentages, 0, 
                        where=[p >= 0 for p in pnl_percentages],
                        alpha=0.3, color='green', label='Profit Zone')
        ax.fill_between(prices, pnl_percentages, 0, 
                        where=[p < 0 for p in pnl_percentages],
                        alpha=0.3, color='red', label='Loss Zone')
        
        # Labels and title
        ax.set_xlabel('قیمت (USDT)', fontsize=12, color=text_color)
        ax.set_ylabel('سود/زیان (%)', fontsize=12, color=text_color)
        ax.set_title(f'نمودار سود و زیان - {position_type}', fontsize=14, fontweight='bold', color=text_color)
        ax.legend(loc='best', fontsize=9)
        ax.grid(True, alpha=0.3)
        ax.tick_params(colors=text_color)
        
        plt.tight_layout()
        return self.fig
    
    def create_trade_history_chart(self, trades, theme='light'):
        """Create chart showing trade history performance"""
        if not trades:
            return None
        
        # Set style based on theme
        if theme == 'dark':
            plt.style.use('dark_background')
            bg_color = '#2d2d2d'
            text_color = 'white'
        else:
            plt.style.use('default')
            bg_color = 'white'
            text_color = 'black'
        
        self.fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), facecolor=bg_color)
        
        # Extract data
        trade_numbers = list(range(1, len(trades) + 1))
        
        # Calculate cumulative P&L if we have tp_results
        cumulative_pnl = []
        total = 0
        for trade in trades:
            if 'tp_results' in trade and trade['tp_results']:
                # Use first TP profit
                profit = trade['tp_results'][0]['profit']
                total += profit
            else:
                total += 0
            cumulative_pnl.append(total)
        
        # Plot cumulative P&L
        ax1.set_facecolor(bg_color)
        ax1.plot(trade_numbers, cumulative_pnl, 'b-o', linewidth=2, markersize=6)
        ax1.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
        ax1.fill_between(trade_numbers, cumulative_pnl, 0, 
                        where=[p >= 0 for p in cumulative_pnl],
                        alpha=0.3, color='green')
        ax1.fill_between(trade_numbers, cumulative_pnl, 0, 
                        where=[p < 0 for p in cumulative_pnl],
                        alpha=0.3, color='red')
        ax1.set_xlabel('شماره معامله', color=text_color)
        ax1.set_ylabel('سود/زیان تجمعی (USDT)', color=text_color)
        ax1.set_title('عملکرد معاملات', fontweight='bold', color=text_color)
        ax1.grid(True, alpha=0.3)
        ax1.tick_params(colors=text_color)
        
        # Plot individual trades
        ax2.set_facecolor(bg_color)
        individual_pnl = []
        for trade in trades:
            if 'tp_results' in trade and trade['tp_results']:
                individual_pnl.append(trade['tp_results'][0]['profit'])
            else:
                individual_pnl.append(0)
        
        colors = ['green' if p >= 0 else 'red' for p in individual_pnl]
        ax2.bar(trade_numbers, individual_pnl, color=colors, alpha=0.7)
        ax2.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
        ax2.set_xlabel('شماره معامله', color=text_color)
        ax2.set_ylabel('سود/زیان (USDT)', color=text_color)
        ax2.set_title('نتیجه هر معامله', fontweight='bold', color=text_color)
        ax2.grid(True, alpha=0.3, axis='y')
        ax2.tick_params(colors=text_color)
        
        plt.tight_layout()
        return self.fig
