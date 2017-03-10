# Pablo Carreira - 08/03/17
import hashlib
from collections import Iterator
from rasterdata import RasterData


# raster_data = RasterData("tests/data/imagem.tiff")
raster_data = RasterData("tests/data/imagem2.tif")


def test_metadata():
    meta = raster_data.meta
    assert meta.block_size == [128, 128]


# noinspection PyProtectedMember
def test_block_list():
    block_list = raster_data._create_blocks_list()
    assert block_list[0] == (0, 0, 128, 128)


def test_create_iterator():
    iterator = raster_data.get_iterator()
    assert isinstance(iterator, Iterator)


def test_clone():
    new_raster = raster_data.clone_empty("tests/data/imagem_clone.tiff")
    assert raster_data.meta == new_raster.meta


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


def test_get_coords():
    raise NotImplementedError




if __name__ == '__main__':
    test_write()