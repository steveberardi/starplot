import hashlib
import imagehash
from PIL import Image


def assert_hashes_equal(filename_1, filename_2):
    """Use two hash algorithms to assert files are equal"""
    assert_imagehash_equal(filename_1, filename_2)
    # assert_md5_equal(filename_1, filename_2)


def assert_imagehash_equal(filename_1, filename_2):
    """Use an image-based hash to determine if the two files are visually similar"""
    hash_1 = imagehash.dhash(Image.open(filename_1))
    hash_2 = imagehash.dhash(Image.open(filename_2))
    assert hash_1 == hash_2


def assert_md5_equal(filename_1, filename_2):
    """Assert both files have the same MD5 sum"""
    with open(filename_1, "rb") as file1, open(filename_2, "rb") as file2:
        md5_1 = hashlib.md5(file1.read()).hexdigest()
        md5_2 = hashlib.md5(file2.read()).hexdigest()
        assert md5_1 == md5_2


def assert_dhash_equal(filename, expected_hash: str):
    actual_hash = str(imagehash.dhash(Image.open(filename)))
    assert actual_hash == expected_hash


def colorhash(filename):
    return str(imagehash.colorhash(Image.open(filename)))


def dhash(filename):
    return str(imagehash.dhash(Image.open(filename)))
