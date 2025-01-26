import logging
import os
import subprocess
from src.exporter import ExportFormat

def handle_export(exporter, args):
    if args.all:
        logging.info("Starting export in all formats")
        for format_type in ExportFormat:
            logging.info(f"Processing format: {format_type.value}")
            if not exporter.export_vault(format_type, args.output_dir):
                logging.error(f"Failed to export {format_type.value}, stopping further exports")
                raise RuntimeError(f"Failed to export {format_type.value}")
    else:
        logging.info(f"Starting export in {args.format} format")
        if not exporter.export_vault(ExportFormat(args.format), args.output_dir):
            raise RuntimeError(f"Failed to export {args.format}")

def cleanup_session(config):
    session_path = config.get("session_path")
    if session_path and os.path.exists(session_path):
        os.remove(session_path)
        logging.info(f"Session file {session_path} deleted")

def logout_bitwarden(config):
    try:
        subprocess.run([config.get("bw_cmd", "bw"), "logout"], check=True)
        logging.info("Logged out from Bitwarden")
    except Exception as e:
        logging.error(f"Logout failed: {str(e)}")
