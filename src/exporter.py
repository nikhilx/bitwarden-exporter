import os
import subprocess
import logging
import getpass
from datetime import datetime
from .authentication import BitwardenAuth
from .utils import verify_cli

class BitwardenExporter:
    def __init__(self, config):
        self.config = config
        self.bw_cmd = verify_cli()
        self.auth = BitwardenAuth(config, self.bw_cmd)

    def export_vault(self, format_type='json', output_dir='exports'):
        if not self.auth.login():
            logging.error("Export failed: Authentication error")
            return False

        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = os.path.join(output_dir, f'bw_export_{timestamp}.{format_type}')

        try:
            cmd = [self.bw_cmd, 'export', '--format', format_type, '--output', output_file]
            if format_type == 'encrypted_json':
                encrypt_password = self.config.get('encrypted_json_password')
                if not encrypt_password:
                    encrypt_password = getpass.getpass("Enter encryption password:")
                cmd.extend(['--password', encrypt_password])

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
