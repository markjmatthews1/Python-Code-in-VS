# Authentication Manager for Catalyst Scanner
#
# Manages authentication for Schwab and E*TRADE APIs with token refresh
# and error handling for real-time data collection.
#
# Author: Investment Catalyst Team
# Date: September 29, 2025

import json
import os
import sys
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime, timedelta
import requests

from utils.logger import get_logger
from utils.error_handler import handle_error, APIError


class AuthenticationManager:
    """
    Unified authentication manager for all API services used by Catalyst Scanner
    """
    
    def __init__(self, auth_file_path: str = None):
        """
        Initialize authentication manager
        
        Args:
            auth_file_path: Path to auth_data.json file
        """
        self.logger = get_logger()
        self.auth_file_path = auth_file_path or self._find_auth_file()
        self.auth_data = {}
        self.tokens = {}
        
        # Load authentication data
        self._load_auth_data()
        
        # Import parent auth modules if available
        self._import_parent_auth_modules()
        
        self.logger.info("Authentication Manager initialized")
    
    def _find_auth_file(self) -> str:
        """Find auth_data.json file in various locations"""
        possible_paths = [
            "auth_data.json",
            "../auth_data.json",
            "../../auth_data.json",
            "config/auth_data.json",
            "C:/Users/mjmat/Python Code in VS/auth_data.json"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                self.logger.info(f"Found auth file: {path}")
                return path
        
        self.logger.warning("No auth_data.json file found")
        return "auth_data.json"
    
    def _load_auth_data(self):
        """Load authentication data from file"""
        try:
            if os.path.exists(self.auth_file_path):
                with open(self.auth_file_path, 'r') as f:
                    self.auth_data = json.load(f)
                
                # Extract tokens
                self.tokens = {
                    'schwab': self.auth_data.get('schwab', {}),
                    'etrade': self.auth_data.get('etrade', {}),
                    'yahoo_finance': self.auth_data.get('yahoo_finance', {})
                }
                
                self.logger.info("Authentication data loaded successfully")
            else:
                self.logger.warning(f"Auth file not found: {self.auth_file_path}")
                
        except Exception as e:
            self.logger.error(f"Failed to load auth data: {e}")
    
    def _import_parent_auth_modules(self):
        """Import authentication modules from parent directory"""
        try:
            # Add parent directory to path
            parent_dir = Path(__file__).parent.parent.parent.absolute()
            if str(parent_dir) not in sys.path:
                sys.path.insert(0, str(parent_dir))
            
            # Change working directory temporarily to parent for token file access
            original_cwd = os.getcwd()
            os.chdir(str(parent_dir))
            
            try:
                # Try to import existing auth modules
                try:
                    import Schwab_auth
                    self.schwab_auth = Schwab_auth
                    self.logger.info("Imported Schwab_auth module")
                except ImportError:
                    self.schwab_auth = None
                    self.logger.warning("Schwab_auth module not available")
                
                try:
                    import etrade_auth
                    self.etrade_auth = etrade_auth
                    self.logger.info("Imported etrade_auth module")
                except ImportError:
                    self.etrade_auth = None
                    self.logger.warning("etrade_auth module not available")
            finally:
                # Restore original working directory
                os.chdir(original_cwd)
                
        except Exception as e:
            self.logger.warning(f"Failed to import parent auth modules: {e}")
    
    def get_schwab_headers(self) -> Dict[str, str]:
        """Get authentication headers for Schwab API"""
        try:
            # First try to use the existing Schwab_auth module with proper working directory
            if self.schwab_auth and hasattr(self.schwab_auth, 'get_valid_access_token'):
                try:
                    # Change to parent directory temporarily for token file access
                    parent_dir = Path(__file__).parent.parent.parent.absolute()
                    original_cwd = os.getcwd()
                    os.chdir(str(parent_dir))
                    
                    try:
                        access_token = self.schwab_auth.get_valid_access_token()
                        self.logger.debug("Successfully obtained Schwab token from parent module")
                        return {
                            'Authorization': f'Bearer {access_token}',
                            'Content-Type': 'application/json',
                            'Accept': 'application/json'
                        }
                    finally:
                        # Always restore original working directory
                        os.chdir(original_cwd)
                        
                except Exception as e:
                    self.logger.warning(f"Failed to get Schwab token from parent module: {e}")
            
            # Fallback to auth_data.json tokens
            schwab_tokens = self.tokens.get('schwab', {})
            access_token = schwab_tokens.get('access_token')
            
            if access_token:
                return {
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json', 
                    'Accept': 'application/json'
                }
            else:
                self.logger.error("No Schwab access token available from any source")
                return {}
                
        except Exception as e:
            self.logger.error(f"Error getting Schwab headers: {e}")
            return {}
    
    def get_etrade_session(self):
        """Get E*TRADE session object"""
        if self.etrade_auth and hasattr(self.etrade_auth, 'get_etrade_session'):
            try:
                return self.etrade_auth.get_etrade_session()
            except Exception as e:
                self.logger.warning(f"Failed to get E*TRADE session: {e}")
        
        return None
    
    def get_headers(self, service: str = 'schwab') -> Dict[str, str]:
        """
        Get authentication headers for specified service
        
        Args:
            service: Service name ('schwab', 'etrade', 'yahoo')
            
        Returns:
            Dict: Authentication headers
        """
        if service.lower() == 'schwab':
            return self.get_schwab_headers()
        elif service.lower() == 'etrade':
            # E*TRADE uses session-based auth, return empty headers
            return {}
        elif service.lower() == 'yahoo':
            # Yahoo Finance doesn't require auth for basic endpoints
            return {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json'
            }
        else:
            return {}
    
    def refresh_schwab_token(self) -> bool:
        """
        Refresh Schwab access token
        
        Returns:
            bool: True if refresh successful
        """
        try:
            schwab_tokens = self.tokens.get('schwab', {})
            refresh_token = schwab_tokens.get('refresh_token')
            
            if not refresh_token:
                self.logger.error("No Schwab refresh token available")
                return False
            
            # Use parent module for token refresh if available
            if self.schwab_auth and hasattr(self.schwab_auth, 'refresh_token'):
                try:
                    new_tokens = self.schwab_auth.refresh_token(refresh_token)
                    
                    # Update stored tokens
                    self.tokens['schwab'].update(new_tokens)
                    self.auth_data['schwab'].update(new_tokens)
                    
                    # Save to file
                    with open(self.auth_file_path, 'w') as f:
                        json.dump(self.auth_data, f, indent=2)
                    
                    self.logger.info("Schwab token refreshed successfully")
                    return True
                    
                except Exception as e:
                    self.logger.error(f"Token refresh failed: {e}")
                    return False
            
            # Fallback: Manual token refresh
            return self._manual_schwab_token_refresh(refresh_token)
            
        except Exception as e:
            self.logger.error(f"Schwab token refresh error: {e}")
            return False
    
    def _manual_schwab_token_refresh(self, refresh_token: str) -> bool:
        """Manual Schwab token refresh implementation"""
        try:
            schwab_config = self.auth_data.get('schwab', {})
            client_id = schwab_config.get('client_id')
            client_secret = schwab_config.get('client_secret')
            
            if not all([client_id, client_secret]):
                self.logger.error("Missing Schwab client credentials")
                return False
            
            # Token refresh endpoint
            token_url = "https://api.schwabapi.com/v1/oauth/token"
            
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            data = {
                'grant_type': 'refresh_token',
                'refresh_token': refresh_token,
                'client_id': client_id,
                'client_secret': client_secret
            }
            
            response = requests.post(token_url, headers=headers, data=data, timeout=30)
            
            if response.status_code == 200:
                token_data = response.json()
                
                # Update tokens
                self.tokens['schwab']['access_token'] = token_data.get('access_token')
                if 'refresh_token' in token_data:
                    self.tokens['schwab']['refresh_token'] = token_data.get('refresh_token')
                
                # Update auth data and save
                self.auth_data['schwab'].update(self.tokens['schwab'])
                with open(self.auth_file_path, 'w') as f:
                    json.dump(self.auth_data, f, indent=2)
                
                self.logger.info("Manual Schwab token refresh successful")
                return True
            else:
                self.logger.error(f"Token refresh failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"Manual token refresh error: {e}")
            return False
    
    def validate_schwab_token(self) -> bool:
        """
        Validate current Schwab access token
        
        Returns:
            bool: True if token is valid
        """
        try:
            # Use the parent module's validation if available
            if self.schwab_auth and hasattr(self.schwab_auth, 'get_valid_access_token'):
                try:
                    access_token = self.schwab_auth.get_valid_access_token()
                    if access_token:
                        self.logger.debug("Schwab token validated via parent module")
                        return True
                except Exception as e:
                    self.logger.warning(f"Schwab token validation failed: {e}")
            
            # Fallback to manual validation
            headers = self.get_schwab_headers()
            if not headers:
                return False
            
            # Test token with a simple API call
            test_url = "https://api.schwabapi.com/v1/accounts"
            response = requests.get(test_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                return True
            elif response.status_code == 401:
                self.logger.info("Schwab token expired, attempting refresh")
                return self.refresh_schwab_token()
            else:
                return False
                
        except Exception as e:
            self.logger.warning(f"Token validation failed: {e}")
            return False
    
    def get_auth_status(self) -> Dict[str, bool]:
        """
        Get authentication status for all services
        
        Returns:
            Dict: Authentication status for each service
        """
        status = {}
        
        # Check Schwab - use parent module if available
        if self.schwab_auth and hasattr(self.schwab_auth, 'get_valid_access_token'):
            try:
                # Change to parent directory temporarily for token file access
                parent_dir = Path(__file__).parent.parent.parent.absolute()
                original_cwd = os.getcwd()
                os.chdir(str(parent_dir))
                
                try:
                    access_token = self.schwab_auth.get_valid_access_token()
                    status['schwab'] = bool(access_token)
                    self.logger.debug("Schwab auth status checked via parent module")
                finally:
                    os.chdir(original_cwd)
                    
            except Exception as e:
                self.logger.debug(f"Schwab auth check failed: {e}")
                status['schwab'] = False
        else:
            # Fallback to checking auth_data.json
            status['schwab'] = bool(self.tokens.get('schwab', {}).get('access_token'))
        
        # Check E*TRADE
        etrade_session = self.get_etrade_session()
        status['etrade'] = etrade_session is not None
        
        # Yahoo Finance doesn't require auth
        status['yahoo_finance'] = True
        
        return status
    
    def is_authenticated(self, service: str = None) -> bool:
        """
        Check if authenticated for specific service or any service
        
        Args:
            service: Service to check, or None for any service
            
        Returns:
            bool: True if authenticated
        """
        auth_status = self.get_auth_status()
        
        if service:
            return auth_status.get(service.lower(), False)
        else:
            # Return True if any service is authenticated
            return any(auth_status.values())


# Singleton instance for global access
_auth_manager = None


def get_auth_manager(auth_file_path: str = None) -> AuthenticationManager:
    """
    Get singleton authentication manager instance
    
    Args:
        auth_file_path: Optional path to auth file
        
    Returns:
        AuthenticationManager: Singleton instance
    """
    global _auth_manager
    
    if _auth_manager is None:
        _auth_manager = AuthenticationManager(auth_file_path)
    
    return _auth_manager


# Convenience functions
def get_schwab_headers() -> Dict[str, str]:
    """Get Schwab API headers"""
    return get_auth_manager().get_schwab_headers()


def get_etrade_session():
    """Get E*TRADE session"""
    return get_auth_manager().get_etrade_session()


def validate_auth() -> Dict[str, bool]:
    """Validate authentication for all services"""
    return get_auth_manager().get_auth_status()


if __name__ == "__main__":
    # Test authentication manager
    print("Testing Authentication Manager...")
    
    auth_mgr = get_auth_manager()
    status = auth_mgr.get_auth_status()
    
    print("Authentication Status:")
    for service, authenticated in status.items():
        print(f"  {service}: {'✅' if authenticated else '❌'}")
    
    # Test Schwab headers
    headers = auth_mgr.get_schwab_headers()
    print(f"Schwab headers available: {'✅' if headers else '❌'}")