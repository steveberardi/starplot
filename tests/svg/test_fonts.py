import re

import pytest
from fontTools.ttLib import TTFont

from starplot.svg import fonts
from starplot.svg.elements import Text

FONT_FAMILY = "inter"


def _get_font_name(font: TTFont) -> str | None:
    name = font["name"].getDebugName(16) or font["name"].getDebugName(1)
    return name.lower() if name else None


def _get_font_weight(font: TTFont) -> int:
    os2 = font.get("OS/2")
    return os2.usWeightClass if os2 else 400


class TestFindFont:
    def test_exact_match(self):
        # GIVEN a font (family, weight, italic) that exists
        # WHEN resolving that font
        result = fonts.find_font(family=FONT_FAMILY, weight=600, italic=False)

        # THEN it returns that font
        assert _get_font_name(result) == FONT_FAMILY
        assert _get_font_weight(result) == 600

    def test_falls_back_to_normal_weight_of_the_same_family(self):
        # GIVEN a font family that has a normal-weight (400) entry, but not an invalid weight (999)
        # WHEN resolving that font
        result = fonts.find_font(family=FONT_FAMILY, weight=9999, italic=False)

        # THEN it falls back to the same family's normal weight
        assert _get_font_name(result) == FONT_FAMILY
        assert _get_font_weight(result) == 400

    def test_falls_back_to_a_fallback_font_family(self):
        # GIVEN a font family that doesn't exist
        font_family = "totally-nonexistent-font-xyz"

        # WHEN finding the font for that family
        result = fonts.find_font(family=font_family, weight=999, italic=False)

        # THEN it falls back to Liberation Sans (the first fallback font)
        assert _get_font_name(result) == "liberation sans"
        assert _get_font_weight(result) == 400


class TestGetTextHw:
    def test_multiline_height_adds_one_line_height_per_extra_line(self):
        # GIVEN the measured height of a single line of text
        one_line, _, _ = fonts.get_text_hw(
            text="A", font_name=FONT_FAMILY, font_size=24
        )

        # WHEN measuring the same text repeated across 2 and 3 lines
        two_lines, _, _ = fonts.get_text_hw(
            text="A\nA", font_name=FONT_FAMILY, font_size=24
        )
        three_lines, _, _ = fonts.get_text_hw(
            text="A\nA\nA", font_name=FONT_FAMILY, font_size=24
        )

        # THEN each extra line adds exactly one line-height (font_size * 1.13)
        line_height = 24 * 1.13
        assert two_lines == pytest.approx(one_line + line_height)
        assert three_lines == pytest.approx(one_line + 2 * line_height)

    def test_multiline_width_is_the_widest_line_not_the_sum(self):
        # GIVEN a two-line text where the first line is much longer than the second line
        # WHEN measuring its width
        _, width, _ = fonts.get_text_hw(
            text="AAAA\nA", font_name=FONT_FAMILY, font_size=24
        )
        _, longest_line_width, _ = fonts.get_text_hw(
            text="AAAA", font_name=FONT_FAMILY, font_size=24
        )

        # THEN the measured width matches the longest line, not the combined width of both lines
        assert width == longest_line_width

    def test_ascent_is_unaffected_by_additional_lines(self):
        # GIVEN texts with 1, 2, and 3 lines
        # WHEN measuring each
        _, _, ascent1 = fonts.get_text_hw(text="A", font_name=FONT_FAMILY, font_size=24)
        _, _, ascent2 = fonts.get_text_hw(
            text="A\nA", font_name=FONT_FAMILY, font_size=24
        )
        _, _, ascent3 = fonts.get_text_hw(
            text="A\nA\nA", font_name=FONT_FAMILY, font_size=24
        )

        # THEN ascent (how far the first line rises above its baseline) is
        # the same regardless of how many lines follow
        assert ascent1 == ascent2 == ascent3

    def test_stays_in_sync_with_text_render_as_path_line_height(self):
        # GIVEN a two-line Text element rendered as glyph paths
        attrs = {
            "font-family": "Arial, sans-serif",
            "font-weight": "400",
            "font-style": "normal",
            "font-size": "24",
        }
        el = Text(x=0, y=0, text="A\nA", attrs=attrs)
        out = el.render(text_as_path=True)
        ys = [float(m) for m in re.findall(r"translate\([\-\d.]+,([\-\d.]+)\)", out)]

        # WHEN measuring the same text with get_text_hw
        single_h, _, _ = fonts.get_text_hw(
            text="A", font_name=FONT_FAMILY, font_size=24
        )
        double_h, _, _ = fonts.get_text_hw(
            text="A\nA", font_name=FONT_FAMILY, font_size=24
        )

        # THEN the actual y-offset between the two rendered lines matches the
        # height increase get_text_hw attributes to the second line -- these
        # two must stay in sync, since get_text_hw's height is used to build
        # label collision-detection boxes for text rendered this same way
        rendered_line_offset = ys[1] - ys[0]
        assert rendered_line_offset == pytest.approx(double_h - single_h)
