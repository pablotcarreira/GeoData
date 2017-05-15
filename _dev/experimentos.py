# Pablo Carreira - 12/05/17

# Mirroring and padding
from typing import List, Tuple, Generator
import numpy as np
from rasterdata import RasterData


def create_blocks_coordinates_array(blk_shape, img_shape):
    # Quantos blocos inteiros cabem, quantos pixels sobram
    n_block_rows, resto_pixel_rows = divmod(img_shape[0], blk_shape[0])
    n_block_cols, resto_pixel_cols = divmod(img_shape[1], blk_shape[1])

    # Quantos blocos cabem, contando os pedacos no final.
    n_block_rows += 1
    n_block_cols += 1

    # Primeiro, cria a matriz de escrita, o bloco tem o tamanho do blk_shape.
    matriz_de_escrita = np.empty((n_block_rows, n_block_cols, 2), dtype=np.uint16)
    for row_index in range(n_block_rows):
        if row_index + 1 == n_block_rows:  # Last row.
            valid_y = img_shape[0] - row_index * blk_shape[0]
        else:
            valid_y = blk_shape[0]
        y_offset = row_index * blk_shape[0]
        for col_index in range(n_block_cols):
            if col_index + 1 == n_block_cols:  # Last column.
                valid_x = img_shape[1] - col_index * blk_shape[1]
            else:
                valid_x = blk_shape[1]
            x_offset = col_index * blk_shape[1]
            matriz_de_escrita[row_index][col_index] = [y_offset, valid_y, x_offset, valid_x]

    print(matriz_de_escrita)
    return matriz_de_escrita


def generate_indices(coords_array):
    """Create a list of array indices (i, j) used to read blocks from an image."""
    shape = coords_array.shape
    indices = []
    for irow in range(shape[0]):
        for icol in range(shape[1]):
            indices.append((irow, icol))
    return indices


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
        mirrored = np.fliplr(block_data[..., :padding])
        return np.hstack((mirrored, block_data))
    elif direction == MIRROR_RIGHT:
        if padding > block_data.shape[1]:
            raise ValueError(error_message)
        s = block_data[..., -padding:]
        mirrored = np.fliplr(s)
        return np.hstack((block_data, mirrored))
    else:
        AttributeError('Direction must be one of [top, bottom, left, right] got: {}.'.format(direction))


def create_block_iterator(raster_data: RasterData, block_position_array: np.ndarray,
                          padding: int, block_indices: List[Tuple[int]]) -> Generator[np.ndarray]:
    """ Cria o iterator para os blocos, em sequencia ou de forma randomica.

    :param raster_data: 
    :param block_position_array: 
    :param padding: Numero de pixels do preenchimento das bordas.
    :param block_indices: The indices of the blocks to read. 
    """
    img_shape = raster_data.meta.shape
    blk_shape = raster_data.meta.block_shape

    # Quantos blocos inteiros cabem, quantos pixels sobram
    n_block_rows, resto_pixel_rows = divmod(img_shape[0], blk_shape[0])
    n_block_cols, resto_pixel_cols = divmod(img_shape[1], blk_shape[1])

    # Number of pixels needed to complete the last row and the last column.
    dif_last_row = blk_shape[0] - resto_pixel_rows
    dif_last_col = blk_shape[1] - resto_pixel_cols

    for index in block_indices:
        row_index, col_index = index
        block_coordinates = block_position_array[row_index, col_index]

        if row_index + 1 == n_block_rows:  # Ultima linha. Completa o que falta e pega o padding dos blocos de cima.
            yo, vy, xo, vx = block_coordinates
            block_coordinates = [yo, vy, xo - dif_last_row - padding, vx]
        elif row_index + 1 != n_block_rows and row_index != 0:
            # Não é ultima linha, nem a primeira, pega o padding do bloco de cima e de baixo.
            yo, vy, xo, vx = block_coordinates
            block_coordinates = [yo, vy, xo - padding, vx + padding]

        if col_index + 1 == n_block_cols:  # Ultima coluna, completa e pega o padding do bloco da esquerda.
            yo, vy, xo, vx = block_coordinates
            block_coordinates = [yo - dif_last_col - padding, vy, xo, vx]
        elif col_index + 1 != n_block_cols and col_index != 0:
            # Nem a ultima nem a primeira coluna. Pega o padding do bloco da direita e da esquerda.
            yo, vy, xo, vx = block_coordinates
            block_coordinates = [yo - padding, vy + padding, xo, vx]

        # Agora pega o bloco.
        block_data = raster_data.read_block_by_coordinates(block_coordinates)

        # E fazemos os espelhamentos para os casos especificos.
        if row_index == 0:  # 1a linha. Espelha para cima.
            block_data = mirror_block(block_data, padding, MIRROR_TOP)
        elif row_index + 1 == n_block_rows:  # Ultima linha. Espelha para baixo.
            block_data = mirror_block(block_data, padding, MIRROR_BOTTOM)

        if col_index == 0:  # 1a coluna. Espelha para a esquerda.
            block_data = mirror_block(block_data, padding, MIRROR_LEFT)
        elif col_index + 1 == n_block_cols:  # Ultima coluna. Espelha para a direita.
            block_data = mirror_block(block_data, padding, MIRROR_RIGHT)

        yield block_data


if __name__ == '__main__':
    nn_output = (388, 388)  # Tamanho da saída da rede neural, também o tamanho do bloco de escrita.
    nn_input = (572, 572)  # Tamanho da entrada na rede neural (tamanho saída + padding)

    img_padding = 94

    # Pega o resterdata
    img = RasterData("samples/Paprika-ilustr.jpg")
    matriz_de_coordenadas = create_blocks_coordinates_array(blk_shape=nn_output, img_shape=img.meta.shape)

    # Talvez não seja necessário alterar o block_size, pq a leitura será calculada?
    img.meta.block_size = nn_output