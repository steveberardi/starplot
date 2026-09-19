import tarfile

from starplot.config import settings
from starplot.data.utils import download

FONTS_PATH = settings.data_path / "fonts"
FONTS_PATH.mkdir(parents=True, exist_ok=True)

# Noto Sans CJK SC
noto_sans_sc_urls = [
    "https://github.com/life888888/cjk-fonts-ttf/releases/download/v0.1.0/NotoSansCJKsc-Regular.ttf",
    "https://github.com/life888888/cjk-fonts-ttf/releases/download/v0.1.0/NotoSansCJKsc-Bold.ttf",
    "https://github.com/life888888/cjk-fonts-ttf/releases/download/v0.1.0/NotoSansCJKsc-Italic.ttf",
]
path = FONTS_PATH / "noto-sans-cjk-sc"
path.mkdir(parents=True, exist_ok=True)
for noto_sans_url in noto_sans_sc_urls:
    filename = noto_sans_url.split("/")[-1]
    download(
        url=noto_sans_url,
        download_path=path / filename,
        description=f"Font ({filename})",
    )

# Liberation Sans
liberation_sans_url = "https://github.com/liberationfonts/liberation-fonts/files/7261482/liberation-fonts-ttf-2.1.5.tar.gz"
path = FONTS_PATH / "liberation-sans"
path.mkdir(parents=True, exist_ok=True)
filename = liberation_sans_url.split("/")[-1]
download_path = path / filename
download(
    url=liberation_sans_url,
    download_path=download_path,
    description=f"Font ({filename})",
)
with tarfile.open(download_path, "r:gz") as tar:
    tar.extractall(path=path)
