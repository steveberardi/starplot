from starplot import ZenithPlot, override_settings, settings


def test_settings_language_valid():
    settings.language = "fr"

    p = ZenithPlot()
    assert p.language == "fr"

    settings.language = "en-us"


def test_override_settings():
    assert settings.svg_text_type == "element"
    assert settings.language == "en-us"

    with override_settings(svg_text_type="path", language="zh-cn"):
        assert settings.svg_text_type == "path"
        assert settings.language == "zh-cn"

    assert settings.svg_text_type == "element"
    assert settings.language == "en-us"
