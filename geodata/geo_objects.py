from typing import Tuple
from warnings import warn


try:
    # noinspection PyUnresolvedReferences
    from osgeo import ogr
except ImportError:
    warn("OGR not available")


class BBox:
    __slots__ = ['xmin', 'ymin', 'xmax', 'ymax']

    def __init__(self, xmin: float, ymin: float, xmax: float, ymax: float):
        """Represents a bounding box.

        :param xmin: X min.
        :param ymin: Y min.
        :param xmax: X max.
        :param ymax: Y max.                
        """
        self.ymax = ymax
        self.xmax = xmax
        self.ymin = ymin
        self.xmin = xmin

    def __str__(self):
        return f"BBox: {self.xmin}, {self.ymin}, {self.xmax}, {self.ymax}"

    def __iter__(self):
        """This magic method allows the BBox to be cast as a sequence."""
        return iter((self.xmin, self.ymin, self.xmax, self.ymax))

    @classmethod
    def create_from_ogr_extent(cls, extent: Tuple):
        """Create a BBox from an OGR layer extent."""
        return cls(extent[0], extent[2], extent[1], extent[3])
        
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
        pass
