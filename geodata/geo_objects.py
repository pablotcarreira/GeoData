from typing import Tuple, Union
from warnings import warn

import numpy as np

from geodata.srs_utils import create_osr_srs

try:
    # noinspection PyUnresolvedReferences
    from osgeo import ogr, osr, gdal
except ImportError:
    warn("OGR not available")


class BBox:
    # __slots__ = ['xmin', 'ymin', 'xmax', 'ymax', '_wkt_srs', '_geometry']

    def __init__(self, xmin: float, ymin: float, xmax: float, ymax: float, wkt_srs: str=None):

        """Represents a bounding box. This is an imutable object and any method should return a new
        BBox.

        :param xmin: X min.
        :param ymin: Y min.
        :param xmax: X max.
        :param ymax: Y max.
        :param wkt_srs: Spatial reference system in well known text format.
        """
        self.ymax = ymax
        self.xmax = xmax
        self.ymin = ymin
        self.xmin = xmin

        # A geometry é a sequência de pontos que reprentam o retângulo, em um determinado srs.
        # esta geometry permanece inalterada durante a vida do bbox.
        self._geometry = ((xmin, ymax), (xmax, ymax), (xmax, ymin), (xmin, ymin))
        self._wkt_srs = wkt_srs

    @property
    def srs(self) -> osr.SpatialReference:
        return create_osr_srs(self.wkt_srs)

    @property
    def wkt_srs(self):
        return self._wkt_srs

    def __str__(self):
        return f"BBox: {self.xmin}, {self.ymin}, {self.xmax}, {self.ymax}"

    def __iter__(self):
        """This magic method allows the BBox to be cast as a sequence."""
        return iter((self.xmin, self.ymin, self.xmax, self.ymax))

    # def transform_srs(self, new_srs: Union[str, int, osr.SpatialReference]):
    def transform_srs(self, new_srs: Union[str, int, osr.SpatialReference]):
        """Transform this BBox to a srs and returns a new BBox."""

        if self._wkt_srs is None:
            raise AttributeError("SRS not defined for this BBox.")

        src_srs = osr.SpatialReference()
        src_srs.ImportFromWkt(self._wkt_srs)

        # Compatibilidade com gdal 3.
        if int(gdal.__version__) >= 3:
            src_srs.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)

        dst_srs = create_osr_srs(new_srs)
        transform = osr.CoordinateTransformation(src_srs, dst_srs)
        new_geom = transform.TransformPoints(self._geometry)
        # Get bbox from new geom:
        new_geom = np.asarray(new_geom)
        xcol = new_geom[:, 0]
        ycol = new_geom[:, 1]
        new_bbox = BBox(xcol.min(), ycol.min(), xcol.max(), ycol.max(), dst_srs.ExportToWkt())
        new_bbox._geometry = tuple(map(tuple, new_geom[:, :2]))
        return new_bbox

    @classmethod
    def create_from_ogr_extent(cls, extent: Tuple, wkt_srs: str=None):
        """Create a BBox from an OGR layer extent."""
        return cls(extent[0], extent[2], extent[1], extent[3], wkt_srs)
        
    def as_ogr_geometry(self):
        """Get bbox as an ogr geometry."""
        ring = ogr.Geometry(ogr.wkbLinearRing)
        ring.AddPoint(self.xmin, self.ymin)
        ring.AddPoint(self.xmax, self.ymin)
        ring.AddPoint(self.xmax, self.ymax)
        ring.AddPoint(self.xmin, self.ymax)
        ring.AddPoint(self.xmin, self.ymin)
        poly_envelope = ogr.Geometry(ogr.wkbPolygon)
        poly_envelope.AddGeometry(ring)
        poly_envelope.FlattenTo2D()
        return poly_envelope

    def as_tuple(self):
        return self.xmin, self.ymin, self.xmax, self.ymax

    @property
    def leaflet_bounds(self):
        """Retorna este bbox no formato LeafLet. https://leafletjs.com/reference-1.7.1.html#latlngbounds"""
        return (self.ymin, self.xmin), (self.ymax, self.xmax)

    @property
    def centro(self):
        return (self.xmax + self.xmin) / 2, (self.ymax + self.ymin) / 2


class RasterDefinition:
    __slots__ = ["rows", "cols", "xmin", "ymax", "xres", "yres", "srs"]

    def __init__(self, rows: int, cols: int, xmin: float, ymax: float, xres: float, yres: float, srs: str):
        """A set of parameters that defines a raster image geometry.
        Used for images with top left origin.

        yres is a negative number.

        :param rows: Image height.
        :param cols: Image width.
        :param xmin: Minimum x coordinate of origin
        :param ymax: Maximum y coordinate of origin
        :param xres: Pixel size in x axis.
        :param yres: Pixel size in y axis (negative value).
        :param srs: Spatial reference in WKT format.
        """
        self.srs = srs
        if yres >= 0:
            raise ValueError("yres should be < 0.")

        self.yres = yres
        self.xres = xres
        self.ymax = ymax
        self.xmin = xmin
        self.cols = cols
        self.rows = rows
