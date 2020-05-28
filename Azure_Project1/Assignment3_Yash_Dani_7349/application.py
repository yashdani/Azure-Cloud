# Yash Dani

from flask import Flask, render_template, request
from datetime import datetime
from json import loads, dumps
import pypyodbc
# import pandas as pd
import random
import time
import redis
import hashlib

app = Flask(__name__, static_url_path='', template_folder='static')

server = 'abc.database.windows.net'
database = 'cloud'
username = 'abc@abc'
password = 'cloud@123'
driver= '{ODBC Driver 17 for SQL Server}'
# cnxn = pypyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1443;DATABASE='+database+';UID='+username+';PWD='+ password)

myHostname = "abc.redis.cache.windows.net"
myPassword = "veJESHUJAnTL1i2oPYrTr0aZtjFdtogSFAdiL9n3FI4="


r = redis.StrictRedis(host=myHostname, port=6380,password=myPassword,ssl=True)

@app.route('/')
def hello_world():
    conn = pypyodbc.connect('DRIVER=' + driver + ';SERVER=' + server + ';PORT=1443;DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
    lstDictionaryData = []
    cursor = conn.cursor()
    startTime = time.time()
    # query = "SELECT TOP 20 time, latitude, longitude, mag, place FROM earthquake_new"
    query = "Select * from earthquake_new"
    # print(query)
    cursor.execute(query)
    
    endTime = time.time()
    row = cursor.fetchone()
    while row:
        lstDictionaryData.append(row)
        # print("hi!" + str(row))
        row = cursor.fetchone()
    # return "hello!!"
    conn.close()
    executionTime = (endTime - startTime) * 1000
    return render_template('index.html', tableData=lstDictionaryData, tableDataLen=lstDictionaryData.__len__(), executionTime=executionTime)

@app.route('/createtable')
def createTable():
    lstDictionaryData = []
    conn = pypyodbc.connect('DRIVER=' + driver + ';SERVER=' + server + ';PORT=1443;DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
    cursor = conn.cursor()
    # query = "CREATE TABLE dbo.all_month (\"time\" datetime, \"latitude\" FLOAT, \"longitude\" FLOAT, \"depth\" FLOAT, \"mag\" FLOAT, \"magType\" TEXT, \"nst\" INT, \"gap\" INT, \"dmin\" FLOAT, \"rms\" FLOAT, \"net\" TEXT, \"id\" TEXT, \"updated\" datetime, \"place\" TEXT, \"type\" TEXT, \"horontalError\" FLOAT, \"depthError\" FLOAT, \"magError\" FLOAT, \"magNst\" INT, \"status\" TEXT, \"locationSource\" TEXT, \"magSource\" TEXT)"
    query = "CREATE TABLE utacloud.dbo.all_month(time DATETIME,latitude FLOAT,longitude FLOAT,depth FLOAT,mag FLOAT,magType TEXT,nst INT,gap INT,dmin FLOAT,rms FLOAT,net TEXT,id TEXT,updated DATETIME,place TEXT,type TEXT,horontalError FLOAT,depthError FLOAT,magError FLOAT,magNst INT,status TEXT,locationSource TEXT,magSource TEXT)"
    # print(query)
    startTime = time.time()
    # cursor.execute(query)
    cursor.execdirect(query)
    print(cursor)
    cursor.execdirect("CREATE INDEX all_month_mag__index ON utacloud.dbo.earthquake_new(mag)")
    cursor.execdirect("CREATE INDEX all_month_lat__index ON utacloud.dbo.earthquake_new(latitude)")
    cursor.execdirect("CREATE INDEX all_month_long__index ON utacloud.dbo.earthquake_new(longitude)")
    endTime = time.time()
    conn.close()
    executionTime = (endTime - startTime) * 1000
    return render_template('index.html', tableData=lstDictionaryData, tableDataLen=lstDictionaryData.__len__(), executionTime=executionTime)

@app.route('/randomqueries')
def randomQueries():
    noOfQueries = int(request.args.get('queries', ''))
    withCache = int(request.args.get('withCache', ''))
    magnitudeStart = float(request.args.get('magnitudeStart', ''))
    magnitudeEnd = float(request.args.get('magnitudeEnd', ''))

    lstDictionaryData = []
    lstDictionaryDataDisplay = []

    conn = pypyodbc.connect('DRIVER=' + driver + ';SERVER=' + server + ';PORT=1443;DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
    cursor = conn.cursor()
    totalExecutionTime = 0
    columns = ['time', 'latitude', 'longitude', 'place', 'mag']

    # without cache
    if withCache == 0:
        # print("hi!")

        magnitude_value = round(random.uniform(magnitudeStart, magnitudeEnd), 1)
        startTime = time.time()
        query = "SELECT locationSource FROM earthquake_new WHERE mag = '" + str(magnitude_value) + "'"
        cursor.execute(query)
        endTime = time.time()
        # print(query)
        lstDictionaryDataDisplay = cursor.fetchall()
        # print(lstDictionaryDataDisplay)
        executionTime = (endTime - startTime) * 1000
        firstExecutionTime = executionTime

        for i in range(noOfQueries-1):
            totalExecutionTime = totalExecutionTime + executionTime
            magnitude_value = round(random.uniform(magnitudeStart, magnitudeEnd), 1)
            startTime = time.time()
            query = "SELECT locationSource FROM earthquake_new WHERE mag = '" + str(magnitude_value) + "'"
            cursor.execute(query)
            # endTime = time.time()
            lstDictionaryData = list(cursor.fetchall())

            memData = []
            for row in lstDictionaryData:
                memDataDict = dict()
                for i, val in enumerate(row):
                    if type(val) == datetime:
                        val = time.mktime(val.timetuple())
                    memDataDict[columns[i]] = val
                memData.append(memDataDict)
            r.set(query, dumps(memData))

            endTime = time.time()
            executionTime = (endTime - startTime) * 1000
            
    # with cache
    else:
        for i in range(noOfQueries):
            magnitude_value = round(random.uniform(1, 10), 2)
            query = "SELECT locationSource FROM earthquake_new WHERE mag = '" + str(magnitude_value) + "'"
            # print("inside else")
            memhash = hashlib.sha256(query.encode()).hexdigest()
            startTime = time.time()
            lstDictionaryData = r.get(memhash)

            if not lstDictionaryData:
                # print("from db")

                cursor.execute(query)
                lstDictionaryData = cursor.fetchall()
                if i == 0:
                    # print("from db")
                    lstDictionaryDataDisplay = lstDictionaryData
                endTime = time.time()
                memData = []
                for row in lstDictionaryData:
                    memDataDict = dict()
                    for i, val in enumerate(row):
                        if type(val) == datetime:
                            val = time.mktime(val.timetuple())
                        memDataDict[columns[i]] = val
                    memData.append(memDataDict)
                r.set(memhash, dumps(memData))
            else:
                lstDictionaryData = loads(lstDictionaryData.decode())
                if i == 0:
                    lstDictionaryDataDisplay = lstDictionaryData
                endTime = time.time()
            executionTime = (endTime - startTime) * 1000
            if i == 0:
                firstExecutionTime = executionTime
            totalExecutionTime = totalExecutionTime + executionTime
    conn.close()
    # print(lstDictionaryData)
    return render_template('index.html', tableData=lstDictionaryDataDisplay, tableDataLen=lstDictionaryDataDisplay.__len__(), executionTime=totalExecutionTime, firstExecutionTime=firstExecutionTime)

@app.route('/queries')
def Queries():
    noOfQueries = int(request.args.get('queries', ''))
    withCache = int(request.args.get('withCache', ''))

    lstDictionaryData = []
    lstDictionaryDataDisplay = []

    conn = pypyodbc.connect('DRIVER=' + driver + ';SERVER=' + server + ';PORT=1443;DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
    cursor = conn.cursor()
    totalExecutionTime = 0
    columns = ['time', 'latitude', 'longitude', 'place', 'mag']

    # without cache
    if withCache == 0:
        
        startTime = time.time()
        query = "SELECT locationSource FROM earthquake_new"
        cursor.execute(query)
        endTime = time.time()
        # print(query)
        lstDictionaryDataDisplay = cursor.fetchall()
        # print(lstDictionaryDataDisplay)
        executionTime = (endTime - startTime) * 1000
        firstExecutionTime = executionTime

        for i in range(noOfQueries-1):
            totalExecutionTime = totalExecutionTime + executionTime
            # magnitude_value = round(random.uniform(magnitudeStart, magnitudeEnd), 1)
            startTime = time.time()
            query = "SELECT locationSource FROM earthquake_new"
            cursor.execute(query)
            # endTime = time.time()
            lstDictionaryData = list(cursor.fetchall())
            # print("inside if")
            # print(lstDictionaryData)

            memData = []
            for row in lstDictionaryData:
                memDataDict = dict()
                for i, val in enumerate(row):
                    if type(val) == datetime:
                        val = time.mktime(val.timetuple())
                    memDataDict[columns[i]] = val
                memData.append(memDataDict)
            r.set(query, dumps(memData))

            endTime = time.time()
            executionTime = (endTime - startTime) * 1000
            
    else:
        for i in range(noOfQueries):
            # magnitude_value = round(random.uniform(1, 10), 2)
            query = "SELECT locationSource FROM earthquake_new"
        # print("inside else")
            memhash = hashlib.sha256(query.encode()).hexdigest()
            startTime = time.time()
            lstDictionaryData = r.get(memhash)

            if not lstDictionaryData:
                # print("from db")

                cursor.execute(query)
                lstDictionaryData = cursor.fetchall()
                if i == 0:
                    # print("from db")
                    lstDictionaryDataDisplay = lstDictionaryData
                endTime = time.time()
                memData = []
                for row in lstDictionaryData:
                    memDataDict = dict()
                    for i, val in enumerate(row):
                        if type(val) == datetime:
                            val = time.mktime(val.timetuple())
                        memDataDict[columns[i]] = val
                    memData.append(memDataDict)
                r.set(memhash, dumps(memData))
            else:
                lstDictionaryData = loads(lstDictionaryData.decode())
                if i == 0:
                    lstDictionaryDataDisplay = lstDictionaryData
                endTime = time.time()
            executionTime = (endTime - startTime) * 1000
            if i == 0:
                firstExecutionTime = executionTime
            totalExecutionTime = totalExecutionTime + executionTime
    conn.close()
    return render_template('index.html', tableData=lstDictionaryDataDisplay, tableDataLen=lstDictionaryDataDisplay.__len__(), executionTime=totalExecutionTime, firstExecutionTime=firstExecutionTime)

if __name__ == '__main__':
  app.run(debug=True)
