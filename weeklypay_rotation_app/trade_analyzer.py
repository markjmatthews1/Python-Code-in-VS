# -*- coding: utf-8 -*-
import pandas as pd
import tkinter as tk
from tkinter import ttk, scrolledtext, font
import os

def create_trade_analyzer():
    root = tk.Tk()
    root.title("WeeklyPay Trade Performance Analyzer")
    root.geometry("1000x750")
    root.configure(bg='#1e1e1e')
    
    # Create header with gradient effect
    header = tk.Frame(root, bg='#2563eb', pady=15)
    header.pack(fill=tk.X)
    title_label = tk.Label(header, text="TRADE PERFORMANCE ANALYZER", 
                           font=("Arial", 20, "bold"), bg='#2563eb', fg='white')
    title_label.pack()
    subtitle = tk.Label(header, text="WeeklyPay Rotation Strategy", 
                       font=("Arial", 12), bg='#2563eb', fg='#dbeafe')
    subtitle.pack()
    
    try:
        if os.path.exists("weeklypay_trades.csv"):
            df = pd.read_csv("weeklypay_trades.csv")
            
            # Calculate performance metrics
            total_trades = len(df)
            buy_trades = df[df['Action'] == 'BUY']
            sell_trades = df[df['Action'] == 'SELL']
            dividend_trades = df[df['Action'] == 'DIVIDEND']
            
            total_invested = buy_trades['Total'].astype(float).sum()
            total_sold = sell_trades['Total'].astype(float).sum()
            total_dividends = dividend_trades['Total'].astype(float).sum()
            
            # Calculate realized capital gains
            realized_gains = total_sold - total_invested if total_sold > 0 else 0
            total_return = realized_gains + total_dividends
            return_pct = (total_return / total_invested * 100) if total_invested > 0 else 0
            
            # Get average WeeklyPay score
            avg_score = pd.to_numeric(buy_trades['WeeklyPay_Score'], errors='coerce').mean()
            
            # Calculate active positions
            position_summary = df.groupby('Ticker').apply(
                lambda x: x[x['Action'] == 'BUY']['Quantity'].sum() - x[x['Action'] == 'SELL']['Quantity'].sum()
            )
            active_positions = (position_summary > 0).sum()
            
            # Create text widget with larger font
            text_frame = tk.Frame(root, bg='#1e1e1e')
            text_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
            
            text_widget = tk.Text(text_frame, font=("Arial", 13), 
                                 bg='#ffffff', fg='#1e1e1e',
                                 wrap=tk.WORD, padx=15, pady=15)
            
            # Add scrollbar
            scrollbar = tk.Scrollbar(text_frame, command=text_widget.yview)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            text_widget.config(yscrollcommand=scrollbar.set)
            text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            # Configure color tags
            text_widget.tag_configure("header", font=("Arial", 16, "bold"), foreground="#2563eb")
            text_widget.tag_configure("section", font=("Arial", 14, "bold"), foreground="#059669")
            text_widget.tag_configure("positive", foreground="#10b981", font=("Arial", 13, "bold"))
            text_widget.tag_configure("negative", foreground="#ef4444", font=("Arial", 13, "bold"))
            text_widget.tag_configure("neutral", foreground="#6b7280", font=("Arial", 13))
            text_widget.tag_configure("highlight", foreground="#8b5cf6", font=("Arial", 13, "bold"))
            text_widget.tag_configure("ticker", foreground="#0284c7", font=("Arial", 13, "bold"))
            text_widget.tag_configure("amount", foreground="#ea580c", font=("Arial", 13, "bold"))
            
            # Insert header
            text_widget.insert(tk.END, "\n")
            text_widget.insert(tk.END, "="*80 + "\n")
            text_widget.insert(tk.END, "               WEEKLYPAY PERFORMANCE ANALYSIS\n", "header")
            text_widget.insert(tk.END, "="*80 + "\n\n")
            
            # TRADE SUMMARY section
            text_widget.insert(tk.END, "TRADE SUMMARY\n", "section")
            text_widget.insert(tk.END, "-"*80 + "\n", "neutral")
            text_widget.insert(tk.END, f"Total Trades: ", "neutral")
            text_widget.insert(tk.END, f"{total_trades}\n", "highlight")
            text_widget.insert(tk.END, f"  Buy Orders: ", "neutral")
            text_widget.insert(tk.END, f"{len(buy_trades)}\n", "positive")
            text_widget.insert(tk.END, f"  Sell Orders: ", "neutral")
            text_widget.insert(tk.END, f"{len(sell_trades)}\n", "neutral")
            text_widget.insert(tk.END, f"  Dividend Payments: ", "neutral")
            text_widget.insert(tk.END, f"{len(dividend_trades)}\n\n", "ticker")
            
            # FINANCIAL METRICS section
            text_widget.insert(tk.END, "FINANCIAL METRICS\n", "section")
            text_widget.insert(tk.END, "-"*80 + "\n", "neutral")
            text_widget.insert(tk.END, f"Total Invested: ", "neutral")
            text_widget.insert(tk.END, f"${total_invested:,.2f}\n", "amount")
            text_widget.insert(tk.END, f"Total Sold: ", "neutral")
            text_widget.insert(tk.END, f"${total_sold:,.2f}\n", "neutral")
            text_widget.insert(tk.END, f"Total Dividends Received: ", "neutral")
            text_widget.insert(tk.END, f"${total_dividends:,.2f}\n\n", "positive")
            
            text_widget.insert(tk.END, f"Realized Capital Gains: ", "neutral")
            gain_tag = "positive" if realized_gains >= 0 else "negative"
            text_widget.insert(tk.END, f"${realized_gains:,.2f}\n", gain_tag)
            
            text_widget.insert(tk.END, f"Total Realized Return: ", "neutral")
            return_tag = "positive" if total_return >= 0 else "negative"
            text_widget.insert(tk.END, f"${total_return:,.2f}\n", return_tag)
            
            text_widget.insert(tk.END, f"Return Percentage: ", "neutral")
            pct_tag = "positive" if return_pct >= 0 else "negative"
            text_widget.insert(tk.END, f"{return_pct:+.2f}%\n\n", pct_tag)
            
            # PORTFOLIO STATUS section
            text_widget.insert(tk.END, "PORTFOLIO STATUS\n", "section")
            text_widget.insert(tk.END, "-"*80 + "\n", "neutral")
            text_widget.insert(tk.END, f"Active Positions: ", "neutral")
            text_widget.insert(tk.END, f"{active_positions}\n", "highlight")
            text_widget.insert(tk.END, f"Average WeeklyPay Score: ", "neutral")
            text_widget.insert(tk.END, f"{avg_score:.2f}\n\n", "ticker")
            
            # CURRENT HOLDINGS WITH LIVE PRICES section
            text_widget.insert(tk.END, "CURRENT HOLDINGS (LIVE PRICES)\n", "section")
            text_widget.insert(tk.END, "-"*80 + "\n", "neutral")
            
            holdings_df = calculate_current_holdings(df)
            
            if not holdings_df.empty and holdings_df['Current_Price'].notna().any():
                # Summary totals
                total_investment = holdings_df['Investment'].sum()
                total_current_value = holdings_df['Current_Value'].sum()
                total_nav_change = holdings_df['NAV_Change'].sum()
                total_dividends_received = holdings_df['Dividends'].sum()
                total_return_value = holdings_df['Total_Return'].sum()
                
                text_widget.insert(tk.END, "Portfolio Summary:\n", "highlight")
                text_widget.insert(tk.END, f"  Total Investment: ", "neutral")
                text_widget.insert(tk.END, f"${total_investment:,.2f}\n", "amount")
                text_widget.insert(tk.END, f"  Current Value: ", "neutral")
                nav_tag = "positive" if total_nav_change >= 0 else "negative"
                text_widget.insert(tk.END, f"${total_current_value:,.2f} ", "amount")
                nav_pct = (total_nav_change / total_investment * 100) if total_investment > 0 else 0
                text_widget.insert(tk.END, f"({nav_pct:+.1f}%)\n", nav_tag)
                text_widget.insert(tk.END, f"  NAV Change: ", "neutral")
                text_widget.insert(tk.END, f"${total_nav_change:+,.2f}\n", nav_tag)
                text_widget.insert(tk.END, f"  Total Dividends: ", "neutral")
                text_widget.insert(tk.END, f"${total_dividends_received:,.2f}\n", "positive")
                text_widget.insert(tk.END, f"  Total Return: ", "neutral")
                total_return_tag = "positive" if total_return_value >= 0 else "negative"
                text_widget.insert(tk.END, f"${total_return_value:+,.2f} ", "amount")
                total_return_pct = (total_return_value / total_investment * 100) if total_investment > 0 else 0
                text_widget.insert(tk.END, f"({total_return_pct:+.1f}%)\n\n", total_return_tag)
                
                # Individual holdings
                text_widget.insert(tk.END, "Individual Holdings:\n", "highlight")
                text_widget.insert(tk.END, f"{'Ticker':<8} {'Shares':<8} {'Avg Cost':<12} {'Current':<12} {'NAV Chg':<14} {'Divs':<12} {'Total Ret':<14}\n", "highlight")
                text_widget.insert(tk.END, "-"*80 + "\n", "neutral")
                
                for idx, holding in holdings_df.iterrows():
                    text_widget.insert(tk.END, f"{holding['Ticker']:<8} ", "ticker")
                    text_widget.insert(tk.END, f"{int(holding['Shares']):<8} ", "neutral")
                    text_widget.insert(tk.END, f"${holding['Avg_Cost']:<11.2f} ", "neutral")
                    text_widget.insert(tk.END, f"${holding['Current_Price']:<11.2f} ", "neutral")
                    
                    # NAV Change with color
                    nav_change_tag = "positive" if holding['NAV_Change'] >= 0 else "negative"
                    text_widget.insert(tk.END, f"${holding['NAV_Change']:+,.2f} ", nav_change_tag)
                    text_widget.insert(tk.END, f"({holding['NAV_Change_Pct']:+.1f}%) ", nav_change_tag)
                    
                    text_widget.insert(tk.END, f"${holding['Dividends']:,.2f}  ", "positive")
                    
                    # Total Return with color
                    total_ret_tag = "positive" if holding['Total_Return'] >= 0 else "negative"
                    text_widget.insert(tk.END, f"${holding['Total_Return']:+,.2f} ", total_ret_tag)
                    text_widget.insert(tk.END, f"({holding['Total_Return_Pct']:+.1f}%)\n", total_ret_tag)
                
                text_widget.insert(tk.END, "\n💡 Total Return = NAV Change + Dividends\n", "neutral")
            else:
                text_widget.insert(tk.END, "No open positions or unable to fetch prices.\n", "neutral")
            
            text_widget.insert(tk.END, "\n")
            
            # TOP TRADED TICKERS section
            text_widget.insert(tk.END, "TOP TRADED TICKERS\n", "section")
            text_widget.insert(tk.END, "-"*80 + "\n", "neutral")
            ticker_counts = df['Ticker'].value_counts().head(10)
            for ticker, count in ticker_counts.items():
                text_widget.insert(tk.END, f"{ticker}: ", "ticker")
                text_widget.insert(tk.END, f"{count} trades\n", "neutral")
            text_widget.insert(tk.END, "\n")
            
            # RECENT ACTIVITY section
            text_widget.insert(tk.END, "RECENT ACTIVITY (Last 10 Trades)\n", "section")
            text_widget.insert(tk.END, "-"*80 + "\n", "neutral")
            text_widget.insert(tk.END, f"{'Date':<12} {'Ticker':<8} {'Action':<10} {'Qty':<8} {'Price':<12} {'Total':<12}\n", "highlight")
            text_widget.insert(tk.END, "-"*80 + "\n", "neutral")
            
            for idx, row in df.tail(10).iterrows():
                # Date and Ticker
                text_widget.insert(tk.END, f"{str(row['Date']):<12} ")
                text_widget.insert(tk.END, f"{str(row['Ticker']):<8} ", "ticker")
                
                # Action with color
                action = str(row['Action'])
                if action == 'BUY':
                    text_widget.insert(tk.END, f"{action:<10} ", "positive")
                elif action == 'SELL':
                    text_widget.insert(tk.END, f"{action:<10} ", "negative")
                else:
                    text_widget.insert(tk.END, f"{action:<10} ", "highlight")
                
                # Quantity
                text_widget.insert(tk.END, f"{str(row['Quantity']):<8} ")
                
                # Price and Total
                text_widget.insert(tk.END, f"${float(row['Price']):<11.2f} ")
                text_widget.insert(tk.END, f"${float(row['Total']):<11.2f}\n", "amount")
            
            # INCOME PROJECTIONS section
            text_widget.insert(tk.END, "\n")
            text_widget.insert(tk.END, "INCOME PROJECTIONS\n", "section")
            text_widget.insert(tk.END, "-"*80 + "\n", "neutral")
            
            if len(dividend_trades) > 0:
                # Calculate date range
                div_dates = pd.to_datetime(dividend_trades['Date'])
                first_div = div_dates.min()
                last_div = div_dates.max()
                days_tracked = (last_div - first_div).days
                
                # Calculate averages
                if days_tracked > 0:
                    months_tracked = days_tracked / 30.44
                    avg_monthly = total_dividends / months_tracked if months_tracked > 0 else total_dividends
                    avg_yearly = avg_monthly * 12
                else:
                    avg_monthly = total_dividends
                    avg_yearly = total_dividends * 12
                
                # Calculate estimated future income
                position_summary = {}
                for ticker in df['Ticker'].unique():
                    ticker_trades = df[df['Ticker'] == ticker]
                    shares_bought = ticker_trades[ticker_trades['Action'] == 'BUY']['Quantity'].sum()
                    shares_sold = ticker_trades[ticker_trades['Action'] == 'SELL']['Quantity'].sum()
                    current_shares = shares_bought - shares_sold
                    
                    if current_shares > 0:
                        ticker_divs = dividend_trades[dividend_trades['Ticker'] == ticker]
                        if len(ticker_divs) > 0:
                            total_payments = len(ticker_divs)
                            total_amount = ticker_divs['Total'].sum()
                            avg_per_payment = total_amount / total_payments
                            position_summary[ticker] = {
                                'shares': current_shares,
                                'avg_div': avg_per_payment,
                                'payments': total_payments
                            }
                
                estimated_yearly = 0
                for ticker, info in position_summary.items():
                    ticker_div_trades = dividend_trades[dividend_trades['Ticker'] == ticker]
                    if len(ticker_div_trades) >= 2:
                        ticker_days = (pd.to_datetime(ticker_div_trades['Date']).max() - 
                                     pd.to_datetime(ticker_div_trades['Date']).min()).days
                        if ticker_days > 0:
                            annual_freq = info['payments'] * (365 / ticker_days)
                            estimated_yearly += info['avg_div'] * annual_freq
                    else:
                        estimated_yearly += info['avg_div'] * 52
                
                estimated_monthly = estimated_yearly / 12
                
                # Display metrics
                text_widget.insert(tk.END, "Historical Performance:\n", "highlight")
                text_widget.insert(tk.END, f"  Tracking Period: ", "neutral")
                text_widget.insert(tk.END, f"{days_tracked} days\n", "ticker")
                text_widget.insert(tk.END, f"  Total Dividend Payments: ", "neutral")
                text_widget.insert(tk.END, f"{len(dividend_trades)}\n\n", "ticker")
                
                text_widget.insert(tk.END, "Average Income (Based on History):\n", "highlight")
                text_widget.insert(tk.END, f"  Monthly Average: ", "neutral")
                text_widget.insert(tk.END, f"${avg_monthly:,.2f}\n", "positive")
                text_widget.insert(tk.END, f"  Yearly Average: ", "neutral")
                text_widget.insert(tk.END, f"${avg_yearly:,.2f}\n\n", "positive")
                
                if position_summary:
                    text_widget.insert(tk.END, "Estimated Future Income (Current Holdings):\n", "highlight")
                    text_widget.insert(tk.END, f"  Est. Monthly: ", "neutral")
                    text_widget.insert(tk.END, f"${estimated_monthly:,.2f}", "positive")
                    if avg_monthly > 0:
                        pct_change = ((estimated_monthly - avg_monthly) / avg_monthly * 100)
                        change_tag = "positive" if pct_change >= 0 else "negative"
                        text_widget.insert(tk.END, f" ({pct_change:+.1f}%)\n", change_tag)
                    else:
                        text_widget.insert(tk.END, "\n")
                    
                    text_widget.insert(tk.END, f"  Est. Yearly: ", "neutral")
                    text_widget.insert(tk.END, f"${estimated_yearly:,.2f}", "positive")
                    if avg_yearly > 0:
                        pct_change = ((estimated_yearly - avg_yearly) / avg_yearly * 100)
                        change_tag = "positive" if pct_change >= 0 else "negative"
                        text_widget.insert(tk.END, f" ({pct_change:+.1f}%)\n\n", change_tag)
                    else:
                        text_widget.insert(tk.END, "\n\n")
                    
                    # Calculate total investment and yields
                    total_investment = 0
                    ticker_investments = {}
                    
                    for ticker in df['Ticker'].unique():
                        ticker_trades = df[df['Ticker'] == ticker]
                        ticker_invested = ticker_trades[ticker_trades['Action'] == 'BUY']['Total'].sum()
                        ticker_sold = ticker_trades[ticker_trades['Action'] == 'SELL']['Total'].sum()
                        net_investment = ticker_invested - ticker_sold
                        if net_investment > 0:
                            ticker_investments[ticker] = net_investment
                            total_investment += net_investment
                    
                    # Calculate overall yields
                    monthly_yield = (avg_monthly / total_investment * 100) if total_investment > 0 else 0
                    yearly_yield = (avg_yearly / total_investment * 100) if total_investment > 0 else 0
                    est_monthly_yield = (estimated_monthly / total_investment * 100) if total_investment > 0 else 0
                    est_yearly_yield = (estimated_yearly / total_investment * 100) if total_investment > 0 else 0
                    
                    text_widget.insert(tk.END, "Return on Investment (Dividend Yield):\n", "highlight")
                    text_widget.insert(tk.END, f"  Total Investment: ", "neutral")
                    text_widget.insert(tk.END, f"${total_investment:,.2f}\n", "amount")
                    text_widget.insert(tk.END, f"  Monthly Yield (Historical): ", "neutral")
                    text_widget.insert(tk.END, f"{monthly_yield:.2f}%\n", "positive")
                    text_widget.insert(tk.END, f"  Annual Yield (Historical): ", "neutral")
                    text_widget.insert(tk.END, f"{yearly_yield:.2f}%\n", "positive")
                    text_widget.insert(tk.END, f"  Est. Monthly Yield: ", "neutral")
                    text_widget.insert(tk.END, f"{est_monthly_yield:.2f}%", "ticker")
                    if monthly_yield > 0:
                        yield_change = est_monthly_yield - monthly_yield
                        yield_tag = "positive" if yield_change >= 0 else "negative"
                        text_widget.insert(tk.END, f" ({yield_change:+.2f}%)\n", yield_tag)
                    else:
                        text_widget.insert(tk.END, "\n")
                    text_widget.insert(tk.END, f"  Est. Annual Yield: ", "neutral")
                    text_widget.insert(tk.END, f"{est_yearly_yield:.2f}%", "ticker")
                    if yearly_yield > 0:
                        yield_change = est_yearly_yield - yearly_yield
                        yield_tag = "positive" if yield_change >= 0 else "negative"
                        text_widget.insert(tk.END, f" ({yield_change:+.2f}%)\n\n", yield_tag)
                    else:
                        text_widget.insert(tk.END, "\n\n")
                    
                    text_widget.insert(tk.END, "Current Positions:\n", "highlight")
                    for ticker, info in position_summary.items():
                        ticker_div_trades = dividend_trades[dividend_trades['Ticker'] == ticker]
                        ticker_days = (pd.to_datetime(ticker_div_trades['Date']).max() - 
                                     pd.to_datetime(ticker_div_trades['Date']).min()).days
                        
                        if len(ticker_div_trades) >= 2 and ticker_days > 0:
                            annual_freq = info['payments'] * (365 / ticker_days)
                            est_annual = info['avg_div'] * annual_freq
                        else:
                            est_annual = info['avg_div'] * 52
                        
                        est_monthly_ticker = est_annual / 12
                        ticker_investment = ticker_investments.get(ticker, 0)
                        ticker_monthly_yield = (est_monthly_ticker / ticker_investment * 100) if ticker_investment > 0 else 0
                        ticker_yearly_yield = (est_annual / ticker_investment * 100) if ticker_investment > 0 else 0
                        
                        text_widget.insert(tk.END, f"  {ticker}: ", "ticker")
                        text_widget.insert(tk.END, f"{info['shares']} shares, ", "neutral")
                        text_widget.insert(tk.END, f"Inv: ${ticker_investment:,.2f}, ", "neutral")
                        text_widget.insert(tk.END, f"Est. ${est_annual:,.2f}/yr ", "positive")
                        
                        # Color code yield based on performance
                        if ticker_yearly_yield >= 10:
                            yield_tag = "positive"
                        elif ticker_yearly_yield >= 5:
                            yield_tag = "ticker"
                        else:
                            yield_tag = "neutral"
                        text_widget.insert(tk.END, f"({ticker_yearly_yield:.2f}% annual)\n", yield_tag)
                else:
                    text_widget.insert(tk.END, "\nNo current positions with dividend history.\n", "neutral")
            else:
                text_widget.insert(tk.END, "No dividend data yet. Log dividend payments to see projections.\n", "neutral")
            
            text_widget.insert(tk.END, "\n")
            text_widget.insert(tk.END, "="*80 + "\n")
            text_widget.insert(tk.END, "                    END OF ANALYSIS\n", "header")
            text_widget.insert(tk.END, "="*80 + "\n")
            
            text_widget.config(state=tk.DISABLED)
            
            # Add close button with better styling
            button_frame = tk.Frame(root, bg='#1e1e1e', pady=10)
            button_frame.pack()
            close_btn = tk.Button(button_frame, text="Close", command=root.destroy,
                                 font=("Arial", 14, "bold"), bg='#ef4444', fg='white',
                                 padx=30, pady=10, cursor='hand2', relief=tk.FLAT)
            close_btn.pack()
            
        else:
            label = tk.Label(root, text="No trade data found. Start logging trades first!", 
                           font=("Arial", 14), bg='#2c3e50', fg='white')
            label.pack(pady=50)
    
    except Exception as e:
        error_label = tk.Label(root, text=f"Error: {e}", font=("Arial", 12), 
                              bg='#2c3e50', fg='#e74c3c')
        error_label.pack(pady=50)
    
    root.mainloop()

if __name__ == "__main__":
    create_trade_analyzer()
