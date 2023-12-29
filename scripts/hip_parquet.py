"""Creates a parquet file of the Hipparcos star catalog"""

from skyfield.api import load
from skyfield.data import hipparcos

# load hipparcos stars via Skyfield API
with load.open(hipparcos.URL) as f:
    hipstars = hipparcos.load_dataframe(f)

# convert to parquet
hipstars.to_parquet("stars.hipparcos.parquet", index=True, compression="gzip")

# also save to CSV for QA
hipstars.to_csv("stars.hipparcos.csv")
