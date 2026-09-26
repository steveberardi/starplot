from unittest.mock import patch

import pytest

from starplot.data.utils import download


class FakeResponse:
    """Stands in for a `requests.Response` from an external URL."""

    def __init__(self, content: bytes, content_length: str | None):
        self.content = content
        self.headers = {}
        if content_length is not None:
            self.headers["content-length"] = content_length

    def iter_content(self, chunk_size):
        for i in range(0, len(self.content), chunk_size):
            yield self.content[i : i + chunk_size]


def _patch_get(response: FakeResponse):
    return patch("starplot.data.utils.requests.get", return_value=response)


class TestDownload:
    def test_writes_full_content_when_no_content_length_header(self, tmp_path):
        content = b"hello world"
        download_path = tmp_path / "out.bin"

        with _patch_get(FakeResponse(content, content_length=None)):
            download("https://example.com/file.bin", download_path, silent=True)

        assert download_path.read_bytes() == content

    def test_streams_and_writes_all_chunks_when_content_length_present(self, tmp_path):
        # bigger than the function's chunk_size (4096) so it spans multiple
        # chunks, plus a final partial chunk
        content = bytes(range(256)) * 50  # 12800 bytes
        download_path = tmp_path / "out.bin"

        with _patch_get(FakeResponse(content, content_length=str(len(content)))):
            download("https://example.com/file.bin", download_path, silent=True)

        assert download_path.read_bytes() == content

    def test_passes_url_and_stream_true_to_requests_get(self, tmp_path):
        download_path = tmp_path / "out.bin"
        url = "https://example.com/file.bin"

        with _patch_get(FakeResponse(b"data", content_length=None)) as mock_get:
            download(url, download_path, silent=True)

        mock_get.assert_called_once_with(url, stream=True)

    @pytest.mark.parametrize("content_length", [None, "4"])
    def test_prints_downloading_message_with_description(
        self, tmp_path, capsys, content_length
    ):
        download_path = tmp_path / "out.bin"

        with _patch_get(FakeResponse(b"data", content_length=content_length)):
            download(
                "https://example.com/file.bin",
                download_path,
                description="Test File",
                silent=False,
            )

        assert "Downloading Test File..." in capsys.readouterr().out

    def test_content_length_present_prints_complete_message(self, tmp_path, capsys):
        content = b"data"
        download_path = tmp_path / "out.bin"

        with _patch_get(FakeResponse(content, content_length=str(len(content)))):
            download("https://example.com/file.bin", download_path, silent=False)

        assert "Download complete!" in capsys.readouterr().out

    def test_progress_bar_reaches_full_completion(self, tmp_path, capsys):
        content = b"x" * 10000
        download_path = tmp_path / "out.bin"

        with _patch_get(FakeResponse(content, content_length=str(len(content)))):
            download("https://example.com/file.bin", download_path, silent=False)

        out = capsys.readouterr().out
        assert "[{}]".format("=" * 25) in out

    def test_silent_suppresses_all_output(self, tmp_path, capsys):
        content = b"data"
        download_path = tmp_path / "out.bin"

        with _patch_get(FakeResponse(content, content_length=str(len(content)))):
            download("https://example.com/file.bin", download_path, silent=True)

        assert capsys.readouterr().out == ""

    def test_silent_suppresses_output_with_no_content_length(self, tmp_path, capsys):
        download_path = tmp_path / "out.bin"

        with _patch_get(FakeResponse(b"data", content_length=None)):
            download("https://example.com/file.bin", download_path, silent=True)

        assert capsys.readouterr().out == ""
