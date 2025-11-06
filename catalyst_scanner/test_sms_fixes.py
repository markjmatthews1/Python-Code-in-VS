"""
Test SMS Credentials Persistence and Enabling
Quick test to verify SMS settings are saved and enabled correctly
"""

import sys
import os

# Add the project directory to the path
project_dir = r'c:\Users\mjmat\Python Code in VS\catalyst_scanner'
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

from alerts.alert_system import AlertSystem
from alerts.sms_service import SMSService

def test_sms_fixes():
    """Test that SMS credentials persist and service gets enabled"""
    print("Testing SMS Credential Persistence and Service Enabling")
    print("=" * 60)
    
    # Test 1: Create alert system and check initial state
    print("\n1. Creating alert system...")
    alert_system = AlertSystem()
    
    # Test 2: Check initial SMS status
    print("\n2. Initial SMS service status:")
    status = alert_system.get_sms_service_status()
    print(f"   Provider: {status.get('current_provider')}")
    print(f"   Enabled: {status.get('enabled')}")
    print(f"   SMS Alerts: {status.get('sms_alerts_enabled')}")
    
    # Test 3: Simulate setting Twilio credentials
    print("\n3. Setting test Twilio credentials...")
    alert_system.update_setting('sms_provider', 'twilio')
    alert_system.update_setting('twilio_account_sid', 'ACtest123456789')
    alert_system.update_setting('twilio_auth_token', 'test_auth_token_123')
    alert_system.update_setting('twilio_phone_number', '+1234567890')
    alert_system.update_setting('sms_phone_number', '+19895469683')
    
    # Test 4: Update SMS credentials
    print("\n4. Updating SMS service with credentials...")
    result = alert_system.update_sms_credentials()
    print(f"   Credential update result: {result}")
    
    # Test 5: Check SMS status after credential update
    print("\n5. SMS service status after credential update:")
    status = alert_system.get_sms_service_status()
    print(f"   Provider: {status.get('current_provider')}")
    print(f"   Enabled: {status.get('enabled')}")
    print(f"   SMS Alerts: {status.get('sms_alerts_enabled')}")
    
    # Test 6: Test SMS service directly
    print("\n6. Testing SMS service directly...")
    sms_service = SMSService()
    sms_status = sms_service.get_provider_status()
    print(f"   SMS Service Provider: {sms_status.get('current_provider')}")
    print(f"   SMS Service Enabled: {sms_status.get('enabled', False)}")
    
    # Test 7: Test connection
    print("\n7. Testing SMS connection...")
    connection_test = alert_system.test_sms_service()
    print(f"   Connection test: {connection_test}")
    
    # Test 8: Try sending test SMS
    print("\n8. Attempting to send test SMS...")
    test_result = alert_system.send_test_sms()
    print(f"   Test SMS result: {test_result}")
    
    print("\n" + "=" * 60)
    if test_result.get('success'):
        print("✅ SUCCESS: SMS service is working correctly!")
        print("   - Credentials are being saved")
        print("   - Service is getting enabled") 
        print("   - Test SMS functionality works")
    else:
        print("❌ ISSUE: SMS service still has problems")
        print(f"   Error: {test_result.get('error', 'Unknown error')}")
        print("   Check the steps above for issues")

if __name__ == "__main__":
    test_sms_fixes()