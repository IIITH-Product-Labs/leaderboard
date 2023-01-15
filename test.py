from flask import Flask,render_template,request,redirect,url_for
import pymongo

from pymongo import MongoClient
app=Flask(__name__)


myclient=pymongo.MongoClient("mongodb+srv://Developer:Bahubhashak@bahubhashaak-project.ascwu.mongodb.net")
mydb=myclient['leaderboard']
mycol=mydb['details']

@app.route('/',methods=['GET'])
def data():
    try:
        items=mycol.find({}).sort("avg",-1)
        return render_template('index.html', items=items)
    except:
        return ("error")



if __name__ == "__main__":
    app.run(host='ec2-13-233-215-141.ap-south-1.compute.amazonaws.com')

