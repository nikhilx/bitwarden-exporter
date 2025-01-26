import os
import logging
import configparser
import getpass

class Config:
    def __init__(self, config_path='config.ini'):
        logging.debug(f"Loading config from: {config_path}")

        self.config = configparser.ConfigParser()
        if os.path.exists(config_path):
            self.config.read(config_path)
            logging.debug("Config loaded successfully")
        else:
            logging.warning(f"Config file not found: {config_path}. Prompting for credentials.")
            self.config['bitwarden'] = {}

        self._ensure_credentials()

    def _ensure_credentials(self):
        if 'client_id' not in self.config['bitwarden']:
            self.config['bitwarden']['client_id'] = input("Enter Bitwarden client ID: ")
        if 'client_secret' not in self.config['bitwarden']:
            self.config['bitwarden']['client_secret'] = getpass.getpass("Enter Bitwarden client secret: ")
        if 'master_password' not in self.config['bitwarden']:
            self.config['bitwarden']['master_password'] = getpass.getpass("Enter Bitwarden master password: ")

    def get(self, key, default=None):
        return self.config['bitwarden'].get(key, default)

    def __getitem__(self, key):
        return self.config['bitwarden'][key]
