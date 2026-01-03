import sys

import requests
import numpy as np


def download(url, download_path, description: str = "", silent=False):
    with open(download_path, "wb") as f:
        if not silent:
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
            if not silent:
                sys.stdout.write("\r[%s%s]" % ("=" * progress, " " * (25 - progress)))
                sys.stdout.flush()

        if not silent:
            print("Download complete!")


def to_pandas(value):
    return value.to_pandas().replace({np.nan: None})
