import geopandas as gpd
import pandas as pd

from shapely.geometry import Polygon

from starplot.data import constellations

from data_settings import BUILD_PATH, RAW_PATH

DATA_PATH = RAW_PATH / "iau"
CRS = "+ellps=sphere +f=0 +proj=latlong +axis=wnu +a=6378137 +no_defs"


def parse_ra(ra_str):
    """Parses RA from border file HH MM SS to 0...360 degree float"""
    h, m, s = ra_str.strip().split(" ")
    return round(15 * (float(h) + float(m) / 60 + float(s) / 3600), 6)


def parse_dec(dec_str):
    """Parses DEC from ONGC CSV from HH:MM:SS to -90...90 degree float"""
    return round(float(dec_str), 6)


def parse_borders(lines):
    coords = []
    for line in lines:
        if "|" not in line:
            continue
        ra_str, dec_str, _ = line.split("|")
        ra = parse_ra(ra_str)
        dec = parse_dec(dec_str)
        coords.append((ra, dec))
    return coords


def build_constellations():
    constellation_records = []
    constellation_star_hips = constellations.CONSTELLATION_HIP_IDS

    for cid, props in constellations.properties.items():
        constellation_dict = {
            "iau_id": cid.lower(),
            "name": props[0].replace("\n", " "),
            "center_ra": props[1] * 15,
            "center_dec": props[2],
            "star_hip_ids": list(constellation_star_hips[cid.lower()]),
        }

        if cid == "Ser":
            ser1_coords = []
            ser2_coords = []
            with open(DATA_PATH / "ser1.txt", "r") as ser1:
                ser1_coords = parse_borders(ser1.readlines())
                ser1_boundary = Polygon(ser1_coords)
                ser1 = constellation_dict.copy()
                ser1["name"] = "Serpens Caput"
                ser1["iau_id"] = "ser1"
                ser1["center_ra"] = 235.2685
                ser1["center_dec"] = 9.3025
                ser1["geometry"] = ser1_boundary
                constellation_records.append(ser1)

            with open(DATA_PATH / "ser2.txt", "r") as ser2:
                ser2_coords = parse_borders(ser2.readlines())
                ser2_boundary = Polygon(ser2_coords)
                ser2 = constellation_dict.copy()
                ser2["name"] = "Serpens Cauda"
                ser2["iau_id"] = "ser2"
                ser2["center_ra"] = 273.1001
                ser2["center_dec"] = -7.2970
                ser2["geometry"] = ser2_boundary
                constellation_records.append(ser2)

        else:
            with open(DATA_PATH / f"{cid.lower()}.txt", "r") as borderfile:
                coords = parse_borders(borderfile.readlines())
                constellation_dict["geometry"] = Polygon(coords)

            constellation_records.append(constellation_dict)

    return constellation_records


def build():
    constellation_records = build_constellations()
    df = pd.DataFrame.from_records(constellation_records)

    gdf = gpd.GeoDataFrame(
        df,
        geometry=df["geometry"],
        # crs=CRS,
    )

    gdf.to_file(
        BUILD_PATH / "constellations.json",
        driver="GeoJSON",
        engine="pyogrio",
    )
    print("Total Constellations: " + str(len(constellation_records)))


if __name__ == "__main__":
    build()
