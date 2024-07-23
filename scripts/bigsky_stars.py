import pandas as pd

DIGITS = 4

df = pd.read_csv(
    # "raw/bigsky.stars.csv.gz",
    "raw/bigsky.stars.mag11.csv.gz",
    header=0,
    names=[
        "tyc_id",
        "hip_id",
        "ccdm",
        "magnitude",
        "bv",
        "ra_degrees_j2000",
        "dec_degrees_j2000",
        "ra_mas_per_year",
        "dec_mas_per_year",
        "parallax_mas",
        # "hip",
        # "magnitude",
        # "ra_hours",
        # "dec_degrees",
        # "parallax_mas",
        # "ra_mas_per_year",
        # "dec_mas_per_year",
        # "bv",
    ],
    compression="gzip",
)

df["ra_hours"] = df.apply(lambda row: round(row.ra_degrees_j2000 / 15, DIGITS), axis=1)

df = df.assign(
    # hip=df["hip_id"],
    # ra_degrees=df["ra_degrees_j2000"],
    # dec_degrees=df["dec_degrees_j2000"],
    epoch_year=2000,
)

df = df.rename(
    columns={
        "hip_id": "hip",
        "ra_degrees_j2000": "ra_degrees",
        "dec_degrees_j2000": "dec_degrees",
    }
)

print(df)

# df.to_parquet("temp/stars.bigsky.parquet", compression="gzip")
df.to_parquet("temp/stars.bigsky.mag11.parquet", compression="gzip")
