from starplot.svg.elements import (
    SVG,
    Circle,
    Element,
    Group,
    Polygon,
    RadialGradient,
    Rectangle,
    Stop,
    Text,
)

def test_render_self_closing_tag_without_children():
    # GIVEN an element with no children
    el = Rectangle(x=1, y=2, height=3, width=4)

    # WHEN rendering it
    result = el.render()

    # THEN it renders as a self-closing tag
    assert result == '<rect x="1" y="2" height="3" width="4" />'


def test_render_includes_id_first():
    # GIVEN an element with an id
    el = Rectangle(id="my-rect", x=1, y=2, height=3, width=4)

    # WHEN rendering it
    result = el.render()

    # THEN the id attribute appears first, before the element's own props
    assert result == '<rect id="my-rect" x="1" y="2" height="3" width="4" />'


def test_render_omits_none_props():
    # GIVEN an element whose optional props (x/y) are left as their None default
    el = SVG(height=100, width=200)

    # WHEN rendering it
    out = el.render()

    # THEN those props are omitted entirely, while set props still appear
    assert ' x="' not in out
    assert ' y="' not in out
    assert 'viewBox="0 0 200 100"' in out


def test_render_attrs_override_props_and_append_new_keys():
    # GIVEN an element whose attrs dict overlaps one prop (x) and adds a new one (fill)
    el = Rectangle(x=1, y=2, height=3, width=4, attrs={"fill": "red", "x": "99"})

    # WHEN rendering it
    out = el.render()

    # THEN attrs wins over the prop value for the shared key
    #  AND the new key is appended after the props
    assert out == '<rect x="99" y="2" height="3" width="4" fill="red" />'


def test_render_uses_render_prop_override():
    # GIVEN an element whose prop has a custom render_<prop> method (points)
    el = Polygon(points=[(0, 0), (1, 1), (2, 0)])

    # WHEN rendering it
    result = el.render()

    # THEN the custom renderer is used instead of a plain str() of the prop
    assert result == '<polygon points="0,0 1,1 2,0" />'


def test_render_offset_and_percentage_overrides():
    # GIVEN a gradient Stop and a RadialGradient, whose props render as percentages
    stop = Stop(offset=0.25, attrs={"stop-color": "red"})
    gradient = RadialGradient(id="g1", cx=0.5, cy=0.5, r=0.5)

    # WHEN rendering each
    stop_out = stop.render()
    gradient_out = gradient.render()

    # THEN their fractional props are rendered as percentages
    assert stop_out == '<stop offset="25%" stop-color="red" />'
    assert gradient_out == '<radialGradient id="g1" cx="50%" cy="50%" r="50%" />'


def test_render_nested_children_are_indented():
    # GIVEN a group containing one child element
    child = Rectangle(x=0, y=0, height=1, width=1)
    group = Group(children=[child])

    # WHEN rendering the group
    result = group.render()

    # THEN the child is rendered on its own line, indented one level deeper
    assert result == '<g>\n  <rect x="0" y="0" height="1" width="1" />\n</g>'


def test_render_empty_group_is_self_closing():
    # GIVEN a group with no children
    group = Group()

    # WHEN rendering it
    result = group.render()

    # THEN it renders as a self-closing tag, just like any other childless element
    assert result == "<g />"


def test_render_group_indent_propagates_to_children():
    # GIVEN a group with one child, rendered starting at a non-zero indent
    child = Circle(cx=1, cy=2, r=3)
    group = Group(children=[child])

    # WHEN rendering the group at indent=2
    out = group.render(indent=2)

    # THEN both the group and its child are indented relative to that base
    lines = out.split("\n")
    assert lines[0] == "    <g>"
    assert lines[1] == '      <circle cx="1" cy="2" r="3" />'
    assert lines[2] == "    </g>"


def test_render_text_element_is_not_self_closing():
    # GIVEN a Text element with no children
    el = Text(x=10, y=20, text="hello", attrs={"font-size": "12"})

    # WHEN rendering it
    result = el.render()

    # THEN it still renders with an open/close tag pair (never self-closing),
    # with its text as the tag's inner content
    assert result == '<text x="10" y="20" font-size="12">hello</text>'


def test_render_escapes_special_characters_in_text_and_attrs():
    # GIVEN a Text element whose text and attrs contain XML special characters
    el = Text(
        x=10,
        y=20,
        text='M31 & "friends" <great>',
        attrs={"data-note": 'a "quoted" & <weird> value'},
    )

    # WHEN rendering it
    out = el.render()

    # THEN &, <, > are escaped everywhere, and " is additionally escaped
    # within attribute values (where it would otherwise break the markup)
    assert (
        out == '<text x="10" y="20" data-note="a &quot;quoted&quot; '
        '&amp; &lt;weird&gt; value">M31 &amp; "friends" &lt;great&gt;</text>'
    )


def test_render_dispatches_to_module_function():
    # GIVEN an element
    el = Rectangle(x=1, y=2, height=3, width=4)

    # WHEN rendering it via the Element.render() method vs. the module-level function
    # THEN both produce identical output
    assert Element.render(el) == el.render()


def test_render_as_path_produces_path_elements_instead_of_text():
    # GIVEN a Text element with font attrs needed to resolve a real font
    el = Text(
        x=0,
        y=0,
        text="A",
        attrs={
            "font-family": "Arial, sans-serif",
            "font-weight": "400",
            "font-style": "normal",
            "font-size": "24",
            "fill": "#000000",
        },
    )

    # WHEN rendering it with text_as_path=True
    out = el.render(text_as_path=True)

    # THEN it renders as <path> glyph outlines instead of a <text> element
    assert "<path" in out
    assert "<text" not in out
    assert 'fill="#000000"' in out


def test_render_as_path_multiline_resets_cursor_and_advances_y():
    # GIVEN a single-line and an equivalent two-line ("A\nA") Text element
    single_line = Text(
        x=0,
        y=0,
        text="A",
        attrs={
            "font-family": "Arial, sans-serif",
            "font-weight": "400",
            "font-style": "normal",
            "font-size": "24",
        },
    )
    two_lines = Text(
        x=0,
        y=0,
        text="A\nA",
        attrs={
            "font-family": "Arial, sans-serif",
            "font-weight": "400",
            "font-style": "normal",
            "font-size": "24",
        },
    )

    # WHEN rendering both with text_as_path=True
    single_out = single_line.render(text_as_path=True)
    double_out = two_lines.render(text_as_path=True)

    # THEN the two-line text produces exactly twice as many path elements,
    # since "\n" resets the cursor back to the left and advances y instead
    # of continuing to advance the cursor rightward
    assert double_out.count("<path") == 2 * single_out.count("<path")


def test_render_as_path_stroke_creates_separate_stroke_and_fill_groups():
    # GIVEN a Text element with a stroke set
    el = Text(
        id="label",
        x=0,
        y=0,
        text="A",
        attrs={
            "font-family": "Arial, sans-serif",
            "font-weight": "400",
            "font-style": "normal",
            "font-size": "24",
            "stroke": "#fff",
            "stroke-width": 2,
            "stroke-opacity": 1,
        },
    )

    # WHEN rendering it with text_as_path=True
    out = el.render(text_as_path=True)

    # THEN the glyph paths are duplicated into separate stroke and fill groups
    assert 'id="label-stroke"' in out
    assert 'id="label-fill"' in out
