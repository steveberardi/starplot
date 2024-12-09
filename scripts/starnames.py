import csv
from pathlib import Path
from pprint import pprint

from starplot.data.stars import STAR_NAMES

HERE = Path(__file__).resolve().parent
DATA_PATH = HERE.parent / "raw"

iau_names = {}

with open(DATA_PATH / "star-names-iau-2024.csv") as namefile:
    reader = csv.reader(namefile)
    next(reader)

    for row in reader:
        hip = row[2]
        name = row[0]

        if hip and hip != "0":
            hip = int(hip)
        else:
            continue

        iau_names[hip] = name

not_in_iau = []

for hip, name in STAR_NAMES.items():
    if hip in iau_names.keys() and name != iau_names[hip]:
        print(f"{name}  ->  {iau_names[hip]}")

    if hip not in iau_names.keys():
        not_in_iau.append(name)

print("Not in IAU :")
pprint(not_in_iau)

ctr = 0
for hip, name in iau_names.items():
    if hip not in STAR_NAMES.keys():
        ctr += 1

print(ctr)


print(f"Count current = {len(STAR_NAMES)}")
print(f"Count IAU = {len(iau_names)}")
# print(iau_names)


pprint(iau_names)
