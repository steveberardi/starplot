from shapely import Point

from starplot import Star, DSO
from starplot.data import Catalog

from .utils import TEST_DATA_PATH


def test_build_star_catalog():
    stars = [
        Star(
            pk=1,
            ra=120,
            dec=10,
            magnitude=1,
            epoch_year=2000,
            name="star1",
            geometry=Point(120, 10),
        ),
        Star(
            pk=2,
            ra=140,
            dec=15,
            magnitude=4,
            epoch_year=2000,
            name="star2",
            geometry=Point(140, 15),
        ),
        Star(
            pk=3,
            ra=160,
            dec=20,
            magnitude=5,
            epoch_year=2000,
            name="star3",
            tyc="12",
            geometry=Point(160, 20),
        ),
    ]

    path = TEST_DATA_PATH / "stars.parquet"

    cat = Catalog(path=path, healpix_nside=2)
    cat.build(
        objects=stars,
        chunk_size=200_000,
        columns=[
            "ra",
            "dec",
            "pk",
            "magnitude",
            "epoch_year",
            "name",
            "geometry",
            "tyc",
        ],
        sorting_columns=[
            "magnitude",
        ],
        compression="snappy",
        row_group_size=100_000,
    )

    star1 = Star.get(name="star1", catalog=cat)

    assert star1.ra == 120
    assert star1.dec == 10
    assert star1.name == "star1"
    assert star1.healpix_index == 21

    star2 = Star.get(name="star2", catalog=cat)
    assert star2.name == "star2"
    assert star2.healpix_index == 4

    star3 = Star.get(name="star3", catalog=cat)
    assert star3.name == "star3"
    assert star3.healpix_index == 27
    assert star3.tyc == "12"

    assert len(list(Star.all(catalog=cat))) == 3


def test_build_dso_catalog():
    dsos = [
        DSO(
            pk=1,
            ra=120,
            dec=10,
            magnitude=1,
            name="dso1",
            geometry=Point(120, 10),
        ),
        DSO(
            pk=2,
            ra=140,
            dec=15,
            magnitude=4,
            name="dso2",
            geometry=Point(140, 15),
            angle=20,
            m="1",
        ),
        DSO(
            pk=3,
            ra=160,
            dec=20,
            magnitude=5,
            name="dso3",
            geometry=Point(160, 20),
            ngc="224",
        ),
    ]

    path = TEST_DATA_PATH / "dsos.parquet"

    cat = Catalog(path=path)
    cat.build(
        objects=dsos,
        chunk_size=200_000,
        columns=[
            "pk",
            "ra",
            "dec",
            "magnitude",
            "name",
            "geometry",
            "m",
            "ngc",
        ],
        sorting_columns=[
            "magnitude",
        ],
        compression="snappy",
        row_group_size=1,
    )

    m1 = DSO.get(m="1", catalog=cat)

    assert m1.ra == 140
    assert m1.dec == 15
    assert m1.name == "dso2"
    assert m1.m == "1"
    assert m1.healpix_index is None

    ngc224 = DSO.get(ngc="224", catalog=cat)
    assert ngc224.ngc == "224"
    assert ngc224.ra == 160
    assert ngc224.dec == 20

    assert len(list(DSO.all(catalog=cat))) == 3
