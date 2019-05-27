#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Charles on 2018/6/16
# Function: 
from pymongo import MongoClient
DB_INSTANCE = None


class DBUtil:
    # __metaclass__ = Singleton
    __instance = None

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = super(DBUtil, cls).__new__(cls, *args, **kwargs)
        return cls.__instance

    def __init__(self, host="127.0.0.1", port=27017, db_name="Huobi", user=None, password=None):
        self._host = host
        self._port = port
        self._db_name = db_name
        self._client = None
        self._db = None
        self._user = user
        self._password = password

    def init(self):
        print("init database!")
        try:
            self._client = MongoClient(self._host, self._port)
            self._db = self._client[self._db_name]
            if self._user and self._password:
                self._db.authenticate(self._user, self._password)
            print("init database successfully!")
            return True
        except Exception as e:
            print("Catch an exception duration database connection. exception: %s" % e)
            self.close_db()
            return False
            #raise (Exception("数据库连接失败！"))

    def close(self):
        print("close database!")
        if self._client:
            self._client.close()
        self._client = None
        self._db = None
        return True

    def is_valid(self):
        return self._client and self._db

    @property
    def db(self):
        return self._db


if __name__ == '__main__':
    dbutil = DBUtil()
    dbutil.init()
    clc = dbutil.db.get_collection("test")
    clc.insert_one({"user": "charles1", "age": 30})
    dbutil.close()
