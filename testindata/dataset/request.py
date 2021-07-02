import requests
import json

class Request:
    def __init__(self, T_key, dataset_id, host):
        self.T_key = T_key
        self.dataset_id = dataset_id
        self.host = ""
        if host:
            self.host = host.rstrip("/")
            self.API_ADDRESS_PREFIX = f"{self.host}/api/v1/"
        else:
            #todo:设置线上服务地址
            raise Exception("the host to the testin-dataset server must be set!")

    def RiseException(self, response_text):
        raise Exception("error msg from server: " + response_text)

    def GetAccess(self):
        api = f'{self.API_ADDRESS_PREFIX}dataset/{self.dataset_id}'
        headers = {"T-Key":self.T_key}
        res = requests.request("GET", api, headers=headers)
        try:
            resData = json.loads(res.text)
        except:
            raise Exception(res.content)


        if resData['code'] != "":
            self.RiseException(res.text)

        ret = {
            # "access_key":resData["data"]["access_key"],
            # "secret_key":resData["data"]["access_token"],
            "hosting_method":resData["data"]["hosting_method"],
            "upload_token":"",
            "endpoint":resData["data"]["endpoint"],
            "file_path": "",
            "bucket":resData["data"]["bucket"],
            "oss_type":resData["data"]["oss_type"],
            "dataset_type":resData["data"]["dataset_type"],
        }

        if "upload_token" in resData["data"].keys():
            ret["upload_token"] = resData["data"]["upload_token"]

        return ret

    def GetUploadUrl(self, object):
        api = f'{self.API_ADDRESS_PREFIX}dataset/{self.dataset_id}/get-upload-url'
        headers = {"T-Key": self.T_key, "Content-Type":"application/json"}

        data1 = {
            "object":object
        }

        res = requests.post(api, headers=headers, data=json.dumps(data1))
        try:
            resData = json.loads(res.text)
        except:
            raise Exception(res.content)

        if resData['code'] != "":
            self.RiseException(res.text)

        ret = {
            "url":resData["data"]["url"]
        }

        return ret


    def Upload(self, data):
        api = f'{self.API_ADDRESS_PREFIX}dataset/{self.dataset_id}/upload'
        headers = {"T-Key": self.T_key, "Content-Type":"application/json"}

        res = requests.post(api, headers=headers, data=json.dumps(data))
        try:
            resData = json.loads(res.text)
        except:
            raise Exception(res.content)

        if resData['code'] != "":
            self.RiseException(res.text)

        ret = {
            "succ": resData["data"]["succ"],
            "fail": resData["data"]["fail"],
        }

        return ret

    def Delete(self, referId):
        api = f'{self.API_ADDRESS_PREFIX}dataset/{self.dataset_id}/fidloc/{referId}'
        headers = {"T-Key": self.T_key}
        res = requests.delete(api, headers=headers)

        try:
            resData = json.loads(res.text)
        except:
            raise Exception(res.content)

        if resData['code'] != "":
            self.RiseException(res.text)

        ret = {
            "file_num": resData["data"]["file_num"],
            "anotation_num": resData["data"]["anotation_num"],
        }

        return ret

    def GetData(self, offset, limit, metaData={}, label="", sensor=""):
        api = f'{self.API_ADDRESS_PREFIX}dataset/{self.dataset_id}/data'
        headers = {"T-Key": self.T_key, "Content-Type": "application/json"}
        data = {
            "offset":offset,
            "limit":limit,
            "meta":metaData,
            "label":label,
            "sensor":sensor,
        }

        res = requests.post(api, headers=headers, data=json.dumps(data))
        try:
            resData = json.loads(res.text)
        except:
            raise Exception(res.content)

        if resData['code'] != "":
            self.RiseException(res.text)


        return resData["data"]

    def GetFileAndLabelByFid(self, fid):
        api = f'{self.API_ADDRESS_PREFIX}dataset/{self.dataset_id}/fidloc/{fid}'
        headers = {"T-Key": self.T_key}
        res = requests.request("GET", api, headers=headers)
        try:
            resData = json.loads(res.text)
        except:
            raise Exception(res.content)

        if resData['code'] != "":
            self.RiseException(res.text)

        return resData["data"]


    def GetFileAndLabelByReferid(self, referId):
        api = f'{self.API_ADDRESS_PREFIX}dataset/{self.dataset_id}/refloc/{referId}'
        headers = {"T-Key": self.T_key}
        res = requests.request("GET", api, headers=headers)
        try:
            resData = json.loads(res.text)
        except:
            raise Exception(res.content)

        if resData['code'] != "":
            self.RiseException(res.text)

        return resData["data"]

    def Update(self, fid, data={}):
        api = f'{self.API_ADDRESS_PREFIX}dataset/{self.dataset_id}/fidloc/{fid}/update'
        headers = {"T-Key": self.T_key, "Content-Type": "application/json"}

        res = requests.request("POST", api, headers=headers, data=json.dumps(data))
        try:
            resData = json.loads(res.text)
        except:
            raise Exception(res.content)

        if resData['code'] != "":
            self.RiseException(res.text)

        return resData["data"]
