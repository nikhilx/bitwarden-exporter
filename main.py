import logging
import argparse
import os
import subprocess
from src.config import Config
from src.exporter import BitwardenExporter
from src.utils import check_cli_version

# Enhanced logging configuration
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - [%(funcName)s] %(message)s',
    handlers=[
        logging.FileHandler("bitwarden_exporter.log"),
        logging.StreamHandler()
    ]
)

def main():
    logging.info("Starting Bitwarden Vault Exporter")
    parser = argparse.ArgumentParser(description='Bitwarden Vault Exporter')
    parser.add_argument('--config', default='config.ini', help='Path to config file')
    parser.add_argument('--format', choices=['json', 'csv', 'encrypted_json'], 
                       help='Export format')
    parser.add_argument('--all', action='store_true',
                       help='Export in all formats (json, csv, encrypted_json)')
    parser.add_argument('--output-dir', default='exports', help='Output directory')
    parser.add_argument('--check-updates', action='store_true',
                       help='Check for CLI updates')
    args = parser.parse_args()

    logging.debug(f"Parsed arguments: {args}")

    if not args.format and not args.all:
        logging.error("No export format specified")
        parser.error("Either --format or --all must be specified")

    try:
        config = Config(args.config)
        exporter = BitwardenExporter(config)
        
        if args.check_updates:
            logging.info("Checking for updates")
            check_cli_version()
            
        if args.all:
            logging.info("Starting export in all formats")
            for format_type in ['json', 'csv', 'encrypted_json']:
                logging.info(f"Processing format: {format_type}")
                if not exporter.export_vault(format_type, args.output_dir):
                    logging.error(f"Failed to export {format_type}, stopping further exports")
                    return 1
        else:
            logging.info(f"Starting export in {args.format} format")
            if not exporter.export_vault(args.format, args.output_dir):
                return 1
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        logging.debug("Exception details:", exc_info=True)
        return 1
    finally:
        session_path = config.get('session_path')
        if session_path and os.path.exists(session_path):
            os.remove(session_path)
            logging.info(f"Session file {session_path} deleted")
        
        # Log out from Bitwarden
        try:
            subprocess.run([config.get('bw_cmd', 'bw'), 'logout'], check=True)
            logging.info("Logged out from Bitwarden")
        except Exception as e:
            logging.error(f"Logout failed: {str(e)}")

    logging.info("Export process completed successfully")
    return 0

if __name__ == "__main__":
    exit(main())