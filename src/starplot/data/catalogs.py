from starplot.config import settings
from starplot.data.catalog import Catalog


BIG_SKY = Catalog(
    path=settings.data_path / "constellations-iau.parquet",
    url="https://github.com/steveberardi/starplot-constellations/releases/download/beta/constellations.parquet"
)

OPEN_NGC = Catalog(
    path=settings.data_path / "constellations-iau.parquet",
    url="https://github.com/steveberardi/starplot-constellations/releases/download/beta/constellations.parquet"
)

CONSTELLATIONS_IAU = Catalog(
    path=settings.data_path / "constellations-iau.parquet",
    url="https://github.com/steveberardi/starplot-constellations/releases/download/beta/constellations.parquet"
)
