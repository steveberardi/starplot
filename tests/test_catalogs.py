from shapely import Point

from starplot import Star
from starplot.data import Catalog

from .utils import TEST_DATA_PATH


def test_build_catalog():
    stars = [
        Star(
            ra=120,
            dec=10,
            magnitude=1,
            epoch_year=2000,
            name="star1",
            geometry=Point(120, 10),
        ),
        Star(
            ra=140,
            dec=15,
            magnitude=4,
            epoch_year=2000,
            name="star2",
            geometry=Point(140, 15),
        ),
        Star(
            ra=160,
            dec=20,
            magnitude=5,
            epoch_year=2000,
            name="star3",
            geometry=Point(160, 20),
        ),
    ]

    path = TEST_DATA_PATH / "stars.parquet"
    Catalog.build(
        objects=stars,
        path=path,
        chunk_size=200_000,
        columns=[
            "ra",
            "dec",
            "magnitude",
            "epoch_year",
            "name",
            "geometry",
        ],
        sorting_columns=[
            "magnitude",
        ],
        compression="snappy",
        row_group_size=100_000,
    )

    cat = Catalog(path=path)
    star1 = Star.get(name="star1", catalog=cat)

    assert star1.ra == 120
    assert star1.dec == 10
    assert star1.name == "star1"
    assert len(list(Star.all(catalog=cat))) == 3
