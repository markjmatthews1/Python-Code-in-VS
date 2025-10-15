import openpyxl
import json
import os
from datetime import datetime

class PortfolioSummaryUpdater:
    """Updates Portfolio Summary sheet values while preserving all formatting"""
    
    def __init__(self):
        self.excel_file = "outputs/Dividends_2025.xlsx"
        self.cache_file = "portfolio_data_cache.json"
    
    def run_update(self):
        """Main update method for Portfolio Summary sheet"""
        print("PORTFOLIO SUMMARY UPDATER")
        print("=" * 35)
        
        # Load cache data
        cache_data = self.load_cache_data()
        if not cache_data:
            return False
        
        # Open workbook
        wb = openpyxl.load_workbook(self.excel_file)
        ws = wb["Portfolio Summary"]
        
        print("STEP 1: Loading current portfolio values...")
        portfolio_values = self.get_portfolio_values(cache_data)
        
        print("STEP 2: Loading dividend estimates...")
        dividend_estimates = self.get_dividend_estimates(cache_data)
        
        print("STEP 3: Calculating performance metrics...")
        performance_data = self.calculate_performance_metrics(portfolio_values)
        
        print("STEP 4: Updating Portfolio Summary values...")
        self.update_current_values(ws, portfolio_values)
        self.update_dividend_estimates(ws, dividend_estimates)
        self.update_account_dividend_breakdown(ws, dividend_estimates)
        self.update_next_update_status(ws, dividend_estimates)
        self.update_account_breakdown(ws, portfolio_values)
        self.update_withdrawal_data(ws)
        self.update_performance_tracking(ws, performance_data)
        self.update_dividend_metrics(ws, dividend_estimates, portfolio_values)
        self.update_dividend_summary_section(ws, dividend_estimates)
        self.update_bito_percentages(ws, cache_data)
        section_positions = self.update_dividend_cuts_section(ws, cache_data)
        self.update_ytd_gain_loss(ws, performance_data)  # New YTD feature
        self.update_dividend_performance_metric(ws, section_positions)  # Dynamic positioning
        self.update_last_updated_date(ws)
        
        # Save workbook
        wb.save(self.excel_file)
        wb.close()
        
        print("\nSUCCESS: Portfolio Summary updated with preserved formatting!")
        return True
    
    def get_portfolio_values(self, cache_data):
        """Get current portfolio values from cache data (use pre-calculated values)"""
        # Use pre-calculated portfolio values from cache instead of calculating from positions
        portfolio_values_data = cache_data.get('portfolio_values', {})
        
        values = {}
        
        # Map cache keys to our internal keys
        values['etrade_ira'] = portfolio_values_data.get('E*TRADE IRA', 0)
        values['etrade_taxable'] = portfolio_values_data.get('E*TRADE Taxable', 0)
        values['schwab_ira'] = portfolio_values_data.get('Schwab IRA', 0)
        values['schwab_individual'] = portfolio_values_data.get('Schwab Individual', 0)
        values['k401_retirement'] = portfolio_values_data.get('401K', 128693.17)
        
        # Calculate total
        values['total_portfolio'] = (values['etrade_ira'] + values['etrade_taxable'] + 
                                   values['schwab_ira'] + values['schwab_individual'] + 
                                   values['k401_retirement'])
        
        print(f"  E*TRADE IRA: ${values['etrade_ira']:,.2f}")
        print(f"  E*TRADE Taxable: ${values['etrade_taxable']:,.2f}") 
        print(f"  Schwab IRA: ${values['schwab_ira']:,.2f}")
        print(f"  Schwab Individual: ${values['schwab_individual']:,.2f}")
        print(f"  401K Retirement: ${values['k401_retirement']:,.2f}")
        print(f"  Total Portfolio: ${values['total_portfolio']:,.2f}")
        
        return values
    
    def get_dividend_estimates(self, cache_data):
        """Calculate dividend estimates from yields data using the working approach"""
        positions_data = cache_data.get('positions', {})
        
        # Get yields data from cache using the correct key 'ticker_yields'
        yields_data = cache_data.get('ticker_yields', {})
        
        print(f"    Found {len(yields_data)} tickers with yield data in cache")
        
        # If no yields in cache, something is wrong
        if not yields_data:
            print("    ERROR: No ticker_yields data found in cache!")
            return {'weekly': 0, 'monthly': 0, 'annual': 0, 'account_breakdown': {}}
        
        estimates = {}
        total_weekly = 0
        total_monthly = 0
        total_annual = 0
        
        account_breakdown = {}
        
        for account, positions in positions_data.items():
            account_annual = 0
            
            for position in positions:
                symbol = position.get('symbol', '').strip().upper()
                market_value = position.get('market_value', 0)
                yield_info = yields_data.get(symbol, {})
                current_yield = yield_info.get('yield', 0.0) / 100.0  # Convert to decimal
                has_dividend = yield_info.get('has_dividend', False)
                
                # Only calculate if position has dividend
                if has_dividend and current_yield > 0:
                    # Calculate annual dividend
                    annual_dividend = market_value * current_yield
                    account_annual += annual_dividend
                    
                    print(f"    {symbol}: ${market_value:.0f} @ {yield_info.get('yield', 0):.2f}% = ${annual_dividend:.0f}/year")
            
            # Map account names
            if account == 'etrade_ira':
                account_breakdown['etrade_ira'] = account_annual
            elif account == 'etrade_taxable':
                account_breakdown['etrade_taxable'] = account_annual
            elif account == 'schwab_ira':
                account_breakdown['schwab_ira'] = account_annual
            elif account == 'schwab_individual':
                account_breakdown['schwab_individual'] = account_annual
            
            total_annual += account_annual
        
        total_weekly = total_annual / 52
        total_monthly = total_annual / 12
        
        estimates['weekly'] = total_weekly
        estimates['monthly'] = total_monthly  
        estimates['annual'] = total_annual
        estimates['account_breakdown'] = account_breakdown
        
        print(f"  Weekly Estimate: ${total_weekly:.2f}")
        print(f"  Monthly Estimate: ${total_monthly:.2f}")
        print(f"  Annual Estimate: ${total_annual:.2f}")
        
        return estimates
    
    def calculate_performance_metrics(self, portfolio_values):
        """Calculate performance tracking metrics from Portfolio Values 2025 sheet"""
        print("  Calculating performance metrics from Portfolio Values 2025...")
        
        try:
            # Open the Excel file to get historical data
            wb = openpyxl.load_workbook(self.excel_file)
            
            if 'Portfolio Values 2025' not in wb.sheetnames:
                print("    Warning: Portfolio Values 2025 sheet not found, using default values")
                return {'weekly_change_amount': 0, 'weekly_change_percent': 0, 'ytd_amount': 0, 'ytd_percent': 0}
            
            portfolio_ws = wb['Portfolio Values 2025']
            max_col = portfolio_ws.max_column
            
            # Get current week total (row 10, latest column)
            current_total = portfolio_ws.cell(row=10, column=max_col).value
            
            # Handle formulas and ensure we get a numeric value
            if isinstance(current_total, str):
                print(f"    Current total is a formula/string: {current_total}")
                current_total = 0
            elif current_total is None:
                current_total = 0
            
            # Find previous week total by going backwards until we find a numeric value
            prev_total = 0
            for col_offset in range(1, min(10, max_col)):  # Look back up to 10 columns
                prev_col = max_col - col_offset
                if prev_col < 1:
                    break
                    
                prev_value = portfolio_ws.cell(row=10, column=prev_col).value
                if isinstance(prev_value, (int, float)) and prev_value > 1000:  # Valid portfolio value
                    prev_total = prev_value
                    print(f"    Using column {prev_col} as previous week: ${prev_total:,.2f}")
                    break
            
            if prev_total == 0:
                prev_total = current_total  # Fallback to prevent division by zero
            
            # Calculate weekly change
            weekly_change_amount = current_total - prev_total
            weekly_change_percent = (weekly_change_amount / prev_total * 100) if prev_total > 0 else 0
            
            # Get year-start value for YTD calculation - look for first numeric value
            ytd_start_total = current_total  # Default fallback
            for col in range(1, min(20, max_col)):  # Look at first 20 columns
                start_value = portfolio_ws.cell(row=10, column=col).value
                if isinstance(start_value, (int, float)) and start_value > 1000:  # Valid portfolio value
                    ytd_start_total = start_value
                    print(f"    Using column {col} as year start: ${ytd_start_total:,.2f}")
                    break
            
            ytd_amount = current_total - ytd_start_total
            ytd_percent = (ytd_amount / ytd_start_total * 100) if ytd_start_total > 0 else 0
            
            print(f"    Current Total: ${current_total:,.2f}")
            print(f"    Previous Week: ${prev_total:,.2f}")
            print(f"    Weekly Change: ${weekly_change_amount:,.2f} ({weekly_change_percent:.2f}%)")
            print(f"    YTD Change: ${ytd_amount:,.2f} ({ytd_percent:.1f}%)")
            
            wb.close()
            
            performance = {
                'weekly_change_amount': weekly_change_amount,
                'weekly_change_percent': weekly_change_percent,
                'ytd_amount': ytd_amount,
                'ytd_percent': ytd_percent
            }
            
            return performance
            
        except Exception as e:
            print(f"    Error calculating performance metrics: {e}")
            import traceback
            traceback.print_exc()
            # Return safe default values
            return {
                'weekly_change_amount': 0,
                'weekly_change_percent': 0,
                'ytd_amount': 0,
                'ytd_percent': 0
            }
    
    def update_current_values(self, ws, portfolio_values):
        """Update current portfolio values (Column B, rows 4-9)"""
        print("  Updating current values...")
        
        # Update individual account values
        ws.cell(row=4, column=2).value = portfolio_values.get('etrade_ira', 0)  # E*TRADE IRA
        ws.cell(row=5, column=2).value = portfolio_values.get('etrade_taxable', 0)  # E*TRADE Taxable
        ws.cell(row=6, column=2).value = portfolio_values.get('schwab_ira', 0)  # Schwab IRA  
        ws.cell(row=7, column=2).value = portfolio_values.get('schwab_individual', 0)  # Schwab Individual
        ws.cell(row=8, column=2).value = portfolio_values.get('k401_retirement', 0)  # 401k Retirement
        ws.cell(row=9, column=2).value = portfolio_values.get('total_portfolio', 0)  # Total Portfolio
        
        print(f"    Updated portfolio total: ${portfolio_values['total_portfolio']:,.2f}")
    
    def update_dividend_estimates(self, ws, dividend_estimates):
        """Update dividend estimates (Column E, rows 4-6)"""
        print("  Updating dividend estimates...")
        
        ws.cell(row=4, column=5).value = dividend_estimates['weekly']  # Weekly Estimate
        ws.cell(row=5, column=5).value = dividend_estimates['monthly']  # Monthly Estimate  
        ws.cell(row=6, column=5).value = dividend_estimates['annual']  # Annual Estimate
        
        print(f"    Updated annual estimate: ${dividend_estimates['annual']:,.2f}")
    
    def update_account_dividend_breakdown(self, ws, dividend_estimates):
        """Update account breakdown annual dividends (Column D-E, rows 9-12)"""
        print("  Updating account dividend breakdown...")
        
        account_breakdown = dividend_estimates.get('account_breakdown', {})
        
        # Update annual dividend amounts for each account (this is the "ACCOUNT BREAKDOWN (Annual)" section)
        ws.cell(row=9, column=4).value = "E*TRADE IRA:"  # Label
        ws.cell(row=9, column=5).value = account_breakdown.get('etrade_ira', 0)  # Annual amount
        
        ws.cell(row=10, column=4).value = "E*TRADE Taxable:"  # Label  
        ws.cell(row=10, column=5).value = account_breakdown.get('etrade_taxable', 0)  # Annual amount
        
        ws.cell(row=11, column=4).value = "Schwab IRA:"  # Label
        ws.cell(row=11, column=5).value = account_breakdown.get('schwab_ira', 0)  # Annual amount
        
        ws.cell(row=12, column=4).value = "Schwab Individual:"  # Label
        ws.cell(row=12, column=5).value = account_breakdown.get('schwab_individual', 0)  # Annual amount
        
        print(f"    Updated account breakdown: E*TRADE IRA ${account_breakdown.get('etrade_ira', 0):,.0f}, E*TRADE Taxable ${account_breakdown.get('etrade_taxable', 0):,.0f}")
    
    def update_next_update_status(self, ws, dividend_estimates):
        """Update dividend status/next update (Row 29, Column E)"""
        print("  Updating dividend status...")
        
        # Update the "Next Update" field which shows dividend status
        ws.cell(row=29, column=4).value = "Next Update:"  # Label
        ws.cell(row=29, column=5).value = "Weekly (Automated)"  # Status
        
        print("    Updated dividend status: Next Update - Weekly (Automated)")
    
    
    def update_account_breakdown(self, ws, portfolio_values):
        """Update account breakdown percentages (Column B, rows 14-18)"""
        print("  Updating account breakdown...")
        
        total = portfolio_values['total_portfolio']
        if total > 0:
            ws.cell(row=14, column=2).value = portfolio_values.get('etrade_ira', 0) / total  # E*TRADE IRA %
            ws.cell(row=15, column=2).value = portfolio_values.get('etrade_taxable', 0) / total  # E*TRADE Taxable %
            ws.cell(row=16, column=2).value = portfolio_values.get('schwab_ira', 0) / total  # Schwab IRA %
            ws.cell(row=17, column=2).value = portfolio_values.get('schwab_individual', 0) / total  # Schwab Individual %
            ws.cell(row=18, column=2).value = portfolio_values.get('k401_retirement', 0) / total  # 401k %
    
    def update_withdrawal_data(self, ws):
        """Update withdrawal data - keep existing values for now"""
        print("  Keeping existing withdrawal data...")
        # These values are likely manually set, so preserve them
    
    def update_performance_tracking(self, ws, performance_data):
        """Update performance tracking data"""
        print("  Updating performance tracking...")
        
        # Weekly change (row 10, column B) - Handle positive and negative values  
        weekly_amount = performance_data['weekly_change_amount']
        weekly_percent = performance_data['weekly_change_percent']
        
        if weekly_amount >= 0:
            weekly_change = f"+${weekly_amount:,.2f} (+{weekly_percent:.2f}%)"
        else:
            weekly_change = f"-${abs(weekly_amount):,.2f} ({weekly_percent:.2f}%)"
        
        ws.cell(row=10, column=2).value = weekly_change
        
        # YTD Performance (row 23, column B) - Handle positive and negative values
        ytd_amount = performance_data['ytd_amount']
        ytd_percent = performance_data['ytd_percent']
        
        if ytd_amount >= 0:
            ytd_performance = f"+${ytd_amount:,.0f} (+{ytd_percent:.1f}%)"
        else:
            ytd_performance = f"-${abs(ytd_amount):,.0f} ({ytd_percent:.1f}%)"
            
        ws.cell(row=23, column=2).value = ytd_performance
    
    def update_dividend_metrics(self, ws, dividend_estimates, portfolio_values):
        """Update dividend metrics (Column E, rows 21-28)"""
        print("  Updating dividend metrics...")
        
        # Net Monthly Income (row 21)
        monthly_income = dividend_estimates['monthly'] - 1718.33  # Subtract withdrawals
        ws.cell(row=21, column=5).value = monthly_income
        
        # Net Annual Income (row 22)
        annual_income = dividend_estimates['annual'] - (1718.33 * 12)  # Subtract annual withdrawals
        ws.cell(row=22, column=5).value = annual_income
        
        # Current Yield (row 26)
        current_yield = dividend_estimates['annual'] / portfolio_values['total_portfolio']
        ws.cell(row=26, column=5).value = current_yield
        
        # Monthly Dividend Coverage (row 27)
        monthly_coverage = dividend_estimates['monthly'] / 1718.33 if 1718.33 > 0 else 0
        coverage_text = f"{monthly_coverage:.1f}x"
        ws.cell(row=27, column=5).value = coverage_text
    
    def update_dividend_summary_section(self, ws, dividend_estimates):
        """Update dividend summary section (row 35 - Current Annual Estimate)"""
        print("  Updating dividend summary section...")
        
        # Row 35: Current Annual Estimate should match row 6 
        ws.cell(row=35, column=5).value = dividend_estimates['annual']
        
        print(f"    Updated row 35 annual estimate: ${dividend_estimates['annual']:,.2f}")
    
    def update_bito_percentages(self, ws, cache_data):
        """Update BITO percentage values in column H"""
        print("  Updating BITO percentages...")
        
        # Get BITO yield from cache data
        ticker_yields = cache_data.get('ticker_yields', {})
        bito_data = ticker_yields.get('BITO', {})
        bito_yield = bito_data.get('yield', 52.64)  # Default to current value if not found
        
        # Update row 24 (H24) 
        ws.cell(row=24, column=8).value = f"BITO: {bito_yield:.2f}% (18 total)"
        
        # Update row 25 (H25)
        ws.cell(row=25, column=8).value = f"BITO: {bito_yield:.2f}% (12 total)"
        
        print(f"    Updated BITO percentage to {bito_yield:.2f}%")
    
    def update_last_updated_date(self, ws):
        """Update the last updated date in row 33"""
        print("  Updating last updated date...")
        
        from datetime import datetime
        current_date = datetime.now().strftime("%m/%d %H:%M")
        
        # Row 33, Column H (Last Updated)
        ws.cell(row=33, column=8).value = current_date
        
        print(f"    Updated last updated date to: {current_date}")
    
    def update_dividend_cuts_section(self, ws, cache_data):
        """Update dividend cuts (G&H) and increases (J&K) sections with DYNAMIC data from Historical Yield comparison"""
        print("  Updating dividend cuts and increases sections with summary totals on top...")
        
        try:
            from openpyxl.styles import Font, PatternFill, Alignment
            
            # Define formatting styles
            header_font = Font(name='Arial', size=12, bold=True)
            header_fill = PatternFill(start_color='C5D9F1', end_color='C5D9F1', fill_type='solid')
            ticker_font = Font(name='Arial', size=12)
            value_font = Font(name='Arial', size=12, color='228B22')  # Green color
            
            # Styles for summary totals at the top
            blue_fill = PatternFill(start_color='4F81BD', end_color='4F81BD', fill_type='solid')
            white_fill = PatternFill(start_color='FFFFFF', end_color='FFFFFF', fill_type='solid')
            white_font_bold = Font(name='Arial', size=12, color='FFFFFF', bold=True)
            right_align = Alignment(horizontal='right')
            
            # Helper function to safely set cell value and format (skip merged cells)
            def safe_set_cell(row, col, value, font=None, fill=None, alignment=None):
                try:
                    cell = ws.cell(row=row, column=col)
                    if hasattr(cell, '_value'):  # Regular cell
                        cell.value = value
                        if font:
                            cell.font = font
                        if fill:
                            cell.fill = fill
                        if alignment:
                            cell.alignment = alignment
                        return True
                    else:  # Merged cell - skip
                        print(f"    Skipping merged cell at row {row}, col {col}")
                        return False
                except Exception:
                    print(f"    Error setting cell at row {row}, col {col}")
                    return False
            
            # Clear expanded dividend sections (rows 5-35 to handle longer lists)
            for row in range(5, 36):
                safe_set_cell(row, 7, None)   # Column G - Cuts tickers
                safe_set_cell(row, 8, None)   # Column H - Cuts values  
                safe_set_cell(row, 10, None)  # Column J - Increases tickers
                safe_set_cell(row, 11, None)  # Column K - Increases values
            
            # Get current positions by account
            positions = cache_data.get('positions', {})
            
            # DYNAMIC YIELD COMPARISON: Get yield changes from Historical Yield sheet
            dividend_cuts, dividend_increases = self.get_dynamic_yield_changes()
            
            # PLACE SUMMARY TOTALS AT THE TOP (Row 5) - Fixed position, won't get overwritten
            if dividend_cuts or dividend_increases:
                # Calculate averages for summary
                if dividend_cuts:
                    avg_cuts = abs(sum(data['cut_percent'] for data in dividend_cuts.values()) / len(dividend_cuts))
                else:
                    avg_cuts = 0
                    
                if dividend_increases:
                    avg_increases = sum(data['increase_percent'] for data in dividend_increases.values()) / len(dividend_increases)
                else:
                    avg_increases = 0
                
                # Calculate net performance (increases - cuts)
                net_dividend_performance = avg_increases - avg_cuts
                
                # Row 5, Column G: Dividend Performance Summary with blue background
                safe_set_cell(5, 7, "Dividend Performance:", font=white_font_bold, fill=blue_fill)
                
                # Row 5, Column H: Net performance with conditional formatting
                if net_dividend_performance >= 0:
                    perf_font = Font(name='Arial', size=12, bold=True, color='228B22')  # Green
                    performance_text = f"+{net_dividend_performance:.1f}% Net Gain"
                else:
                    perf_font = Font(name='Arial', size=12, bold=True, color='FF0000')  # Red
                    performance_text = f"{net_dividend_performance:.1f}% Net Loss"
                
                safe_set_cell(5, 8, performance_text, font=perf_font, fill=white_fill, alignment=right_align)
                
                # Row 5, Columns J&K: Summary counts
                safe_set_cell(5, 10, f"Total Changes:", font=white_font_bold, fill=blue_fill)
                summary_text = f"{len(dividend_cuts)} cuts, {len(dividend_increases)} increases"
                safe_set_cell(5, 11, summary_text, font=ticker_font, fill=white_fill, alignment=right_align)
                
                print(f"    Added dividend summary at row 5: {performance_text}")
                print(f"    (Avg Increases: {avg_increases:.1f}% - Avg Cuts: {avg_cuts:.1f}%)")
            
            # Start individual items below the summary (Row 7+)
            cuts_row = 7    # Start cuts at row 7 (below summary)
            increases_row = 7  # Start increases at row 7 (below summary)
            
            # Process each account
            account_names = {
                'etrade_ira': 'Etrade IRA',
                'etrade_taxable': 'Etrade Taxable', 
                'schwab_ira': 'Schwab IRA',
                'schwab_individual': 'Schwab Individual'
            }
            
            for account_key, account_name in account_names.items():
                if account_key in positions and positions[account_key]:
                    # Extract tickers from positions list
                    account_positions = positions[account_key]
                    account_tickers = set()
                    
                    # positions[account] is a list of position objects
                    for position in account_positions:
                        if isinstance(position, dict) and 'symbol' in position:
                            account_tickers.add(position['symbol'])
                    
                    # Find dividend cuts and increases for this account
                    account_cuts = []
                    account_increases = []
                    
                    for ticker in account_tickers:
                        if ticker in dividend_cuts:
                            account_cuts.append(ticker)
                        if ticker in dividend_increases:
                            account_increases.append(ticker)
                    
                    # Process dividend CUTS (Columns G & H)
                    if account_cuts:
                        # Account header for cuts
                        if safe_set_cell(cuts_row, 7, account_name):
                            safe_set_cell(cuts_row, 8, f"{len(account_cuts)} dividend cuts:")
                        cuts_row += 1
                        
                        # Show each cut
                        for ticker in sorted(account_cuts):
                            cut_info = dividend_cuts[ticker]
                            if safe_set_cell(cuts_row, 7, f"  {ticker} ↓"):
                                cut_text = f"{cut_info['cut_percent']:.1f}% ({cut_info['old_yield']:.2f}% → {cut_info['new_yield']:.2f}%)"
                                safe_set_cell(cuts_row, 8, cut_text)
                            cuts_row += 1
                        
                        cuts_row += 1  # Extra space between accounts
                    
                    # Process dividend INCREASES (Columns J & K) with formatting
                    if account_increases:
                        # Account header for increases with blue background and bold font
                        if safe_set_cell(increases_row, 10, account_name, font=header_font, fill=header_fill):
                            safe_set_cell(increases_row, 11, f"{len(account_increases)} dividend increases:", font=header_font, fill=header_fill)
                        increases_row += 1
                        
                        # Show each increase with proper formatting
                        for ticker in sorted(account_increases):
                            increase_info = dividend_increases[ticker]
                            # Ticker with Arial 12 font
                            if safe_set_cell(increases_row, 10, f"  {ticker} ↑", font=ticker_font):
                                increase_text = f"+{increase_info['increase_percent']:.1f}% ({increase_info['old_yield']:.2f}% → {increase_info['new_yield']:.2f}%)"
                                # Values with green font
                                safe_set_cell(increases_row, 11, increase_text, font=value_font)
                            increases_row += 1
                        
                        increases_row += 1  # Extra space between accounts
            
            print(f"    Updated dividend cuts (G&H) and increases (J&K) sections with summary totals on top")
            
            # Return the final row positions (no longer needed for dynamic summary placement)
            return {'cuts_final_row': cuts_row, 'increases_final_row': increases_row}
            
        except Exception as e:
            print(f"    Error updating dividend sections: {e}")
            import traceback
            traceback.print_exc()
            return {'cuts_final_row': 7, 'increases_final_row': 7}  # Safe fallback

    def get_dynamic_yield_changes(self):
        """Extract dividend cuts and increases by comparing Historical Yield sheet Column O vs P"""
        try:
            # Load workbook to read Historical Yield sheet
            import openpyxl
            wb = openpyxl.load_workbook(self.excel_file)
            hist_ws = wb['Accounts Div historical yield']
            
            dividend_cuts = {}
            dividend_increases = {}
            
            # Scan the Historical Yield sheet for yield changes
            for row in range(3, 53):  # Typical data range
                ticker_cell = hist_ws.cell(row=row, column=1)  # Column A - Ticker
                prev_yield_cell = hist_ws.cell(row=row, column=15)  # Column O - Previous yield
                curr_yield_cell = hist_ws.cell(row=row, column=16)  # Column P - Current yield
                
                if ticker_cell.value and prev_yield_cell.value is not None and curr_yield_cell.value is not None:
                    ticker = str(ticker_cell.value).strip().upper()
                    
                    try:
                        # Handle percentage values
                        prev_yield = float(prev_yield_cell.value)
                        curr_yield = float(curr_yield_cell.value)
                        
                        # Convert from decimal to percentage if needed
                        if prev_yield < 1.0:
                            prev_yield *= 100
                        if curr_yield < 1.0:
                            curr_yield *= 100
                        
                        # Calculate change
                        if prev_yield > 0:  # Avoid division by zero
                            change_percent = ((curr_yield - prev_yield) / prev_yield) * 100
                            
                            # Significant changes (more than 1% change)
                            if abs(change_percent) > 1.0:
                                if change_percent < 0:  # Dividend cut
                                    dividend_cuts[ticker] = {
                                        'old_yield': prev_yield,
                                        'new_yield': curr_yield,
                                        'cut_percent': change_percent
                                    }
                                else:  # Dividend increase
                                    dividend_increases[ticker] = {
                                        'old_yield': prev_yield,
                                        'new_yield': curr_yield,
                                        'increase_percent': change_percent
                                    }
                    except (ValueError, TypeError):
                        continue  # Skip invalid yield data
            
            print(f"    Dynamic analysis found: {len(dividend_cuts)} cuts, {len(dividend_increases)} increases")
            return dividend_cuts, dividend_increases
            
        except Exception as e:
            print(f"    Warning: Could not read Historical Yield sheet for dynamic analysis: {e}")
            # Fall back to empty data if historical sheet unavailable
            return {}, {}

    def update_ytd_gain_loss(self, ws, performance_data):
        """Update YTD gain/loss at row 11 columns A&B with conditional formatting"""
        print("  Updating YTD gain/loss...")
        
        try:
            from openpyxl.styles import Font, PatternFill, Alignment
            
            # Get YTD data from performance_data using correct keys
            ytd_change = performance_data.get('ytd_amount', 0)
            ytd_percent = performance_data.get('ytd_percent', 0)
            
            # Define styling
            blue_fill = PatternFill(start_color='4F81BD', end_color='4F81BD', fill_type='solid')
            white_fill = PatternFill(start_color='FFFFFF', end_color='FFFFFF', fill_type='solid')
            white_font_bold = Font(name='Arial', size=12, color='FFFFFF', bold=True)  # White bold text
            right_align = Alignment(horizontal='right')  # Right alignment
            
            # Conditional formatting for positive/negative values on white background
            if ytd_change >= 0:
                value_font = Font(name='Arial', size=12, bold=True, color='228B22')  # Green for positive
            else:
                value_font = Font(name='Arial', size=12, bold=True, color='FF0000')  # Red for negative
            
            # Row 11 Column A: Description with white bold text on blue background
            ws.cell(row=11, column=1).value = "YTD Gain/Loss:"
            ws.cell(row=11, column=1).font = white_font_bold
            ws.cell(row=11, column=1).fill = blue_fill
            
            # Row 11 Column B: Value with conditional formatting, white background, right aligned
            if ytd_change >= 0:
                ytd_text = f"+${ytd_change:,.2f} (+{ytd_percent:.1f}%)"
            else:
                ytd_text = f"-${abs(ytd_change):,.2f} ({ytd_percent:.1f}%)"
            
            ws.cell(row=11, column=2).value = ytd_text
            ws.cell(row=11, column=2).font = value_font
            ws.cell(row=11, column=2).fill = white_fill  # White background for better readability
            ws.cell(row=11, column=2).alignment = right_align  # Right justify
            
            # Also update row 10 column B to be right aligned (Weekly Change)
            ws.cell(row=10, column=2).alignment = right_align
            
            print(f"    Updated YTD: {ytd_text}")
            
        except Exception as e:
            print(f"    Error updating YTD gain/loss: {e}")
            import traceback
            traceback.print_exc()

    def update_dividend_performance_metric(self, ws, section_positions=None):
        """Clean up any old dividend performance data since summary is now at the top (row 5)"""
        print("  Cleaning up old dividend performance data (summary now at top)...")
        
        try:
            # Clear any existing dividend performance data from the old dynamic position area
            for clear_row in range(25, 40):
                cell_j = ws.cell(row=clear_row, column=10)
                cell_k = ws.cell(row=clear_row, column=11)
                if cell_j.value and "Dividend Performance" in str(cell_j.value):
                    cell_j.value = None
                    cell_k.value = None
                    print(f"    Cleared old dividend performance data from row {clear_row}")
            
            print("    Dividend performance summary is now integrated at row 5 (top of cuts/increases section)")
            
        except Exception as e:
            print(f"    Error cleaning up old dividend performance data: {e}")
            import traceback
            traceback.print_exc()
    
    def load_cache_data(self):
        """Load cache data"""
        try:
            with open(self.cache_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"ERROR loading cache: {e}")
            return None

if __name__ == "__main__":
    updater = PortfolioSummaryUpdater()
    success = updater.run_update()
    
    if success:
        print("\nSUCCESS: Portfolio Summary sheet updated!")
    else:
        print("\nERROR: Portfolio Summary update failed!")