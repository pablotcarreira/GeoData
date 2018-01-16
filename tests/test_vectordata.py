# Pablo Carreira - 22/06/17
import os

import ogr
from vectordata import VectorData

from geodata.vector_utils import create_ogr_linestring_from_list


def test_create_vectordata_gpkg():
    src_file = "/home/pablo/Desktop/geo_array/tests/data/vector.gpkg"
    try:
        os.remove(src_file)
    except FileNotFoundError:
        pass
    vector = VectorData(src_file, "GPKG", srs=4326, overwrite=True)
    assert os.path.isfile(src_file)


def test_create_vectordata_shape():
    src_file = "/home/pablo/Desktop/geo_array/tests/data/vector.shp"
    try:
        os.remove(src_file)
    except FileNotFoundError:
        pass
    vector = VectorData(src_file, "ESRI Shapefile", srs=4326, overwrite=True)
    vector.create_layer()
    assert os.path.isfile(src_file)


def test_create_ogr_linestring():
    linha = [[207603.9472469226, 7798935.968343082], [207604.00814469813, 7798936.151036409]]
    geom = create_ogr_linestring_from_list(linha)
    assert isinstance(geom, ogr.Geometry)






# def test_create_srs():
#     srs_string = 'PROJCS["WGS 84 / UTM zone 23S",GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433],AUTHORITY["EPSG","4326"]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",-45],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",10000000],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AUTHORITY["EPSG","32723"]]'
#     srs = osr.SpatialReference()
#     srs.ImportFromWkt(srs_string)
#     print(srs.ExportToPrettyWkt())


if __name__ == '__main__':
    # test_create_vectordata_shape()
    # test_create_srs()
    test_create_ogr_linestring()