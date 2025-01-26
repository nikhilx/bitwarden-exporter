# Bitwarden Vault Exporter

A Python-based CLI tool for automated Bitwarden vault exports with enhanced authentication handling and configurable export formats.

## Features

- Multiple export formats support (JSON, CSV, encrypted JSON)
- Automatic CLI version checking
- API key authentication support

## Installation

1. Clone the repository
2. Install dependencies:
```sh
pip install -r requirements.txt
```
3. Ensure Bitwarden CLI is installed and available in your PATH
4. Configure your `config.ini` file:
```ini
[bitwarden]
client_id = your_client_id
client_secret = your_client_secret
session_path = .bw/session.txt
```
If `config.ini` is not provided, you will be prompted for `client_id`, `client_secret`, and `master_password` during execution.

## Usage

Basic usage with format selection:
```sh
python main.py --format json
```

Export in all available formats:
```sh
python main.py --all
```

Additional options:
```sh
python main.py --config custom_config.ini --format json --output-dir custom_exports
```

### Command Line Arguments

- `--config`: Path to config file (default: config.ini)
- `--format`: Export format (choices: json, csv, encrypted_json)
- `--all`: Export in all formats
- `--output-dir`: Custom output directory (default: exports)
- `--check-updates`: Check for Bitwarden CLI updates


## Development

The project uses Python 3.12 and follows standard Python project structure. Debug logging is enabled by default for development purposes.

## License

MIT License