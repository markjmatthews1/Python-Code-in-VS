#!/usr/bin/env python3
"""
Enhanced Day Trading System Status Dashboard
============================================

Quick status check and maintenance dashboard for the enhanced system.
Run this to get an overview of system health and performance.

Author: GitHub Copilot
Date: September 26, 2025
"""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

def check_system_status():
    """Check overall system status"""
    
    print("🚀 ENHANCED DAY TRADING SYSTEM STATUS")
    print("=" * 50)
    print(f"📅 Report Date: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
    print()
    
    # 1. File System Check
    print("📁 FILE SYSTEM STATUS")
    print("-" * 25)
    
    base_path = Path(__file__).parent
    critical_files = [
        ('main.py', 'Main application'),
        ('enhanced_system.py', 'Core system'),
        ('config/trading_config.py', 'Configuration'),
        ('core/risk_manager.py', 'Risk management'),
        ('core/time_filter.py', 'Time filtering'),
        ('core/ensemble_signals.py', 'Signal generation'),
        ('ml/feature_engineer.py', 'Feature engineering'),
        ('ml/enhanced_trainer.py', 'ML training'),
        ('auth/auth_manager.py', 'Authentication')
    ]
    
    all_files_present = True
    for file_path, description in critical_files:
        full_path = base_path / file_path
        if full_path.exists():
            size_kb = full_path.stat().st_size / 1024
            print(f"✅ {file_path} ({size_kb:.1f}KB) - {description}")
        else:
            print(f"❌ {file_path} - MISSING!")
            all_files_present = False
            
    print(f"\n🎯 Core Files Status: {'✅ ALL PRESENT' if all_files_present else '❌ MISSING FILES'}")
    
    # 2. Configuration Check
    print(f"\n⚙️  CONFIGURATION STATUS")
    print("-" * 25)
    
    try:
        sys.path.append(str(base_path))
        from config.trading_config import (
            ENHANCED_TARGET_PCT, ENHANCED_STOP_PCT, 
            DASHBOARD_CONFIG, ESSENTIAL_FEATURES, 
            OPTIMAL_TRADING_HOURS
        )
        
        risk_reward_ratio = ENHANCED_TARGET_PCT / ENHANCED_STOP_PCT
        breakeven_rate = ENHANCED_STOP_PCT / (ENHANCED_TARGET_PCT + ENHANCED_STOP_PCT)
        
        print(f"✅ Risk/Reward Ratio: {risk_reward_ratio:.1f}:1")
        print(f"✅ Breakeven Win Rate: {breakeven_rate:.1%}")
        print(f"✅ Dashboard Port: {DASHBOARD_CONFIG['port']}")
        print(f"✅ Essential Features: {len(ESSENTIAL_FEATURES)} features")
        print(f"✅ Trading Windows: {len(OPTIMAL_TRADING_HOURS)} optimal periods")
        config_ok = True
        
    except ImportError as e:
        print(f"❌ Configuration Error: {e}")
        config_ok = False
        
    # 3. Data Files Check
    print(f"\n💾 DATA FILES STATUS")
    print("-" * 25)
    
    data_files = [
        ('enhanced_model.pkl', 'ML Model'),
        ('enhanced_trade_log.csv', 'Trade Log'),
        ('enhanced_performance.csv', 'Performance Log'),
        ('enhanced_trader.log', 'System Log')
    ]
    
    data_files_present = 0
    for file_path, description in data_files:
        full_path = base_path / file_path
        if full_path.exists():
            size_kb = full_path.stat().st_size / 1024
            modified = datetime.fromtimestamp(full_path.stat().st_mtime)
            days_old = (datetime.now() - modified).days
            
            age_status = "📅 Recent" if days_old < 7 else f"⏰ {days_old} days old"
            print(f"✅ {file_path} ({size_kb:.1f}KB) - {age_status}")
            data_files_present += 1
        else:
            print(f"⚪ {file_path} - Will be created at runtime")
            
    print(f"\n📊 Data Files: {data_files_present}/{len(data_files)} present")
    
    # 4. Dependencies Check
    print(f"\n📦 DEPENDENCIES STATUS")
    print("-" * 25)
    
    required_packages = [
        ('pandas', 'Data manipulation'),
        ('numpy', 'Numerical computing'),
        ('scikit-learn', 'Machine learning'),
        ('joblib', 'Model persistence')
    ]
    
    missing_deps = []
    for package, description in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} - {description}")
        except ImportError:
            print(f"❌ {package} - MISSING! Install with: pip install {package}")
            missing_deps.append(package)
            
    # Optional dependencies
    optional_packages = [
        ('talib', 'Technical analysis (for advanced features)'),
        ('dash', 'Dashboard (for web interface)')
    ]
    
    print(f"\nOptional packages:")
    for package, description in optional_packages:
        try:
            __import__(package)
            print(f"✅ {package} - {description}")
        except ImportError:
            print(f"⚪ {package} - Optional: {description}")
    
    # 5. System Comparison
    print(f"\n📈 SYSTEM COMPARISON")
    print("-" * 25)
    
    comparison_data = {
        "Original System": {
            "Win Rate": "24%",
            "Risk/Reward": "1:2",
            "Breakeven": "67%",
            "Features": "30+",
            "Port": "8050"
        },
        "Enhanced System": {
            "Win Rate": "60-70% (target)",
            "Risk/Reward": f"{risk_reward_ratio:.1f}:1" if config_ok else "2:1",
            "Breakeven": f"{breakeven_rate:.0%}" if config_ok else "33%",
            "Features": f"{len(ESSENTIAL_FEATURES)}" if config_ok else "10",
            "Port": f"{DASHBOARD_CONFIG['port']}" if config_ok else "8051"
        }
    }
    
    print(f"{'Metric':<15} {'Original':<15} {'Enhanced':<20}")
    print("-" * 50)
    for metric in ["Win Rate", "Risk/Reward", "Breakeven", "Features", "Port"]:
        orig = comparison_data["Original System"][metric]
        enh = comparison_data["Enhanced System"][metric]
        print(f"{metric:<15} {orig:<15} {enh:<20}")
    
    # 6. Quick Start Guide
    print(f"\n🚀 QUICK START")
    print("-" * 15)
    print("To start the enhanced system:")
    print(f"  1. cd \"{base_path}\"")
    print("  2. python main.py")
    print(f"  3. Open http://localhost:{DASHBOARD_CONFIG['port'] if config_ok else '8051'}")
    print()
    print("To start via E*Trade menu:")
    print("  1. Run Etrade_menu.py")
    print("  2. Click '🚀 Enhanced Day Trading System' (Option 5)")
    
    # 7. System Health Score
    print(f"\n🏥 SYSTEM HEALTH SCORE")
    print("-" * 25)
    
    health_score = 0
    max_score = 4
    
    if all_files_present:
        health_score += 1
    if config_ok:
        health_score += 1
    if len(missing_deps) == 0:
        health_score += 1
    if data_files_present >= 2:  # At least some data files present or will be created
        health_score += 1
        
    health_percentage = (health_score / max_score) * 100
    
    if health_percentage >= 75:
        health_status = "🟢 EXCELLENT"
    elif health_percentage >= 50:
        health_status = "🟡 GOOD"
    else:
        health_status = "🔴 NEEDS ATTENTION"
        
    print(f"Health Score: {health_score}/{max_score} ({health_percentage:.0f}%)")
    print(f"Status: {health_status}")
    
    # 8. Next Steps
    print(f"\n📋 RECOMMENDED NEXT STEPS")
    print("-" * 30)
    
    if not all_files_present:
        print("❗ Fix missing critical files before proceeding")
    elif len(missing_deps) > 0:
        print(f"❗ Install missing dependencies: {', '.join(missing_deps)}")
    elif health_percentage == 100:
        print("✅ System ready for testing!")
        print("  1. Start in paper trading mode")
        print("  2. Monitor performance vs original system")
        print("  3. Gradually increase position sizes if performing well")
    else:
        print("⚪ Review any issues noted above")
        print("⚪ Run file_tracker.py for detailed analysis")
        
    print(f"\n{'=' * 50}")
    print(f"Enhanced Day Trading System Status Check Complete")
    print(f"For detailed maintenance info, see: MASTER_PLAN.md")
    print(f"For daily operations, see: QUICK_REFERENCE.md")
    print(f"{'=' * 50}")

def show_performance_summary():
    """Show performance summary if data exists"""
    
    base_path = Path(__file__).parent
    performance_file = base_path / 'enhanced_performance.csv'
    trade_log = base_path / 'enhanced_trade_log.csv'
    
    if not (performance_file.exists() or trade_log.exists()):
        print("\n📊 PERFORMANCE DATA")
        print("-" * 20)
        print("⚪ No performance data yet - system hasn't traded")
        print("📝 Data will be created when system starts trading")
        return
        
    print("\n📊 PERFORMANCE SUMMARY")
    print("-" * 25)
    print("📈 Performance tracking files found!")
    
    if performance_file.exists():
        size_kb = performance_file.stat().st_size / 1024
        modified = datetime.fromtimestamp(performance_file.stat().st_mtime)
        print(f"✅ Enhanced Performance Log: {size_kb:.1f}KB, updated {modified.strftime('%m/%d/%Y')}")
        
    if trade_log.exists():
        size_kb = trade_log.stat().st_size / 1024
        modified = datetime.fromtimestamp(trade_log.stat().st_mtime)
        print(f"✅ Enhanced Trade Log: {size_kb:.1f}KB, updated {modified.strftime('%m/%d/%Y')}")
        
    print("💡 Use dashboard or analyze CSV files for detailed performance metrics")

if __name__ == "__main__":
    check_system_status()
    show_performance_summary()
    
    print(f"\n💡 TIP: Run this script regularly to monitor system health!")
    print(f"Save as bookmark: python status_check.py")