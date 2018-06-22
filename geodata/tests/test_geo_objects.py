# Pablo Carreira
from geodata.geo_objects import BBox


def test_bbox():
    bbox = BBox(0, 0, 10, 10)
    ogr_geom = bbox.as_ogr_geometry()
    assert ogr_geom.Area() == 100.0


if __name__ == '__main__':
    test_bbox()
