# Pablo Carreira - 15/05/17


import numpy as np
from _dev.experimentos import mirror_block, MIRROR_TOP, MIRROR_BOTTOM, MIRROR_LEFT, MIRROR_RIGHT, \
    create_blocks_coordinates_array, generate_array_indices, sample_block_indices, create_block_iterator, \
    fake_neural_net_padding_crop, cut_valid_data, write_block
from rasterdata import RasterData
import matplotlib.pyplot as plt

block_data = np.asarray([
    [1, 1, 1, 1, 1, 1, 1],
    [2, 2, 2, 2, 2, 2, 2],
    [3, 3, 3, 3, 3, 3, 3],
    [1, 2, 3, 4, 5, 6, 7],
    [5, 5, 5, 5, 5, 5, 5],
    [6, 6, 6, 6, 6, 6, 6],
    [7, 7, 7, 7, 7, 7, 7]
], np.uint8)


def mirroring():
    padding = 3
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


def test_fake_neural_net():
    result = fake_neural_net_padding_crop(block_data, padding=2)
    expected = [[3, 3, 3],
                [3, 4, 5],
                [5, 5, 5]]
    assert result.toarray() == expected




def test_create_block_iterator():
    blk_shape = (32, 32)
    img_padding = 10
    img = RasterData("/home/pablo/Desktop/geo_array/_dev/samples/Paprika-ilustr.tiff")  # 1
    matriz_de_coordenadas = create_blocks_coordinates_array(blk_shape=blk_shape, img_shape=img.meta.shape)  # 2
    indices = generate_array_indices(matriz_de_coordenadas)  # 3
    # Todo: Filtrar apenas parte da imagem.

    indices_selected, indices_not_selected = sample_block_indices(indices, 0.6)  # 4
    indices_sim_nao = indices[0::2]



    blk_iter = create_block_iterator(img, matriz_de_coordenadas, indices_sim_nao, blk_shape, img_padding)  # 5
    img_out = img.clone_empty("/home/pablo/Desktop/geo_array/_dev/out/teste.tiff")

    rodada = 1
    for img_blk, valid_data, blk_coords in blk_iter:
        print("Rodada: ", rodada)
        blk_shape = img_blk.shape

        # Plota a imagem.
        if rodada == 22220:
            plt.imshow(img_blk)
            plt.gray()
            plt.show()

        if blk_shape != (52, 52, 3):
            raise RuntimeError("""
                Foi gerado um bloco de tamanho incorreto. 
                Ver bug referente ao ultimo bloco ser menor que o padding.""")

        saida = fake_neural_net_padding_crop(img_blk, img_padding)

        # plt.imshow(saida)
        # plt.gray()
        # plt.show()

        saida = cut_valid_data(img_blk, valid_data)
        write_block(img_out, saida, blk_coords)
        rodada += 1


if __name__ == '__main__':
    # mirroring()
    # test_create_blocks_coordinates_array()
    # test_generate_array_indices()
    # test_sample_block_indices()
    # test_fake_neural_net()
    test_create_block_iterator()

