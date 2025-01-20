from starplot.data import DataFiles, bigsky


from settings import BUILD_PATH, RAW_PATH


def build():
    bigsky.download_if_not_exists(
        filename=str(RAW_PATH / bigsky.BIG_SKY_MAG11_FILENAME),
        url=bigsky.get_url(bigsky.BIG_SKY_VERSION, bigsky.BIG_SKY_MAG11_FILENAME),
        download_path=RAW_PATH,
        download_filename=bigsky.BIG_SKY_MAG11_FILENAME,
        build_file=DataFiles.BIG_SKY_MAG11,
    )


if __name__ == "__main__":
    build()
