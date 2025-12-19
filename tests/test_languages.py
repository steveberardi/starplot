import pytest


from starplot import DSO, Star, Constellation, override_settings


class TestLanguages:
    @pytest.mark.parametrize(
        "star_hip_id, language, expected_value",
        [
            (11767, "en-us", "Polaris"),
            (11767, "fr", "Étoile Polaire"),
            (11767, "zh-cn", "北极星"),
            (11767, "lt", "Šiaurinė žvaigždė (Polaris)"),
            (11767, "fa", "ستاره قطبی"),
        ],
    )
    def test_star_name(self, star_hip_id, language, expected_value):
        with override_settings(language=language):
            star = Star.get(hip=star_hip_id)
            assert star.name == expected_value

    @pytest.mark.parametrize(
        "constellation_id, language, expected_value",
        [
            ("cma", "en-us", "Canis Major"),
            ("cma", "fr", "Grand chien"),
            ("cma", "zh-cn", "大犬"),
            ("cma", "lt", "Didysis Šuo"),
            ("cma", "fa", "سگ بزرگ"),
        ],
    )
    def test_constellation_name(self, constellation_id, language, expected_value):
        with override_settings(language=language):
            constellation = Constellation.get(iau_id=constellation_id)
            assert constellation.name == expected_value

    @pytest.mark.parametrize(
        "messier, language, expected_value",
        [
            ("11", "en-us", "Wild Duck Cluster"),
            ("11", "fr", "Amas du Canard sauvage"),
            ("11", "zh-cn", "野鸭星团"),
            ("11", "lt", "Laukinės anties spiečius (M11)"),
            ("11", "fa", "خوشه اردک وحشی"),
        ],
    )
    def test_dso_name(self, messier, language, expected_value):
        with override_settings(language=language):
            dso = DSO.get(m=messier)
            assert dso.common_names == [expected_value]
