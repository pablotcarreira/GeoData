# Pablo Carreira - 08/03/17
import cv2
import osr
from rasterdata import RasterData
import matplotlib.pylab as plt

#
#
# raster_data = RasterData("tests/data/imagem.tiff")
# bl = raster_data._create_blocks_list()
# # new_clone = raster_data.clone_empty("tests/data/imagem_clone.tiff")
#
#
#
#
#
# # cv2.imshow('image', pedaco[0])
# # cv2.waitKey(0)
# # cv2.destroyAllWindows()

print("oi")

def test_coords():
    raster_data = RasterData("tests/data/imagem2.tif")
    entrada_red = raster_data.get_iterator(banda=1)
    for indice, red_array in enumerate(entrada_red):
        coords = raster_data.get_block_coordinates(indice)
        print(coords)


test_coords()