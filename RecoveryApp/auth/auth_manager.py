"""
Authentication wrapper for RecoveryApp
Uses existing auth renewal apps from parent directory
Enhanced with 401 error handling and automatic token refresh
"""
import sys
import os
import requests

# Add parent directory to path for accessing existing auth modules
# Go up two levels: RecoveryApp/auth -> RecoveryApp -> Parent
current_file = os.path.abspath(__file__)
auth_dir = os.path.dirname(current_file)  # RecoveryApp/auth
recovery_app_dir = os.path.dirname(auth_dir)  # RecoveryApp
parent_dir = os.path.dirname(recovery_app_dir)  # Parent directory with etrade_auth.py
sys.path.insert(0, parent_dir)

def get_etrade_session():
    """Get E*Trade session using existing auth"""
    try:
        from etrade_auth import get_etrade_session as parent_get_session
        return parent_get_session()
    except ImportError as e:
        print(f"Error importing E*Trade auth: {e}")
        return None, None

def make_etrade_request(url, params=None, method='GET', retry_on_401=True):
    """
    Make E*Trade API request with automatic 401 error handling and token refresh
    
    Args:
        url: API endpoint URL
        params: Request parameters
        method: HTTP method (GET, POST, etc.)
        retry_on_401: Whether to retry with new session on 401 error
        
    Returns:
        requests.Response object or None if failed
    """
    try:
        # Import the etrade session functions
        from etrade_auth import get_etrade_session, clear_session_cache
        
        # Get current session
        session, base_url = get_etrade_session()
        if not session or not base_url:
            print("❌ Could not get E*Trade session")
            return None
        
        # Make the API request
        print(f"🔄 Making E*Trade API request to: {url}")
        if method.upper() == 'GET':
            response = session.get(url, params=params, timeout=10)
        elif method.upper() == 'POST':
            response = session.post(url, json=params, timeout=10)
        else:
            response = session.request(method, url, params=params, timeout=10)
        
        print(f"📡 E*Trade API response: {response.status_code}")
        
        # Handle 401 Unauthorized - token expired
        if response.status_code == 401 and retry_on_401:
            print("🔑 401 Unauthorized detected - refreshing E*Trade session...")
            
            # Clear cached session and get new one
            clear_session_cache()
            session, base_url = get_etrade_session(force_new=True)
            
            if not session or not base_url:
                print("❌ Failed to refresh E*Trade session")
                return None
            
            print("✅ E*Trade session refreshed, retrying request...")
            
            # Retry the request with new session
            if method.upper() == 'GET':
                response = session.get(url, params=params, timeout=10)
            elif method.upper() == 'POST':
                response = session.post(url, json=params, timeout=10)
            else:
                response = session.request(method, url, params=params, timeout=10)
            
            print(f"📡 E*Trade API retry response: {response.status_code}")
            
            # If still 401 after refresh, there's a deeper issue
            if response.status_code == 401:
                print("❌ Still getting 401 after token refresh - authentication issue")
                return None
        
        return response
        
    except Exception as e:
        print(f"❌ E*Trade API request error: {e}")
        return None

def get_fmp_key():
    """Get Financial Modeling Prep API key"""
    try:
        # Try to import from existing config files
        from config import FMP_API_KEY
        return FMP_API_KEY
    except ImportError:
        try:
            import json
            with open(os.path.join(parent_dir, 'config.json'), 'r') as f:
                config = json.load(f)
            return config.get('FMP_API_KEY')
        except FileNotFoundError:
            print("Config file not found")
            return None

def get_schwab_tokens():
    """Get Schwab API tokens"""
    try:
        # Look for existing Schwab auth in parent directory
        import json
        with open(os.path.join(parent_dir, 'auth_data.json'), 'r') as f:
            auth_data = json.load(f)
        return auth_data.get('schwab', {})
    except FileNotFoundError:
        print("Schwab auth data not found")
        return {}