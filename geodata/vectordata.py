# Pablo Carreira - 21/03/17
import os
from typing import Union, Iterator

from osgeo import ogr, osr

from geodata.geo_objects import BBox


class VectorData:
    def __init__(self, src_file: str, ogr_format: str=None, srs: Union[str, int, osr.SpatialReference]=None,
                 overwrite: bool=False, update=False):
        """                
        :param src_file: 
        :param ogr_format: One of OGR compatible formats: http://gdal.org/1.11/ogr/ogr_formats.html
        :param srs: Proj4 string, EPSG code or OSR.srs object.
        :param overwrite: Aways create a new file.
        """
        self.layers = {}
        self.src_file = src_file
        self.ogr_datasource = None
        self.ogr_format = ogr_format
        self.update = update

        # Set the srs.
        if isinstance(srs, osr.SpatialReference):
            self.srs = srs.clone()
        elif isinstance(srs, int):
            self.srs = osr.SpatialReference()
            self.srs.ImportFromEPSG(srs)
        elif isinstance(srs, str):
            self.srs = osr.SpatialReference()
            self.srs.ImportFromWkt(srs)

        file_exists = os.path.isfile(src_file)
        if file_exists and not overwrite:
            self.open_file()
        else:
            if ogr_format is None:
                raise ValueError("File format not specified for the new file.")
            else:
                try:
                    os.remove(src_file)
                except FileNotFoundError:
                    pass
                self.create_datasource()

    def get_bbox(self, layer: Union[str, int]=0) -> BBox:
        """Returns the bounding box for this vector data."""
        layer = self.ogr_datasource.GetLayer(layer)
        if layer is None:
            raise ValueError("Layer not found: {}.".format(layer))
        extent = layer.GetExtent()
        print(extent)
        return BBox(extent[1], extent[0], extent[2], extent[3])

    def open_file(self) -> None:
        """Opens the vector file."""
        ogr_datasource = ogr.Open(self.src_file, 1 if self.update else 0)
        if not ogr_datasource:
            raise IOError("Can't open file: {}".format(self.src_file))
        self.ogr_datasource = ogr_datasource

    def create_datasource(self) -> None:
        """Creates the OGR datasource (creates a new geographic file) using the format specified by
        self.ogr_format.
        """
        driver = ogr.GetDriverByName(self.ogr_format)
        if not driver:
            raise ValueError("Can't create OGR driver with this format: {}".format(self.ogr_format))
        ogr_datasource = driver.CreateDataSource(self.src_file)
        if ogr_datasource is None:
            raise IOError("Can't create the file in this location: {}".format(self.src_file))
        self.ogr_datasource = ogr_datasource

    def create_layer(self, layer_name: str="1", geom_type: str=ogr.wkbLineString):
        if layer_name in self.layers.keys():
            raise AttributeError("Layer with name {} already exists".format(layer_name))
        self.layers[layer_name] = self.ogr_datasource.CreateLayer(layer_name, self.srs, geom_type)
        # Cria o campo id, o unico que vai ser usado por enquanto.
        # FIXME: Deve estar na layer.
        id_field = ogr.FieldDefn("ID", ogr.OFTInteger)
        self.layers[layer_name].CreateField(id_field)
        return self.layers[layer_name]

    def get_features_iterator(self) -> Iterator[ogr.Feature]:
        """Returns the first layer."""
        layer = self.ogr_datasource.GetLayerByIndex(0)
        layer.ResetReading()
        return layer

    def add_feature_to_layer(self, geometry: ogr.Geometry, properties: dict, layer_name: str):
        # Fixme - Deve estar na layer, pode estar aqui apenas por um atalho de conveniência.
        layer = self.layers[layer_name]
        feature = ogr.Feature(layer.GetLayerDefn())
        feature.SetGeometry(geometry)
        for k, v in properties.items():
            feature.SetField(k, v)
        layer.CreateFeature(feature)