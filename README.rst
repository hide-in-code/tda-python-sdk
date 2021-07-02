testindata Python SDK
=====================

`云测数据 <http://ai.testin.cn/>`__\ 数据集管理系统python SDK

准备工作
--------

-  从私有化部署产品或者SAAS服务系统中创建好适合您需求的数据集。
-  从系统中获取您用于身份认证使用的「AccessKey」。
-  通过SDK可以对您的数据进行上传和读取的操作，并能使用数据集管理系统提供的数据格式对您的数据做可视化展示。

安装
----

.. code:: console

    pip install testindata

    使用本SDK须Python 3.6或更高版本。

快速入门
--------

上传文件并添加可视化数据
~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    from testindata.TDA import TDA

    #AccessKey 可以从系中对应的位置获取
    AccessKey = "your_AccessKey"

    #datasetId 从系统对应位置获取
    datasetId = "ds_yourdatasetId"

    #实例化全局TDA操作对象, 如果您使用的是SAAS服务，无需设置host，如果您使用的是私有化部署产品，则您需要指明您的数据集服务ip地址
    tda = TDA(AccessKey, host="https://dataset.testin.cn/")

    #设置要操作的数据集
    tda.SetDataset(datasetId)

上传文件并添加可视化数据
~~~~~~~~~~~~~~~~~~~~~~~~

云测数据数据集管理系统提供了数据可视化的功能，您可以将数据转换为系统规定的数据格式，并由sdk上传至系统，即可从系统中查看可视化的数据。

.. code:: python

    from testindata.TDA import TDA

    AccessKey = "0fbe149adf07e5f4afa01a7a4e787fde"
    host = "xx.xx.xx.xx"

    tda = TDA(AccessKey, host=host)

    #进入debug模式，该模式下sdk会打印出执行信息
    tda.Debug()

    dataset = tda.SetDataset("ds_******")

    metaData = {
        "metaKey1":"metaVal1",
        "metaKey2":"metaVal2",
        "metaKey3":"metaVal3",
    }

    #添加一个用于可视化的文件
    file = tda.AddFile("/path/to/your/fileRootPath/11.jpg", referId="myTestRefId", metaData=metaData)

    box = {
        "x": 10,
        "y": 10,
        "width": 100,
        "height": 100,
    }

    label = "myTestLabelName"

    attr = {
        "attrKey1":"attrVal1",
        "attrKey2":"attrVal2",
        "attrKey3":"attrVal3",
    }

    #为该文件添加一个标注结果
    file.AddBox2D(box, label=label, attrs=attr)

    #上传该文件
    print(tda.Upload())

进入DEBUG模式
~~~~~~~~~~~~~

.. code:: python

    tda = TDA(AccessKey, debug=True) 或者 tda.debug()

    在debug模式下，sdk会输出很多执行过程中的信息，以方便您监控整个程序的执行过程。

获取文件列表数据
~~~~~~~~~~~~~~~~

.. code:: python

    filesData = tda.GetData(offset=1000, limit=1000)

    for file in fileData["files"]:   
        print(file.fid)
        print(file.referId)
        print(file.meta)
        print(file.md5)
        print(file.path)
        
        for label in file.labeldata.labels:
            print(label)

    offset默认从0开始，limit最大值为1000

获取标注结果
~~~~~~~~~~~~

.. code:: python

    #根据fid 获取标注结果
    file = tda.GetFileAndLabel(fid="fs_N7T02AgYJGF6yxAbk75R")

    #根据ref_id获取标注结果
    file = tda.GetFileAndLabel(ref_id="myreferId1")

    print(file.fid)
    print(file.referId)
    print(file.meta)
    print(file.md5)
    print(file.path)

    for label in file.labeldata.labels:
        print(label)

    fid
    是数据集系统存储文件的唯一id，该id可以唯一定位一个上传文件；ref\_id是需要您自己维护的一个用于唯一定位资源的id，我们强烈建议您设置资源文件的ref\_id，用于关联您自己的业务系统。

更多信息查看\ `sdk官方文档地址 <https://testindata.gitbook.io/dataset/python-sdk/untitled>`__
