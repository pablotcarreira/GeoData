# Pablo Carreira - 29/06/17
from osgeo import osr
from typing import Union


def create_osr_srs(in_srs: Union[osr.SpatialReference, int, str]) -> osr.SpatialReference:
    """Creates an osr.SpatialReference object either from an EPSG code or a Wkt.
    If the srs is already an osr.SpatialReference, return a clone.
    """
    if isinstance(in_srs, osr.SpatialReference):
        srs = in_srs.Clone()
    elif isinstance(in_srs, int):
        srs = osr.SpatialReference()
        srs.ImportFromEPSG(in_srs)
    elif isinstance(in_srs, str):
        srs = osr.SpatialReference()
        srs.ImportFromWkt(in_srs)
    else:
        raise ValueError("Formato srs desconhecido.")
    return srs


def epsg_para_wkt(epsg: int) -> str:
    """Converte um código EPSG para WKT SRS."""
    return create_osr_srs(epsg).ExportToWkt()


def find_utm_epsg(longitude, latitude):
    """EPSG=32700-ROUND((45+latitude)/90;0)*100+ROUND((183+longitude)/6;0)
    :param latitude:
    :param longitude:
    :return:
    """
    return 32700 - round((45+latitude)/90)*100+round((183+longitude)/6)
