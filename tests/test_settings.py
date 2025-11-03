from starplot import ZenithPlot, settings, override_settings


def test_settings_language_valid():
    settings.language = "fr"

    p = ZenithPlot()
    assert p.language == "fr"

    settings.language = "en-us"


def test_override_settings():
    assert settings.svg_text_type == "path"
    assert settings.language == "en-us"

    with override_settings(svg_text_type="element", language="zh-cn"):
        assert settings.svg_text_type == "element"
        assert settings.language == "zh-cn"

    assert settings.svg_text_type == "path"
    assert settings.language == "en-us"
