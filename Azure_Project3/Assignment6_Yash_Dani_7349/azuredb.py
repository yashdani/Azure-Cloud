import pymysql

username = 'yash'
password = 'yashdani'
database = 'adb'
port = 3306
server = 'cloud-adb.c6dyuwuzxull.us-east-2.rds.amazonaws.com'

connect = pymysql.connect(server, username, password, database)
