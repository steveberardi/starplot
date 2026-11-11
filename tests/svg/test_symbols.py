from starplot.svg import symbols

X, Y, SIZE = 50, 50, 20
ATTRS = {"fill": "red"}


class TestSymbols:
    def test_circle_renders_expected_svg(self):
        # GIVEN a circle symbol
        element = symbols.circle(X, Y, SIZE, ATTRS)

        # WHEN rendering it
        out = element.render()

        # THEN it's a single <circle> with radius = size / 2
        assert out == '<circle cx="50" cy="50" r="10.0" fill="red" />'

    def test_circle_cross_renders_expected_svg(self):
        # GIVEN a circle-cross symbol
        element = symbols.circle_cross(X, Y, SIZE, ATTRS)

        # WHEN rendering it
        out = element.render()

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
        element = symbols.circle_crosshair(X, Y, SIZE, ATTRS)

        # WHEN rendering it
        out = element.render()

        # THEN it's a group containing a small circle and 4 tick marks, one per side
        assert out == (
            '<g fill="red">\n'
            '  <circle cx="50" cy="50" r="10.0" />\n'
            '  <line x1="50" y1="40.0" x2="50" y2="30.0" />\n'
            '  <line x1="60.0" y1="50" x2="70.0" y2="50" />\n'
            '  <line x1="50" y1="60.0" x2="50" y2="70.0" />\n'
            '  <line x1="40.0" y1="50" x2="30.0" y2="50" />\n'
            "</g>"
        )

    def test_circle_line_renders_expected_svg(self):
        # GIVEN a circle-line symbol
        element = symbols.circle_line(X, Y, SIZE, ATTRS)

        # WHEN rendering it
        out = element.render()

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
        element = symbols.ellipse(X, Y, SIZE, ATTRS)

        # WHEN rendering it
        out = element.render()

        # THEN it's a single <ellipse>, rotated -20 degrees around its center
        assert out == (
            '<ellipse cx="50" cy="50" rx="10.3968" ry="6.2381" '
            'transform="rotate(-20, 50, 50)" fill="red" />'
        )

    def test_square_renders_expected_svg(self):
        # GIVEN a square symbol
        element = symbols.square(X, Y, SIZE, ATTRS)

        # WHEN rendering it
        out = element.render()

        # THEN it's a single <rect> centered on (x, y)
        assert out == '<rect x="40.0" y="40.0" height="20" width="20" fill="red" />'

    def test_triangle_renders_expected_svg(self):
        # GIVEN a triangle symbol
        element = symbols.triangle(X, Y, SIZE, ATTRS)

        # WHEN rendering it
        out = element.render()

        # THEN it's a single <polygon> with 3 points
        assert out == (
            '<polygon points="50.0,41.3397 60.0,58.6603 40.0,58.6603" fill="red" />'
        )

    def test_diamond_renders_expected_svg(self):
        # GIVEN a diamond symbol
        element = symbols.diamond(X, Y, SIZE, ATTRS)

        # WHEN rendering it
        out = element.render()

        # THEN it's a single <polygon> with 4 points (top, right, bottom, left)
        assert out == (
            '<polygon points="50,40.0 60.0,50 50,60.0 40.0,50" fill="red" />'
        )

    def test_star_renders_expected_svg(self):
        # GIVEN a 5-pointed star symbol
        element = symbols.SYMBOL_FUNCTIONS["star"](X, Y, SIZE, ATTRS)

        # WHEN rendering it
        out = element.render()

        # THEN it's a single <polygon> with 10 points (5 outer, 5 inner)
        assert out == (
            '<polygon points="50.0,40.0 52.3511,46.7639 59.5106,46.9098 '
            "53.8042,51.2361 55.8779,58.0902 50.0,54.0 44.1221,58.0902 "
            '46.1958,51.2361 40.4894,46.9098 47.6489,46.7639" fill="red" />'
        )

    def test_star_4_renders_expected_svg(self):
        # GIVEN a 4-pointed star symbol
        element = symbols.SYMBOL_FUNCTIONS["star_4"](X, Y, SIZE, ATTRS)

        # WHEN rendering it
        out = element.render()

        # THEN it's a single <polygon> with 8 points (4 outer, 4 inner)
        assert out == (
            '<polygon points="50.0,40.0 52.8284,47.1716 60.0,50.0 52.8284,52.8284 '
            '50.0,60.0 47.1716,52.8284 40.0,50.0 47.1716,47.1716" fill="red" />'
        )

    def test_star_8_renders_expected_svg(self):
        # GIVEN an 8-pointed star symbol
        element = symbols.SYMBOL_FUNCTIONS["star_8"](X, Y, SIZE, ATTRS)

        # WHEN rendering it
        out = element.render()

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
        element = symbols.plus(X, Y, SIZE, ATTRS)

        # WHEN rendering it
        out = element.render()

        # THEN it's a single <polygon> tracing the 12-point plus-sign outline
        assert out == (
            '<polygon points="47.5,40.0 52.5,40.0 52.5,47.5 60.0,47.5 60.0,52.5 '
            "52.5,52.5 52.5,60.0 47.5,60.0 47.5,52.5 40.0,52.5 40.0,47.5 "
            '47.5,47.5" fill="red" />'
        )

    def test_comet_renders_expected_svg(self):
        # GIVEN a comet symbol, using a small step count for a readable arc
        element = symbols.comet(X, Y, SIZE, ATTRS, steps=4)

        # WHEN rendering it
        out = element.render()

        # THEN it's a single <polygon>: a tip, the two points where the tail
        # meets the head circle, and the arc (5 points for steps=4) between them
        assert out == (
            '<polygon points="60.0,40.00000000000001 '
            "41.51063091594711,51.19539779401368 41.51063091594711,51.19539779401368 "
            "40.0,54.842383439033284 41.51063091594711,58.48936908405289 "
            "45.157616560966716,60.0 48.80460220598632,58.48936908405289 "
            "48.80460220598632,58.48936908405289 "
            '60.0,40.00000000000001" fill="red" />'
        )

    def test_satellite_renders_expected_svg(self):
        # GIVEN a satellite symbol
        element = symbols.satellite(X, Y, SIZE, ATTRS)

        # WHEN rendering it
        out = element.render()

        # THEN it's a group (rotated -45 degrees) with 2 solar panels, a body,
        # grid lines on each panel, and lines connecting the panels to the body
        assert out == (
            '<g fill="red" transform="rotate(-45, 50, 50)">\n'
            '  <rect x="38.5095" y="47.3483" height="5.3033" width="7.955" />\n'
            '  <rect x="53.5355" y="47.3483" height="5.3033" width="7.955" />\n'
            '  <rect x="47.5693" y="47.7903" height="4.4194" width="4.8614" />\n'
            '  <line x1="41.1612" y1="47.3483" x2="41.1612" y2="52.6516" />\n'
            '  <line x1="43.8128" y1="47.3483" x2="43.8128" y2="52.6516" />\n'
            '  <line x1="38.5095" y1="50" x2="46.4645" y2="50" />\n'
            '  <line x1="56.1872" y1="47.3483" x2="56.1872" y2="52.6516" />\n'
            '  <line x1="58.8388" y1="47.3483" x2="58.8388" y2="52.6516" />\n'
            '  <line x1="53.5355" y1="50" x2="61.4905" y2="50" />\n'
            '  <line x1="46.4645" y1="50" x2="47.5693" y2="50" />\n'
            '  <line x1="52.4307" y1="50" x2="53.5355" y2="50" />\n'
            "</g>"
        )

    def test_circle_double_border_renders_expected_svg(self):
        # GIVEN a circle-double-border symbol
        element = symbols.circle_double_border(X, Y, SIZE, ATTRS)

        # WHEN rendering it
        out = element.render()

        # THEN it's a group with a solid center circle and two unfilled rings
        # that inherit stroke styling from the group
        assert out == (
            '<g fill="red">\n'
            '  <circle cx="50" cy="50" r="10.0" stroke-dasharray="none" />\n'
            '  <circle cx="50" cy="50" r="13.888" fill="none" />\n'
            '  <circle cx="50" cy="50" r="17.038" fill="none" />\n'
            "</g>"
        )


class TestExtent:
    def test_symbols_that_fit_in_their_box_have_an_extent_equal_to_size(self):
        for symbol in ("circle", "square", "diamond", "star", "plus", "triangle"):
            assert symbols.extent(symbol, 20) == (20, 20)

    def test_circle_line_extends_horizontally_past_its_circle(self):
        assert symbols.extent("circle_line", 20) == (36, 20)

    def test_circle_crosshair_extends_to_twice_its_circle(self):
        assert symbols.extent("circle_crosshair", 20) == (40, 40)

    def test_circle_double_border_extends_to_its_outer_ring(self):
        width, height = symbols.extent("circle_double_border", 20)
        assert width == height == 20 * 0.8519 * 2

    def test_extent_matches_rendered_symbol(self):
        # the outermost point of the rendered symbol should be half the extent from the center
        crosshair = symbols.circle_crosshair(0, 0, 20, {}).render()
        assert 'x2="20.0"' in crosshair  # right tick ends at half of extent (40 / 2)

        line = symbols.circle_line(0, 0, 20, {}).render()
        assert 'x2="18.0"' in line  # line ends at half of extent (36 / 2)


class TestCircleSize:
    def test_circle_family_symbols_have_a_circle_with_the_size_as_diameter(self):
        # so a circle-based symbol can be swapped for a plain circle without changing its size
        for symbol in (
            "circle",
            "circle_cross",
            "circle_line",
            "circle_crosshair",
            "circle_double_border",
        ):
            element = symbols.create(0, 0, 20, symbol, {})
            circles = element.children if element.children else [element]
            center = next(c for c in circles if c.name == "circle")
            assert center.r == 10.0


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
        element = symbols.create(X, Y, SIZE, "circle", None)

        # WHEN rendering it
        out = element.render()

        # THEN no extra attributes are added to the element
        assert out == '<circle cx="50" cy="50" r="10.0" />'
