# Pablo Carreira - 22/06/17

import json

import ogr

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

