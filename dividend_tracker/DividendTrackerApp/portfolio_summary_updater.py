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
        """Calculate performance tracking metrics"""
        # These would need historical data - using placeholders for now
        performance = {
            'weekly_change_amount': 2834.85,
            'weekly_change_percent': 0.55,
            'ytd_amount': 47836,
            'ytd_percent': 10.1
        }
        return performance
    
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
        
        # Weekly change (row 10, column B)  
        weekly_change = f"+${performance_data['weekly_change_amount']:,.2f} (+{performance_data['weekly_change_percent']:.2f}%)"
        ws.cell(row=10, column=2).value = weekly_change
        
        # YTD Performance (row 23, column B)
        ytd_performance = f"+${performance_data['ytd_amount']:,} ({performance_data['ytd_percent']:.1f}%)"
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