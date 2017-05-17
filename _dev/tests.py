# Pablo Carreira - 15/05/17


import numpy as np
from _dev.experimentos import mirror_block, MIRROR_TOP, MIRROR_BOTTOM, MIRROR_LEFT, MIRROR_RIGHT, \
    create_blocks_coordinates_array, generate_array_indices, sample_block_indices, create_block_iterator
from rasterdata import RasterData


def mirroring():
    padding = 3
    block_data = np.asarray([
        [1, 1, 1, 1, 1, 1, 1],
        [2, 2, 2, 2, 2, 2, 2],
        [3, 3, 3, 3, 3, 3, 3],
        [1, 2, 3, 4, 5, 6, 7],
        [5, 5, 5, 5, 5, 5, 5],
        [6, 6, 6, 6, 6, 6, 6],
        [7, 7, 7, 7, 7, 7, 7]
    ], np.uint8)
    tblr = [mirror_block(block_data, padding, MIRROR_TOP),
            mirror_block(block_data, padding, MIRROR_BOTTOM),
            mirror_block(block_data, padding, MIRROR_LEFT),
            mirror_block(block_data, padding, MIRROR_RIGHT)]
    resultados_experados = [
        [[3, 3, 3, 3, 3, 3, 3],
         [2, 2, 2, 2, 2, 2, 2],
         [1, 1, 1, 1, 1, 1, 1],
         [1, 1, 1, 1, 1, 1, 1],
         [2, 2, 2, 2, 2, 2, 2],
         [3, 3, 3, 3, 3, 3, 3],
         [1, 2, 3, 4, 5, 6, 7],
         [5, 5, 5, 5, 5, 5, 5],
         [6, 6, 6, 6, 6, 6, 6],
         [7, 7, 7, 7, 7, 7, 7]],
        [[1, 1, 1, 1, 1, 1, 1],
         [2, 2, 2, 2, 2, 2, 2],
         [3, 3, 3, 3, 3, 3, 3],
         [1, 2, 3, 4, 5, 6, 7],
         [5, 5, 5, 5, 5, 5, 5],
         [6, 6, 6, 6, 6, 6, 6],
         [7, 7, 7, 7, 7, 7, 7],
         [7, 7, 7, 7, 7, 7, 7],
         [6, 6, 6, 6, 6, 6, 6],
         [5, 5, 5, 5, 5, 5, 5]],
        [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
         [2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
         [3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
         [3, 2, 1, 1, 2, 3, 4, 5, 6, 7],
         [5, 5, 5, 5, 5, 5, 5, 5, 5, 5],
         [6, 6, 6, 6, 6, 6, 6, 6, 6, 6],
         [7, 7, 7, 7, 7, 7, 7, 7, 7, 7]],
        [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
         [2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
         [3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
         [1, 2, 3, 4, 5, 6, 7, 7, 6, 5],
         [5, 5, 5, 5, 5, 5, 5, 5, 5, 5],
         [6, 6, 6, 6, 6, 6, 6, 6, 6, 6],
         [7, 7, 7, 7, 7, 7, 7, 7, 7, 7]]]
    for resultado, experado in zip(tblr, resultados_experados):
        assert resultado.tolist() == experado


def test_create_blocks_coordinates_array():
    coords_array = create_blocks_coordinates_array(blk_shape=(3, 3), img_shape=(5, 5))
    expected = [[[0, 3, 0, 3], [0, 3, 3, 5]], [[3, 5, 0, 3], [3, 5, 3, 5]]]
    # print(coords_array)
    assert coords_array.tolist() == expected


def test_generate_array_indices():
    coords_array = np.array([[[0, 3, 0, 3], [0, 3, 3, 5]], [[3, 5, 0, 3], [3, 5, 3, 5]]])
    indices = generate_array_indices(coords_array)
    print(indices)


def test_sample_block_indices():
    elements = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]
    selected, not_selected = sample_block_indices(array_indices=elements, ratio=0.3)
    assert selected == ['I', 'H', 'F']
    assert not_selected == ['A', 'B', 'C', 'D', 'E', 'G', 'J']
    # should raise exceptions:
    sample_block_indices(array_indices=elements, ratio=0)
    sample_block_indices(array_indices=elements, ratio=-1)
    sample_block_indices(array_indices=elements, ratio=1)
    sample_block_indices(array_indices=elements, ratio=1.1)


def test_create_block_iterator():
    blk_shape = (32, 32)
    img_padding = 15
    img = RasterData("/home/pablo/Desktop/geo_array/_dev/samples/Paprika-ilustr.tiff")  # 1
    matriz_de_coordenadas = create_blocks_coordinates_array(blk_shape=blk_shape, img_shape=img.meta.shape)  # 2
    indices = generate_array_indices(matriz_de_coordenadas)  # 3
    blk_iter = create_block_iterator(img, matriz_de_coordenadas, img_padding, indices)  # 5





if __name__ == '__main__':
    # mirroring()
    # test_create_blocks_coordinates_array()
    # test_generate_array_indices()
    test_sample_block_indices()

