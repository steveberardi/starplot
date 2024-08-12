import sys

import requests


def download(url, download_path, description=""):
    with open(download_path, "wb") as f:
        print(f"Downloading {description}...")

        response = requests.get(url, stream=True)
        total_size = response.headers.get("content-length")

        if total_size is None:
            f.write(response.content)
            return

        bytes_written = 0
        total_size = int(total_size)
        for chunk in response.iter_content(chunk_size=4096):
            bytes_written += len(chunk)
            f.write(chunk)

            progress = int(25 * bytes_written / total_size)
            sys.stdout.write("\r[%s%s]" % ("=" * progress, " " * (25 - progress)))
            sys.stdout.flush()

        print("Download complete!")
