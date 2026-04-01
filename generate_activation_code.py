import argparse
import os
from pathlib import Path

from utils.license_manager import LicenseManager


def load_env_file(env_path: Path) -> None:
    """Load key/value pairs from .env into process environment."""
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate activation key for POS system."
    )
    parser.add_argument(
        "--hardware-id",
        "-hwid",
        dest="hardware_id",
        help="Hardware ID from activation screen (format: XXXX-XXXX-XXXX-XXXX).",
    )
    args = parser.parse_args()

    load_env_file(Path(".env"))

    if args.hardware_id:
        hwid = args.hardware_id.strip().upper()
        key = LicenseManager.generate_activation_key(hwid)
        print(f"Hardware ID   : {hwid}")
        print(f"Activation Key: {key}")
        return

    local_hwid = LicenseManager.get_hardware_id()
    local_key = LicenseManager.generate_activation_key(local_hwid)
    print(f"Local Hardware ID   : {local_hwid}")
    print(f"Local Activation Key: {local_key}")


if __name__ == "__main__":
    main()
