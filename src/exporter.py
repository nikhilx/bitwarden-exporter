import os
import subprocess
import logging
import getpass
from datetime import datetime
from enum import Enum
from .authentication import BitwardenAuth
from .utils import verify_cli

class ExportFormat(Enum):
    JSON = 'json'
    CSV = 'csv'
    PASSWORD_ENCRYPTED_JSON = 'account_encrypted_json'
    ACCOUNT_ENCRYPTED_JSON = 'password_encrypted_json'

FORMAT_EXTENSION_MAP = {
    ExportFormat.JSON: 'json',
    ExportFormat.CSV: 'csv',
    ExportFormat.PASSWORD_ENCRYPTED_JSON: 'json',
    ExportFormat.ACCOUNT_ENCRYPTED_JSON: 'json'
}

BITWARDEN_FORMAT_MAP = {
    ExportFormat.JSON: 'json',
    ExportFormat.CSV: 'csv',
    ExportFormat.PASSWORD_ENCRYPTED_JSON: 'encrypted_json',
    ExportFormat.ACCOUNT_ENCRYPTED_JSON: 'encrypted_json'
}

class BitwardenExporter:
    def __init__(self, config):
        self.config = config
        self.bw_cmd = verify_cli()
        self.auth = BitwardenAuth(config, self.bw_cmd)

    def export_vault(self, format_type=ExportFormat.JSON, output_dir='exports'):
        if not self.auth.login():
            logging.error("Export failed: Authentication error")
            return False

        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        file_extension = FORMAT_EXTENSION_MAP[format_type]
        encrypt_password = self.config.get('encrypted_json_password')

        if format_type == ExportFormat.PASSWORD_ENCRYPTED_JSON:
            suffix = '_password_encrypted'
            if not encrypt_password:
                encrypt_password = getpass.getpass("Enter encryption password:")
        elif format_type == ExportFormat.ACCOUNT_ENCRYPTED_JSON:
            suffix = '_account_encrypted'
        else:
            suffix = ''

        output_file = os.path.join(output_dir, f'Bitwarden_Export_{timestamp}{suffix}.{file_extension}')

        try:
            cmd = [self.bw_cmd, 'export', '--format', BITWARDEN_FORMAT_MAP[format_type], '--output', output_file]
            if format_type == ExportFormat.PASSWORD_ENCRYPTED_JSON and encrypt_password:
                logging.debug("Using custom password for encryption.")
                cmd.extend(['--password', encrypt_password])
            elif format_type == ExportFormat.ACCOUNT_ENCRYPTED_JSON:
                logging.debug("Using account key for encryption.")

            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            master_password = self.config.get('master_password')
            if not master_password:
                master_password = getpass.getpass("Enter master password: ")
            
            stdout, stderr = process.communicate(input=f"{master_password}\n")
            
            if process.returncode == 0:
                logging.info(f"Export successful: {output_file}")
                return True
            else:
                logging.error(f"Export failed: {stderr}")
                return False

        except Exception as e:
            logging.error(f"Export error: {str(e)}")
            return False
