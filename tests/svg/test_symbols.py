from starplot.svg import symbols

X, Y, SIZE = 50, 50, 20
ATTRS = {"fill": "red"}


class TestSymbols:
    def test_circle_renders_expected_svg(self):
        # GIVEN a circle symbol
        el = symbols.circle(X, Y, SIZE, ATTRS)

        # WHEN rendering it
        out = el.render()

        # THEN it's a single <circle> with radius = size / 2
        assert out == '<circle cx="50" cy="50" r="10.0" fill="red" />'

    def test_circle_cross_renders_expected_svg(self):
        # GIVEN a circle-cross symbol
        el = symbols.circle_cross(X, Y, SIZE, ATTRS)

        # WHEN rendering it
        out = el.render()

        # THEN it's a group containing the circle and its two crossing lines
        assert out == (
            '<g fill="red">\n'
            '  <circle cx="50" cy="50" r="10.0" />\n'
            '  <line x1="40.0" y1="50" x2="60.0" y2="50" />\n'
            '  <line x1="50" y1="60.0" x2="50" y2="40.0" />\n'
            "</g>"
        )

    def test_circle_crosshair_renders_expected_svg(self):
        # GIVEN a circle-crosshair symbol
        el = symbols.circle_crosshair(X, Y, SIZE, ATTRS)

        # WHEN rendering it
        out = el.render()

        # THEN it's a group containing a small circle and 4 tick marks, one per side
        assert out == (
            '<g fill="red">\n'
            '  <circle cx="50" cy="50" r="5.0" />\n'
            '  <line x1="50" y1="45.0" x2="50" y2="40.0" />\n'
            '  <line x1="55.0" y1="50" x2="60.0" y2="50" />\n'
            '  <line x1="50" y1="55.0" x2="50" y2="60.0" />\n'
            '  <line x1="45.0" y1="50" x2="40.0" y2="50" />\n'
            "</g>"
        )

    def test_circle_line_renders_expected_svg(self):
        # GIVEN a circle-line symbol
        el = symbols.circle_line(X, Y, SIZE, ATTRS)

        # WHEN rendering it
        out = el.render()

        # THEN it's a group with the circle and a horizontal line, whose
        # stroke-width is doubled from the (default) base width of 2
        assert out == (
            '<g fill="red">\n'
            '  <circle cx="50" cy="50" r="10.0" />\n'
            '  <line x1="32.0" y1="50" x2="68.0" y2="50" stroke-width="4" />\n'
            "</g>"
        )

    def test_ellipse_renders_expected_svg(self):
        # GIVEN an ellipse symbol
        el = symbols.ellipse(X, Y, SIZE, ATTRS)

        # WHEN rendering it
        out = el.render()

        # THEN it's a single <ellipse>, rotated -20 degrees around its center
        assert out == (
            '<ellipse cx="50" cy="50" rx="10.0" ry="6.0" '
            'transform="rotate(-20, 50, 50)" fill="red" />'
        )

    def test_square_renders_expected_svg(self):
        # GIVEN a square symbol
        el = symbols.square(X, Y, SIZE, ATTRS)

        # WHEN rendering it
        out = el.render()

        # THEN it's a single <rect> centered on (x, y)
        assert out == '<rect x="40.0" y="40.0" height="20" width="20" fill="red" />'

    def test_triangle_renders_expected_svg(self):
        # GIVEN a triangle symbol
        el = symbols.triangle(X, Y, SIZE, ATTRS)

        # WHEN rendering it
        out = el.render()

        # THEN it's a single <polygon> with 3 points
        assert out == (
            '<polygon points="50.0,38.453 60.0,55.7735 40.0,55.7735" fill="red" />'
        )

    def test_diamond_renders_expected_svg(self):
        # GIVEN a diamond symbol
        el = symbols.diamond(X, Y, SIZE, ATTRS)

        # WHEN rendering it
        out = el.render()

        # THEN it's a single <polygon> with 4 points (top, right, bottom, left)
        assert out == (
            '<polygon points="50,40.0 60.0,50 50,60.0 40.0,50" fill="red" />'
        )

    def test_star_renders_expected_svg(self):
        # GIVEN a 5-pointed star symbol
        el = symbols.SYMBOL_FUNCTIONS["star"](X, Y, SIZE, ATTRS)

        # WHEN rendering it
        out = el.render()

        # THEN it's a single <polygon> with 10 points (5 outer, 5 inner)
        assert out == (
            '<polygon points="50.0,40.0 52.3511,46.7639 59.5106,46.9098 '
            "53.8042,51.2361 55.8779,58.0902 50.0,54.0 44.1221,58.0902 "
            '46.1958,51.2361 40.4894,46.9098 47.6489,46.7639" fill="red" />'
        )

    def test_star_4_renders_expected_svg(self):
        # GIVEN a 4-pointed star symbol
        el = symbols.SYMBOL_FUNCTIONS["star_4"](X, Y, SIZE, ATTRS)

        # WHEN rendering it
        out = el.render()

        # THEN it's a single <polygon> with 8 points (4 outer, 4 inner)
        assert out == (
            '<polygon points="50.0,40.0 52.8284,47.1716 60.0,50.0 52.8284,52.8284 '
            '50.0,60.0 47.1716,52.8284 40.0,50.0 47.1716,47.1716" fill="red" />'
        )

    def test_star_8_renders_expected_svg(self):
        # GIVEN an 8-pointed star symbol
        el = symbols.SYMBOL_FUNCTIONS["star_8"](X, Y, SIZE, ATTRS)

        # WHEN rendering it
        out = el.render()

        # THEN it's a single <polygon> with 16 points (8 outer, 8 inner)
        assert out == (
            '<polygon points="50.0,40.0 51.5307,46.3045 57.0711,42.9289 '
            "53.6955,48.4693 60.0,50.0 53.6955,51.5307 57.0711,57.0711 "
            "51.5307,53.6955 50.0,60.0 48.4693,53.6955 42.9289,57.0711 "
            "46.3045,51.5307 40.0,50.0 46.3045,48.4693 42.9289,42.9289 "
            '48.4693,46.3045" fill="red" />'
        )

    def test_plus_renders_expected_svg(self):
        # GIVEN a plus symbol
        el = symbols.plus(X, Y, SIZE, ATTRS)

        # WHEN rendering it
        out = el.render()

        # THEN it's a single <polygon> tracing the 12-point plus-sign outline
        assert out == (
            '<polygon points="47.5,40.0 52.5,40.0 52.5,47.5 60.0,47.5 60.0,52.5 '
            "52.5,52.5 52.5,60.0 47.5,60.0 47.5,52.5 40.0,52.5 40.0,47.5 "
            '47.5,47.5" fill="red" />'
        )

    def test_comet_renders_expected_svg(self):
        # GIVEN a comet symbol, using a small step count for a readable arc
        el = symbols.comet(X, Y, SIZE, ATTRS, steps=4)

        # WHEN rendering it
        out = el.render()

        # THEN it's a single <polygon>: a tip, the two points where the tail
        # meets the head circle, and the arc (5 points for steps=4) between them
        assert out == (
            '<polygon points="59.89949493661167,40.10050506338834 '
            "47.56755267271828,47.56755267271828 47.56755267271828,47.56755267271828 "
            "46.56,50.0 47.56755267271828,52.43244732728172 50.0,53.44 "
            "52.43244732728172,52.43244732728172 52.43244732728172,52.43244732728172 "
            '59.89949493661167,40.10050506338834" fill="red" />'
        )

    def test_satellite_renders_expected_svg(self):
        # GIVEN a satellite symbol
        el = symbols.satellite(X, Y, SIZE, ATTRS)

        # WHEN rendering it
        out = el.render()

        # THEN it's a group (rotated -45 degrees) with 2 solar panels, a body,
        # grid lines on each panel, and lines connecting the panels to the body
        assert out == (
            '<g fill="red" transform="rotate(-45, 50, 50)">\n'
            '  <rect x="39.6" y="47.6" height="4.8" width="7.2" />\n'
            '  <rect x="53.2" y="47.6" height="4.8" width="7.2" />\n'
            '  <rect x="47.8" y="48.0" height="4.0" width="4.4" />\n'
            '  <line x1="42.0" y1="47.6" x2="42.0" y2="52.4" />\n'
            '  <line x1="44.4" y1="47.6" x2="44.4" y2="52.4" />\n'
            '  <line x1="39.6" y1="50" x2="46.8" y2="50" />\n'
            '  <line x1="55.6" y1="47.6" x2="55.6" y2="52.4" />\n'
            '  <line x1="58.0" y1="47.6" x2="58.0" y2="52.4" />\n'
            '  <line x1="53.2" y1="50" x2="60.4" y2="50" />\n'
            '  <line x1="46.8" y1="50" x2="47.8" y2="50" />\n'
            '  <line x1="52.2" y1="50" x2="53.2" y2="50" />\n'
            "</g>"
        )


class TestCreate:
    def test_dispatches_to_the_matching_symbol_function(self):
        # GIVEN the same inputs passed directly to a symbol function and via create()
        direct = symbols.circle(X, Y, SIZE, ATTRS)
        dispatched = symbols.create(X, Y, SIZE, "circle", ATTRS)

        # WHEN rendering both
        # THEN they produce identical SVG
        assert direct.render() == dispatched.render()

    def test_none_attrs_defaults_to_empty_dict(self):
        # GIVEN a call to create() with attrs=None
        el = symbols.create(X, Y, SIZE, "circle", None)

        # WHEN rendering it
        out = el.render()

        # THEN no extra attributes are added to the element
        assert out == '<circle cx="50" cy="50" r="10.0" />'
