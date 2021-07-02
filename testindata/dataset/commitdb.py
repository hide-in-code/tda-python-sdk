import sys, os
import sqlite3
import shutil

from testindata.utils import util
from testindata.dataset.file import File

class CommitDb():
    def __init__(self, commitId=""):
        self.commitId = commitId

        self.newDbFlag = False
        if self.commitId  == "":#新db
            self.commitId = "commit_" + util.getRandomSet(32)
            self.newDbFlag = True

        home = "USERPROFILE" if os.name == "nt" else "HOME"
        configDir = os.path.join(os.environ[home], ".tda/")
        if not os.path.exists(configDir):
            os.makedirs(configDir)

        self.dbDir = os.path.join(configDir, self.commitId)
        if not os.path.exists(self.dbDir):
            os.makedirs(self.dbDir)

        self.dbFile = os.path.join(self.dbDir, self.commitId + ".db")
        if not os.path.exists(self.dbFile) and not self.newDbFlag:
            raise Exception(f"commit db [{self.commitId}] not exist, have you ever commited them?")

        if not os.path.exists(self.dbFile) and self.newDbFlag:
            self.initDb()

    def initDb(self):
        self.conn = sqlite3.connect(self.dbFile)
        self.cur = self.conn.cursor()

        if self.newDbFlag:
            createSql = '''CREATE TABLE TDADATA
                   (filepath CHAR(1024) PRIMARY KEY NOT NULL,
                    osspath CHAR(1024) NOT NULL,
                    objectPath CHAR(1024) NOT NULL,
                    filename CHAR(521) NOT NULL,
                    md5 CHAR(32) NOT NULL,
                    frame_id CHAR(512) NOT NULL,
                    sensor CHAR(32) NOT NULL,
                    referid CHAR(128) NOT NULL,
                    filesize INT NOT NULL,
                    metadata CHAR(1024) NOT NULL,
                    labeldata BLOB NOT NULL
                   );'''
            self.cur.execute(createSql)

        self.conn.close()

    def close(self):
        self.conn.close()

    def getDataByFilepath(self, filepath):
        self.conn = sqlite3.connect(self.dbFile)
        self.cur = self.conn.cursor()
        res = self.cur.execute(f"SELECT * FROM TDADATA WHERE filepath = '{filepath}'")
        return res


    def insertVal(self, data = []):
        self.conn = sqlite3.connect(self.dbFile)
        self.cur = self.conn.cursor()

        for file in data:
            file.SelfCheck()            
            self.cur.execute(f"SELECT * FROM TDADATA WHERE filepath = '{file.filepath}'")
            res = self.cur.fetchone()
            if res != None:
                print(file.filepath + " already commited, continue! you can updload them whenever you want.")
                continue
            try:
                self.cur.execute("INSERT INTO TDADATA (filepath, osspath, objectPath, filename, md5, frame_id, sensor, referid, filesize, metadata, labeldata) VALUES (?,?,?,?,?,?,?,?,?,?,?)", (str(file.filepath), str(file.osspath), str(file.objectPath), str(file.filename), str(file.md5), str(file.frameId), str(file.sensor), str(file.referId), str(file.filesize), str(file.metadata.ToString()), str(file.labeldata.ToString())))
            except:
                raise Exception(f"failed in insert into tdadata, values:{str(file.filepath)}, {str(file.osspath)}, {str(file.objectPath)}, {str(file.filename)}, {str(file.md5)}, {str(file.frameId)}, {str(file.sensor)}, {str(file.referId)}, {str(file.filesize)}, {str(file.metadata.ToString())}, {str(file.labeldata.ToString())}")

        self.conn.commit()
        self.conn.close()


    def fetchAll(self):
        ret = []
        self.conn = sqlite3.connect(self.dbFile)
        self.cur = self.conn.cursor()
        sql = f"SELECT * FROM TDADATA;"
        res = self.cur.execute(sql)
        for row in res:
            tmp = {
                "filepath":row[0],
                "osspath":row[1],
                "objectPath":row[2],
                "filename":row[3],
                "md5":row[4],
                "frame_id":row[5],
                "sensor":row[6],
                "referid":row[7],
                "filesize":row[8],
                "metadata":row[9],
                "labeldata":row[10],
            }

            ret.append(tmp)
        self.conn.close()
        return ret

    def clearCache(self):
        shutil.rmtree(self.dbDir)





