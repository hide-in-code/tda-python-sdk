import click
import json
import os
import requests
import testindata

from testindata.TDA import TDA
from testindata.utils import util

def _config_filepath():
    home = "USERPROFILE" if os.name == "nt" else "HOME"
    configDir = os.path.join(os.environ[home], ".tda/")
    if not os.path.exists(configDir):
        os.makedirs(configDir)

    return os.path.join(configDir, "tda.conf")


def _noLoginMessage():
    click.echo(" you have not set your account yet, to set your account with:\n")
    click.echo("  tda config <access_key> [host] \n")
    click.echo(" more about this command, use：\n")
    click.echo("  tda config --help")
    exit()


def _check():
    configFile = _config_filepath()
    if not os.path.exists(configFile):
        _noLoginMessage()

    with open(configFile, "r") as config:
        try:
            jsonObj = json.load(config)
        except:
            _noLoginMessage()

        if "access_key" not in jsonObj.keys():
            _noLoginMessage()

        if jsonObj["access_key"] == None or jsonObj["access_key"] == "":
            _noLoginMessage()

    return True


def _getConf():
    configFile = _config_filepath()
    if _check():
        with open(configFile, "r") as config:
            return json.load(config)

def _download(url, savePath):
    res = requests.get(url)
    with open(savePath, 'wb') as f:
        f.write(res.content)

def printVersion(ctx, param, value):
    if hasattr(testindata, "VERSION"):
        click.echo(f'TDA Version {testindata.VERSION}')
        ctx.exit()
    click.echo('TDA Version 0.0.1')
    ctx.exit()

@click.group()
@click.option("-ak", "--accessKey", 'access_key', default="", help="access key to Testin dataset system, see: https://dataset.testin.cn/accesskey")
@click.option("-host", "--host", 'host', default="https://dataset.testin.cn/", help="domain name that access to dataset system you would like to operate, default will be: https://dataset.testin.cn/")
@click.option('--debug/--no-debug', default=False, help="using debug mod or not, default is False")
@click.pass_context
def main(ctx, access_key, host, debug):
    """ testin dataset system management tool  """
    info = {
        "access_key": access_key,
        "host": host,
        "DEBUG": debug
    }

    _tda = None

    if access_key == "":
        configFile = _config_filepath()
        if os.path.exists(configFile):
            with open(configFile, "r", encoding="utf-8") as cf:
                if cf.read() != "":
                    info = _getConf()
                    info["DEBUG"] = debug

    if info["access_key"] != "":
        _tda = TDA(info["access_key"], info["host"])
        if info["DEBUG"]:
            _tda.Debug()

    ctx.obj = _tda



@main.command()
@click.option("-ak", "--accessKey", 'access_key', default="", help="access key to Testin dataset system, see: https://dataset.testin.cn/accesskey")
@click.option("-host", "--host", 'host', default="https://dataset.testin.cn/", help="domain name that access to dataset system you would like to operate, default will be: https://dataset.testin.cn/")
def config(access_key, host):
    """ setting your account """
    configFile = _config_filepath()
    if access_key == "":
        if _check():
            click.echo("logged user:")
            print(_getConf())
            exit()
    else:
        conf = {
            "access_key": access_key,
            "host": host,
        }
        with open(configFile, "w") as config:
            json.dump(conf, config)
            click.echo("login success")
            print(conf)
            exit()

@main.command()
@click.option("-ds", "--datasetId", 'ds_id', default="", help="the dataset you wolud like to download")
@click.option("-save", "--saveDir", 'save_dir', default="", help="save path for downloaded files")
@click.pass_context
def download(ctx, ds_id, save_dir):
    """ download dataset data """
    if ctx.obj == None:
        _noLoginMessage()

    ctx.obj.SetDataset(ds_id)
    saveDir = os.path.join(save_dir, ds_id)
    if not os.path.exists(saveDir):
        os.makedirs(saveDir)

    page = 0
    limit = 100
    fileTotal = 1
    while True:
        offset = page * limit
        fileData = ctx.obj.GetData(offset, limit)
        if len(fileData["files"]) <= 0:
            break
        page += 1
        for file in fileData["files"]:
            picPath = file.path.split(ds_id)[1].strip("/")
            basename = os.path.basename(picPath)
            tmpPath = picPath.replace(basename, "").strip("/")
            fileDir = os.path.join(saveDir, tmpPath)
            if not os.path.exists(fileDir):
                os.makedirs(fileDir)
            filePath = os.path.join(fileDir, tmpPath, basename)
            if os.path.exists(filePath):
                fmd5 = util.getFileMd5(filePath)
                if fmd5 != file.md5:
                    _download(file.url, filePath)
                    if ctx.obj.debug:
                        print(f"[SAVE_FILE]file total: {fileTotal}, truncate file, redo: [{filePath}]")
                else:
                    if ctx.obj.debug:
                        print(f"[SAVE_FILE]file total: {fileTotal}, file already exist: [{filePath}]")
            else:
                _download(file.url, filePath)
                if ctx.obj.debug:
                    print(f"[SAVE_FILE]file total: {fileTotal}, file download and save: [{filePath}]")

            labelData = ctx.obj.GetFileAndLabel(fid=file.fid)
            jsonname = ".".join(basename.split(".")[:-1])
            jsonPath = os.path.join(fileDir, tmpPath, jsonname + "_label.json")
            with open(jsonPath, "w", encoding="utf-8") as jf:
                json.dump(labelData.anotations.labels, jf)
                if ctx.obj.debug:
                    print(f"[SAVE_LABEL]file total: {fileTotal}, save label data: [{jsonPath}]")

            fileTotal += 1

    if ctx.obj.debug:
        print("done!")

if __name__ == '__main__':
    main(obj={})



