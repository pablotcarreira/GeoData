# Pablo Carreira - 30/05/17
import collections
from typing import Sequence

import numpy as np
from raster_utils import mirror_block, MIRROR_TOP, MIRROR_BOTTOM, MIRROR_LEFT, MIRROR_RIGHT
from rasterdata import RasterData


class RasterPaddingIterator(collections.Iterator):
    def __init__(self, raster_data: RasterData, block_indices: Sequence,
                 block_size: Sequence, padding: int, block_coordinates, infinite: bool = False):
        """Iterates over a single raster, yelds image blocks with an extra padding around it.

        :param raster_data: The image RasterData.
        :param block_coordinates: The coordinates of the image blocks.
        :param block_indices: The indices of the blocks, passing the indices allows to iterate over specific blocks.
        :param block_size: The shape of the blocks without the padding.
        :param padding: The size in pixels of the padding.     
        :param infinite: If the iterator should run infinite times.
                :returns: The block data (with padding), the valid data region, the block coordinates at the image.
        """
        raster_data.n_bandas = 3  # Override no numero de bandas.
        self.block_indices = block_indices
        self.infinite = infinite
        self.block_coordinates = block_coordinates
        self.padding = padding
        self.block_size = block_size
        self.raster_data = raster_data

        self.index = 0

        img_shape = raster_data.shape

        # Quantos blocos inteiros cabem, quantos pixels sobram
        self.n_block_rows, self.resto_pixel_rows = divmod(img_shape[0], block_size[0])
        self.n_block_cols, self.resto_pixel_cols = divmod(img_shape[1], block_size[1])

        # Number of pixels needed to complete the last row and the last column.
        self.dif_last_row = block_size[0] - self.resto_pixel_rows
        self.dif_last_col = block_size[1] - self.resto_pixel_cols
        # If those number are equal to the block size, this means that nothing is missing.
        if self.dif_last_row == block_size[0]:
            self.dif_last_row = 0
        if self.dif_last_col == block_size[1]:
            self.dif_last_col = 0

        # Caso haja um pedaço sobrando do final, inclui mais um bloco.
        # FIXME: Muito deselegante, pegar o numero de blocos do shape do block_coordinates.
        if self.resto_pixel_rows != 0:
            self.n_block_rows += 1
        if self.resto_pixel_cols != 0:
            self.n_block_cols += 1

        double_padding = 2 * padding  # Padding on both sizes is equal to...
        self.expected_shape = (block_size[0] + double_padding, block_size[1] + double_padding)

    def __next__(self):
        try:
            self.index += 1
            row_index, col_index = self.block_indices[self.index]
        except IndexError:
            if self.infinite is True:
                # Se o iterator acaba (IndexError) reinicia a iteração para o caso de infinite=True.
                self.index = 0
                row_index, col_index = self.block_indices[self.index]
            else:
                raise

        # Position of the data that is valid for write (excludes padding and block completion).
        # [vy0, vy1, vx0, vx1]
        block_valid_data = [0, self.block_size[0], 0, self.block_size[1]]
        original_block_coordinates = self.block_coordinates[row_index, col_index]
        a_block_coordinates = self.block_coordinates[row_index, col_index]

        # Linhas ---------------------
        if row_index + 1 == self.n_block_rows:
            # Ultima linha. Completa o que falta e pega o padding dos blocos de cima.
            y0, y1, x0, x1 = a_block_coordinates
            a_block_coordinates = [y0 - self.dif_last_row - self.padding, y1, x0, x1]
            block_valid_data[0] = self.dif_last_row
        elif row_index + 2 == self.n_block_rows:
            # Penultima linha. Verifica se a ultima linha é maior que o padding.
            if self.padding > self.resto_pixel_rows:
                # Se for maior, não pode pegar o padding de baixo, pega apenas o que tem disponível, depois
                # será feito o mirror para completar.
                y0, y1, x0, x1 = a_block_coordinates
                a_block_coordinates = [y0 - self.padding, y1 + self.resto_pixel_rows, x0, x1]
            else:
                # Se não for maior, procede normalmente pegando o padding de cima e de baixo
                y0, y1, x0, x1 = a_block_coordinates
                a_block_coordinates = [y0 - self.padding, y1 + self.padding, x0, x1]
        elif row_index + 1 != self.n_block_rows and row_index != 0:
            # Não é ultima linha, nem a primeira, pega o padding do bloco de cima e de baixo.
            y0, y1, x0, x1 = a_block_coordinates
            a_block_coordinates = [y0 - self.padding, y1 + self.padding, x0, x1]

        # Colunas |||||||||||||||
        if col_index + 1 == self.n_block_cols:
            # Ultima coluna, completa e pega o padding do bloco da esquerda.
            y0, y1, x0, x1 = a_block_coordinates
            a_block_coordinates = [y0, y1, x0 - self.dif_last_col - self.padding, x1]
            block_valid_data[2] = self.dif_last_col
        elif col_index + 2 == self.n_block_cols:
            # Penultima coluna. Verifica se a ultima coluna é maior que o padding.
            if self.padding > self.resto_pixel_cols:
                # Se for maior, não pode pegar o padding da direita, pega apenas o que tem disponível, depois
                # será feito o mirror para completar.
                y0, y1, x0, x1 = a_block_coordinates
                a_block_coordinates = [y0, y1, x0 - self.padding, x1 + self.resto_pixel_cols]
            else:
                # Se não for maior, procede normalmente pegando o padding da direita e da esquerda.
                y0, y1, x0, x1 = a_block_coordinates
                a_block_coordinates = [y0, y1, x0 - self.padding, x1 + self.padding]
        elif col_index + 1 != self.n_block_cols and col_index != 0:
            # Nem a ultima, nem a penultima, nem a primeira coluna. Pega o padding do bloco da direita e da esquerda.
            y0, y1, x0, x1 = a_block_coordinates
            a_block_coordinates = [y0, y1, x0 - self.padding, x1 + self.padding]

        # Primeira linha e coluna. (talvez juntar como elif acima?)
        if row_index == 0:
            # Primeira linha, adiciona o padding do bloco de baixo.
            y0, y1, x0, x1 = a_block_coordinates
            a_block_coordinates = [y0, y1 + self.padding, x0, x1]
        if col_index == 0:
            # Primeira coluna, adiciona o padding do bloco da direita.
            y0, y1, x0, x1 = a_block_coordinates
            a_block_coordinates = [y0, y1, x0, x1 + self.padding]

        # Agora pega o bloco.
        block_data = self.raster_data.read_block_by_coordinates(*a_block_coordinates)

        # E fazemos os espelhamentos para os casos especificos.
        # Linhas ------
        if row_index == 0:  # 1a linha. Espelha para cima.
            block_data = mirror_block(block_data, self.padding, MIRROR_TOP)
        elif row_index + 1 == self.n_block_rows:  # Ultima linha. Espelha para baixo.
            block_data = mirror_block(block_data, self.padding, MIRROR_BOTTOM)
        elif row_index + 2 == self.n_block_rows:  # Penultima linha, verifica se deve completar com espelhamento.
            if self.padding > self.resto_pixel_rows:
                # Se o padding é maior, completa com o espelhamento.
                block_data = mirror_block(block_data, self.padding - self.resto_pixel_rows, MIRROR_BOTTOM)

        # Colunas |||||||
        if col_index == 0:  # 1a coluna. Espelha para a esquerda.
            block_data = mirror_block(block_data, self.padding, MIRROR_LEFT)
        elif col_index + 1 == self.n_block_cols:  # Ultima coluna. Espelha para a direita.
            block_data = mirror_block(block_data, self.padding, MIRROR_RIGHT)
        elif col_index + 2 == self.n_block_cols:  # Penultima coluna, verifica se deve completar com espelhamento.
            if self.padding > self.resto_pixel_cols:
                # Se o padding é maior, completa com o espelhamento.
                block_data = mirror_block(block_data, self.padding - self.resto_pixel_cols, MIRROR_RIGHT)

        # Por segurança verifica se o bloco gerado tem o tamanho correto.
        if block_data.shape[:2] != self.expected_shape:
            raise RuntimeError("""
                       Foi gerado um bloco de tamanho incorreto. 
                       Esperado: {},  Gerado: {}.""".format(self.expected_shape, block_data.shape[:2]))

        # print(a_block_coordinates == original_block_coordinates)

        # Normalização e Transpose (passos 6 e 6b)
        # Fixme: Passar os objetos que executariam a normalização e o transpose.
        block_data = np.expand_dims(normalize_channel_range(block_data), 0)  # Normaliza e adiciona uma dimensão.
        block_data = np.transpose(block_data, (0, 3, 1, 2))

        # FIXME: Transformar este trio em um objeto "raster_block".
        return block_data, block_valid_data, original_block_coordinates
