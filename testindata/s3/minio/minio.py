from minio import Minio
from minio.error import InvalidResponseError as ResponseError
from datetime import timedelta
import requests

#约定：s3包下面的所有文件均是对存储对象的操作，里面所有的变量，单词，描述，均是和存储对象相关的，不允许出现dataset相关的用语
class YcMinio():
    def __init__(self, req = None):
        self.upUrl = ""
        self.req = req

    def PutObject(self, bucketName, objectName, filePath):
        urlInfo = self.req.GetUploadUrl(objectName)
        upUrl = urlInfo["url"]
        with open(filePath, 'rb') as file:
            try:
                response = requests.put(upUrl, data=file)
            except ResponseError as err:
                raise Exception("failed in deleting file", err)
