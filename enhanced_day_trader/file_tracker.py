#!/usr/bin/env python3
"""
Enhanced Day Trading System - File Tracker & Maintenance Helper
===============================================================

This script helps track all files in the enhanced system and provides
maintenance utilities for updates, backups, and system health checks.

Author: GitHub Copilot
Date: September 26, 2025
"""

import os
import json
import hashlib
from datetime import datetime
from pathlib import Path

class SystemFileTracker:
    """Track and maintain all files in the enhanced trading system"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.file_registry = {}
        self.load_file_registry()
        
    def get_file_hash(self, filepath):
        """Calculate MD5 hash of file for change detection"""
        try:
            with open(filepath, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except:
            return None
            
    def scan_system_files(self):
        """Scan all system files and record their status"""
        
        system_files = {
            # Core application files
            'main.py': {
                'purpose': 'Main application entry point',
                'critical': True,
                'backup_needed': True
            },
            'enhanced_system.py': {
                'purpose': 'Core system integration',
                'critical': True,
                'backup_needed': True
            },
            
            # Configuration files
            'config/trading_config.py': {
                'purpose': 'Central configuration',
                'critical': True,
                'backup_needed': True
            },
            
            # Core components
            'core/risk_manager.py': {
                'purpose': 'Enhanced risk management',
                'critical': True,
                'backup_needed': True
            },
            'core/time_filter.py': {
                'purpose': 'Time-based filtering',
                'critical': True,
                'backup_needed': True
            },
            'core/ensemble_signals.py': {
                'purpose': 'Multi-confirmation signals',
                'critical': True,
                'backup_needed': True
            },
            
            # Machine learning
            'ml/feature_engineer.py': {
                'purpose': 'Feature engineering',
                'critical': True,
                'backup_needed': True
            },
            'ml/enhanced_trainer.py': {
                'purpose': 'ML model training',
                'critical': True,
                'backup_needed': True
            },
            
            # Authentication
            'auth/auth_manager.py': {
                'purpose': 'Authentication wrapper',
                'critical': True,
                'backup_needed': True
            },
            
            # Documentation
            'README.md': {
                'purpose': 'System documentation',
                'critical': False,
                'backup_needed': True
            },
            'MASTER_PLAN.md': {
                'purpose': 'Master plan and maintenance guide',
                'critical': False,
                'backup_needed': True
            },
            'QUICK_REFERENCE.md': {
                'purpose': 'Daily operations guide',
                'critical': False,
                'backup_needed': True
            },
            'IMPLEMENTATION_COMPLETE.md': {
                'purpose': 'Implementation summary',
                'critical': False,
                'backup_needed': True
            },
            
            # Analysis and comparison
            'system_comparison.py': {
                'purpose': 'Performance comparison analysis',
                'critical': False,
                'backup_needed': True
            },
            
            # Data files (created at runtime)
            'enhanced_model.pkl': {
                'purpose': 'Trained ML model',
                'critical': True,
                'backup_needed': True,
                'runtime_created': True
            },
            'enhanced_trade_log.csv': {
                'purpose': 'Trade execution log',
                'critical': False,
                'backup_needed': True,
                'runtime_created': True
            },
            'enhanced_performance.csv': {
                'purpose': 'Performance metrics',
                'critical': False,
                'backup_needed': True,
                'runtime_created': True
            }
        }
        
        # Scan files and record status
        current_scan = {
            'scan_date': datetime.now().isoformat(),
            'files': {}
        }
        
        for rel_path, info in system_files.items():
            filepath = self.base_path / rel_path
            
            file_info = info.copy()
            file_info.update({
                'exists': filepath.exists(),
                'size': filepath.stat().st_size if filepath.exists() else 0,
                'modified': datetime.fromtimestamp(filepath.stat().st_mtime).isoformat() if filepath.exists() else None,
                'hash': self.get_file_hash(filepath) if filepath.exists() else None,
                'full_path': str(filepath)
            })
            
            current_scan['files'][rel_path] = file_info
            
        return current_scan
        
    def load_file_registry(self):
        """Load existing file registry"""
        registry_path = self.base_path / 'file_registry.json'
        if registry_path.exists():
            try:
                with open(registry_path, 'r') as f:
                    self.file_registry = json.load(f)
            except:
                self.file_registry = {}
                
    def save_file_registry(self, scan_data):
        """Save file registry with scan data"""
        registry_path = self.base_path / 'file_registry.json'
        
        # Add scan to history
        if 'scan_history' not in self.file_registry:
            self.file_registry['scan_history'] = []
            
        self.file_registry['scan_history'].append(scan_data)
        self.file_registry['last_scan'] = scan_data['scan_date']
        
        # Keep only last 10 scans
        self.file_registry['scan_history'] = self.file_registry['scan_history'][-10:]
        
        with open(registry_path, 'w') as f:
            json.dump(self.file_registry, f, indent=2)
            
    def detect_changes(self):
        """Detect changes since last scan"""
        if not self.file_registry.get('scan_history'):
            return {'message': 'No previous scan found'}
            
        current_scan = self.scan_system_files()
        last_scan = self.file_registry['scan_history'][-1]
        
        changes = {
            'scan_date': current_scan['scan_date'],
            'changes': []
        }
        
        for filepath, current_info in current_scan['files'].items():
            if filepath in last_scan['files']:
                last_info = last_scan['files'][filepath]
                
                # Check for changes
                if current_info['hash'] != last_info['hash']:
                    changes['changes'].append({
                        'file': filepath,
                        'type': 'modified',
                        'last_modified': current_info['modified'],
                        'previous_hash': last_info['hash'],
                        'current_hash': current_info['hash']
                    })
            else:
                # New file
                changes['changes'].append({
                    'file': filepath,
                    'type': 'new',
                    'created': current_info['modified']
                })
                
        # Check for deleted files
        for filepath in last_scan['files']:
            if filepath not in current_scan['files']:
                changes['changes'].append({
                    'file': filepath,
                    'type': 'deleted'
                })
                
        return changes
        
    def generate_system_health_report(self):
        """Generate comprehensive system health report"""
        scan_data = self.scan_system_files()
        
        report = {
            'report_date': datetime.now().isoformat(),
            'system_status': 'healthy',
            'issues': [],
            'recommendations': []
        }
        
        # Check critical files
        critical_files = [f for f, info in scan_data['files'].items() if info.get('critical', False)]
        missing_critical = [f for f in critical_files if not scan_data['files'][f]['exists']]
        
        if missing_critical:
            report['system_status'] = 'critical'
            report['issues'].extend([f"Missing critical file: {f}" for f in missing_critical])
            
        # Check for large files that might need cleanup
        large_files = [(f, info['size']) for f, info in scan_data['files'].items() 
                      if info['exists'] and info['size'] > 50 * 1024 * 1024]  # >50MB
        
        if large_files:
            report['recommendations'].extend([f"Large file detected: {f} ({size/1024/1024:.1f}MB)" 
                                            for f, size in large_files])
            
        # Check for old files that might need updates
        old_files = []
        for f, info in scan_data['files'].items():
            if info['exists'] and info['modified']:
                modified_date = datetime.fromisoformat(info['modified'])
                days_old = (datetime.now() - modified_date).days
                if days_old > 30:  # Older than 30 days
                    old_files.append((f, days_old))
                    
        if old_files:
            report['recommendations'].extend([f"Old file (may need update): {f} ({days} days old)" 
                                            for f, days in old_files])
            
        return report
        
    def backup_critical_files(self):
        """Create backup of critical files"""
        scan_data = self.scan_system_files()
        backup_dir = self.base_path / 'backups' / datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        backed_up = []
        
        for filepath, info in scan_data['files'].items():
            if info.get('backup_needed', False) and info['exists']:
                source = Path(info['full_path'])
                dest = backup_dir / filepath.replace('/', '_').replace('\\', '_')
                
                try:
                    import shutil
                    shutil.copy2(source, dest)
                    backed_up.append(filepath)
                except Exception as e:
                    print(f"Failed to backup {filepath}: {e}")
                    
        return {
            'backup_date': datetime.now().isoformat(),
            'backup_dir': str(backup_dir),
            'files_backed_up': backed_up
        }

def main():
    """Main function for file tracking and maintenance"""
    
    tracker = SystemFileTracker()
    
    print("Enhanced Day Trading System - File Tracker")
    print("=" * 50)
    
    # Perform system scan
    print("Scanning system files...")
    scan_data = tracker.scan_system_files()
    
    # Show file status
    print(f"\nFile Status (as of {scan_data['scan_date']}):")
    print("-" * 40)
    
    critical_files = 0
    missing_files = 0
    
    for filepath, info in scan_data['files'].items():
        status = "✅" if info['exists'] else "❌"
        critical = " (CRITICAL)" if info.get('critical', False) else ""
        size = f" ({info['size']} bytes)" if info['exists'] else ""
        
        print(f"{status} {filepath}{critical}{size}")
        
        if info.get('critical', False):
            critical_files += 1
        if not info['exists']:
            missing_files += 1
            
    print(f"\nSummary:")
    print(f"Total files tracked: {len(scan_data['files'])}")
    print(f"Critical files: {critical_files}")
    print(f"Missing files: {missing_files}")
    
    # Save scan data
    tracker.save_file_registry(scan_data)
    
    # Check for changes
    print(f"\nChecking for changes...")
    changes = tracker.detect_changes()
    
    if changes.get('changes'):
        print(f"Found {len(changes['changes'])} changes:")
        for change in changes['changes']:
            print(f"  {change['type'].upper()}: {change['file']}")
    else:
        print("No changes detected since last scan.")
        
    # Generate health report
    print(f"\nSystem Health Check:")
    print("-" * 20)
    health_report = tracker.generate_system_health_report()
    print(f"Status: {health_report['system_status'].upper()}")
    
    if health_report['issues']:
        print("Issues:")
        for issue in health_report['issues']:
            print(f"  ⚠️  {issue}")
            
    if health_report['recommendations']:
        print("Recommendations:")
        for rec in health_report['recommendations']:
            print(f"  💡 {rec}")
            
    if not health_report['issues'] and not health_report['recommendations']:
        print("✅ All systems operational!")
        
    print(f"\nFile registry saved to: file_registry.json")
    print(f"Run this script regularly to track system changes.")

if __name__ == "__main__":
    main()