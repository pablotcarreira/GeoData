# Pablo Carreira - 12/05/17

from random import Random
# Mirroring and padding
from typing import List, Tuple, Sequence, Iterator

import numpy as np
from rasterdata import RasterData


def create_blocks_coordinates_array(blk_shape, img_shape):
    """Creates an array containing the coordinates (in image pixels) for each block.
    
    Coordinates are: y0, y1, x0, x1
    """
    # Quantos blocos inteiros cabem, quantos pixels sobram
    n_block_rows, resto_pixel_rows = divmod(img_shape[0], blk_shape[0])
    n_block_cols, resto_pixel_cols = divmod(img_shape[1], blk_shape[1])
    # Caso haja um pedaço sobrando do final, inclui mais um bloco.
    if resto_pixel_rows != 0:
        n_block_rows += 1
    if resto_pixel_cols != 0:
        n_block_cols += 1

    # Primeiro, cria a matriz de escrita, o bloco tem o tamanho do blk_shape.
    matriz_de_escrita = np.empty((n_block_rows, n_block_cols, 4), dtype=np.uint16)
    for row_index in range(n_block_rows):
        y0 = row_index * blk_shape[0]
        if row_index + 1 == n_block_rows:  # Last row.
            y1 = img_shape[0]
        else:
            y1 = blk_shape[0] * (row_index + 1)

        for col_index in range(n_block_cols):
            x0 = col_index * blk_shape[1]
            if col_index + 1 == n_block_cols:  # Last column.
                x1 = img_shape[1]
            else:
                x1 = blk_shape[1] * (col_index + 1)

            matriz_de_escrita[row_index][col_index] = [y0, y1, x0, x1]
    return matriz_de_escrita


def generate_array_indices(array: np.ndarray) -> List:
    """Create a list of array indices (i, j) for the first two dimensions of an array.
    The format is different from numpy.indices, numpy indices creates indices like [[i0, i1, in...], [j0, j1, jn, ...]]
    this functions creates [[i0, j0], [i1, j1], [in, jn], ...]
    
    :param array: A numpy array with at least two dimensions.
    :returns: A list of indices (e.g. [[i0, j0], [i1, j1], [in, jn], ...])
    """
    shape = array.shape
    indices = []
    for irow in range(shape[0]):
        for icol in range(shape[1]):
            indices.append((irow, icol))
    return indices


def sample_block_indices(array_indices: Sequence, ratio: float=None, n_samples: int=None, random_seed: str="abc"):
    """Take samples from an array, by a percentage or by a number of samples.
    
    Elements are taken randomly, if you want the same elements to be taken every time, make
    sure that you always use the same seed.
        
    :param array_indices: The list of indices.
    :param ratio: The ration of selected / not selected elements (0 < ratio < 1), if omited, 
    it expects a number of samples to be provided.
    :param n_samples: Number of samples.
    :param random_seed: A string to be used as the seed sor the pseudo random generator.
    """
    if ratio is not None:
        if ratio < 0 or ratio > 1:
            raise ValueError("Ratio must be < 1 and > 0")
        n_blocks = len(array_indices)
        n_selected = int(n_blocks * ratio)
    elif n_samples is not None:
        n_selected = n_samples
    else:
        raise AttributeError("Must provide ratio or n_samples.")

    random_generator = Random(random_seed)
    # Obs: Para otimização, é possível copiar e reproduzir a função sample,
    # separando os selecionados e não selecionados.
    selected = random_generator.sample(array_indices, n_selected)
    # Agora calcula os não selecionados:
    not_selected = []
    for item in array_indices:
        if item not in selected:
            not_selected.append(item)
    return selected, not_selected


MIRROR_TOP = "top"
MIRROR_BOTTOM = "bottom"
MIRROR_LEFT = "left"
MIRROR_RIGHT = "right"


def mirror_block(block_data: np.ndarray, padding: int, direction: str):
    """Mirrors a portion of a block by a given padding.
        
    :param block_data: A image block. 
    :param padding: The size of the mirroring in px.
    :param direction: top, bottom, left, right.
    :returns: The block added of the mirror padding. 
    """
    error_message = "Padding bigger than block dimension."

    if direction == MIRROR_TOP:
        if padding > block_data.shape[0]:
            raise ValueError(error_message)
        mirrored = np.flipud(block_data[:padding])
        return np.vstack((mirrored, block_data))
    elif direction == MIRROR_BOTTOM:
        if padding > block_data.shape[0]:
            raise ValueError(error_message)
        mirrored = np.flipud(block_data[-padding:])
        return np.vstack((block_data, mirrored))
    elif direction == MIRROR_LEFT:
        if padding > block_data.shape[1]:
            raise ValueError(error_message)
        mirrored = np.fliplr(block_data[:, :padding])
        return np.hstack((mirrored, block_data))
    elif direction == MIRROR_RIGHT:
        if padding > block_data.shape[1]:
            raise ValueError(error_message)
        mirrored = np.fliplr(block_data[:, -padding:])
        return np.hstack((block_data, mirrored))
    else:
        AttributeError('Direction must be one of [top, bottom, left, right] got: {}.'.format(direction))


def create_block_iterator(raster_data: RasterData,
                          block_coordinates: np.ndarray,
                          block_indices: List[Tuple[int, int]],
                          block_shape: Sequence[int],
                          padding: int,
                          ) -> Iterator[Tuple[np.ndarray, List, List]]:
    """Creates a generator that yelds image blocks with an extra padding around it.
   
    :param raster_data: The image RasterData.
    :param a_block_coordinates: The coordinates of the image blocks.
    :param block_indices: The indices of the blocks, passing the indices allows to iterate over specific blocks.
    :param block_shape: The shape of the blocks without the padding.
    :param padding: The size in pixels of the padding.     
    :returns: The block data (with padding), the valid data region, the block coordinates at the image.
    """
    img_shape = raster_data.meta.shape

    # Quantos blocos inteiros cabem, quantos pixels sobram
    n_block_rows, resto_pixel_rows = divmod(img_shape[0], block_shape[0])
    n_block_cols, resto_pixel_cols = divmod(img_shape[1], block_shape[1])

    # Number of pixels needed to complete the last row and the last column.
    dif_last_row = block_shape[0] - resto_pixel_rows
    dif_last_col = block_shape[1] - resto_pixel_cols
    # If those number are equal to the block size, this means that nothing is missing.
    if dif_last_row == block_shape[0]:
        dif_last_row = 0
    if dif_last_col == block_shape[1]:
        dif_last_col = 0
    # Caso haja um pedaço sobrando do final, inclui mais um bloco.
    # FIXME: Muito deselegante, pegar o numero de blocos do shape do block_coordinates.
    if resto_pixel_rows != 0:
        n_block_rows += 1
    if resto_pixel_cols != 0:
        n_block_cols += 1

    double_padding = 2 * padding  # Padding on both sizes is equal to...
    expected_shape = (block_shape[0] + double_padding, block_shape[1] + double_padding)

    for index in block_indices:
        # Position of the data that is valid for write (excludes padding and block completion).
        # [vy0, vy1, vx0, vx1]
        block_valid_data = [0, block_shape[0], 0, block_shape[1]]

        row_index, col_index = index
        original_block_coordinates = block_coordinates[row_index, col_index]
        a_block_coordinates = block_coordinates[row_index, col_index]

        if row_index + 1 == n_block_rows:
            # Ultima linha. Completa o que falta e pega o padding dos blocos de cima.
            y0, y1, x0, x1 = a_block_coordinates
            a_block_coordinates = [y0 - dif_last_row - padding, y1, x0, x1]
            block_valid_data[0] = dif_last_row

        elif row_index + 1 != n_block_rows and row_index != 0:
            # Não é ultima linha, nem a primeira, pega o padding do bloco de cima e de baixo.
            y0, y1, x0, x1 = a_block_coordinates
            a_block_coordinates = [y0 - padding, y1 + padding, x0, x1]

        if col_index + 1 == n_block_cols:
            # Ultima coluna, completa e pega o padding do bloco da esquerda.
            y0, y1, x0, x1 = a_block_coordinates
            a_block_coordinates = [y0, y1, x0 - dif_last_col - padding, x1]
            block_valid_data[2] = dif_last_col


        elif col_index + 1 != n_block_cols and col_index != 0:
            # Nem a ultima nem a primeira coluna. Pega o padding do bloco da direita e da esquerda.
            y0, y1, x0, x1 = a_block_coordinates
            a_block_coordinates = [y0, y1, x0 - padding, x1 + padding]

        if row_index == 0:
            # Primeira linha, adiciona o padding do bloco de baixo.
            y0, y1, x0, x1 = a_block_coordinates
            a_block_coordinates = [y0, y1 + padding, x0, x1]

        if col_index == 0:
            # Primeira coluna, adiciona o padding do bloco da direita.
            y0, y1, x0, x1 = a_block_coordinates
            a_block_coordinates = [y0, y1, x0, x1 + padding]

        # Agora pega o bloco.
        block_data = raster_data.read_block_by_coordinates(*a_block_coordinates)

        # E fazemos os espelhamentos para os casos especificos.
        if row_index == 0:  # 1a linha. Espelha para cima.
            block_data = mirror_block(block_data, padding, MIRROR_TOP)
        elif row_index + 1 == n_block_rows:  # Ultima linha. Espelha para baixo.
            block_data = mirror_block(block_data, padding, MIRROR_BOTTOM)

        if col_index == 0:  # 1a coluna. Espelha para a esquerda.
            block_data = mirror_block(block_data, padding, MIRROR_LEFT)
        elif col_index + 1 == n_block_cols:  # Ultima coluna. Espelha para a direita.
            block_data = mirror_block(block_data, padding, MIRROR_RIGHT)


        if block_data.shape[:2] != expected_shape:
            raise RuntimeError("""
                Foi gerado um bloco de tamanho incorreto. 
                Ver bug referente ao ultimo bloco ser menor que o padding.""")

        print(a_block_coordinates == original_block_coordinates)
        yield block_data, block_valid_data, original_block_coordinates


def fake_neural_net_padding_crop(image, padding):
    return image[padding:-padding, padding:-padding]


def cut_valid_data(block_data, valid_region):
    """Cuts a region of the block."""
    # FIXME: Poderia ser renomeado para ser um crop genérico.
    return block_data[valid_region[0]:valid_region[1], valid_region[2]:valid_region[3]]


def write_block(output_raster_data: RasterData, block_data: np.ndarray, block_position: Sequence):
    # Cast to integers.
    block_position = [int(p) for p in block_position]

    # loop para escrever todas as bandas.
    for b in range(output_raster_data.meta.n_bandas):
        band_data = block_data[...,b]
        # FIXME: Acredito que o GDAL utilize column first.
        output_raster_data.gdal_dataset.GetRasterBand(b + 1).WriteArray(band_data, block_position[2], block_position[0])
    output_raster_data.gdal_dataset.FlushCache()


if __name__ == '__main__':
    # nn_output = (388, 388)  # Tamanho da saída da rede neural, também o tamanho do bloco de escrita.
    # nn_input = (572, 572)  # Tamanho da entrada na rede neural (tamanho saída + padding)

    nn_output = (32, 32)
    nn_input = (50, 50)
    img_padding = 15

    # Pega o resterdata e executa os passos até o iterator (1-5)
    img = RasterData("/home/pablo/Desktop/geo_array/_dev/samples/Paprika-ilustr.tiff")  # 1
    img.meta.block_size = nn_output
    matriz_de_coordenadas = create_blocks_coordinates_array(blk_shape=nn_output, img_shape=img.meta.shape)  # 2
    indices_matriz = generate_array_indices(matriz_de_coordenadas)  # 3
    indices_selected, indices_not_selected = sample_block_indices(indices_matriz, 0.6)  # 4
    block_iterator_selected = create_block_iterator(img, matriz_de_coordenadas, img_padding, indices_selected)  # 5
    block_iterator_not_selected = create_block_iterator(img, matriz_de_coordenadas, img_padding, indices_not_selected)

    # Cria as imagens de saída (7)
    saida_selecionado = img.clone_empty("/home/pablo/Desktop/geo_array/_dev/out/selecionado.tif")
    saida_nao_selecionado = img.clone_empty("/home/pablo/Desktop/geo_array/_dev/out/nao_selecionado.tif")

    # Roda os iterators e escreve (8-10)
    for bloco, valid_data, block_position in block_iterator_selected:
        saida = fake_neural_net_padding_crop(bloco, img_padding)
        saida = cut_valid_data(saida, valid_data)
        write_block(img, saida, block_position)

    for bloco, valid_data, block_position in block_iterator_not_selected:
        saida = fake_neural_net_padding_crop(bloco, img_padding)
        saida = cut_valid_data(saida, valid_data)
        write_block(img, saida, block_position)
