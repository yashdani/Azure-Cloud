# Yash Dani - 7349
# CS-6331-001
# Assignment4

from flask import Flask, render_template, request
from datetime import datetime
# from json import loads, dumps
import pypyodbc
from matplotlib import pyplot as plt
# import pandas as pd
import time
import redis
# import hashlib
# from werkzeug.utils import secure_filename

app = Flask(__name__, static_url_path='', template_folder='static')

server = 'abc.database.windows.net'
database = 'cloud'
username = 'abc'
password = 'cloud@123'
driver= '{ODBC Driver 17 for SQL Server}'


@app.route('/')
def hello_world():

    return render_template('index.html')

@app.route('/bar')
def bar_chart():

    conn = pypyodbc.connect('DRIVER=' + driver + ';SERVER=' + server + ';PORT=1443;DATABASE=' + database + ';UID=' + username + ';PWD=' + password)

    cursor = conn.cursor()

    query = '''select t.range as magnitudes, count(*) as occurences from
                          (select case
                              when mag >= 0 and mag < 1 then 1
                              when mag >= 1 and mag < 2 then 2
    	                      when mag >= 2 and mag < 3 then 3
                              when mag >= 3 and mag < 4 then 4
    	                      when mag >= 4 and mag < 5 then 5
                              when mag >= 5 and mag < 6 then 6
    	                      when mag >= 6 and mag < 7 then 7
                              when mag >= 7 and mag < 8 then 8
    	                      when mag >= 8 and mag < 9 then 9
                              when mag >= 9 and mag < 10 then 10
                              else 11 end as range
                           from earthquake_new) t
                        group by t.range order by magnitudes;'''
    # print(query)
    cursor.execute(query)
    result_set = cursor.fetchall()
    conn.close()

    return render_template('bar.html', tableData=result_set)

@app.route('/pie')
def hello():

    conn = pypyodbc.connect('DRIVER=' + driver + ';SERVER=' + server + ';PORT=1443;DATABASE=' + database + ';UID=' + username + ';PWD=' + password)

    cursor = conn.cursor()

    query = '''select t.range as magnitudes, count(*) as occurences from
                          (select case
                              when mag >= 0 and mag < 1 then 1
                              when mag >= 1 and mag < 2 then 2
    	                      when mag >= 2 and mag < 3 then 3
                              when mag >= 3 and mag < 4 then 4
    	                      when mag >= 4 and mag < 5 then 5
                              when mag >= 5 and mag < 6 then 6
    	                      when mag >= 6 and mag < 7 then 7
                              when mag >= 7 and mag < 8 then 8
    	                      when mag >= 8 and mag < 9 then 9
                              when mag >= 9 and mag < 10 then 10
                              else 11 end as range
                           from earthquake_new) t
                        group by t.range order by magnitudes;'''
    # print(query)
    cursor.execute(query)
    result_set = cursor.fetchall()
    result = {}
    for row in result_set:
        result[row[0]]=row[1]

    conn.close()

    return render_template('pie.html', tableData=result)

@app.route('/line')
def line_chart():

    conn = pypyodbc.connect('DRIVER=' + driver + ';SERVER=' + server + ';PORT=1443;DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
    lstDictionaryData = []
    cursor = conn.cursor()
    # startTime = time.time()
    query = 'SELECT substring(time, 1, 10) as date, count(*) as occurences from earthquake_new group by substring(time, 1, 10) order by date'
    # print(query)
    cursor.execute(query)
    result_set = cursor.fetchall()
    print(result_set)

    conn.close()
    return render_template('linechart.html', tableData=result_set)

@app.route('/scatter2')
def scatter_latitude():


    latitudeStart = (request.args.get('latitudeStart', ''))
    latitudeEnd = (request.args.get('latitudeEnd', ''))

    conn = pypyodbc.connect('DRIVER=' + driver + ';SERVER=' + server + ';PORT=1443;DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
    lstDictionaryData = []
    cursor = conn.cursor()
    # startTime = time.time()
    query = 'SELECT "longitude", "latitude" FROM EARTHQUAKE_NEW'
    # print(query)
    cursor.execute(query)
    result_set = cursor.fetchall()
    # print(len(result_set))

    conn.close()
    return render_template('scatter.html', tableData=result_set)

@app.route('/scatter')
def scatter():

    conn = pypyodbc.connect('DRIVER=' + driver + ';SERVER=' + server + ';PORT=1443;DATABASE=' + database + ';UID=' + username + ';PWD=' + password)

    cursor = conn.cursor()

    query = '''select t.range as magnitudes, count(*) as occurences from
                          (select case
                              when mag >= 0 and mag < 1 then 1
                              when mag >= 1 and mag < 2 then 2
    	                      when mag >= 2 and mag < 3 then 3
                              when mag >= 3 and mag < 4 then 4
    	                      when mag >= 4 and mag < 5 then 5
                              when mag >= 5 and mag < 6 then 6
    	                      when mag >= 6 and mag < 7 then 7
                              when mag >= 7 and mag < 8 then 8
    	                      when mag >= 8 and mag < 9 then 9
                              when mag >= 9 and mag < 10 then 10
                              else 11 end as range
                           from earthquake_new) t
                        group by t.range order by magnitudes;'''
    # print(query)
    cursor.execute(query)
    result_set = cursor.fetchall()
    result = {}
    for row in result_set:
        result[row[0]]=row[1]

    conn.close()

    return render_template('scatter.html', tableData=result_set)


if __name__ == '__main__':
  app.run(debug=True)
