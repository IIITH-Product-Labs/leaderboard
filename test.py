
from flask import Flask,render_template,request,redirect,url_for
import pymongo

from pymongo import MongoClient
app=Flask(__name__)



myclient=pymongo.MongoClient("mongodb://localhost:27017/")
mydb=myclient["leaderboard1"]
mycol=mydb['details']



@app.route('/',methods=['GET'])
def data():
    try:
        items=mycol.find({}).sort("avg",-1)
        return render_template('index.html', items=items)
    except:
        return ("error")



if __name__=='__main__':
    app.run(debug=True)

