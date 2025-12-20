from starplot.data import DataFiles, utils, bigsky


from data_settings import RAW_PATH


def build():
    full_download_path = RAW_PATH / bigsky.BIG_SKY_FILENAME

    if not bigsky.exists(full_download_path):
        utils.download(
            url=bigsky.get_url(bigsky.BIG_SKY_VERSION, bigsky.BIG_SKY_FILENAME),
            download_path=full_download_path,
            description="Big Sky Star Catalog",
        )

    bigsky.build(
        source_path=full_download_path,
        destination_path="data/build/bigsky-11.parquet",
        limiting_magnitude=11,
    )


if __name__ == "__main__":
    build()
