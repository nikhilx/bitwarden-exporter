import os
import subprocess
import json
import logging

class BitwardenAuth:
    def __init__(self, config, bw_cmd):
        self.config = config
        self.bw_cmd = bw_cmd
        self.session = None

    def _get_session(self):
        session_path = self.config.get('session_path')
        if session_path and os.path.exists(session_path):
            with open(session_path, 'r') as f:
                return f.read().strip()
        return None

    def _save_session(self, session_key):
        session_path = self.config.get('session_path')
        if session_path:
            # Ensure directory exists
            os.makedirs(os.path.dirname(os.path.abspath(session_path)), exist_ok=True)
            
            with open(session_path, 'w') as f:
                f.write(session_key)

    def login(self):
        try:
            if self._check_existing_session():
                logging.debug("Existing session found, skipping login")
                return True

            # Perform new login
            subprocess.run([self.bw_cmd, 'logout'], capture_output=True)

            # Set API credentials and login
            os.environ['BW_CLIENTID'] = self.config['client_id']
            os.environ['BW_CLIENTSECRET'] = self.config['client_secret']
            
            # First login with API key
            login_result = subprocess.run(
                [self.bw_cmd, 'login', '--apikey'],
                capture_output=True,
                text=True
            )

            if login_result.returncode != 0:
                logging.error(f"API login failed: {login_result.stderr}")
                return False

            # Then unlock to get session key
            unlock_result = subprocess.run(
                [self.bw_cmd, 'unlock', '--raw'],
                input=f"{self.config.get('master_password', '')}\n",
                capture_output=True,
                text=True
            )

            logging.debug(f"Unlock result: {unlock_result.stdout}")
            if unlock_result.returncode != 0:
                logging.error(f"Unlock failed: {unlock_result.stderr}")
                return False

            # Save and set session
            self.session = unlock_result.stdout.strip()
            os.environ['BW_SESSION'] = self.session
            self._save_session(self.session)
            logging.debug(f"Session saved to: {self.config.get('session_path')}")
            
            # Verify unlock worked
            verify = subprocess.run([self.bw_cmd, 'sync'], capture_output=True, text=True)
            logging.debug(f"Sync result: {verify.stdout}")
            return verify.returncode == 0

        except Exception as e:
            logging.error(f"Login failed: {str(e)}")
            return False

    def _check_existing_session(self):
        self.session = self._get_session()
        if not self.session:
            logging.debug("No existing session found, logging in...")
            return False
            
        os.environ['BW_SESSION'] = self.session
        
        try:
            status = subprocess.run(
                [self.bw_cmd, 'status'], 
                capture_output=True, 
                text=True
            )
            status_data = json.loads(status.stdout)
            return status_data['status'] == 'unlocked'
        except Exception as e:
            logging.error(f"Session check failed: {str(e)}")
            return False
