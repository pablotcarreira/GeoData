# Pablo Carreira - 29/06/17
from typing import Union

from osgeo import osr


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
    return srs


