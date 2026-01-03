from shapely import MultiPolygon
from shapely import (
    MultiPoint,
    intersection,
    delaunay_triangles,
    distance,
)

from starplot.data import DataFiles
from starplot.styles import PathStyle


CONSTELLATION_HIP_IDS = {
    "and": {
        2912,
        1473,
        7607,
        677,
        116805,
        5447,
        9640,
        3881,
        116584,
        3693,
        4463,
        3031,
        3092,
        4436,
        116631,
        5434,
        113726,
    },
    "ant": {46515, 51172, 53502},
    "aps": {81065, 72370, 81852, 80047},
    "aql": {
        97804,
        95501,
        93805,
        97649,
        99473,
        93747,
        98036,
        96468,
        93429,
        93244,
        97278,
    },
    "aqr": {
        112961,
        114724,
        114341,
        106278,
        111497,
        112716,
        115438,
        110960,
        110672,
        109074,
        109139,
        110003,
        113136,
        115033,
        102618,
        110395,
    },
    "ara": {85792, 83081, 88714, 85258, 83153, 85267, 82363, 85727},
    "ari": {8832, 13209, 9884, 8903},
    "aur": {24608, 28358, 23015, 28360, 25428, 23767, 23416, 28380, 23453},
    "boo": {
        70497,
        71075,
        69732,
        69673,
        74666,
        72105,
        69483,
        71053,
        67275,
        73555,
        71795,
        67927,
    },
    "cae": {21770, 23595, 21060, 21861},
    "cam": {23040, 23522, 16228, 17959, 29997, 17884, 33694, 22783},
    "cap": {100064, 102978, 106723, 107556, 106985, 105881, 104139, 102485, 100345},
    "car": {
        54463,
        42913,
        52419,
        50371,
        53253,
        30438,
        38827,
        41037,
        39953,
        50099,
        45556,
        45238,
        51576,
        54301,
        54751,
    },
    "cas": {746, 3179, 4427, 8886, 6686},
    "cen": {
        55425,
        71683,
        67464,
        65936,
        68245,
        60823,
        68002,
        56243,
        71352,
        59449,
        68282,
        59196,
        68933,
        70090,
        65109,
        61789,
        68702,
        66657,
        61932,
        73334,
        68862,
    },
    "cep": {
        109857,
        101093,
        105199,
        106032,
        110991,
        112724,
        109492,
        102422,
        116727,
        107259,
    },
    "cet": {
        13954,
        12706,
        12387,
        8645,
        8102,
        6537,
        10826,
        5364,
        14135,
        1562,
        3419,
        11484,
        12828,
    },
    "cha": {60000, 58484, 52633, 40702, 51839},
    "cir": {74824, 75323, 71908},
    "cma": {33152, 35904, 33347, 31592, 33160, 33579, 34444, 30324, 34045, 32349},
    "cmi": {36188, 37279},
    "cnc": {44066, 40526, 42806, 42911, 43103},
    "col": {25859, 30277, 28199, 28328, 26634, 27628},
    "com": {64241, 64394, 60742},
    "cra": {93825, 94114, 90982, 94160, 94005},
    "crb": {77512, 76267, 75695, 78159, 76952, 78493, 76127},
    "crt": {57283, 55687, 56633, 53740, 58188, 55282, 55705, 54682},
    "cru": {62434, 59747, 61084, 60718},
    "crv": {60965, 61359, 59316, 59803, 59199},
    "cvn": {63125, 61317},
    "cyg": {100453, 99848, 95947, 97165, 95853, 102098, 103413, 102488, 94779, 104732},
    "del": {102532, 101958, 101769, 102281, 101421},
    "dor": {21281, 23693, 27890, 26069, 19893, 27100},
    "dra": {
        61281,
        75458,
        87585,
        97433,
        85829,
        85670,
        94376,
        80331,
        89937,
        56211,
        68756,
        89908,
        83895,
        87833,
        78527,
    },
    "equ": {104521, 104858, 104987},
    "eri": {
        21248,
        19587,
        13701,
        11407,
        21393,
        15510,
        13847,
        16537,
        7588,
        18216,
        12843,
        9007,
        20535,
        17593,
        14146,
        23875,
        21444,
        12486,
        20042,
        17874,
        22109,
        17378,
        12770,
        16611,
        16870,
        18543,
        18673,
        15474,
        17651,
        12413,
    },
    "for": {13147, 9677, 14879},
    "gem": {
        31681,
        36962,
        37826,
        30883,
        34693,
        30343,
        34088,
        32362,
        37740,
        36046,
        29655,
        36850,
        35350,
        32246,
        28734,
        33018,
        35550,
    },
    "gru": {113638, 112623, 109268, 108085, 110997, 109111, 112122},
    "her": {
        87808,
        83207,
        86414,
        84379,
        84380,
        81693,
        81833,
        80170,
        87933,
        80816,
        85112,
        85693,
        86974,
        77760,
        80463,
        88794,
        81126,
        81008,
        79992,
        84345,
        79101,
    },
    "hor": {14240, 12225, 19747, 12484, 12653, 13884},
    "hya": {
        56343,
        45336,
        54682,
        68895,
        42402,
        43813,
        42799,
        49841,
        46390,
        64962,
        47431,
        42313,
        52943,
        57936,
        43234,
        48356,
        43109,
        53740,
        49402,
        72571,
        51069,
    },
    "hyi": {11001, 9236, 2021, 17678},
    "ind": {105319, 101772, 108431, 103227, 102333},
    "lac": {111104, 111169, 111944, 110538, 111022, 110351, 110609, 109937, 109754},
    "leo": {
        57632,
        46146,
        47908,
        49669,
        48455,
        55434,
        54879,
        49583,
        50583,
        54872,
        55642,
        46750,
        50335,
    },
    "lep": {
        27072,
        25985,
        23685,
        25606,
        27654,
        28103,
        24327,
        24845,
        28910,
        24305,
        27288,
    },
    "lib": {74785, 76333, 72622, 73714, 76470, 76600},
    "lmi": {51233, 46952, 53229, 51056, 49593},
    "lup": {75264, 77634, 75141, 76297, 75177, 78384, 71860, 73273, 74395},
    "lyn": {45860, 33449, 30060, 36145, 41075, 45688, 44700, 44248},
    "lyr": {91971, 92420, 93194, 91919, 92791, 91262},
    "men": {23467, 29271},
    "mic": {103738, 105140, 105382, 102831},
    "mon": {32578, 37447, 31978, 31216, 34769, 30419, 30867, 29651, 39863},
    "mus": {61199, 61585, 62322, 57363, 59929, 63613},
    "nor": {80000, 78914, 80582, 78639},
    "oct": {107089, 112405, 70638},
    "oph": {
        81377,
        87108,
        79593,
        79882,
        84970,
        84012,
        85423,
        86032,
        88048,
        80473,
        80883,
        80628,
        86742,
        80343,
        83000,
        80569,
        80894,
    },
    "ori": {
        27913,
        22797,
        22549,
        28716,
        22957,
        22449,
        23607,
        22845,
        25281,
        28614,
        26311,
        25930,
        23123,
        27989,
        26207,
        27366,
        26727,
        22509,
        29038,
        29426,
        24436,
        25336,
    },
    "pav": {
        92609,
        105858,
        88866,
        99240,
        100751,
        91792,
        86929,
        90098,
        93015,
        102395,
        98495,
    },
    "peg": {
        109410,
        677,
        113963,
        112748,
        109176,
        1067,
        107315,
        109427,
        112440,
        113881,
        107354,
        112029,
        112158,
    },
    "per": {
        8068,
        19343,
        14354,
        17448,
        14632,
        18614,
        18246,
        14668,
        17358,
        13268,
        13531,
        19167,
        18532,
        19812,
        20070,
        12777,
        14576,
        15863,
        14328,
    },
    "phe": {2081, 5348, 7083, 5165, 6867, 765},
    "pic": {27321, 27530, 32607},
    "psa": {109285, 111954, 112948, 111188, 107380, 113368, 107608, 113246},
    "psc": {
        116928,
        116771,
        8198,
        4906,
        3786,
        7884,
        5742,
        9487,
        6193,
        5586,
        115830,
        7097,
        115738,
        114971,
        118268,
    },
    "pup": {
        35264,
        39429,
        31685,
        30438,
        39757,
        37229,
        37677,
        39953,
        36917,
        38070,
        38170,
    },
    "pyx": {43409, 42515, 42828, 39429},
    "ret": {17440, 19921, 19780, 18597},
    "scl": {4577, 117452, 115102, 116231},
    "sco": {
        85696,
        78401,
        87073,
        78820,
        85927,
        82729,
        86670,
        84143,
        80112,
        79374,
        81266,
        82514,
        86228,
        78104,
        78265,
        80763,
        82396,
        87261,
    },
    "sct": {90595, 91117, 91726, 92175},
    "ser1": {
        77450,
        77516,
        77070,
        77233,
        76852,
        76276,
        77622,
        78072,
    },
    "ser2": {86263, 89962, 88048, 92946},
    "sex": {51437, 49641, 51362, 48437},
    "sge": {98337, 96837, 96757, 97365},
    "sgr": {
        90496,
        95168,
        93506,
        93864,
        90185,
        92041,
        89931,
        89642,
        93085,
        93683,
        92855,
        89341,
        88635,
        94141,
    },
    "tau": {
        18724,
        20455,
        20205,
        21421,
        26451,
        16083,
        25428,
        16852,
        20889,
        18907,
        15900,
        20894,
    },
    "tel": {89112, 90422, 90568},
    "tra": {77952, 82273, 74946, 76440},
    "tri": {10064, 8796, 10670},
    "tuc": {110130, 118322, 2484, 114996, 110838, 1599},
    "uma": {
        46853,
        54539,
        46733,
        58001,
        53910,
        55203,
        54061,
        55219,
        44471,
        57399,
        48319,
        50372,
        44127,
        65378,
        67301,
        41704,
        62956,
        50801,
        59774,
    },
    "umi": {82080, 79822, 11767, 72607, 75097, 85822, 77055},
    "vel": {42913, 48774, 50191, 44816, 39953, 45941, 52727, 46651},
    "vir": {
        60129,
        65474,
        58948,
        57380,
        69701,
        68520,
        66249,
        64238,
        63090,
        61941,
        71957,
        63608,
        72220,
        57757,
    },
    "vol": {41312, 34481, 39794, 35228, 44382},
    "vul": {95771, 97886},
}


class ExperimentalPlotterMixin:
    def _constellation_borders(self):
        from shapely import LineString, MultiLineString
        from shapely.ops import unary_union
        import geopandas as gpd

        constellation_borders = gpd.read_file(
            DataFiles.CONSTELLATIONS,
            engine="pyogrio",
            use_arrow=True,
            bbox=self._extent_mask(),
        )

        if constellation_borders.empty:
            return

        geometries = []

        for i, constellation in constellation_borders.iterrows():
            geometry_types = constellation.geometry.geom_type

            # equinox = LineString([[0, 90], [0, -90]])
            """
            Problems:
                - Need to handle multipolygon borders too (SER)
                - Shapely's union doesn't handle geodesy (e.g. TRI + AND)
                - ^^ TRI is plotted with ra < 360, but AND has ra > 360
                - ^^ idea: create union first and then remove duplicate lines?
            
                TODO: create new static data file of constellation border lines
            """

            if "Polygon" in geometry_types and "MultiPolygon" not in geometry_types:
                polygons = [constellation.geometry]

            elif "MultiPolygon" in geometry_types:
                polygons = constellation.geometry.geoms

            for p in polygons:
                coords = list(zip(*p.exterior.coords.xy))
                # coords = [(ra * -1, dec) for ra, dec in coords]

                new_coords = []

                for i, c in enumerate(coords):
                    ra, dec = c
                    if i > 0:
                        if new_coords[i - 1][0] - ra > 60:
                            ra += 360

                        elif ra - new_coords[i - 1][0] > 60:
                            new_coords[i - 1][0] += 360

                    new_coords.append([ra, dec])

                ls = LineString(new_coords)
                geometries.append(ls)

        mls = MultiLineString(geometries)
        geometries = unary_union(mls)

        for ls in list(geometries.geoms):
            x, y = ls.xy

            self.line(zip(x, y), self.style.constellation_borders)
            # x, y = ls.xy
            # newx = [xx * -1 for xx in list(x)]
            # self.ax.plot(
            #     # list(x),
            #     newx,
            #     list(y),
            #     # **self._plot_kwargs(),
            #     # transform=self._geodetic,
            #     transform=self._plate_carree,
            #     **style_kwargs,
            # )

    def _plot_constellation_labels_experimental(
        self,
        style: PathStyle = None,
        label_fn=None,
    ):
        def sorter(g):
            # higher score is better
            d = distance(g.centroid, points_line.centroid)
            # d = distance(g.centroid, constellation.boundary.centroid)
            extent = abs(g.bounds[2] - g.bounds[0])
            area = g.area / constellation.boundary.area
            # return ((extent**3)) * area**2
            # return ((extent**2) - (d/2)) * area**2
            # print(str(extent) + " " + str(area) + " " + str(d))
            return d**2 * -1
            return (extent / 2 + area) - (d / 5)

        for constellation in self.objects.constellations:
            constellation_stars = [
                s
                for s in self.objects.stars
                if s.constellation_id == constellation.iau_id and s.magnitude < 5
            ]
            constellation_line_stars = [
                s
                for s in self.objects.stars
                if s.constellation_id == constellation.iau_id
                # and s.hip in CONSTELLATION_HIP_IDS[constellation.iau_id]
            ]
            points = MultiPoint([(s.ra, s.dec) for s in constellation_stars])
            points_line = MultiPoint([(s.ra, s.dec) for s in constellation_line_stars])

            triangles = delaunay_triangles(
                geometry=points,
                tolerance=2,
            )
            print(constellation.name + " " + str(len(triangles.geoms)))

            polygons = []
            for t in triangles.geoms:
                try:
                    inter = intersection(t, constellation.boundary)
                except Exception:
                    continue
                if (
                    inter.geom_type == "Polygon"
                    and len(list(zip(*inter.exterior.coords.xy))) > 2
                ):
                    polygons.append(inter)

            p_by_area = {pg.area: pg for pg in polygons}
            polygons_sorted = [
                p_by_area[k] for k in sorted(p_by_area.keys(), reverse=True)
            ]

            # sort by combination of horizontal extent and area
            polygons_sorted = sorted(polygons_sorted, key=sorter, reverse=True)

            if len(polygons_sorted) > 0:
                i = 0
                ra, dec = polygons_sorted[i].centroid.x, polygons_sorted[i].centroid.y
            else:
                ra, dec = constellation.ra, constellation.dec

            text = label_fn(constellation)
            style = style or self.style.constellation.label
            style.anchor_point = "center"
            self.text(
                text,
                ra,
                dec,
                style,
                hide_on_collision=self.hide_colliding_labels,
                area=MultiPolygon(polygons_sorted[:3])
                if len(polygons_sorted)
                else constellation.boundary,
            )
