import sys

from starplot.data import stars, constellations


def get_constellation_hips():
    """Returns list of HIP ids for all stars in constellations"""
    consdata = constellations.load()
    hips = []
    for _, lines in consdata:
        for s1, s2 in lines:
            hips.extend([s1, s2])
    return hips


def trim_hip(
    filename_in: str = "hip_main.dat",
    filename_out: str = "hip_trim.dat",
    limiting_magnitude: float = stars.BASE_LIMITING_MAG,
    separator: str = "|",
):
    """Trims the HIP data file to only stars brighter than limiting_magnitude"""
    count = 0
    outfile = open(filename_out, "w")
    constellation_hips = get_constellation_hips()
    limiting_magnitude_con = 0

    with open(filename_in) as hipfile:
        for starline in hipfile:
            star = [c.strip() for c in starline.rstrip().split(separator)]
            hip = int(star[1])

            if not star[5]:
                print(f"No magnitude found for HIP-{str(hip)}")
                continue

            mag = float(star[5])  # use Vmag for magnitude

            if hip in constellation_hips and mag > limiting_magnitude_con:
                limiting_magnitude_con = mag

            if mag <= limiting_magnitude or hip in constellation_hips:
                outfile.write(starline)
                count += 1

    outfile.close()
    print(f"Trimmed to {str(count)} stars!")
    print(f"Limiting magnitude of constellation stars: {str(limiting_magnitude_con)}")


if __name__ == "__main__":
    filename_in = sys.argv[1]
    filename_out = sys.argv[2]
    limiting_mag = float(sys.argv[3])
    trim_hip(filename_in, filename_out, limiting_mag)
