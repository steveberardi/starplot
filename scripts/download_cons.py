import time

import requests

from starplot.data import constellations


BASE_URL = "https://www.iau.org/static/public/constellations/txt/"

for c in constellations.iterator():
    response = requests.get(f"{BASE_URL}{c.lower()}.txt")
    if response.status_code != 200:
        print(f"Non-200: {c}")
        continue
    else:
        print("ok")

    with open(f"raw/iau/{c.lower()}.txt", "wb") as outfile:
        outfile.write(response.content)

    time.sleep(0.5)
