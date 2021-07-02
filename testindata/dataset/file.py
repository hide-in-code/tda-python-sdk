import os, sys
import hashlib

from testindata.dataset.metadata import MetaData
from testindata.dataset.labeldata import LabelData
from testindata.utils import util


class File():
    def __init__(self, filepath, objectName, filePrefix, endpoint, fileType):
        self.TYPE_IMAGE = 0
        self.TYPE_VIDEO = 1
        self.TYPE_AUDIO = 2
        self.TYPE_POINT_CLOUD = 3
        self.TYPE_FUSION_POINT_CLOUD = 4
        self.TYPE_POINT_CLOUD_SEMANTIC_SEGMENTATION = 5
        self.TYPE_TEXT = 6

        self.metadata = MetaData({})
        self.labeldata = LabelData()
        self.filePrefix = filePrefix
        self.fileType = fileType
        self.frameId = ""
        self.sensor = ""
        if objectName == "":
            # fatherDir = os.path.abspath(os.path.dirname(filepath))
            # parentDir = os.path.abspath(os.path.dirname(os.path.dirname(filepath)))
            # lastDir = fatherDir.replace(parentDir, "").strip("/").strip("\\")
            # self.objectPath = lastDir + "/" + os.path.basename(filepath)
            # self.osspath = self.filePrefix + "/" + self.objectPath
            self.objectPath = os.path.basename(filepath)
            self.osspath = self.filePrefix + "/" + self.objectPath
        else:
            if len(objectName) > 2048:
                raise Exception("objectName length must less than 2048!")
            self.objectPath = objectName.replace("\\", "/")
            self.osspath = self.filePrefix + "/" + self.objectPath

        if "http://" in endpoint or "https://" in endpoint:
            self.osspath = endpoint.rstrip("/") + "/" + self.osspath
        else:
            self.osspath = "http://" + endpoint.strip("/") + "/" + self.osspath


        self.referId = ""
        self.filepath = filepath
        self.filename = os.path.basename(filepath)
        if len(self.filename) > 256:
            raise Exception("file basename length must less than 256!")

        self.md5 = util.getFileMd5(self.filepath)
        self.filesize = int(util.getFileSize(self.filepath))
        self.type = util.getFiletype(self.filepath)

    #数据自查
    def SelfCheck(self):
        # if not self.referId:
        #     raise Exception(f"referid must be set!")

        if self.fileType == self.TYPE_FUSION_POINT_CLOUD:
            if not self.frameId:
                raise Exception(f"3D fusion data must set frameId")

            if not self.sensor:
                raise Exception(f"3D fusion data must set sensor")


    def SetMetaData(self, madedata):
        self.metadata = MetaData(madedata)

    def SetReferId(self, ref_id):
        if ref_id == "":
            raise Exception(f"referId can not be empty string!")
        self.referId = ref_id

    def SetFreamId(self, frame_id = ""):
        self.frameId = frame_id

    def SetSensor(self, sensor = ""):
        self.sensor = sensor

    def AddBox2D(self, box2d, label="", instance="", attrs={}):
        '''
        AddBox2D
        :param box2d:
        :param label:
        :param instance:
        :param attrs:
        :return:
        '''
        # 数据格式检查
        if not type(box2d) is dict:
            raise Exception(f"box must be a dict, {type(box2d)} gavin")

        keys = list(set(box2d.keys()))
        keys.sort()
        if keys != ['height', 'width', 'x', 'y']:
            raise Exception(f"box keys must be ['height', 'width', 'x', 'y'], {keys} gavin")

        data = {
            "x":float(box2d["x"]),
            "y":float(box2d["y"]),
            "width":float(box2d["width"]),
            "height":float(box2d["height"]),
        }

        self.labeldata.AddLabels(label=label, instance=instance, attrs=attrs, type="box2d", data=data)

    #添加椭圆
    def AddEllipse(self, ellipse, label="", instance="", attrs={}):
        '''
        AddEllipse
        :param ellipse:
        :param label:
        :param instance:
        :param attrs:
        :return:
        '''
        if not type(ellipse) is dict:
            raise Exception(f"ellipse must be a dict, {type(ellipse)} gavin")

        keys = list(set(ellipse.keys()))
        keys.sort()
        if keys != ['height', 'width', 'x', 'y']:
            raise Exception(f"ellipse keys must be ['height', 'width', 'x', 'y'], {keys} gavin")

        data = {
            "x":float(ellipse["x"]),
            "y":float(ellipse["y"]),
            "width":float(ellipse["width"]),
            "height":float(ellipse["height"]),
        }

        self.labeldata.AddLabels(label=label, instance=instance, attrs=attrs, type="ellipse", data=data)


    def AddPolygon(self, polygon, label="", instance="", attrs={}, index = 0):
        '''
        AddPolygon
        :param polygon:
        :param label:
        :param instance:
        :param attrs:
        :param index:
        :return:
        '''
        if not type(polygon) is list:
            raise Exception(f"polygon must be a list, {type(polygon)} gavin")

        data = []
        for poly in polygon:
            keys = list(set(poly.keys()))
            if keys != ["x", "y"] and keys != ["y", "x"]:
                raise Exception(f"poly point keys must be ['x', 'y'], {list(set(poly.keys()))} gavin")
            data.append({"x":float(poly["x"]), "y":float(poly["y"])})

        self.labeldata.AddLabels(label=label, instance=instance, attrs=attrs, type="polygon", data=data, index=index)

    def AddLine(self, line, label="", instance="", attrs={}):
        '''
        AddLine
        :param line:
        :param label:
        :param instance:
        :param attrs:
        :return:
        '''
        if not type(line) is list:
            raise Exception(f"line must be a list, {type(line)} gavin")

        data = []
        for point in line:
            keys = list(set(point.keys()))
            if keys != ["x", "y"] and keys != ["y", "x"]:
                raise Exception(f"line point keys must be ['x', 'y'], {keys} gavin")
            data.append({"x": float(point["x"]), "y": float(point["y"])})

        self.labeldata.AddLabels(label=label, instance=instance, attrs=attrs, type="line", data=data)


    def AddCurve(self, curve, label="", instance="", attrs={}):
        '''
        AddCurve
        :param curve:
        :param label:
        :param instance:
        :param attrs:
        :return:
        '''
        if not type(curve) is list:
            raise Exception(f"curve must be a list, {type(curve)} gavin")

        data = []
        for point in curve:
            keys = list(set(point.keys()))
            if keys != ["x", "y"] and keys != ["y", "x"]:
                raise Exception(f"curve point keys must be ['x', 'y'], {keys} gavin")
            data.append({"x": float(point["x"]), "y": float(point["y"])})

        self.labeldata.AddLabels(label=label, instance=instance, attrs=attrs, type="curve", data=data)


    def AddPoint(self, point, label="", instance="", attrs={}):
        '''
        AddPoint
        :param point:
        :param label:
        :param instance:
        :param attrs:
        :return:
        '''
        if not type(point) is dict:
            raise Exception(f"curve must be a list, {type(point)} gavin")

        keys = list(set(point.keys()))
        if keys != ["x", "y"] and keys != ["y", "x"]:
            raise Exception(f"curve point keys must be ['x', 'y'], {keys} gavin")

        data = {"x": float(point["x"]), "y": float(point["y"])}
        self.labeldata.AddLabels(label=label, instance=instance, attrs=attrs, type="point", data=data)


    def AddParallel(self, parallel, label="", instance="", attrs={}):
        '''
        AddParallel
        :param parallel:
        :param label:
        :param instance:
        :param attrs:
        :return:
        '''
        if not type(parallel) is list:
            raise Exception(f"parallel must be a list, {type(parallel)} gavin")

        if len(parallel) != 4:
            raise Exception(f"parallel points numbers must be 4, {len(parallel)} gavin")

        data = []
        for point in parallel:
            keys = list(set(point.keys()))
            if keys != ["x", "y"] and keys != ["y", "x"]:
                raise Exception(f"parallel point keys must be ['x', 'y'], {keys} gavin")
            data.append({"x": float(point["x"]), "y": float(point["y"])})

        self.labeldata.AddLabels(label=label, instance=instance, attrs=attrs, type="parallel", data=data)


    def AddBox3D(self, box3d, label="", instance="", attrs={}):
        '''
        AddBox3D
        :param box3d:
        :param label:
        :param instance:
        :param attrs:
        :return:
        '''
        # 数据格式检查
        if not type(box3d) is dict:
            raise Exception(f"box3D must be a dict, {type(box3d)} gavin")

        keys = list(set(box3d.keys()))
        keys.sort()
        if keys != ['position', 'rotation', 'scale']:
            raise Exception(f"box3D keys must be ['position', 'rotation', 'scale'], {keys} gavin")

        data = {
            "position":{
                "x":float(box3d["position"]["x"]),
                "y":float(box3d["position"]["y"]),
                "z":float(box3d["position"]["z"]),
            },
            "rotation":{
                "x":float(box3d["rotation"]["x"]),
                "y":float(box3d["rotation"]["y"]),
                "z":float(box3d["rotation"]["z"]),
            },
            "scale":{
                "x":float(box3d["scale"]["x"]),
                "y":float(box3d["scale"]["y"]),
                "z":float(box3d["scale"]["z"]),
            }
        }

        self.labeldata.AddLabels(label=label, instance=instance, attrs=attrs, type="box3d", data=data)

    def AddCuboid(self, cuboid, label="", instance="", attrs={}):
        '''
        AddCuboid
        :param cuboid:
        :param label:
        :param instance:
        :param attrs:
        :return:
        '''
        # 数据格式检查
        if not type(cuboid) is dict:
            raise Exception(f"cuboid must be a dict, {type(cuboid)} gavin")

        keys = list(set(cuboid.keys()))
        keys.sort()
        if keys != ['back', 'front']:
            raise Exception(f"cuboid keys must be ['back', 'front'], {keys} gavin")

        data = {
            "back":[],
            "front":[],
        }

        if len(cuboid["back"]) != 4:
            raise Exception(f"cuboid back length must be 4, {len(cuboid['back'])} gavin")

        for point in cuboid["back"]:
            keys = list(set(point.keys()))
            if keys != ["x", "y"] and keys != ["y", "x"]:
                raise Exception(f"cuboid point keys must be ['x', 'y'], {keys} gavin")
            data["back"].append({"x": float(point["x"]), "y": float(point["y"])})

        if len(cuboid["front"]) != 4:
            raise Exception(f"cuboid front length must be 4, {len(cuboid['front'])} gavin")

        for point in cuboid["front"]:
            keys = list(set(point.keys()))
            if keys != ["x", "y"] and keys != ["y", "x"]:
                raise Exception(f"cuboid point keys must be ['x', 'y'], {keys} gavin")
            data["front"].append({"x": float(point["x"]), "y": float(point["y"])})

        self.labeldata.AddLabels(label=label, instance=instance, attrs=attrs, type="cuboid", data=data)

    def AddSideCuboid(self, sideCuboid, label="", instance="", attrs={}):
        '''
        AddSideCuboid
        :param sideCuboid:
        :param label:
        :param instance:
        :param attrs:
        :return:
        '''
        # 数据格式检查
        if not type(sideCuboid) is dict:
            raise Exception(f"box3D must be a dict, {type(sideCuboid)} gavin")

        keys = list(set(sideCuboid.keys()))
        keys.sort()
        if keys != ['back', 'front']:
            raise Exception(f"box3D keys must be ['back', 'front'], {keys} gavin")

        data = {
            "back":[],
            "front":[],
        }

        if len(sideCuboid["back"]) != 2:
            raise Exception(f"cuboid back length must be 4, {len(sideCuboid['back'])} gavin")

        for point in sideCuboid["back"]:
            keys = list(set(point.keys()))
            if keys != ["x", "y"] and keys != ["y", "x"]:
                raise Exception(f"cuboid point keys must be ['x', 'y'], {keys} gavin")
            data["back"].append({"x": float(point["x"]), "y": float(point["y"])})

        if len(sideCuboid["front"]) != 4:
            raise Exception(f"cuboid front length must be 4, {len(sideCuboid['front'])} gavin")

        for point in sideCuboid["front"]:
            keys = list(set(point.keys()))
            if keys != ["x", "y"] and keys != ["y", "x"]:
                raise Exception(f"cuboid point keys must be ['x', 'y'], {keys} gavin")
            data["back"].append({"x": float(point["x"]), "y": float(point["y"])})

        self.labeldata.AddLabels(label=label, instance=instance, attrs=attrs, type="side_cuboid", data=data)

