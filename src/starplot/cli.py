import sys

from starplot.styles import fonts
from starplot.config import settings
from starplot.data import db
from starplot.data.catalogs import download_all_catalogs

COMMANDS = ["setup"]


def setup(options):
    print("Installing DuckDB spatial extension...")

    con = db.connect()
    con.load_extension("spatial")

    fonts.load()

    print(f"Downloading data catalogs to: {settings.data_path}")
    download_all_catalogs()


def main():
    command = sys.argv[1].lower()

    if command not in COMMANDS:
        print(f"Unrecognized command: {command}")

    if command == "setup":
        setup(sys.argv[2:])
