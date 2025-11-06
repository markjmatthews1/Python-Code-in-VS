"""
Phase 4 Integration Guide - Catalyst Scanner Advanced Features
============================================================

Complete integration instructions for Phase 4 advanced features:
1. Real-time market data streaming
2. Live catalyst scoring with ML enhancement
3. Portfolio impact assessment
4. Performance tracking and validation
5. Live dashboard with risk monitoring
6. AI-powered predictive modeling

Author: GitHub Copilot & Investment Catalyst Team
Date: October 1, 2025
Status: ✅ IMPLEMENTATION COMPLETE - Ready for Integration
"""

# PHASE 4 INTEGRATION CHECKLIST
# ============================

## 1. CORE INFRASTRUCTURE ✅ COMPLETE
## ----------------------------------

### Real-Time Data Streaming (real_time_data_stream.py)
- ✅ Multi-threaded data fetching with concurrent API calls
- ✅ Volume surge detection and market hours awareness  
- ✅ Automatic retry logic with exponential backoff
- ✅ Live quote streaming with RealTimeQuote dataclass
- ✅ Market state detection (pre-market, regular, after-hours, closed)

### Live Catalyst Scoring (live_catalyst_scorer.py)
- ✅ Real-time catalyst impact analysis
- ✅ ML-enhanced scoring with market reaction correlation
- ✅ Confidence scoring based on historical accuracy
- ✅ Multi-timeframe analysis (1min, 5min, 15min, 1hour)
- ✅ Alert level classification (LOW/MEDIUM/HIGH)

### Market Impact Calculator (market_impact_calculator.py)
- ✅ Portfolio-wide impact assessment
- ✅ Position-weighted catalyst scoring
- ✅ Risk exposure calculation with correlation analysis
- ✅ Real-time P&L impact estimation
- ✅ Diversification scoring and concentration risk

### Performance Tracker (performance_tracker.py)
- ✅ Catalyst prediction accuracy tracking
- ✅ SQLite database for persistent storage
- ✅ Hit/miss/partial outcome classification
- ✅ Performance attribution analysis
- ✅ Model feedback loop for continuous improvement

### Live Dashboard Panel (live_dashboard_panel.py)
- ✅ Real-time tabbed interface
- ✅ Live catalyst scores visualization
- ✅ Portfolio impact monitoring
- ✅ Performance metrics display
- ✅ Risk monitoring with alerts


## 2. INTEGRATION STEPS
## ===================

### Step 1: Update Main Catalyst Scanner (main.py)
```python
# Add to imports
from gui.live_dashboard_panel import integrate_live_dashboard

# Add to main window initialization
class CatalystScannerApp:
    def __init__(self):
        # ... existing initialization ...
        
        # Add Phase 4 live dashboard
        self.live_dashboard = integrate_live_dashboard(
            self.root, 
            self.portfolio_loader
        )
        
        # Add menu item for live dashboard
        self.view_menu.add_command(
            label="Live Dashboard",
            command=self.show_live_dashboard
        )
    
    def show_live_dashboard(self):
        """Show live dashboard window"""
        if self.live_dashboard:
            # Create new window or bring to front
            dashboard_window = tk.Toplevel(self.root)
            dashboard_window.title("Catalyst Scanner - Live Dashboard")
            dashboard_window.geometry("1200x800")
            
            # Re-initialize dashboard in new window
            self.live_dashboard = integrate_live_dashboard(
                dashboard_window, 
                self.portfolio_loader
            )
```

### Step 2: Update Requirements (requirements.txt)
```
# Add new dependencies for Phase 4
numpy>=1.21.0
pandas>=1.3.0
sqlite3  # Usually included with Python
concurrent.futures  # Part of standard library
```

### Step 3: Update Configuration (config.py)
```python
# Add Phase 4 configuration
PHASE4_CONFIG = {
    'real_time_data': {
        'update_frequency': 30,  # seconds
        'max_concurrent_requests': 10,
        'retry_attempts': 3,
        'timeout_seconds': 10
    },
    'catalyst_scoring': {
        'confidence_threshold': 0.6,
        'alert_thresholds': {
            'low': 5.0,
            'medium': 7.0, 
            'high': 8.5
        },
        'historical_lookback_days': 30
    },
    'portfolio_impact': {
        'risk_thresholds': {
            'low': 0.02,
            'medium': 0.05,
            'high': 0.10,
            'critical': 0.15
        },
        'correlation_threshold': 0.7
    },
    'performance_tracking': {
        'evaluation_periods': [1, 4, 24, 72],  # hours
        'accuracy_thresholds': {
            'hit': 0.7,
            'partial': 0.3,
            'miss': 0.0
        }
    }
}
```

### Step 4: Update Data Collectors Integration
```python
# In data_collectors/__init__.py or main data collector
from analyzers.real_time_data_stream import RealTimeDataStream
from analyzers.live_catalyst_scorer import LiveCatalystScorer

class EnhancedDataCollector:
    def __init__(self):
        # ... existing initialization ...
        
        # Add Phase 4 components
        self.real_time_stream = RealTimeDataStream()
        self.live_scorer = LiveCatalystScorer()
        
    def collect_enhanced_data(self, symbols):
        """Enhanced data collection with real-time scoring"""
        # Get real-time quotes
        quotes = self.real_time_stream.get_real_time_quotes(symbols)
        
        # Score catalysts in real-time
        scores = self.live_scorer.update_live_scores(quotes)
        
        return {
            'quotes': quotes,
            'catalyst_scores': scores,
            'timestamp': datetime.now()
        }
```

### Step 5: Update Portfolio Integration
```python
# In portfolio loader or manager
from analyzers.market_impact_calculator import MarketImpactCalculator

class EnhancedPortfolioManager:
    def __init__(self):
        # ... existing initialization ...
        
        # Add impact calculator
        self.impact_calculator = MarketImpactCalculator(self)
        
    def get_real_time_impact(self, catalyst_scores, quotes):
        """Get real-time portfolio impact"""
        return self.impact_calculator.calculate_portfolio_impact(
            catalyst_scores, quotes
        )
```


## 3. TESTING AND VALIDATION
## =========================

### Unit Tests
```python
# tests/test_phase4_integration.py
import unittest
from analyzers.real_time_data_stream import RealTimeDataStream
from analyzers.live_catalyst_scorer import LiveCatalystScorer
from analyzers.market_impact_calculator import MarketImpactCalculator
from analyzers.performance_tracker import PerformanceTracker

class TestPhase4Integration(unittest.TestCase):
    
    def test_data_stream_basic_functionality(self):
        """Test real-time data streaming"""
        stream = RealTimeDataStream()
        quotes = stream.get_real_time_quotes(['AAPL', 'MSFT'])
        self.assertIsInstance(quotes, dict)
        
    def test_catalyst_scorer_integration(self):
        """Test live catalyst scoring"""
        scorer = LiveCatalystScorer()
        mock_quotes = {'AAPL': {'price': 150, 'change_percent': 2.5}}
        scores = scorer.update_live_scores(mock_quotes)
        self.assertIsInstance(scores, list)
        
    def test_impact_calculator(self):
        """Test portfolio impact calculation"""
        calculator = MarketImpactCalculator()
        # Test with mock data
        self.assertIsNotNone(calculator)
        
    def test_performance_tracker(self):
        """Test performance tracking"""
        tracker = PerformanceTracker()
        # Test database initialization
        self.assertTrue(tracker.db_path.exists())

if __name__ == '__main__':
    unittest.main()
```

### Integration Test
```python
# Run full integration test
python -c "
from gui.live_dashboard_panel import LiveDashboardPanel
import tkinter as tk

root = tk.Tk()
dashboard = LiveDashboardPanel(root)
print('✅ Phase 4 integration test successful')
root.destroy()
"
```


## 4. PERFORMANCE OPTIMIZATION
## ===========================

### Database Optimization
```sql
-- Add indexes for performance
CREATE INDEX idx_catalyst_outcomes_symbol ON catalyst_outcomes(symbol);
CREATE INDEX idx_catalyst_outcomes_prediction_time ON catalyst_outcomes(prediction_time);
CREATE INDEX idx_performance_metrics_calculation_date ON performance_metrics(calculation_date);
```

### API Rate Limiting
```python
# In real_time_data_stream.py
# Implement rate limiting to avoid API throttling
from time import sleep
import threading

class RateLimiter:
    def __init__(self, max_requests_per_minute=60):
        self.max_requests = max_requests_per_minute
        self.requests = []
        self.lock = threading.Lock()
    
    def wait_if_needed(self):
        with self.lock:
            now = time.time()
            # Remove requests older than 1 minute
            self.requests = [t for t in self.requests if now - t < 60]
            
            if len(self.requests) >= self.max_requests:
                sleep_time = 60 - (now - self.requests[0])
                if sleep_time > 0:
                    sleep(sleep_time)
            
            self.requests.append(now)
```

### Memory Management
```python
# In live components, implement cleanup
class ComponentManager:
    def __init__(self):
        self.components = []
    
    def register_component(self, component):
        self.components.append(component)
    
    def cleanup_all(self):
        for component in self.components:
            if hasattr(component, 'cleanup'):
                component.cleanup()
```


## 5. DEPLOYMENT CHECKLIST
## =======================

### Pre-Deployment
- [ ] All Phase 4 files created and in correct directories
- [ ] Import statements updated in main application
- [ ] Configuration updated with Phase 4 settings
- [ ] Requirements.txt updated with new dependencies
- [ ] Unit tests passing for all Phase 4 components

### Deployment Steps
1. [ ] Backup existing catalyst_scanner directory
2. [ ] Copy Phase 4 files to appropriate directories:
   - `analyzers/real_time_data_stream.py`
   - `analyzers/live_catalyst_scorer.py` 
   - `analyzers/market_impact_calculator.py`
   - `analyzers/performance_tracker.py`
   - `gui/live_dashboard_panel.py`
3. [ ] Update main application files with integration code
4. [ ] Test basic functionality
5. [ ] Test live dashboard launch
6. [ ] Verify real-time data streaming
7. [ ] Test portfolio impact calculations

### Post-Deployment Validation
- [ ] Live dashboard opens without errors
- [ ] Real-time data streams successfully
- [ ] Catalyst scoring updates in real-time
- [ ] Portfolio impact calculations work
- [ ] Performance tracking database created
- [ ] All tabs in dashboard functional
- [ ] Risk monitoring alerts working


## 6. USAGE INSTRUCTIONS
## ====================

### Starting Live Monitoring
1. Launch Catalyst Scanner application
2. Load portfolio data (if available)
3. Open Live Dashboard from View menu
4. Click "START LIVE MONITORING" 
5. Set update frequency (10-120 seconds)
6. Monitor real-time catalyst scores and portfolio impact

### Dashboard Features
- **Live Scores Tab**: Real-time catalyst scores with market data
- **Portfolio Impact Tab**: Position-by-position impact analysis
- **Performance Tab**: Historical accuracy and prediction tracking
- **Risk Monitor Tab**: Portfolio risk metrics and alerts

### Performance Tracking
1. Catalyst predictions automatically recorded
2. Outcomes evaluated after specified time periods
3. Accuracy metrics calculated and stored
4. Performance summaries available in dashboard

### Risk Monitoring
- Correlation risk analysis
- Position concentration monitoring
- Real-time P&L impact estimation
- Automated risk level alerts


## 7. TROUBLESHOOTING
## ==================

### Common Issues

**Import Errors**
```
Error: Import "analyzers.real_time_data_stream" could not be resolved
Solution: Ensure Python path includes catalyst_scanner directory
export PYTHONPATH="${PYTHONPATH}:/path/to/catalyst_scanner"
```

**API Rate Limiting**
```
Error: Too many API requests
Solution: Increase update frequency or implement rate limiting
```

**Database Errors**
```
Error: Database locked or not accessible
Solution: Check file permissions and ensure SQLite is available
```

**GUI Thread Errors**
```
Error: GUI updates from wrong thread
Solution: Use root.after() for thread-safe GUI updates
```

### Debug Mode
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Test individual components
from analyzers.real_time_data_stream import RealTimeDataStream
stream = RealTimeDataStream()
quotes = stream.get_real_time_quotes(['AAPL'])
print(f"Debug quotes: {quotes}")
```


## 8. FUTURE ENHANCEMENTS
## ======================

### Phase 5 Considerations
- Machine learning model training pipeline
- Advanced correlation analysis with sector data
- Integration with trading platforms for live execution
- Mobile app companion for alerts
- Advanced charting and technical analysis
- Social sentiment integration
- Options flow analysis
- Institutional activity tracking

### Scalability Improvements
- Microservices architecture for large deployments
- Redis caching for frequently accessed data
- Apache Kafka for real-time data streaming
- Docker containerization
- Cloud deployment options (AWS, Azure, GCP)


## 9. MAINTENANCE
## ==============

### Regular Tasks
- Monitor database size and performance
- Update API endpoints as needed
- Calibrate ML models based on performance data
- Review and adjust risk thresholds
- Backup performance tracking database

### Updates
- Phase 4 components designed for modular updates
- Configuration-driven parameters for easy tuning
- Versioned database schema for safe upgrades
- Backward compatibility maintained where possible


## 10. SUPPORT
## ============

### Documentation
- Code comments provide implementation details
- Docstrings explain class and method functionality
- Type hints improve code readability
- Error handling with descriptive messages

### Monitoring
- Comprehensive logging throughout all components
- Performance metrics tracked automatically
- Error rates and success rates monitored
- Resource usage tracking available

---

**Phase 4 Status: ✅ IMPLEMENTATION COMPLETE**
**Integration Status: 🔄 READY FOR DEPLOYMENT**
**Next Steps: Integrate with main application and deploy**