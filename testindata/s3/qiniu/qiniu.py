from qiniu import Auth, put_file, etag
import qiniu.config

class Qiniu():
    def __init__(self, upload_token):
        self.upload_token = upload_token


    #上传单个文件数据
    def PutObject(self, bucketName, objectName, filePath, content_type='application/octet-stream', metadata=None):
        try:
            # print(self.upload_token)
            # print(objectName)
            # print(filePath)
            # exit()
            ret, info = put_file(self.upload_token, objectName, filePath)
        except:
            raise Exception("failed in putting file")
