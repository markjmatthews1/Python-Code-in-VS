"""
Automation Engine for RecoveryApp
Provides scheduled operations, market hour monitoring, and enhanced persistence
"""
import schedule
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
import json
import os
import logging
from dataclasses import asdict

# Import RecoveryApp components
from utils.models import TickerPosition, TradeEntry, PortfolioManager
from utils.strategy_engine import (
    OptionChainAnalyzer, 
    PutOverlayEvaluator, 
    CallOverlayEvaluator, 
    SyntheticRecoveryEvaluator,
    estimate_recovery_time
)

class MarketHours:
    """Market hours and trading day utilities"""
    
    @staticmethod
    def is_market_open() -> bool:
        """Check if market is currently open (simplified US market hours)"""
        now = datetime.now()
        
        # Check if it's a weekday (Monday=0, Sunday=6)
        if now.weekday() >= 5:  # Saturday or Sunday
            return False
        
        # Market hours: 9:30 AM - 4:00 PM ET (simplified, no holidays)
        market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
        market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)
        
        return market_open <= now <= market_close
    
    @staticmethod
    def next_market_open() -> datetime:
        """Get the next market open time"""
        now = datetime.now()
        
        # If currently weekday and before market open, return today's open
        if now.weekday() < 5 and now.time() < datetime.strptime("09:30", "%H:%M").time():
            return now.replace(hour=9, minute=30, second=0, microsecond=0)
        
        # Otherwise, find next weekday
        days_ahead = 1
        while True:
            next_day = now + timedelta(days=days_ahead)
            if next_day.weekday() < 5:  # Weekday
                return next_day.replace(hour=9, minute=30, second=0, microsecond=0)
            days_ahead += 1
    
    @staticmethod
    def time_until_market_open() -> timedelta:
        """Get time remaining until next market open"""
        return MarketHours.next_market_open() - datetime.now()

class PersistenceManager:
    """Enhanced persistence layer for comprehensive data management"""
    
    def __init__(self, data_directory: str = "data"):
        self.data_dir = data_directory
        self.ensure_data_directory()
        
        # File paths
        self.portfolio_file = os.path.join(data_directory, "portfolio.json")
        self.trades_file = os.path.join(data_directory, "trades_history.json")
        self.recovery_status_file = os.path.join(data_directory, "recovery_status.json")
        self.automation_log_file = os.path.join(data_directory, "automation.log")
        self.market_data_cache = os.path.join(data_directory, "market_cache.json")
        
        # Setup logging
        self.setup_logging()
        
    def ensure_data_directory(self):
        """Create data directory if it doesn't exist"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            
    def setup_logging(self):
        """Setup logging for automation activities"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.automation_log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def save_portfolio(self, portfolio: PortfolioManager) -> bool:
        """Save complete portfolio with all positions and trades"""
        try:
            portfolio_data = {
                'saved_at': datetime.now().isoformat(),
                'positions': []
            }
            
            for position in portfolio.positions:
                position_data = {
                    'ticker': position.ticker,
                    'cost_basis': position.cost_basis,
                    'qty': position.qty,
                    'purchase_date': position.purchase_date,
                    'notes': position.notes,
                    'target_recovery_price': position.target_recovery_price,
                    'trades': [trade.to_dict() for trade in position.trades]
                }
                portfolio_data['positions'].append(position_data)
            
            with open(self.portfolio_file, 'w') as f:
                json.dump(portfolio_data, f, indent=2)
            
            self.logger.info(f"Portfolio saved: {len(portfolio.positions)} positions")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save portfolio: {str(e)}")
            return False
    
    def load_portfolio(self) -> PortfolioManager:
        """Load complete portfolio with all positions and trades"""
        portfolio = PortfolioManager()
        
        try:
            if os.path.exists(self.portfolio_file):
                with open(self.portfolio_file, 'r') as f:
                    data = json.load(f)
                
                for pos_data in data.get('positions', []):
                    # Create position
                    position = TickerPosition(
                        ticker=pos_data['ticker'],
                        cost_basis=pos_data['cost_basis'],
                        qty=pos_data['qty'],
                        purchase_date=pos_data['purchase_date'],
                        notes=pos_data.get('notes', ''),
                        target_recovery_price=pos_data.get('target_recovery_price')
                    )
                    
                    # Add trades
                    for trade_data in pos_data.get('trades', []):
                        trade = TradeEntry.from_dict(trade_data)
                        position.trades.append(trade)
                    
                    portfolio.add_position(position)
                
                self.logger.info(f"Portfolio loaded: {len(portfolio.positions)} positions")
            
        except Exception as e:
            self.logger.error(f"Failed to load portfolio: {str(e)}")
        
        return portfolio
    
    def save_trades_history(self, trades_history: List[Dict]) -> bool:
        """Save complete trades history"""
        try:
            history_data = {
                'saved_at': datetime.now().isoformat(),
                'trades': trades_history
            }
            
            with open(self.trades_file, 'w') as f:
                json.dump(history_data, f, indent=2)
            
            self.logger.info(f"Trades history saved: {len(trades_history)} trades")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save trades history: {str(e)}")
            return False
    
    def load_trades_history(self) -> List[Dict]:
        """Load complete trades history"""
        try:
            if os.path.exists(self.trades_file):
                with open(self.trades_file, 'r') as f:
                    data = json.load(f)
                
                trades = data.get('trades', [])
                self.logger.info(f"Trades history loaded: {len(trades)} trades")
                return trades
            
        except Exception as e:
            self.logger.error(f"Failed to load trades history: {str(e)}")
        
        return []
    
    def save_recovery_status(self, recovery_status: Dict) -> bool:
        """Save recovery status and analysis results"""
        try:
            status_data = {
                'updated_at': datetime.now().isoformat(),
                'recovery_analysis': recovery_status
            }
            
            with open(self.recovery_status_file, 'w') as f:
                json.dump(status_data, f, indent=2)
            
            self.logger.info("Recovery status saved")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save recovery status: {str(e)}")
            return False
    
    def load_recovery_status(self) -> Dict:
        """Load recovery status and analysis results"""
        try:
            if os.path.exists(self.recovery_status_file):
                with open(self.recovery_status_file, 'r') as f:
                    data = json.load(f)
                
                recovery_status = data.get('recovery_analysis', {})
                self.logger.info("Recovery status loaded")
                return recovery_status
            
        except Exception as e:
            self.logger.error(f"Failed to load recovery status: {str(e)}")
        
        return {}
    
    def save_market_cache(self, market_data: Dict) -> bool:
        """Save market data cache for offline access"""
        try:
            cache_data = {
                'cached_at': datetime.now().isoformat(),
                'market_data': market_data
            }
            
            with open(self.market_data_cache, 'w') as f:
                json.dump(cache_data, f, indent=2)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save market cache: {str(e)}")
            return False
    
    def load_market_cache(self) -> Dict:
        """Load cached market data"""
        try:
            if os.path.exists(self.market_data_cache):
                with open(self.market_data_cache, 'r') as f:
                    data = json.load(f)
                
                # Check if cache is recent (within 1 hour)
                cached_at = datetime.fromisoformat(data['cached_at'])
                if datetime.now() - cached_at < timedelta(hours=1):
                    return data.get('market_data', {})
            
        except Exception as e:
            self.logger.error(f"Failed to load market cache: {str(e)}")
        
        return {}

class AutomationEngine:
    """Main automation engine for scheduled operations"""
    
    def __init__(self, portfolio_manager: PortfolioManager, persistence_manager: PersistenceManager):
        self.portfolio = portfolio_manager
        self.persistence = persistence_manager
        self.logger = persistence_manager.logger
        
        # Strategy evaluators
        self.option_analyzer = OptionChainAnalyzer()
        self.put_evaluator = PutOverlayEvaluator(self.option_analyzer)
        self.call_evaluator = CallOverlayEvaluator(self.option_analyzer)
        self.synthetic_evaluator = SyntheticRecoveryEvaluator(self.option_analyzer)
        
        # Automation state
        self.is_running = False
        self.scheduler_thread = None
        self.market_scan_thread = None
        self.scan_interval = 300  # 5 minutes during market hours
        
        # Callbacks for updates
        self.update_callbacks: List[Callable] = []
        
        # Market scan results
        self.last_scan_results = {}
        self.scan_history = []
        
    def add_update_callback(self, callback: Callable):
        """Add callback function to be called on updates"""
        self.update_callbacks.append(callback)
    
    def notify_callbacks(self):
        """Notify all registered callbacks of updates"""
        for callback in self.update_callbacks:
            try:
                callback()
            except Exception as e:
                self.logger.error(f"Callback error: {str(e)}")
    
    def start_automation(self):
        """Start the automation engine"""
        if self.is_running:
            self.logger.warning("Automation already running")
            return
        
        self.is_running = True
        self.logger.info("🚀 Starting RecoveryApp Automation Engine")
        
        # Setup scheduled tasks
        self.setup_schedule()
        
        # Start scheduler thread
        self.scheduler_thread = threading.Thread(target=self.run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        # Start market scanning thread
        self.market_scan_thread = threading.Thread(target=self.run_market_scanner, daemon=True)
        self.market_scan_thread.start()
        
        self.logger.info("✅ Automation engine started successfully")
    
    def stop_automation(self):
        """Stop the automation engine"""
        if not self.is_running:
            return
        
        self.is_running = False
        self.logger.info("⏹️ Stopping automation engine...")
        
        # Save final state
        self.save_all_data()
        
        self.logger.info("✅ Automation engine stopped")
    
    def setup_schedule(self):
        """Setup all scheduled tasks"""
        # Daily tasks
        schedule.every().day.at("09:00").do(self.daily_refresh)
        schedule.every().day.at("16:30").do(self.end_of_day_summary)
        
        # Pre-market preparation
        schedule.every().day.at("08:00").do(self.pre_market_preparation)
        
        # Weekly portfolio review
        schedule.every().monday.at("08:30").do(self.weekly_portfolio_review)
        
        # Data backup
        schedule.every().day.at("23:00").do(self.backup_data)
        
        self.logger.info("📅 Scheduled tasks configured")
    
    def run_scheduler(self):
        """Run the schedule checker"""
        while self.is_running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except Exception as e:
                self.logger.error(f"Scheduler error: {str(e)}")
                time.sleep(60)
    
    def run_market_scanner(self):
        """Run continuous market scanning during market hours"""
        while self.is_running:
            try:
                if MarketHours.is_market_open():
                    self.market_hour_scan()
                    time.sleep(self.scan_interval)
                else:
                    # Check every 30 minutes when market is closed
                    time.sleep(1800)
            except Exception as e:
                self.logger.error(f"Market scanner error: {str(e)}")
                time.sleep(300)  # Wait 5 minutes on error
    
    def daily_refresh(self):
        """Daily refresh of all portfolio data"""
        self.logger.info("🔄 Starting daily refresh")
        
        try:
            # Refresh portfolio data
            self.refresh_portfolio_data()
            
            # Update recovery analysis
            self.update_recovery_analysis()
            
            # Save updated data
            self.save_all_data()
            
            # Notify callbacks
            self.notify_callbacks()
            
            self.logger.info("✅ Daily refresh completed")
            
        except Exception as e:
            self.logger.error(f"Daily refresh failed: {str(e)}")
    
    def pre_market_preparation(self):
        """Pre-market preparation tasks"""
        self.logger.info("🌅 Pre-market preparation")
        
        try:
            # Load overnight data changes
            self.portfolio = self.persistence.load_portfolio()
            
            # Prepare market scan parameters
            self.prepare_market_scan()
            
            self.logger.info("✅ Pre-market preparation completed")
            
        except Exception as e:
            self.logger.error(f"Pre-market preparation failed: {str(e)}")
    
    def market_hour_scan(self):
        """Continuous scanning during market hours"""
        try:
            scan_results = {}
            
            for position in self.portfolio.positions:
                # Get current price (placeholder - would use real-time data)
                current_price = position.cost_basis * 0.85  # Simulate underwater position
                
                # Analyze all strategies
                position_analysis = {
                    'ticker': position.ticker,
                    'current_price': current_price,
                    'timestamp': datetime.now().isoformat(),
                    'strategies': {}
                }
                
                # Put overlay analysis
                try:
                    put_results = self.put_evaluator.evaluate_put_overlay(position, current_price)
                    position_analysis['strategies']['put_overlay'] = put_results
                except Exception as e:
                    self.logger.warning(f"Put overlay analysis failed for {position.ticker}: {str(e)}")
                
                # Call overlay analysis
                try:
                    call_results = self.call_evaluator.evaluate_call_overlay(position, current_price)
                    position_analysis['strategies']['call_overlay'] = call_results
                except Exception as e:
                    self.logger.warning(f"Call overlay analysis failed for {position.ticker}: {str(e)}")
                
                # Synthetic recovery analysis
                try:
                    synthetic_results = self.synthetic_evaluator.evaluate_synthetic_recovery(position, current_price)
                    position_analysis['strategies']['synthetic_recovery'] = synthetic_results
                except Exception as e:
                    self.logger.warning(f"Synthetic analysis failed for {position.ticker}: {str(e)}")
                
                # Recovery time estimation
                try:
                    recovery_time = estimate_recovery_time(
                        position.ticker, 
                        current_price, 
                        position.target_recovery_price or position.cost_basis
                    )
                    position_analysis['recovery_time'] = recovery_time
                except Exception as e:
                    self.logger.warning(f"Recovery time estimation failed for {position.ticker}: {str(e)}")
                
                scan_results[position.ticker] = position_analysis
            
            # Update scan results
            self.last_scan_results = scan_results
            self.scan_history.append({
                'timestamp': datetime.now().isoformat(),
                'results': scan_results
            })
            
            # Keep only last 100 scans
            if len(self.scan_history) > 100:
                self.scan_history = self.scan_history[-100:]
            
            # Cache market data
            self.persistence.save_market_cache(scan_results)
            
        except Exception as e:
            self.logger.error(f"Market scan failed: {str(e)}")
    
    def end_of_day_summary(self):
        """End of day summary and cleanup"""
        self.logger.info("🌆 End of day summary")
        
        try:
            # Generate summary
            summary = self.generate_daily_summary()
            
            # Save summary
            self.save_daily_summary(summary)
            
            # Save all data
            self.save_all_data()
            
            self.logger.info("✅ End of day summary completed")
            
        except Exception as e:
            self.logger.error(f"End of day summary failed: {str(e)}")
    
    def weekly_portfolio_review(self):
        """Weekly comprehensive portfolio review"""
        self.logger.info("📊 Weekly portfolio review")
        
        try:
            # Comprehensive analysis
            review = self.generate_weekly_review()
            
            # Save review
            self.save_weekly_review(review)
            
            self.logger.info("✅ Weekly review completed")
            
        except Exception as e:
            self.logger.error(f"Weekly review failed: {str(e)}")
    
    def backup_data(self):
        """Backup all data"""
        self.logger.info("💾 Data backup")
        
        try:
            # Create backup directory
            backup_dir = f"backups/{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            os.makedirs(backup_dir, exist_ok=True)
            
            # Copy all data files
            import shutil
            for file_path in [
                self.persistence.portfolio_file,
                self.persistence.trades_file,
                self.persistence.recovery_status_file,
                self.persistence.market_data_cache
            ]:
                if os.path.exists(file_path):
                    shutil.copy2(file_path, backup_dir)
            
            self.logger.info(f"✅ Data backup completed: {backup_dir}")
            
        except Exception as e:
            self.logger.error(f"Data backup failed: {str(e)}")
    
    def refresh_portfolio_data(self):
        """Refresh all portfolio data"""
        # This would integrate with real-time data sources
        for position in self.portfolio.positions:
            try:
                # Update current prices, option chains, etc.
                # Placeholder for real data integration
                pass
            except Exception as e:
                self.logger.warning(f"Failed to refresh data for {position.ticker}: {str(e)}")
    
    def update_recovery_analysis(self):
        """Update recovery analysis for all positions"""
        recovery_status = {}
        
        for position in self.portfolio.positions:
            try:
                current_price = position.cost_basis * 0.85  # Placeholder
                
                recovery_analysis = {
                    'position_status': 'underwater' if current_price < position.cost_basis else 'recovered',
                    'unrealized_loss': (current_price - position.cost_basis) * position.qty,
                    'loss_percentage': ((current_price - position.cost_basis) / position.cost_basis) * 100,
                    'updated_at': datetime.now().isoformat()
                }
                
                recovery_status[position.ticker] = recovery_analysis
                
            except Exception as e:
                self.logger.warning(f"Recovery analysis failed for {position.ticker}: {str(e)}")
        
        self.persistence.save_recovery_status(recovery_status)
    
    def prepare_market_scan(self):
        """Prepare parameters for market scanning"""
        # Configure scan parameters based on portfolio
        self.logger.info("🔧 Preparing market scan parameters")
    
    def generate_daily_summary(self) -> Dict:
        """Generate daily summary"""
        return {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'portfolio_size': len(self.portfolio.positions),
            'scan_count': len(self.scan_history),
            'last_scan': self.last_scan_results,
            'generated_at': datetime.now().isoformat()
        }
    
    def save_daily_summary(self, summary: Dict):
        """Save daily summary"""
        summary_file = os.path.join(self.persistence.data_dir, f"daily_summary_{datetime.now().strftime('%Y%m%d')}.json")
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
    
    def generate_weekly_review(self) -> Dict:
        """Generate weekly review"""
        return {
            'week_of': datetime.now().strftime('%Y-%m-%d'),
            'portfolio_performance': {},
            'strategy_effectiveness': {},
            'generated_at': datetime.now().isoformat()
        }
    
    def save_weekly_review(self, review: Dict):
        """Save weekly review"""
        review_file = os.path.join(self.persistence.data_dir, f"weekly_review_{datetime.now().strftime('%Y%m%d')}.json")
        with open(review_file, 'w') as f:
            json.dump(review, f, indent=2)
    
    def save_all_data(self):
        """Save all current data"""
        self.persistence.save_portfolio(self.portfolio)
        
        # Save scan history as trades history
        if self.scan_history:
            self.persistence.save_trades_history(self.scan_history)
    
    def get_status(self) -> Dict:
        """Get current automation status"""
        return {
            'is_running': self.is_running,
            'market_open': MarketHours.is_market_open(),
            'next_market_open': MarketHours.next_market_open().isoformat(),
            'last_scan': self.last_scan_results.get('timestamp') if self.last_scan_results else None,
            'scheduled_tasks': len(schedule.jobs),
            'portfolio_size': len(self.portfolio.positions)
        }