import sys

from starplot.styles import fonts

COMMANDS = ["setup"]


def setup(options):
    from starplot.config import settings
    from starplot.data import db, bigsky

    print("Installing DuckDB spatial extension...")

    con = db.connect()
    con.load_extension("spatial")

    fonts.load()

    print(f"Installed to: {settings.data_path}")

    if "--install-big-sky" in options:
        bigsky.download_if_not_exists()
        print(f"Big Sky Catalog downloaded and installed to: {settings.download_path}")


def main():
    command = sys.argv[1].lower()

    if command not in COMMANDS:
        print(f"Unrecognized command: {command}")

    if command == "setup":
        setup(sys.argv[2:])
