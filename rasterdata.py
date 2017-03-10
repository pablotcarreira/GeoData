# Pablo Carreira - 08/03/17
from typing import Iterator, overload, List

import gdal
import osr
import numpy as np


class RasterMetadata:
    """Metadados sobre uma imagem raster.

    Permite fazer o teste de igualdade para ver se os datasets são iguais, em relação ao
    tamanho da imagem (shape), block size, projeção, origem e tamanho do pixel. Não compara
    numero de bandas nem tipo de dados.
    """
    # Aguardando python 3.6 para poder usar o typing aqui. Ficaria assim:
    # n_bandas: int = 1 ou apenas n_bandas: int
    n_bandas = 1
    proj = None
    origem = None
    pixel_size = None

    def __init__(self, cols=None, rows=None, block_size=None):
        self.rows = rows
        self.block_size = block_size
        self.cols = cols

    def __eq__(self, other: 'RasterMetadata') -> bool:
        # FIXME: Não compara a projeção
        spatial_self = osr.SpatialReference(self.proj)
        spatial_other = osr.SpatialReference(other.proj)
        same_spatial = spatial_self.IsSame(spatial_other)

        return (self.rows == other.rows and
                self.cols == other.cols and
                self.block_size == other.block_size and
                self.x_origem == other.x_origem and
                self.y_origem == other.y_origem and
                self.pixel_size == other.pixel_size and
                same_spatial)


class RasterData:
    """Representa uma matriz raster com características espaciais."""
    _block_list = None
    _block_indices = None

    def __init__(self, img_file: str, write_enabled: bool=False):
        """
        :param img_file: Caminho para o arquivo tiff da imagem.
        :param write_enabled: Habilita a escrita para o arquivo. 
        """
        #: Caminho para o arquivo tiff da imagem (fonte de dados).
        self.img_file = img_file
        self.write_enabled = write_enabled
        self.src_image = img_file
        self.meta = RasterMetadata()
        self._load_metadata()

    # noinspection PyTypeChecker
    @property
    def block_indices(self) -> np.ndarray:
        """Contêm o índice dos elementos de qualquer bloco. É lazy."""
        if self._block_indices is None:
            self._block_indices = np.indices(self.meta.block_size)
        return self._block_indices

    @property
    def block_list(self) -> List:
        """Propriedade lazy contendo a lista de blocos."""
        if not self._block_list:
            self._block_list = self._create_blocks_list()
        return self._block_list

    def _load_metadata(self):
        """Lê meta informações do arquivo."""
        gdal_dataset = gdal.Open(self.src_image, gdal.GA_Update if self.write_enabled else gdal.GA_ReadOnly)
        if not gdal_dataset:
            raise IOError("Erro ao abrir o arquivo ou arquivo inexistente.")

        self.gdal_dataset = gdal_dataset

        # Informacoes gerais.
        self.meta.cols = gdal_dataset.RasterXSize
        self.meta.rows = gdal_dataset.RasterYSize
        self.meta.n_bandas = gdal_dataset.RasterCount
        self.meta.proj = gdal_dataset.GetProjection()

        geot = gdal_dataset.GetGeoTransform()
        print(geot)
        self.meta.origem = (geot[0], geot[3])
        self.meta.pixel_size = geot[1]

        src_band = gdal_dataset.GetRasterBand(1)
        self.meta.block_size = src_band.GetBlockSize()

        print("Image shape {}x{}px. ".format(self.meta.cols, self.meta.rows))
        print("Origem: {}m , {}m.".format(round(self.meta.origem[0], 2), round(self.meta.origem[1], 2)))
        print("Resolucao: {}m.".format(round(self.meta.pixel_size, 2)))
        print("Bandas: {}".format(self.meta.n_bandas))
        print("Projecao: \n {}".format(self.meta.proj))

        # Informações por banda.
        for item in range(self.meta.n_bandas):
            src_band = gdal_dataset.GetRasterBand(item + 1)
            src_block_size = src_band.GetBlockSize()
            print("Banda {} - Block shape {}x{}px.".format(item + 1, *src_block_size))

    def _create_blocks_list(self):
        """Cretes a list of block reading coordinates."""
        meta = self.meta
        blk_width, blk_height = meta.block_size

        # Get the number of blocks.
        x_blocks = int((meta.cols + blk_width - 1) / blk_width)
        y_blocks = int((meta.rows + blk_height - 1) / blk_height)
        # print("Creating blocks list with {} blocks ({} x {}).".format(
        #     x_blocks * y_blocks, x_blocks, y_blocks))

        blocks_list = []
        for block_column in range(0, x_blocks):
            # Recalculate the shape of the rightmost block.
            if block_column == x_blocks - 1:
                valid_x = meta.cols - block_column * blk_width
            else:
                valid_x = blk_width
            xoff = block_column * blk_width
            # loop through Y lines
            for block_row in range(0, y_blocks):
                # Recalculate the shape of the final block.
                if block_row == y_blocks - 1:
                    valid_y = meta.rows - block_row * blk_height
                else:
                    valid_y = blk_height
                yoff = block_row * blk_height
                blocks_list.append((xoff, yoff, valid_x, valid_y))
        return blocks_list

    def get_iterator(self, banda: int=1) -> Iterator:
        """Retorna um iterator sobre a imagem, retornando um pedaço do
        tamanho do block size a cada passo.

        :param banda: Banda da imagem para gerar o iterator.
        """
        blocks_list = self.block_list
        src_band = self.gdal_dataset.GetRasterBand(banda)
        for index, block in enumerate(blocks_list, 1):
            block_data = src_band.ReadAsArray(*block)
            yield block_data

    def clone_empty(self, new_img_file: str, bandas: int=0, data_type=gdal.GDT_Byte) -> 'RasterData':
        """Cria uma nova imagem RasterData com as mesmas características desta imagem,
        a nova imagem é vazia e pronta para a escrita.
        A finalidade é criar imagens para a saída de processamentos.
        São copiados os tamanhos, progeção, geo transform e bandas.

        Caso as bandas não sejam sefinidas usa o numero de bandas desta imagem.

        Não é possível determinar o block size das camadas de saída, portanto a escrita
        ocorre de forma menos eficiente nas imagens criadas quando iteradas com imagens
        obtidas que não possuem tamanho padrão de block (tiled vs. scanline).
        """
        # Criado na unha para poder ajustar parâmetros.

        if bandas == 0:
            bandas = self.meta.n_bandas

        gdal_driver = self.gdal_dataset.GetDriver()

        geotiff_options = ["TILED=YES",
                           "BLOCKXSIZE=" + str(self.meta.block_size[0]),
                           "BLOCKYSIZE=" + str(self.meta.block_size[1])]

        new_dataset = gdal_driver.Create(new_img_file,
                                         self.meta.cols, self.meta.rows,
                                         bands=bandas,
                                         eType=data_type,
                                         options=geotiff_options)

        # Copia as informações georreferenciadas.
        new_dataset.SetProjection(self.gdal_dataset.GetProjection())
        new_dataset.SetGeoTransform(self.gdal_dataset.GetGeoTransform())

        new_dataset.FlushCache()  # Garante a escrita no disco.
        return RasterData(new_img_file, write_enabled=True)

    def get_block_coordinates(self, block_index: int) -> np.ndarray:
        """Retorna uma matriz com as coordenadas geográficas dos pixels do bloco.

        :param block_index: 
        """
        block_position = self.block_list[block_index]
        block_coords = np.empty(self.block_indices.shape)
        for eixo in range(self.block_indices.shape[0]):
            # TODO: Converter para array.
            c = self.block_indices[eixo] + (block_position[eixo] * self.meta.pixel_size) + self.meta.origem[eixo]



            block_coords[eixo] = c
        return block_coords

    def write_block(self, data_array: np.ndarray, block_index: int, banda: int=1):
        """Escreve um bloco de dados em uma banda.

        :param block_index: O índice do bloco para escrever.
        """
        block_position = self.block_list[block_index]
        self.gdal_dataset.GetRasterBand(banda).WriteArray(data_array, block_position[0], block_position[1])
        self.gdal_dataset.FlushCache()



