from skyfield.data import stellarium

from starplot.data import load as _load


"""
Dictionary of properties for each constellation

Keys: Constellation's 3-letter IAU abbreviation
Value: Tuple of full name (with newlines), right ascension (RA), and declination (DEC)

The RA/DEC for each constellation is the initial position of the label (to avoid overlapping),
but this position could change after adjusting all labels together before the final plot is saved.
"""
properties = {
    "And": ("Andromeda", 0.93, 43.57),
    "Ant": ("Antlia", 10.57, -35.71),
    "Aps": ("Apus", 15.95, -78.42),
    "Aql": ("Aquila", 19.25, -0.5),
    "Aqr": ("Aquarius", 22.52, -8.17),
    "Ara": ("Ara", 17.34, -55.03),
    "Ari": ("Aries", 2.68, 22.56),
    "Aur": ("Auriga", 5.43, 41.15),
    "Boo": ("Bootes", 14.52, 35.68),
    "CMa": ("Canis Major", 6.95, -23.18),
    "CMi": ("Canis\nMinor", 7.86, 6.83),
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
    "Col": ("Columba", 5.92, -39.28),
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
    "Scl": ("Sculptor", 0.33, -32.01),
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
    "Tuc": ("Tucana", 23.84, -64.81),
    "UMa": ("Ursa Major", 10.87, 51.95),
    "UMi": ("Ursa Minor", 16.25, 83.28),
    "Vel": ("Vela", 9.49, -48.38),
    "Vir": ("Virgo", 13.67, 1.02),
    "Vol": ("Volans", 8.01, -67.92),
    "Vul": ("Vulpecula", 20.13, 22.21),
}


def load():
    with _load.open("constellations_hip.fab") as f:
        consdata = stellarium.parse_constellations(f)
    return consdata


def get(constellation_id: str):
    return properties.get(constellation_id)


def iterator():
    for c in properties.keys():
        yield c
