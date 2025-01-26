import logging
import subprocess
import requests
import time
from packaging import version

def check_cli_version(cli_cmd='bw'):
    try:
        current = subprocess.run([cli_cmd, '--version'], capture_output=True, text=True)
        current_version = version.parse(current.stdout.strip())

        response = requests.get(
            "https://api.github.com/repos/bitwarden/cli/releases/latest",
            timeout=5
        )
        response.raise_for_status()
        
        latest = version.parse(response.json()["tag_name"].lstrip('v'))

        if current_version < latest:
            logging.warning(
                f"Update available: {current_version} → {latest}\n"
                "Download: https://github.com/bitwarden/cli/releases"
            )
        
        return True

    except requests.exceptions.RequestException as e:
        logging.error(f"Update check failed: {e}")
        return False

def verify_cli():
    logging.debug("Verifying Bitwarden CLI installation")
    try:
        result = subprocess.run(['bw', '--version'], capture_output=True, text=True)
        logging.info(f"Found Bitwarden CLI version: {result.stdout.strip()}")
        return 'bw'
    except FileNotFoundError:
        logging.error("Bitwarden CLI not found in PATH")
        raise SystemError("Bitwarden CLI not found. Please install it first.")

def sanitize_path(path):
    return path.strip()

def retry_with_backoff(func, retries=3, backoff_in_seconds=1):
    last_exception = None
    for attempt in range(retries):
        try:
            return func()
        except Exception as e:
            last_exception = e
            wait = backoff_in_seconds * (2 ** attempt)
            logging.warning(f"Attempt {attempt + 1} failed. Retrying in {wait} seconds")
            time.sleep(wait)
    
    raise last_exception
