# Pablo Carreira - 21/03/17
import os
from typing import Union, Iterator

from osgeo import ogr, osr

from geodata.geo_objects import BBox


class VectorData:
    def __init__(self, src_file: str, update=False):
        """                
        :param src_file:

        :param overwrite: Aways create a new file.
        """
        self.layers = {}
        self.src_file = src_file
        self.ogr_datasource = None
        self.ogr_format = None
        self.update = update
        self.srs = None

        if not os.path.isfile(src_file):
            raise NotImplementedError(f"Not a file: {src_file}. \n Use VectorData.create() to create a new file.")
        self.open_file()

    @classmethod
    def create(cls, file_name: str, ogr_format: str, srs: Union[str, int, osr.SpatialReference],
               geom_type: str = ogr.wkbLineString, overwrite: bool = False):
        """Creates the OGR datasource (creates a new geographic file) using the format specified.

        :param ogr_format: One of OGR compatible formats: http://gdal.org/1.11/ogr/ogr_formats.html
        :param srs: Proj4 string, EPSG code or OSR.srs object.

        """
        file_exists = os.path.isfile(file_name)
        if file_exists and not overwrite:
            raise RuntimeError("Arquivo existente. Coloque overwrite=True se quiser sobrescrever.")

        if isinstance(srs, osr.SpatialReference):
            asrs = srs.clone()
        elif isinstance(srs, int):
            asrs = osr.SpatialReference()
            asrs.ImportFromEPSG(srs)
        elif isinstance(srs, str):
            asrs = osr.SpatialReference()
            asrs.ImportFromWkt(srs)
        else:
            raise TypeError("Tipo do SRS não suportado.")

        driver = ogr.GetDriverByName(ogr_format)
        if not driver:
            raise ValueError("Can't create OGR driver with this format: {}".format(ogr_format))
        ogr_datasource = driver.CreateDataSource(file_name)
        if ogr_datasource is None:
            raise IOError("Can't create the file in this location: {}".format(file_name))

        camada = ogr_datasource.CreateLayer("camada", asrs, geom_type)
        camada.CreateField(ogr.FieldDefn("ID", ogr.OFTInteger))
        del ogr_datasource
        v = VectorData(file_name, update=True)
        v.srs = asrs
        return v

    def get_layer(self):
        """Retorna a camada 0."""
        return self.ogr_datasource.GetLayerByIndex(0)

    def get_bbox(self, layer: Union[str, int] = 0) -> BBox:
        """Returns the bounding box for this vector data."""
        layer = self.ogr_datasource.GetLayer(layer)
        if layer is None:
            raise ValueError("Layer not found: {}.".format(layer))
        extent = layer.GetExtent()
        srs = layer.GetSpatialRef().ExportToWkt()
        return BBox.create_from_ogr_extent(extent, srs)

    def open_file(self) -> None:
        """Opens the vector file."""
        ogr_datasource = ogr.Open(self.src_file, 1 if self.update else 0)
        if not ogr_datasource:
            raise IOError("Can't open file: {}".format(self.src_file))
        self.ogr_datasource = ogr_datasource

    def create_layer(self, layer_name: str="1", geom_type: str=ogr.wkbLineString):
        if layer_name in self.layers.keys():
            raise AttributeError("Layer with name {} already exists".format(layer_name))
        self.layers[layer_name] = self.ogr_datasource.CreateLayer(layer_name, self.srs, geom_type)
        id_field = ogr.FieldDefn("ID", ogr.OFTInteger)
        self.layers[layer_name].CreateField(id_field)
        return self.layers[layer_name]

    def get_features_iterator(self) -> Iterator[ogr.Feature]:
        """Returns the first layer."""
        layer = self.ogr_datasource.GetLayerByIndex(0)
        layer.ResetReading()
        return layer

    def add_feature_to_layer(self, geometry: ogr.Geometry, properties: dict):
        # Fixme - Deve estar na layer, pode estar aqui apenas por um atalho de conveniência.
        layer = self.ogr_datasource.GetLayerByIndex(0)
        feature = ogr.Feature(layer.GetLayerDefn())
        feature.SetGeometry(geometry)
        for k, v in properties.items():
            feature.SetField(k, v)
        layer.CreateFeature(feature)