OGR/GDAL High level abstraction.

Be careful, this package will change.

https://github.com/pablotcarreira/GeoData

## Install:
`python setup.py`

## Examples
### Create a new Geotiff:
```
raster = RasterData.create(img_file="filename.tif",
                           rows=10, cols=10, pixel_size=10
                           xmin=0, ymax=100, bands=1, data_type=gdal.GDT_Float32))
                           
raster.write_all(matriz)
```
