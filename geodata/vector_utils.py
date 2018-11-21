# Pablo Carreira - 22/06/17

import json

from osgeo import ogr, osr

ogr.UseExceptions()


def create_ogr_linestring_from_list(geom: list) -> ogr.Geometry:
    """Creates a geometry from a Json geometry object"""
    return ogr.CreateGeometryFromJson(json.dumps({"type": 'LineString', 'coordinates': geom}))


def create_ogr_geom(geom) -> ogr.Geometry:
    """Creates a ogr geometry from a wkt ou wkb.

    :param geom:
    :return:
    """
    if isinstance(geom, ogr.Geometry):
        return geom

    # Converte os tipos para diferentes situações (python 2.7).
    # if isinstance(geom, str):
    #     geom = str(geom)
    # elif isinstance(geom, unicode):
    #     geom = str(geom)
    try:
        ogr_geom = ogr.CreateGeometryFromWkb(geom)
    except RuntimeError:
        ogr_geom = ogr.CreateGeometryFromWkt(geom)
    if not ogr_geom:
        ogr_geom = ogr.CreateGeometryFromWkt(geom)
    return ogr_geom


def create_osr_transform(src_epsg: int, dst_epsg: int):
    """Creates an OSR transform from epsg codes."""
    src_srs = osr.SpatialReference()
    src_srs.ImportFromEPSG(src_epsg)
    dst_srs = osr.SpatialReference()
    dst_srs.ImportFromEPSG(dst_epsg)
    return osr.CoordinateTransformation(src_srs, dst_srs)

