import json

class MetaData():
    def __init__(self, metadata):
        # 数据格式检查
        if not type(metadata) is dict:
            raise Exception(f"metadata must be a dict, {type(metadata)} gavin")

        for k, v in metadata.items():
            if "/" in k:
                raise Exception(f"metadata keys can not contain special char:'/'")

        self.meta = metadata

    def ToString(self):
        return json.dumps(self.meta)
