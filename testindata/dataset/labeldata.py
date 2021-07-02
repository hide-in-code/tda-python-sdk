import json

class LabelData():
    def __init__(self):
        self.labels = []

    def AddLabels(self, label="", instance="", attrs={}, type="", data={}, index=""):
        if label == "":
            raise Exception(f"label can not be empty!")

        label = {
            "label":label,
            "instance":instance,
            "type":type,
            "attrs":attrs,
            "data":data,
        }

        if index:
            label["index"] = index

        self.labels.append(label)

    def ToString(self):
        return json.dumps(self.labels)

    def LoadFromList(self, jsonData):
        if not type(jsonData) is list:
            raise Exception(f"Labeldata load from list error, {type(jsonData)} gavin")

        for data in jsonData:
            keys = list(data.keys())
            keys.sort()
            if keys != ['ano_id', 'attrs', 'data', 'index', 'instance', 'label', 'type'] and keys != ['ano_id', 'attrs', 'data', 'instance', 'label', 'type']:
                raise Exception(f"Labeldata load from list error, label data keys must be ['ano_id', 'attrs', 'data', 'index', 'instance', 'label', 'type'] or ['ano_id', 'attrs', 'data', 'instance', 'label', 'type']")

        self.labels = jsonData



