import numpy as np

from skyfield.api import load
from skyfield.data import stellarium


"""
Dictionary of labels for each constellation

Keys: Constellation's 3-letter IAU abbreviation
Value: Tuple of full name (with newlines), right ascension (RA), and declination (DEC)

The RA/DEC for each constellation is the initial position of the label (to avoid overlapping),
but this position could change after adjusting all labels together before the final plot is saved.
"""
labels = {
    "And": ("Andromeda", 23.23, 37.35),
    "Ant": ("Antlia", 10.57, -35.71),
    "Aps": ("Apus", 15.95, -78.42),
    "Aql": ("Aquila", 19.25, -0.5),
    "Aqr": ("Aquarius", 22.52, -8.17),
    "Ara": ("Ara", 17.34, -55.03),
    "Ari": ("Aries", 1.97, 21.19),
    "Aur": ("Auriga", 5.43, 41.15),
    "Boo": ("Bootes", 14.52, 35.68),
    "CMa": ("Canis Major", 6.85, -19.8),
    "CMi": ("Canis Minor", 7.66, 5.23),
    "CVn": ("Canes\nVenatici", 12.73, 36.42),
    "Cae": ("Caelum", 4.82, -38.16),
    "Cam": ("Camelopardalis", 5.13, 66.24),
    "Cap": ("Capricornus", 21.1, -19.05),
    "Car": ("Carina", 9.7, -61.11),
    "Cas": ("Cassiopeia", 0.37, 60.52),
    "Cen": ("Centaurus", 13.82, -45.72),
    "Cep": ("Cepheus", 21.92, 65.42),
    "Cet": ("Cetus", 2.01, -3.02),
    "Cha": ("Chamaeleon", 10.79, -78.72),
    "Cir": ("Circinus", 15.0, -61.89),
    "Cnc": ("Cancer", 8.68, 18.57),
    "Col": ("Columba", 5.8, -36.68),
    "Com": ("Coma\nBerenices", 13.08, 22.7),
    "CrA": ("Corona\nAustralis", 19.14, -38.7),
    "CrB": ("Corona\nBorealis", 16.35, 27.64),
    "Crt": ("Crater", 11.86, -14.29),
    "Cru": ("Crux", 12.62, -61.39),
    "Crv": ("Corvus", 12.38, -20.02),
    "Cyg": ("Cygnus", 20.52, 32.64),
    "Del": ("Delphinus", 20.67, 14.6),
    "Dor": ("Dorado", 5.19, -59.22),
    "Dra": ("Draco", 16.35, 63.07),
    "Equ": ("Equuleus", 21.25, 7.63),
    "Eri": ("Eridanus", 3.62, -24.61),
    "For": ("Fornax", 3.01, -30.7),
    "Gem": ("Gemini", 7.07, 23.87),
    "Gru": ("Grus", 22.36, -44.26),
    "Her": ("Hercules", 16.88, 34.86),
    "Hor": ("Horologium", 3.06, -51.99),
    "Hya": ("Hydra", 10.23, -9.93),
    "Hyi": ("Hydrus", 2.14, -70.43),
    "Ind": ("Indus", 21.11, -53.22),
    "LMi": ("Leo Minor", 10.3, 35.27),
    "Lac": ("Lacerta", 22.21, 41.4),
    "Leo": ("Leo", 10.93, 18.13),
    "Lep": ("Lepus", 5.61, -17.76),
    "Lib": ("Libra", 15.34, -18.19),
    "Lup": ("Lupus", 15.62, -43.57),
    "Lyn": ("Lynx", 7.12, 53.08),
    "Lyr": ("Lyra", 18.82, 30.63),
    "Men": ("Mensa", 6.17, -74.75),
    "Mic": ("Microscopium", 20.83, -33.78),
    "Mon": ("Monoceros", 6.81, 0.93),
    "Mus": ("Musca", 12.5, -69.27),
    "Nor": ("Norma", 16.24, -48.03),
    "Oct": ("Octans", 19.64, -80.81),
    "Oph": ("Ophiuchus", 17.42, -1.48),
    "Ori": ("Orion", 5.45, 7.13),
    "Pav": ("Pavo", 19.29, -65.19),
    "Peg": ("Pegasus", 22.93, 16.95),
    "Per": ("Perseus", 3.53, 45.68),
    "Phe": ("Phoenix", 0.87, -47.82),
    "Pic": ("Pictor", 6.32, -59.05),
    "PsA": ("Piscis Austrinus", 22.46, -31.42),
    "Psc": ("Pisces", 1.28, 12.56),
    "Pup": ("Puppis", 7.68, -32.69),
    "Pyx": ("Pyxis", 8.48, -36.17),
    "Ret": ("Reticulum", 4.06, -62.0),
    "Scl": ("Sculptor", 16.04, -30.01),
    "Sco": ("Scorpius", 16.9, -33.55),
    "Sct": ("Scutum", 18.54, -12.35),
    "Ser": ("Serpens", 16.45, 3.59),
    "Sex": ("Sextans", 10.55, -4.24),
    "Sge": ("Sagitta", 19.74, 14.92),
    "Sgr": ("Sagittarius", 18.81, -26.05),
    "Tau": ("Taurus", 4.31, 15.24),
    "Tel": ("Telescopium", 18.32, -45.96),
    "TrA": ("Triangulum Australe", 15.91, -66.86),
    "Tri": ("Triangulum", 2.11, 32.8),
    "Tuc": ("Tucana", 15.49, -62.81),
    "UMa": ("Ursa Major", 10.87, 51.95),
    "UMi": ("Ursa Minor", 16.25, 83.28),
    "Vel": ("Vela", 9.49, -48.38),
    "Vir": ("Virgo", 13.67, 1.02),
    "Vol": ("Volans", 8.01, -67.92),
    "Vul": ("Vulpecula", 20.13, 22.21),
}


def get_constellation_data():
    url = "https://raw.githubusercontent.com/Stellarium/stellarium/master/skycultures/modern_st/constellationship.fab"
    with load.open(url) as f:
        consdata = stellarium.parse_constellations(f)
    return consdata


def create_projected_constellation_lines(stardata_projected):
    consdata = get_constellation_data()
    stars_1 = []
    stars_2 = []
    for _, lines in consdata:
        for s1, s2 in lines:
            stars_1.append(s1)
            stars_2.append(s2)
    xy1 = stardata_projected[["x", "y"]].loc[stars_1].values
    xy2 = stardata_projected[["x", "y"]].loc[stars_2].values

    return np.rollaxis(np.array([xy1, xy2]), 1)
