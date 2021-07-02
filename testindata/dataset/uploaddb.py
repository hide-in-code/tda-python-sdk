import os
import sqlite3
import shutil


class UploadDb():
    def __init__(self, datasetId):
        self.datasetId = datasetId

        home = "USERPROFILE" if os.name == "nt" else "HOME"
        self.configDir = os.path.join(os.environ[home], ".tda/upload")
        if not os.path.exists(self.configDir):
            os.makedirs(self.configDir)

        self.dbFile = os.path.join(self.configDir, self.datasetId + ".db")
        if not os.path.exists(self.dbFile):
            self.conn = sqlite3.connect(self.dbFile)
            self.cur = self.conn.cursor()
            createSql = '''CREATE TABLE UPLOAD 
                              (
                                num INTEGER PRIMARY KEY,
                                filepath CHAR(1024)  NOT NULL,
                                object CHAR(1024) NOT NULL
                               );'''
            self.cur.execute(createSql)
            self.conn.close()

    def close(self):
        self.conn.close()

    def insertVal(self, filepath="", osspath=""):
        if filepath != "" and osspath != "":
            self.conn = sqlite3.connect(self.dbFile)
            self.cur = self.conn.cursor()
            self.cur.execute("INSERT INTO UPLOAD (num, filepath, object) values (?, ?, ?)", (None, filepath, osspath))
            self.conn.commit()
            self.conn.close()

    def findByFilePath(self, filepath="", osspath=""):
        if filepath != "" and osspath != "":
            self.conn = sqlite3.connect(self.dbFile)
            self.cur = self.conn.cursor()
            res = self.cur.execute(f"SELECT * FROM UPLOAD WHERE filepath = '{filepath}' and object = '{osspath}'")
            if len(res.fetchall()) >= 1:
                return True

        return False


