import datetime
import json
import time
import os
import pytz
import urllib.request

from peewee import *
from dotenv import load_dotenv
from os.path import join, dirname

db_user = db_password = db_host = ""
import pandas

try:
    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)
    # accessing variables
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    db_host = os.getenv('DB_HOST')
except BaseException:
    print("讀取env檔案失敗")
    exit(1)

# connect to Google Cloud SQL database
db = MySQLDatabase('csc', user=db_user, password=db_password,
                   host=db_host, charset='utf8')


# database model define
class BaseModel(Model):
    class Meta:
        database = db


class CSCRecord(BaseModel):
    year = CharField(max_length=4)
    month = CharField(max_length=4)
    date = CharField(max_length=4)
    weekday = CharField(max_length=4)
    hour = CharField(max_length=4)
    minute = CharField(max_length=4)
    gym = IntegerField(default=0)
    swim = IntegerField(default=0)

    class Meta:
        database = db


class CSSCRecords(CSCRecord):
    class Meta:
        db_table = 'CSSCRecords'


class LZCSCRecords(CSCRecord):
    class Meta:
        db_table = 'LZCSCRecords'


class NGSCRecords(CSCRecord):
    class Meta:
        db_table = 'NGSCRecords'


class XZCSCRecords(CSCRecord):
    class Meta:
        db_table = 'XZCSCRecords'


def csv2list(csv):
    list = []
    for row in csv.values:
        list.append({'year': row[0], 'month': row[1], 'date': row[2],
                     'weekday': row[3], 'hour': row[4], 'minute': row[5],
                     'gym': row[6], 'swim': row[7]})

    return list


if __name__ == '__main__':
    db.connect()
    db.create_tables([XZCSCRecords])
    db.create_tables([NGSCRecords])
    db.create_tables([LZCSCRecords])
    db.create_tables([CSSCRecords])

# 讀取csv檔案
cssc_csv = pandas.read_csv('cssc.csv')
lzcsc_csv = pandas.read_csv('lzcsc.csv')
ngsc_csv = pandas.read_csv('ngsc.csv')
xzcsc_csv = pandas.read_csv('xzcsc.csv')

CSSCRecords.insert_many(csv2list(cssc_csv)).execute()
LZCSCRecords.insert_many(csv2list(lzcsc_csv)).execute()
NGSCRecords.insert_many(csv2list(ngsc_csv)).execute()
XZCSCRecords.insert_many(csv2list(xzcsc_csv)).execute()
