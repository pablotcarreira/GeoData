# Pablo Carreira
from osgeo import osr

from geodata.geo_objects import BBox


def test_bbox_as_ogr_geometry():
    bbox = BBox(0, 0, 10, 10)
    ogr_geom = bbox.as_ogr_geometry()
    assert ogr_geom.Area() == 100.0


def test_bbox_transform_srs():
    srs = osr.SpatialReference()

    srs.ImportFromEPSG(4326)
    wgs84 = srs.ExportToWkt()

    srs.ImportFromEPSG(32722)
    utm22s = srs.ExportToWkt()

    srs.ImportFromEPSG(32723)
    utm23s = srs.ExportToWkt()

    b_wgs84 = BBox(-48.10120865150, -22.66876590, -48.08080826, -21.678076337272, wgs84)
    b_utm22 = b_wgs84.transform_srs(utm22s)
    assert int(b_utm22.xmin) == 799980
    assert int(b_utm22.ymin) == 7490200
    assert int(b_utm22.xmax) == 802092
    assert int(b_utm22.ymax) == 7600000

    b_utm23 = b_wgs84.transform_srs(utm23s)
    b_utm22 = b_utm23.transform_srs(utm22s)
    assert int(b_utm22.xmin) == 799980
    assert int(b_utm22.ymin) == 7490200
    assert int(b_utm22.xmax) == 802092
    assert int(b_utm22.ymax) == 7600000

if __name__ == '__main__':
    test_bbox_transform_srs()
