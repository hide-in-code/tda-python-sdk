import sys
import os

from testindata.s3.minio.minio import YcMinio
from testindata.s3.qiniu.qiniu import Qiniu
from testindata.dataset.request import Request
from testindata.dataset.updatefile import UpdateFile

class Dataset():
    def __init__(self, T_key, datasetName, host):
        self.OSS_TYPE_DEFAULT = 0
        self.OSS_TYPE_MINIO = 0
        self.OSS_TYPE_ALI = 1
        self.OSS_TYPE_AWS = 2
        self.OSS_TYPE_QINIU = 3

        self.DATASET_TYPE_IMAGE = 0
        self.DATASET_TYPE_VIDEO = 1
        self.DATASET_TYPE_AUDIO = 2
        self.DATASET_TYPE_POINT_CLOUD = 3
        self.DATASET_TYPE_FUSION_POINT_CLOUD = 4
        self.DATASET_TYPE_POINT_CLOUD_SEMANTIC_SEGMENTATION = 5
        self.DATASET_TYPE_TEXT = 6

        #授权云存储
        self.HOSTING_METHOD_CLOUD = 1
        #自由云存储
        self.HOSTING_METHOD_OWN_STORAGE = 2

        self.req = Request(T_key, datasetName, host)
        info = self.req.GetAccess()

        # self.access_key = info['access_key']
        # self.secret_key = info['secret_key']
        self.upload_token = info['upload_token']
        self.endpoint = info['endpoint']

        self.bucket = info['bucket']
        self.file_path = info["file_path"]
        self.oss_type = info['oss_type']
        self.datasetName = datasetName
        self.datasetType = info["dataset_type"]
        self.hostingMethod = info["hosting_method"]
        self.host = host

        #非实际云存储
        if self.hostingMethod != self.HOSTING_METHOD_OWN_STORAGE:
            if self.oss_type == self.OSS_TYPE_MINIO or \
                self.oss_type == self.OSS_TYPE_DEFAULT or \
                self.oss_type == self.OSS_TYPE_ALI or \
                self.oss_type == self.OSS_TYPE_AWS:
                # self.client = YcMinio(self.access_key, self.secret_key, self.endpoint)
                # if self.bucket not in self.client.ListAllBucket():
                #     raise Exception(f"bucket:{self.bucket} is not exist!")
                self.client = YcMinio(self.req)
            elif self.oss_type == self.OSS_TYPE_QINIU:
                self.client = Qiniu(self.upload_token)
            else:
                raise Exception("尚未支持其他类型的云存储")
        else:
            self.client = None

    def PutFileToDataset(self, objectName, filePath):
        if self.oss_type == self.OSS_TYPE_QINIU:
            self.client.PutObject(self.bucket, self.datasetName + "/" + objectName, filePath)
        else:
            self.client.PutObject(self.bucket, objectName, filePath)

        # if not self.file_path:
        #     self.client.PutObject(self.bucket, self.datasetName + "/" + objectName, filePath)
        # else:
        #     self.client.PutObject(self.bucket, self.file_path + "/" + self.datasetName + "/" + objectName, filePath)

    def SyncDataToWeb(self, data):
        info = self.req.Upload(data)
        return info

    def GetData(self, offset, limit, metaData={}, label="", sensor="", debug=False):
        info = self.req.GetData(offset, limit, metaData, label, sensor)
        if "total" not in info.keys() or "files" not in info.keys():
            return {"total":0,"files":[]}

        ret = {
            "total":info["total"],
            "files":[]
        }

        for item in info["files"]:
            file = UpdateFile(item, self.req, self.datasetType, debug=debug)
            ret["files"].append(file)

        return ret

    def GetFileAndLabelByFid(self, fid, debug=False):
        info = self.req.GetFileAndLabelByFid(fid)
        if "file" not in info.keys() or info["file"] == {}:
            return

        file = UpdateFile(info["file"], self.req, self.datasetType, debug=debug)
        file.anotations.LoadFromList(info["anotations"])
        return file

    def GetFileAndLabelByReferid(self, referId, debug=False):
        info = self.req.GetFileAndLabelByReferid(referId)
        if "file" not in info.keys() or info["file"] == {}:
            return

        file = UpdateFile(info["file"], self.req, self.datasetType, debug=debug)
        file.anotations.LoadFromList(info["anotations"])
        return file

