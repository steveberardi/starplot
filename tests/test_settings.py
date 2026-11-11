import pytest

from starplot import ZenithPlot, settings


def test_settings_language_valid():
    settings.language = "fr"

    p = ZenithPlot()
    assert p.language == "fr"

    settings.language = "en-us"


def test_settings_context_manager():
    assert settings.svg_text_type == "element"
    assert settings.language == "en-us"

    with settings(svg_text_type="path", language="zh-cn"):
        assert settings.svg_text_type == "path"
        assert settings.language == "zh-cn"

    assert settings.svg_text_type == "element"
    assert settings.language == "en-us"


def test_settings_context_manager_nested():
    with settings(language="de"):
        with settings(language="fr", precision=0):
            assert settings.language == "fr"
            assert settings.precision == 0

        assert settings.language == "de"
        assert settings.precision == 4

    assert settings.language == "en-us"


def test_settings_context_manager_restores_on_error():
    try:
        with settings(language="de"):
            raise ValueError
    except ValueError:
        pass

    assert settings.language == "en-us"


def test_settings_context_manager_unknown_setting():
    with pytest.raises(AttributeError):
        settings(not_a_setting=1)
