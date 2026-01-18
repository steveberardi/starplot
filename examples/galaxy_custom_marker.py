import numpy as np
import matplotlib.path as mpath
import matplotlib.patches as mpatches
import cartopy.crs as ccrs
from astropy.coordinates import SkyCoord

from starplot import MapPlot, LambertAzEqArea, _
from starplot.styles import PlotStyle, extensions

group_blue = {
    "M81": {"RA": 148.888, "DEC": 69.065, "distance": 3.70},
    "M82": {"RA": 148.971, "DEC": 69.679, "distance": 3.61},
    "NGC3077": {"RA": 150.829, "DEC": 68.734, "distance": 3.85},
    "NGC2403": {"RA": 114.213, "DEC": 65.602, "distance": 3.19},
    "NGC4236": {"RA": 184.175, "DEC": 69.462, "distance": 4.41},
    "NGC4244": {"RA": 184.372, "DEC": 37.807, "distance": 4.31},
    "NGC4449": {"RA": 187.046, "DEC": 44.093, "distance": 4.27},
}
gal_ra = np.array([g["RA"] for g in group_blue.values()])
gal_dec = np.array([g["DEC"] for g in group_blue.values()])
gal_names = list(group_blue.keys())

group_silver = {
    "NGC4214": {"RA": 183.912, "DEC": 36.327, "distance": 2.94},
    "HolmII": {"RA": 124.767, "DEC": 70.714, "distance": 3.39},
    "NGC4395": {"RA": 186.458, "DEC": 33.5461, "distance": 4.61},
    "M94": {"RA": 192.723, "DEC": 41.1194, "distance": 4.66},
    "NGC2366": {"RA": 112.228, "DEC": 69.2053, "distance": 3.19},
    "DDO82": {"RA": 157.646, "DEC": 70.6194, "distance": 4.00},
    "DDO168": {"RA": 198.619, "DEC": 45.9194, "distance": 4.33},
    "DO165": {"RA": 196.612, "DEC": 67.7042, "distance": 4.57},
    "IC3687": {"RA": 190.563, "DEC": 38.5019, "distance": 4.57},
    "HolmI": {"RA": 145.135, "DEC": 71.1864, "distance": 3.84},
}
other_gal_ra = np.array([g["RA"] for g in group_silver.values()])
other_gal_dec = np.array([g["DEC"] for g in group_silver.values()])
other_gal_names = list(group_silver.keys())


def get_hurricane():
    u = np.array(
        [
            [2.444, 7.553],
            [0.513, 7.046],
            [-1.243, 5.433],
            [-2.353, 2.975],
            [-2.578, 0.092],
            [-2.075, -1.795],
            [-0.336, -2.870],
            [2.609, -2.016],
        ]
    )
    u[:, 0] -= 0.098
    codes = [1] + [2] * (len(u) - 2) + [2]
    u = np.append(u, -u[::-1], axis=0)
    codes += codes
    # Scale to angular size
    scale = 1.15 / np.max(np.abs(u))
    return mpath.Path(scale * u, codes, closed=False)


hurricane = get_hurricane()

center_coord = SkyCoord(ra=160, dec=58, unit="deg")
center_ra = center_coord.ra.deg
center_dec = center_coord.dec.deg

style = PlotStyle().extend(
    extensions.BLUE_LIGHT,
    extensions.MAP,
)
p = MapPlot(
    projection=LambertAzEqArea(center_ra=center_ra, center_dec=center_dec),
    ra_min=120,
    ra_max=200,
    dec_min=33,
    dec_max=78,
    style=style,
    resolution=4000,
    autoscale=True,
)

p.stars(
    where=[_.magnitude < 8],
    bayer_labels=True,
    where_labels=[_.magnitude < 1.75],
    alpha_fn=lambda star: max(0.01, 1.0 - 0.1 * star.magnitude),
)

for ra, dec, name in zip(gal_ra, gal_dec, gal_names):
    # Build hurricane polygon in sky coordinates (degrees)
    ra_offsets = hurricane.vertices[:, 0] / np.cos(
        np.radians(dec)
    )  # Adjust angular size for declination
    dec_offsets = hurricane.vertices[:, 1]
    hurricane_lon = ra + ra_offsets
    hurricane_lat = dec + dec_offsets
    # Convert RA to the longitude convention starplot/cartopy use (RA increases eastward)
    hurricane_lon_cartopy = np.mod(360.0 - hurricane_lon, 360.0)
    # Transform each vertex into the map projection
    projected_vertices = np.array(
        [
            p.ax.projection.transform_point(lon, lat, ccrs.PlateCarree())
            for lon, lat in zip(hurricane_lon_cartopy, hurricane_lat)
        ]
    )

    patch = mpatches.PathPatch(
        mpath.Path(projected_vertices, hurricane.codes),
        facecolor="lightblue",
        edgecolor="navy",
        linewidth=5.0,
        zorder=30,
    )
    p.ax.add_patch(patch)
    p.marker(
        ra=ra,
        dec=dec,
        style={
            "marker": {
                "symbol": "circle",
                "size": 10,
                "color": "darkblue",
                "edge_color": "navy",
                "edge_width": 3.0,
            }
        },
    )
    p.text(
        text=name,
        ra=ra,
        dec=dec,
        style={
            "font_color": "navy",
            "font_size": 28,
            "font_weight": 700,
            "offset_x": 35,
            "offset_y": 35,
        },
    )

for ra, dec, name in zip(other_gal_ra, other_gal_dec, other_gal_names):
    p.marker(
        ra=ra,
        dec=dec,
        style={
            "marker": {
                "symbol": "ellipse",
                "size": 30,
                "color": "orange",
                "edge_color": "black",
                "edge_width": 2.0,
            }
        },
    )
    p.text(
        text=name,
        ra=ra,
        dec=dec,
        style={
            "font_color": "black",
            "font_size": 28,
            "offset_x": 15.0,
            "offset_y": 40.0,
        },
    )

p.gridlines()
p.constellations(style__color="#78d78e", style__alpha=0.25)
p.constellation_borders(style__color="#035019", style__alpha=0.25)
p.constellation_labels(style__font_size=28, style__font_color="#035019")
p.milky_way()
p.ecliptic()
p.celestial_equator()
p.ax.tick_params(axis="both", labelsize=28)

p.export("galaxy_custom_marker.png", padding=0.3, transparent=True)
