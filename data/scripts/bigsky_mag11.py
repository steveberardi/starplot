from starplot.data import DataFiles, bigsky


from settings import BUILD_PATH

bigsky.download(
    url=bigsky.get_url(bigsky.BIG_SKY_VERSION, bigsky.BIG_SKY_MAG11_FILENAME),
    download_path=BUILD_PATH,
    download_filename = bigsky.BIG_SKY_MAG11_FILENAME,
    build_file= DataFiles.BIG_SKY_MAG11,
)
