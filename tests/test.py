# Pablo Carreira - 08/03/17
import hashlib
import os
from collections import Iterator

from geodata.rasterdata import RasterData
from geodata.srs_utils import create_osr_srs

raster_data = RasterData("tests/data/imagem.tiff")


def test_metadata():
    assert raster_data.block_size == [400, 64]


# noinspection PyProtectedMember
def test_block_list():
    block_list = raster_data._create_blocks_list()
    assert block_list[0] == (0, 0, 400, 64)


def test_create_iterator():
    iterator = raster_data.get_iterator()
    assert isinstance(iterator, Iterator)


def test_clone():
    new_raster = raster_data.clone_empty("tests/data/imagem_clone.tiff")
    assert raster_data == new_raster


def test_write():
    source_raster = RasterData("tests/data/imagem.tiff")
    new_raster = source_raster.clone_empty("tests/data/imagem_copy.tiff")

    # MD5 Hashes precalculados.
    source = "3c0d567c0554030c65927505dc9e9e07"
    clone_empty = "c9adee7d31b4ae5449bdeda811ca1049"
    clone_written = "399abfa3d08f027240fa67cf93a12829"

    # Verifica se a origem não foi alterada.
    with open(source_raster.img_file, 'rb') as source_file:
        md5 = hashlib.md5(source_file.read()).hexdigest()
        assert md5 == source

    # Verifica se o clone está vazio.
    with open(new_raster.img_file, 'rb') as source_file:
        md5 = hashlib.md5(source_file.read()).hexdigest()
        assert md5 == clone_empty

    entrada_red = source_raster.get_iterator(banda=1)
    for indice, red_array in enumerate(entrada_red):
        new_raster.write_block(red_array, indice)

    # Verifica se foi escrito corretamente.
    with open(new_raster.img_file, 'rb') as source_file:
        md5 = hashlib.md5(source_file.read()).hexdigest()
        assert md5 == clone_written


def test_create():
    img_path = os.path.abspath("tests/data/test_image.tif")
    try:
        os.remove(img_path)
    except FileNotFoundError:
        pass
    a = RasterData.create(img_path, 10, 10, 1, 0, 0)
    assert isinstance(a, RasterData)


def test_set_projection():
    img_path = os.path.abspath("tests/data/test_image.tif")
    try:
        os.remove(img_path)
    except FileNotFoundError:
        pass
    source_raster = RasterData.create(img_path, 10, 10, 1, 0, 0)
    source_raster.set_srs(4326)
    srs = create_osr_srs(source_raster.proj)
    assert srs.GetAttrValue("AUTHORITY", 1) == '4326'


def test_read_all():
    source_raster = RasterData("tests/data/imagem.tiff")
    array = source_raster.read_all()
    assert array.shape == (3, 400, 400)


if __name__ == '__main__':
    test_clone()
    # test_read_all()
    # test_set_projection()
    # test_create()
