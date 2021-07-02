import os

from testindata.dataset.metadata import MetaData
from testindata.dataset.labeldata import LabelData
from testindata.dataset.file import File


class UrlFile(File):
    def __init__(self, url, fileType):
        self.TYPE_IMAGE = 0
        self.TYPE_VIDEO = 1
        self.TYPE_AUDIO = 2
        self.TYPE_POINT_CLOUD = 3
        self.TYPE_FUSION_POINT_CLOUD = 4
        self.TYPE_POINT_CLOUD_SEMANTIC_SEGMENTATION = 5
        self.TYPE_TEXT = 6

        self.filepath = ""
        self.url = url

        self.metadata = MetaData({})
        self.labeldata = LabelData()
        self.filePrefix = ""
        self.fileType = fileType
        self.frameId = ""
        self.sensor = ""

        self.objectPath = ""
        self.osspath = self.url

        self.referId = ""
        self.filename = os.path.basename(self.url)
        self.md5 = ""
        self.filesize = 0
        self.type = ""
