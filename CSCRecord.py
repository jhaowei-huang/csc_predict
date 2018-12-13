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

interval = 60
url_xzcsc = "https://xzcsc.cyc.org.tw/api"
url_lzcsc = "https://lzcsc.cyc.org.tw/api"
url_cssc = "https://cssc.cyc.org.tw/api"
url_ngsc = "https://ngsc.cyc.org.tw/api"
fieldnames = ["year", "month", "date", "weekday", "hour", "minute", "gym", "swim"]

taipei = pytz.timezone('Asia/Taipei')

cssc = []
lzcsc = []
ngsc = []
xzcsc = []


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


def get_json_data(url):
    return json.load(urllib.request.urlopen(url))


def get_current_time():
    return datetime.datetime.now().astimezone(taipei)


def get_csc_number(csc, url):
    # url open
    data = get_json_data(url)
    # current date and time
    current_time = get_current_time()
    year = current_time.year
    month = current_time.month
    date = current_time.day
    weekday = current_time.isoweekday()
    hour = current_time.hour
    minute = current_time.minute

    # print
    print(csc, current_time.strftime("%Y-%m-%d %H:%M"), weekday, data['gym'][0], data['swim'][0])
    # return model object
    return {'year': year, 'month': month, 'date': date,
            'weekday': weekday, 'hour': hour, 'minute': minute,
            'gym': data['gym'][0], 'swim': data['swim'][0]}


# XZCSCRecords.create(year="2018", month=12, date=16, weekday=2, hour=14, minute=5, gym=16, swim=20)
def update_db():
    CSSCRecords.insert_many(cssc).execute()
    LZCSCRecords.insert_many(lzcsc).execute()
    NGSCRecords.insert_many(ngsc).execute()
    XZCSCRecords.insert_many(xzcsc).execute()

    cssc.clear()
    lzcsc.clear()
    ngsc.clear()
    xzcsc.clear()


if __name__ == '__main__':
    db.connect()
    db.create_tables([XZCSCRecords])
    db.create_tables([NGSCRecords])
    db.create_tables([LZCSCRecords])
    db.create_tables([CSSCRecords])

while 1:
    try:
        cssc.append(get_csc_number('cssc', url_cssc))
        lzcsc.append(get_csc_number('lzcsc', url_lzcsc))
        ngsc.append(get_csc_number('ngsc', url_ngsc))
        xzcsc.append(get_csc_number('xzcsc', url_xzcsc))

        # update database every 5 records
        if len(xzcsc) == 10:
            update_db()

        # wait for 60 seconds
        time.sleep(interval)
        print("=========================")
    except BaseException:
        print('發生錯誤，重新嘗試')
        time.sleep(10)
