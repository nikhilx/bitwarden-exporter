import logging
import argparse
from src.config import Config
from src.exporter import BitwardenExporter, ExportFormat
from src.utils import check_cli_version
from src.export_utils import handle_export, cleanup_session, logout_bitwarden

# Enhanced logging configuration
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - [%(funcName)s] %(message)s",
    handlers=[logging.FileHandler("bitwarden_exporter.log"), logging.StreamHandler()],
)

def parse_arguments():
    parser = argparse.ArgumentParser(description="Bitwarden Vault Exporter")
    parser.add_argument("--config", default="config.ini", help="Path to config file")
    parser.add_argument(
        "--format", choices=[e.value for e in ExportFormat], help="Export format"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Export in all formats (json, csv, password_encrypted_json, account_encrypted_json)",
    )
    parser.add_argument("--output-dir", default="exports", help="Output directory")
    parser.add_argument(
        "--check-updates", action="store_true", help="Check for CLI updates"
    )
    args = parser.parse_args()

    logging.debug(f"Parsed arguments: {args}")

    if not args.format and not args.all:
        logging.error("No export format specified")
        parser.error("Either --format or --all must be specified")

    return args

def main():
    logging.info("Starting Bitwarden Vault Exporter")
    args = parse_arguments()

    try:
        config = Config(args.config)
        exporter = BitwardenExporter(config)

        if args.check_updates:
            logging.info("Checking for updates")
            check_cli_version()

        handle_export(exporter, args)
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        logging.debug("Exception details:", exc_info=True)

    finally:
        cleanup_session(config)
        logout_bitwarden(config)

    logging.info("Export process completed successfully")

if __name__ == "__main__":
    exit(main())
