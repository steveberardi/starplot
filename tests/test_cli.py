import zipfile
from pathlib import Path
from unittest.mock import patch

import pytest

from starplot import cli
from starplot.data.catalogs import (
    BIG_SKY,
    BIG_SKY_MAG9,
    BIG_SKY_MAG11,
    CONSTELLATION_BORDERS,
    CONSTELLATIONS_IAU,
    MILKY_WAY,
    OPEN_NGC,
)
from starplot.svg.fonts import RECOMMENDED_FONTS

FONT_URLS = [props["url"] for props in RECOMMENDED_FONTS.values()]

# maps each zip font's URL to the members it extracts, so the fake download
# below can produce a real, validly-structured zip -- needed so the real
# (unmocked) extraction step in download_fonts() has something valid to
# extract, since download() itself is mocked here (it already has its own
# test coverage in tests/data/test_utils.py)
ZIP_FONT_MEMBERS = {
    props["url"]: props["extract_files"]
    for props in RECOMMENDED_FONTS.values()
    if props["extract_files"]
}


def _fake_download(url, download_path, description="", silent=False):
    download_path = Path(download_path)
    download_path.parent.mkdir(parents=True, exist_ok=True)
    extract_files = ZIP_FONT_MEMBERS.get(url)
    if extract_files:
        with zipfile.ZipFile(download_path, "w") as zf:
            for member in extract_files:
                zf.writestr(member, b"")
    else:
        download_path.touch()


@pytest.fixture
def mock_downloads():
    with (
        patch("starplot.svg.fonts.download", side_effect=_fake_download) as fonts_dl,
        patch(
            "starplot.data.catalogs.download", side_effect=_fake_download
        ) as catalogs_dl,
    ):
        yield fonts_dl, catalogs_dl


def _urls_called(mock_download) -> list:
    return [call.kwargs["url"] for call in mock_download.call_args_list]


class TestCLI:
    def test_unrecognized_command_prints_message(self, monkeypatch, capsys):
        monkeypatch.setattr("sys.argv", ["starplot", "frobnicate"])

        cli.main()

        assert "Unrecognized command: frobnicate" in capsys.readouterr().out

    def test_setup_command_dispatches_to_setup(
        self, monkeypatch, temp_data_path, mock_downloads
    ):
        monkeypatch.setattr("sys.argv", ["starplot", "setup"])
        fonts_dl, _ = mock_downloads

        cli.main()

        assert FONT_URLS[0] in _urls_called(fonts_dl)

    @pytest.mark.parametrize("expected_url", FONT_URLS)
    def test_downloads_font(self, temp_data_path, mock_downloads, expected_url):
        fonts_dl, _ = mock_downloads

        cli.setup([])

        assert expected_url in _urls_called(fonts_dl)

    @pytest.mark.parametrize(
        "expected_url",
        [
            BIG_SKY.url,
            BIG_SKY_MAG9.url,
            BIG_SKY_MAG11.url,
            OPEN_NGC.url,
            CONSTELLATIONS_IAU.url,
            CONSTELLATION_BORDERS.url,
            MILKY_WAY.url,
        ],
    )
    def test_downloads_catalog(self, temp_data_path, mock_downloads, expected_url):
        _, catalogs_dl = mock_downloads

        cli.setup([])

        assert expected_url in _urls_called(catalogs_dl)

    def test_skips_catalogs_that_already_exist_on_a_second_run(
        self, temp_data_path, mock_downloads
    ):
        cli.setup([])

        with patch(
            "starplot.data.catalogs.download", side_effect=_fake_download
        ) as second_run_catalogs_dl:
            cli.setup([])

        assert second_run_catalogs_dl.call_count == 0
