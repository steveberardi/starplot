import imagehash
from PIL import Image


def assert_hash_equal(filename_1, filename_2):
    """Use an image-based hash to determine if the two files are visually similar"""
    hash_1 = imagehash.dhash(Image.open(filename_1))
    hash_2 = imagehash.dhash(Image.open(filename_2))
    assert hash_1 == hash_2
