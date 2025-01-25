import sys

from starplot.styles import fonts

COMMANDS = ["setup"]


def setup(options):
    from starplot import settings
    from starplot.data import db, bigsky

    print("Installing DuckDB spatial extension...")

    con = db.connect()
    con.load_extension("spatial")

    fonts.load()

    print(f"Installed to: {settings.DUCKDB_EXTENSION_PATH}")

    if "--install-big-sky" in options:
        bigsky.download_if_not_exists()
        print(f"Big Sky Catalog downloaded and installed to: {settings.DOWNLOAD_PATH}")


def main():
    command = sys.argv[1].lower()

    if command not in COMMANDS:
        print(f"Unrecognized command: {command}")

    if command == "setup":
        setup(sys.argv[2:])
