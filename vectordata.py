# Pablo Carreira - 21/03/17
import ogr


class VectorData:
    def __init__(self, src_file: str):
        self.src_file = src_file
        self.ogr_datasource = None
        self.open_file()

    def open_file(self):
        ogr_datasource = ogr.Open(self.src_file)
        if not ogr_datasource:
            raise IOError("Can't open file: {}".format(self.src_file))
        self.ogr_datasource = ogr_datasource
