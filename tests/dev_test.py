# Pablo Carreira - 08/03/17
import cv2

import osr
import gdal
from rasterdata import RasterData
import matplotlib.pylab as plt
import numpy as np
from vectordata import VectorData

raster_data = RasterData("/home/pablo/Desktop/LinhasDePlantio/dados/originais/Mosaico/Rancho_Novo_Falhas.tif")
# vector_data = VectorData("/home/pablo/Desktop/LinhasDePlantio/dados/originais/Contorno/Rancho_Novo.shp")
vector_data = VectorData("/home/pablo/Desktop/LinhasDePlantio/dados/originais/Resultado/Linhas/Fileiras_Cana.shp")


vec2raster_out = raster_data.clone_empty("vec2raster.tiff", bandas=1)
layer = vector_data.ogr_datasource.GetLayerByIndex(0)


gdal.RasterizeLayer(vec2raster_out.gdal_dataset, [1], layer, options= ['ALL_TOUCHED=TRUE'])





# Parte efetiva da transformação:

# RasterizeOptions
# Create a RasterizeOptions() object that can be passed to gdal.Rasterize()
# Keyword arguments are :
#   options --- can be be an array of strings, a string or let empty and filled from other keywords.
#   format --- output format ("GTiff", etc...)
#   creationOptions --- list of creation options
#   outputBounds --- assigned output bounds: [minx, miny, maxx, maxy]
#   outputSRS --- assigned output SRS
#   width --- width of the output raster in pixel
#   height --- height of the output raster in pixel
#   xRes, yRes --- output resolution in target SRS
#   targetAlignedPixels --- whether to force output bounds to be multiple of output resolution
#   noData --- nodata value
#   initValues --- Value or list of values to pre-initialize the output image bands with.  However, it is not marked as the nodata value in the output file.  If only one value is given, the same value is used in all the bands.
#   bands --- list of output bands to burn values into
#   inverse --- whether to invert rasterization, i.e. burn the fixed burn value, or the burn value associated  with the first feature into all parts of the image not inside the provided a polygon.
#   allTouched -- whether to enable the ALL_TOUCHED rasterization option so that all pixels touched by lines or polygons will be updated, not just those on the line render path, or whose center point is within the polygon.
#   burnValues -- list of fixed values to burn into each band for all objects. Excusive with attribute.
#   attribute --- identifies an attribute field on the features to be used for a burn-in value. The value will be burned into all output bands. Excusive with burnValues.
#   useZ --- whether to indicate that a burn value should be extracted from the "Z" values of the feature. These values are added to the burn value given by burnValues or attribute if provided. As of now, only points and lines are drawn in 3D.
#   layers --- list of layers from the datasource that will be used for input features.
#   SQLStatement --- SQL statement to apply to the source dataset
#   SQLDialect --- SQL dialect ('OGRSQL', 'SQLITE', ...)
#   where --- WHERE clause to apply to source layer(s)
#   callback --- callback method
#   callback_data --- user data for callback

