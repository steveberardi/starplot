from starplot import settings, ZenithPlot


def test_settings_language_valid():
    settings.language = "fr"

    p = ZenithPlot()
    assert p.language == "fr"
