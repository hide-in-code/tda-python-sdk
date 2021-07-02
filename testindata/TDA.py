import os
import sys
import json
import time
import re

from testindata.dataset.dataset import Dataset
from testindata.dataset.metadata import MetaData
from testindata.dataset.file import File
from testindata.dataset.urlfile import UrlFile
from testindata.dataset.commitdb import CommitDb
from testindata.dataset.uploaddb import UploadDb
from testindata.utils import util

#sdk entrance
class TDA():
    def __init__(self, accessKey, host="", debug=False):
        if host == "":
            self.host = "https://dataset.testin.cn/"
        else:
            if "http://" in host or "https://" in host:
                self.host = host.rstrip("/") + "/"
            else:
                self.host = "http://" + host.strip("/") + "/"
        self.__debug = debug
        self.T_key = accessKey
        self.commitFlag = False
        self.commitId = ""
        self.datasetId = ""
        self.fileList = []

    def Debug(self):
        """
        set sdk to debug mod
        """
        self.__debug = True

    @property
    def debug(self):
        '''
        debug read only
        :return:
        '''
        return self.__debug

    def SetDataset(self, datasetId):
        '''
        Set the dataset to be processed
        :param datasetId: the id of the dataset
        :return:
        '''
        self.datasetId = datasetId

        if self.debug:
            print(f"\033[0;37;44m[SET_DATASET] dataset: {self.datasetId} , service: {self.host}\033[0m")

        self.dataset = Dataset(self.T_key, datasetId, self.host)

        self.filePrefix = self.datasetId
        if self.dataset.file_path != "":
            self.filePrefix = self.dataset.file_path.strip("/") + "/" + self.datasetId.strip("/")

        if self.dataset.oss_type not in [self.dataset.OSS_TYPE_ALI, self.dataset.OSS_TYPE_QINIU]:
            self.filePrefix = self.dataset.bucket + "/" + self.filePrefix

        # return self.dataset#close for new feature

    def RiseException(self):
        raise Exception("You have not set the dataset name yet!")

    def UploadFilesToDataset(self, rootPath, ext=""):
        '''
        Upload files to dataset service directly
        :param rootPath: local file root path
        :param ext: if set, files endswith this extension will be uploaded
        :return:
        '''
        if self.debug:
            print(f"[UPLOAD_FILES] upload file to dataset without metedata and annotations!")

        if not self.datasetId:
            self.RiseException()

        total = 0
        for root, dir, files in os.walk(rootPath):
            for fileName in files:
                if fileName.endswith(ext):
                    total += 1

        if self.debug:
            print(f"[UPLOAD_FILES] file total: {total}")

        syncData = []
        j = 0
        i = 0
        retInfo = {'succ': 0, 'fail': 0}
        dirname = os.path.dirname(rootPath.rstrhost("/"))

        for root, dir, files in os.walk(rootPath):
            for fileName in files:
                if fileName.endswith(ext):
                    filePath = os.path.join(root, fileName)
                    objectName = filePath.replace(dirname, "").lstrhost("/")
                    self.__UploadFileToDataset(filePath, objectName)
                    tmp = {
                        "ref_id": "",
                        "name": fileName,
                        "path": self.filePrefix + "/" + objectName,
                        "size": int(util.getFileSize(filePath)),
                        "md5": util.getFileMd5(filePath),
                        "frame_id":"",
                        "sensor":"",
                        "meta": {},
                        "anotations": {},
                    }
                    syncData.append(tmp)
                    i += 1
                    if self.debug:
                        per = (i * 100) // total
                        showText = filePath + " =====> " + objectName
                        process = "\r[UPLOAD_FILES][%3s%%]: %s" % (per, showText)
                        print(process)


                    j += 1
                    if j >= 1000:
                        j = 0
                        info = self.dataset.SyncDataToWeb(syncData)
                        if self.debug:
                            print(f"[UPLOAD_FILES] sync data to server, success:{info['succ']}, fail:{info['fail']}")

                        retInfo["succ"] += info["succ"]
                        retInfo["fail"] += info["fail"]
                        syncData = []

        if len(syncData) >= 0:#最后几个没同步的数据
            info = self.dataset.SyncDataToWeb(syncData)
            if self.debug:
                print(f"[UPLOAD_FILES] sync data to server, success:{info['succ']}, fail:{info['fail']}")
            retInfo["succ"] += info["succ"]
            retInfo["fail"] += info["fail"]

        return retInfo

    def UploadFileToDataset(self, filePath):
        '''
        Upload one file to dataset service directly
        :param filePath: local file path
        :return:
        '''
        pathInfo = os.path.split(filePath)
        parentDir = os.path.abspath(os.path.join(pathInfo[0], ".."))
        objectName = pathInfo[0].replace(parentDir, "").strip("/").strip("\\") + "/" + pathInfo[1]
        self.__UploadFileToDataset(filePath, objectName)

        if self.debug:
            print(f"[UPLOAD_ONE_FILE][{filePath}  =====> {objectName}]")

        syncData = {
            "ref_id": "",
            "name": os.path.basename(filePath),
            "path": self.filePrefix+ "/" + objectName,
            "size": int(util.getFileSize(filePath)),
            "md5": util.getFileMd5(filePath),
            "frame_id":"",
            "sensor":"",
            "meta": {},
            "anotations": {},
        }

        info = self.dataset.SyncDataToWeb([syncData])
        if self.debug:
            print(f"[UPLOAD_ONE_FILE] sync data to server, success:{info['succ']}, fail:{info['fail']}")

        return info

    def __UploadFileToDataset(self, filePath, objectName, overlay=False):
        """
        Upload one file to OSS
        :param filePath: local file path
        :param objectName: OSS object name
        :param overlay: overlay upload or not
        :return:
        """
        if not self.datasetId:
            self.RiseException()

        if overlay:
            return self.dataset.PutFileToDataset(objectName, filePath)

        db = UploadDb(self.datasetId)

        if db.findByFilePath(filePath, objectName):
            if self.debug:
                print(f"[UPLOAD_FILE]file: {filePath} already upload")
            db.close()
            return

        db.insertVal(filePath, objectName)
        db.close()

        try:
            res = self.dataset.PutFileToDataset(objectName, filePath)
        except:
            retry = 0
            while True:
                try:
                    res = self.dataset.PutFileToDataset(objectName, filePath)
                    break
                except Exception as e:
                    # print(e)
                    retry += 1
                    if self.debug:
                        print(f"[UPLOAD_FILES][{self.commitId}]Internet error, retry after 5s, attempts: {retry}")
                    time.sleep(5)
                    continue


        return res

    def AddFile(self, filepath, objectName="", referId="", metaData={}, sensor="", frameId="") -> File:
        """
        Create a File object which is used for visualize data
        :param filepath: local file path
        :param objectName: OSS object name
        :param referId: referId
        :param metaData: metaData
        :param sensor: sensor
        :param frameId: frameId
        :return:
        """
        if not self.datasetId:
            self.RiseException()

        if self.dataset.hostingMethod == self.dataset.HOSTING_METHOD_OWN_STORAGE:
            raise Exception(f"own hosting type dataset can not add files, you need use AddUrlFile method instead!")

        if not filepath:
            raise Exception(f"filepath must be set")

        objectName = objectName.replace("\\", "/")

        file = File(filepath, objectName.strip("/"), self.filePrefix, self.dataset.endpoint, self.dataset.datasetType)
        self.fileList.append(file)
        if self.debug:
            print(f"[ADD FILE] total:{len(self.fileList)} filepath:{filepath}, objectName:{file.objectPath}")

        if referId != "":
            if len(referId) > 64:
                raise Exception("referId length must less than 64!")

            if not type(referId) is str:
                raise Exception(f"referId must be a str, {type(referId)} gavin")
            file.referId = referId

        if metaData != {}:
            file.metadata = MetaData(metaData)

        if sensor != "":
            if not type(sensor) is str:
                raise Exception(f"sensor must be a str, {type(sensor)} gavin")
            file.sensor = sensor

        if frameId != "":
            if len(frameId) > 64:
                raise Exception("frameId length must less than 64!")

            if not type(frameId) is str:
                raise Exception(f"frameId must be a str, {type(frameId)} gavin")
            file.frameId = frameId

        return file

    def AddUrlFile(self, url, referId="", metaData={}, sensor="", frameId="", filename="", md5="", filesize=0) -> File:
        """
        Create a UrlFile object which is used for visualize data
        :param url: url of the file you would like to upload
        :param referId: referId
        :param metaData: metaData
        :param sensor: sensor
        :param frameId: frameId
        :param filename: optional, default will be basename of the url
        :param md5: optional, default will be empty sting
        :param filesize: optional, default will be 0
        :return:
        """
        if not self.datasetId:
            self.RiseException()

        if self.dataset.hostingMethod != self.dataset.HOSTING_METHOD_OWN_STORAGE:
            raise Exception(f"cloud-hosting type dataset can not add url files, you need use AddFile method instead!")

        if not url:
            raise Exception(f"url must be set")

        file = UrlFile(url,  self.dataset.datasetType)
        self.fileList.append(file)
        if self.debug:
            print(f"[ADD URL FILE] url:{url}")

        if referId != "":
            if not type(referId) is str:
                raise Exception(f"referId must be a str, {type(referId)} gavin")
            file.referId = referId

        if metaData != {}:
            file.metadata = MetaData(metaData)

        if sensor != "":
            if not type(sensor) is str:
                raise Exception(f"sensor must be a str, {type(sensor)} gavin")
            file.sensor = sensor

        if frameId != "":
            if not type(frameId) is str:
                raise Exception(f"frameId must be a str, {type(frameId)} gavin")
            file.frameId = frameId

        if filename != "":
            if not type(filename) is str:
                raise Exception(f"filename must be a str, {type(filename)} gavin")
            file.filename = filename

        if md5 != "":
            if not type(md5) is str:
                raise Exception(f"md5 must be a str, {type(md5)} gavin")
            file.md5 = md5

        if filesize != "":
            if not type(filesize) is int:
                raise Exception(f"filesize must be a int, {type(filesize)} gavin")
            file.filesize = filesize

        return file

    def Commit(self, commitId = ""):
        """
        commit a dataset data
        :param commitId: if set, this commit will add to the committed data before
        """
        if not self.datasetId:
            self.RiseException()

        db = CommitDb(commitId)
        if self.debug:
            if commitId:
                print(f"[COMMIT FILE] with commitId:{commitId}")
            else:
                print(f"[COMMIT FILE] without commitId!")
            print(f"[COMMIT FILE] begin insert data to local db")

        if len(self.fileList) <= 0:
            raise Exception("you should add 1 file at least")

        db.insertVal(self.fileList)

        if self.debug:
            print(f"[COMMIT FILE] end insert data to local db")

        db.close()

        self.commitFlag = True
        self.commitId = db.commitId
        return db.commitId

    def Upload(self, overlay=False, commitId = ""):
        """
        upload a committed dataset data and sync annotations to the testin-dataser server
        :param overlay: overlay upload to OSS or not
        :param commitId: if set, this commit will be upload and snync
        """
        if not self.datasetId:
            self.RiseException()

        if commitId != "":
            self.commitFlag = True
            self.commitId = commitId
            if self.debug:
                print(f"[UPLOAD_VISUALIZE_FILE] upload visualize files to dataset with committed data: {self.commitId}")

        if not self.commitFlag:
            self.commitId = self.Commit(commitId)
            if self.debug:
                print(f"[UPLOAD_VISUALIZE_FILE] upload visualize files to dataset without commit, auto commit:{self.commitId}")

        if not self.commitId:
            self.commitId = self.Commit(commitId)
            if self.debug:
                print(f"[UPLOAD_VISUALIZE_FILE] upload visualize files to dataset without commit, auto commit:{self.commitId}")

        db = CommitDb(self.commitId)
        allData = db.fetchAll()
        total = len(allData)
        if total <= 0:
            raise Exception("you should add 1 file at least")

        if self.debug:
            print(f"[UPLOAD_FILES]files total count: {total}")

        syncData = []
        i = 0
        j = 0
        retInfo = {'succ': 0, 'fail': 0}
        for data in allData:
            if data["filepath"] != "" and data["objectPath"] != "":
                self.__UploadFileToDataset(data["filepath"], data["objectPath"], overlay=overlay)

            tmp = {
                "ref_id":data["referid"],
                "name":data["filename"],
                "path":data["osspath"],
                "size":data["filesize"],
                "md5":data["md5"],
                "frame_id":data["frame_id"],
                "sensor":data["sensor"],
                "meta":json.loads(data["metadata"]),
                "anotations":json.loads(data["labeldata"]),
            }
            syncData.append(tmp)
            i += 1
            j += 1

            if self.debug:
                per = (j * 100) // total
                if self.dataset.hostingMethod == self.dataset.HOSTING_METHOD_OWN_STORAGE:
                    showText = data["osspath"]
                    process = f"\r[UPLOAD_URL_FILES][{self.commitId}][%3s%%]: %s" % (per, showText)
                else:
                    showText = data['filepath'] + " =====> " + data['objectPath']
                    process = f"\r[UPLOAD_FILES][{self.commitId}][%3s%%]: %s" % (per, showText)
                print(process)

            if i >= 100:
                i = 0
                info = self.dataset.SyncDataToWeb(syncData)
                if self.debug:
                    print(f"[UPLOAD_FILES] sync data to server, success:{info['succ']}, fail:{info['fail']}")
                retInfo["succ"] += info["succ"]
                retInfo["fail"] += info["fail"]
                syncData = []


        if len(syncData) >= 0:#最后几个没同步的数据
            info = self.dataset.SyncDataToWeb(syncData)
            if self.debug:
                print(f"[UPLOAD_FILES] sync data to server, success:{info['succ']}, fail:{info['fail']}")
            retInfo["succ"] += info["succ"]
            retInfo["fail"] += info["fail"]

        db.clearCache()

        return retInfo

    def GetData(self, offset=0, limit=1000, metaData={}, label="", sensor=""):
        """
        search data from testin-dataset service by criteria
        :param offset: offset of the search result
        :param limit: numbers of the search result
        :param metaData: which metadata you would like to use to search
        :param label: search by label
        :param sensor: search by sensor
        all above criteria will be juxtaposition
        """
        if limit > 1000:
            raise Exception("limit must less than 1000")

        return self.dataset.GetData(offset, limit, metaData=metaData, label=label, sensor=sensor, debug=self.debug)

    def GetFileAndLabel(self, fid="", referId=""):
        """
        search data from testin-dataset service by fid or ref_id
        :param fid: fid
        :param ref_id: referid you set when you upload data to testin-dataset service
        """
        if fid == "" and referId == "":
            raise Exception("fid or ref_id must be set")

        if fid:
            return self.dataset.GetFileAndLabelByFid(fid, debug=self.debug)

        return self.dataset.GetFileAndLabelByReferid(referId, debug=self.debug)





