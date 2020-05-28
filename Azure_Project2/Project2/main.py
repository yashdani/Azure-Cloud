import os
from flask import Flask,redirect,render_template,request
import urllib
import json
import hashlib
from copy import deepcopy
import numpy as np
import pymysql
from matplotlib import pyplot as plt
from sklearn.cluster import KMeans
plt.rcParams['figure.figsize'] = (16, 9)
plt.style.use('ggplot')

app = Flask(__name__)

dbServerName    = "35.237.45.39"
dbUser          = "root"
dbPassword      = "root"
dbName          = "sqldb"
charSet         = "utf8mb4"
cusrorType      = pymysql.cursors.DictCursor

 

connectionObject = pymysql.connect(host=dbServerName, user=dbUser, password=dbPassword,db=dbName, charset=charSet,cursorclass=cusrorType)
   
def randrange():
    cursor = connectionObject.cursor()
    success='SELECT age,fare from titanic'
    cursor.execute(success)
    
    result_set = cursor.fetchall()
    age =[]
    fare =[]	
    for row in result_set:
       age.append(row['age'])
       fare.append(row['fare'])	   
    X = np.array(list(zip(age, fare)))
    kmeans = KMeans(n_clusters = int(8))
    kmeans.fit(X)
    centroid = kmeans.cluster_centers_
    labels = kmeans.labels_

    all = [[]] * 8
    for i in range(len(X)):

        # print(index)
        # print(X[i], labels[i])

        colors = ["b.", "r.", "g.", "w.", "y.", "c.", "m.", "k."]
        for i in range(len(X)):
            plt.plot(X[i][0], X[i][1], colors[labels[i]], markersize=3)

        plt.scatter(centroid[:, 0], centroid[:, 1], marker="x", s=150, linewidths=5, zorder=10)
        plt.show()
        return render_template('success.html')		
	
def piechart():
    cursor = connectionObject.cursor()
    success='SELECT count(*) from titanic where sex="female" and survived ="1" group by pclass'
    cursor.execute(success)
    
    result_set = cursor.fetchall()
    age =[]
    for row in result_set:
       age.append(row['count(*)'])

    labels = ('PC1', 'PC2', 'PC3')
    colors = ['gold', 'yellowgreen', 'lightcoral']
    sizes = [age[0],age[1],age[2]]
    explode = (0.1, 0, 0)

    plt.pie(sizes, explode=explode, labels=labels, colors=colors,autopct='%1.1f%%', shadow=True, startangle=140)
    plt.axis('equal')
    plt.show()

    return render_template('success.html')
	
def barchart():
    cursor = connectionObject.cursor()
    success='SELECT count(*) from titanic where sex="male" and survived ="1" group by pclass'
    cursor.execute(success)
    
    result_set = cursor.fetchall()
    age =[]
    for row in result_set:
       age.append(row['count(*)'])
   
    objects = ('PC1', 'PC2', 'PC3')
    y_pos = np.arange(len(objects))
    performance = [age[0],age[1],age[2]]
 
    plt.bar(y_pos, performance, align='center', alpha=0.5)
    plt.xticks(y_pos, objects)
    plt.ylabel('Count')
    plt.title('numbers of male survivors')
    plt.show()
	
    return render_template('success.html')
		
@app.route('/multiplerun', methods=['GET'])
def randquery():
    return randrange()

@app.route('/pie', methods=['GET'])
def piec():
    return piechart()

@app.route('/bar', methods=['GET'])
def barc():
    return barchart() 	

@app.route('/')
def hello_world():
  return render_template('index.html')

if __name__ == '__main__':
  app.run()
