from flask import Flask,render_template,request,redirect,url_for,session,jsonify
from flask_cors import CORS
import os
import io
from io import StringIO
from io import BytesIO
import pymongo
import json
from minio import Minio
from flask import send_file,make_response
import requests
from bson import ObjectId
import subprocess
from sacrebleu import sacrebleu
from sacrebleu.metrics import BLEU, CHRF, TER
from sacrebleu import raw_corpus_bleu
import subprocess
from pymongo import MongoClient
import boto3
import botocore
from bson import ObjectId

app=Flask(__name__)
CORS(app)
app.secret_key = "secret_key"
# s3 = boto3.client('s3')



AWS_ACCESS_KEY_ID= "AKIA3BOLL3RQYEWKMV4B"
AWS_ACCESS_KEY_SECRET= "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"
AWS_S3_REGION="ap-south-1"
AWS_S3_BUCKET="tto-asset"


#myclient=pymongo.MongoClient("mongodb://localhost:27017/")
myclient=pymongo.MongoClient("mongodb+srv://Developer:Bahubhashak@bahubhashaak-project.ascwu.mongodb.net")
mydb=myclient["leaderboard"]
mycol=mydb['details']
collection = mydb["submitresult"]
testcollection = mydb["UploadedTests"]
admincollection=mydb["admindetails"]
usercollection=mydb["userdetails"]
organisationcollection=mydb["approved"]
toolcollection=mydb["tools"]

counter = 1
count=1
ucount=1



#pages rendering


@app.route('/about')
def about_data():
    data = {
        "title": "HIMANGY",
        "description": "HIMANGY (HIndustani Machini ANuvaad TechnoloGY) is an Indian Language to Indian Language Machine Translation project. It is a consortium based project under BHASHINI and is funded by Ministry of Electronics and Information Technology (Meity), Government of India. IIIT-Hyderabad is the lead institute of the project.",
        # Add more data as needed
    }
    return jsonify(data)


@app.route('/objective')
def objective_api():
    data = {
        "title": "Our Objective",
        "content": "This is our objective content in JSON format."
    }
    return jsonify(data)


@app.route('/consortium')
def consortium_api():
    data = {
        "title": "Our Consortium",
        "content": "This is our consortium content in JSON format.",
        "details": "You can include additional data here."
    }
    return jsonify(data)

@app.route('/documents')
def documents_api():
    data = {
        "title": "Documents",
        "content": "This is the documents content in JSON format.",
        "details": "You can include additional data here."
    }
    return jsonify(data)
    

@app.route('/adminabout')
def adminabout_api():
    data2 = {
        "title": "Admin About",
        "content": "This is the admin about content in JSON format.",
        "details": "You can include additional data here."
    }
    return jsonify(data2)  
  
@app.route('/adminobjective')
def adminobjective():
    return render_template('objective_a.html')

@app.route('/api/adminobjective')
def adminobjective_api():
    data = {
        "title": "Admin Objective",
        "content": "This is the admin objective content in JSON format.",
        "details": "You can include additional data here."
    }
    return jsonify(data)
@app.route('/adminconsortium')
def adminconsortium():
    return render_template('consortium_a.html')
@app.route('/api/adminconsortium')
def adminconsortium_api():
    data = {
        "title": "Admin Consortium",
        "content": "This is the admin consortium content in JSON format.",
        "details": "You can include additional data here."
    }
    return jsonify(data)
@app.route('/admindocuments')
def admindocuments():
    return render_template('documents_a.html')
@app.route('/api/admindocuments')
def admindocuments_api():
    data = {
        "title": "Admin Documents",
        "content": "This is the admin documents content in JSON format.",
        "details": "You can include additional data here."
    }
    return jsonify(data)
# @app.route('/tools')
# def tools():
#     try:
#         items = toolcollection.find({})
#         print(items)
#         return render_template('tools.html',items=items)
#     except:
#         return ("Unable to load page")
    
@app.route('/tools', methods=['GET'])
def tools_api():
    language = request.args.get('languageselect')

    if language is None:
        language = 'english'  # Set default language

    try:
        # Assuming you have a MongoDB collection named 'toolcollection'
        items = toolcollection.find({"language": language, "status": "published"})

        # Convert MongoDB cursor to a list of dictionaries
        tool_list = []
        for item in items:
            item["_id"] = str(item["_id"])  # Convert ObjectId to string
            tool_list.append(item)

        # Return the data as JSON
        response_data = {
            "language": language,
            "tools": tool_list
        }

        return jsonify(response_data)

    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/leaderboard', methods=['GET'])
def leaderboard():
    try:
        items=collection.find({"tasktype":"Translation","status":"published"})
        items1=items.sort("version",-1)
        print(items)
        
        return render_template('leaderboard a.html',items=items)
    except:
        return ("Unable to load page")

@app.route('/api/leaderboard', methods=['GET'])
def leaderboard_api():
    try:
        items = collection.find({"tasktype": "Translation", "status": "published"})
        items = items.sort("version", -1)

        # Convert MongoDB cursor to a list of dictionaries
        leaderboard_list = []
        for item in items:
            item_dict = dict(item)
            item_dict["_id"] = str(item_dict["_id"])
            leaderboard_list.append(item_dict)

        # Return the data as JSON
        response_data = {
            "items": leaderboard_list
        }

        return jsonify(response_data)
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/download', methods=['GET'])
def download():
    try:
        data = testcollection.find({})
        return render_template('down_test_set.html',data=data)
    except:
        return ("Unable to load page")
    
@app.route('/api/download', methods=['GET'])
def download_api():
    try:
        data = testcollection.find()

        # Convert MongoDB cursor to a list of dictionaries
        download_list = []
        for item in data:
            item["_id"] = str(item["_id"])  # Convert ObjectId to string
            download_list.append(item)

        # Return the data as JSON
        response_data = {
            "data": download_list
        }

        return jsonify(response_data)
    except Exception as e:
        return jsonify({"error": str(e)})
@app.route('/submit', methods=['GET'])
def submit():
    try:
        items = organisationcollection.find({"status":"Accepted"})
        print(items)
        data=organisationcollection.find({"status":"Accepted"})
        data1=organisationcollection.find({"status":"Accepted"})
        data2=testcollection.find({})
        return render_template('submit_result.html',items=items,data=data,data1=data1,data2=data2)
    except:
        return ("Unable to load page")

@app.route('/api/submit', methods=['GET'])
def submit_api():
    try:
        items = organisationcollection.find({"status": "Accepted"})
        data = organisationcollection.find({"status": "Accepted"})
        data1 = organisationcollection.find({"status": "Accepted"})
        data2 = testcollection.find()

        # Convert MongoDB cursors to lists of dictionaries
        items_list = [dict(item, _id=str(item['_id'])) for item in items]
        data_list = [dict(item, _id=str(item['_id'])) for item in data]
        data1_list = [dict(item, _id=str(item['_id'])) for item in data1]
        data2_list = [dict(item, _id=str(item['_id'])) for item in data2]

        # Construct the response data
        response_data = {
            "items": items_list,
            "data": data_list,
            "data1": data1_list,
            "data2": data2_list
        }

        return jsonify(response_data)
    except Exception as e:
        return jsonify({"error": str(e)})
    
@app.route('/register', methods=['GET'])
def register():
    try:
        return render_template('register.html')
    except:
        return ("Unable to load page")
@app.route('/api/register', methods=['GET'])
def register_api():
    try:
        # You can include any data retrieval or processing logic here if needed
        # Construct the response data
        response_data = {
            "message": "Register API is under development",
            "status": "success"
        }
        return jsonify(response_data)
    except Exception as e:
        return jsonify({"error": str(e)})

""" @app.route('/approval',methods=['GET','POST'])
def approval():
    try:
        items = organisationcollection.find({})
        print(items)
        return render_template('approval.html',items=items)
    except:
        return ("Unable to load page") """

@app.route('/api/approval', methods=['GET', 'POST'])
def approval_api():
    if request.method == 'GET':
        try:
            # Retrieve data from the database
            items = organisationcollection.find({})

            # Convert MongoDB cursor to a list of dictionaries, convert ObjectId to string
            items_list = []
            for item in items:
                item['_id'] = str(item['_id'])
                items_list.append(item)

            # Construct the response data
            response_data = {
                "data": items_list,
                "status": "success"
            }
            return jsonify(response_data)
        except Exception as e:
            return jsonify({"error": str(e)})

    if request.method == 'POST':
        try:
            # Handle the POST request data here
            data = request.json  # Assumes data is sent in JSON format
            # Perform any necessary processing and database operations with the data

            # Construct a response indicating success
            response_data = {
                "message": "Data received and processed successfully",
                "status": "success",
                "received_data": data
            }
            return jsonify(response_data)
        except Exception as e:
            return jsonify({"error": str(e)})
@app.route('/upload', methods=['GET'])
def upload():
    try:
        items = organisationcollection.find({"status":"Accepted"})
        print(items)
        data=organisationcollection.find({"status":"Accepted"})
        data1=organisationcollection.find({"status":"Accepted"})
        return render_template('upload.html',items=items,data=data,data1=data1)
    except:
        return ("Unable to load page")
@app.route('/api/upload', methods=['GET'])
def upload_api():
    try:
        items = organisationcollection.find({"status": "Accepted"})

        # You can include any additional data processing logic here if needed
        # Construct the response data
        response_data = {
            "items": items,  # Include your data here
            "status": "success"
        }
        return jsonify(response_data)
    except Exception as e:
        return jsonify({"error": str(e)})
@app.route('/addtools', methods=['GET'])
def addtools():
    try:
        items = toolcollection.find({})
        print(items)
        # data=organisationcollection.find({"status":"Accepted"})
        # data1=organisationcollection.find({"status":"Accepted"})
        return render_template('addtools.html',items=items)
    except:
        return ("Unable to load page")

@app.route('/api/addtools', methods=['GET'])
def addtools_api():
    try:
        items = toolcollection.find({})

        # Convert MongoDB cursor to a list of dictionaries, convert ObjectId to string
        items_list = []
        for item in items:
            item['_id'] = str(item['_id'])
            items_list.append(item)

        # Construct the response data
        response_data = {
            "items": items_list,  # Include your data here
            "status": "success"
        }
        return jsonify(response_data)
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/edit',methods=['GET','POST'])
def edit():
    try:
        items=collection.find({"tasktype":"Translation","status":"published"})
        items1=items.sort("version",-1)
        print(items)   
        return render_template('edit.html',items=items)
    except:
        return ("Unable to load page")

@app.route('/api/edit', methods=['GET', 'POST'])
def edit_api():
    try:
        if request.method == 'POST':
            # Handle POST request data and update the database as needed
            data = request.json
            # ...
            return jsonify({"status": "success"})

        # Handle GET request and return data from the database
        items = collection.find({"tasktype": "Translation", "status": "published"}).sort("version", -1)

        # Convert MongoDB cursor to a list of dictionaries, convert ObjectId to string
        items_list = []
        for item in items:
            item['_id'] = str(item['_id'])
            items_list.append(item)

        # Construct the response data
        response_data = {
            "items": items_list,  # Include your data here
            "status": "success"
        }
        return jsonify(response_data)
    except Exception as e:
        return jsonify({"error": str(e)})

    

@app.route('/userleaderboard', methods=['GET'])
def userleaderboard():
    try:
        items=collection.find({"tasktype":"Translation","status":"published"})
        items1=items.sort("version",-1)
        
        return render_template('leaderboard.html',items=items)
    except:
        return ("Unable to load page")
@app.route('/api/userleaderboard', methods=['GET'])
def userleaderboard_api():
    try:
        items = list(collection.find({"tasktype": "Translation", "status": "published"}).sort("version", -1))
        items = [{**item, "_id": str(item["_id"])} for item in items]  # Convert ObjectId to string
        response_data = {
            "items": items,
            "status": "success"
        }
        return jsonify(response_data)
    except Exception as e:
        return jsonify({"error": str(e)})
@app.route('/userdownload', methods=['GET'])
def userdownload():
    try:
        data = testcollection.find({})
        return render_template('download1.html',data=data)
    except:
        return ("Unable to load page")

@app.route('/api/userdownload', methods=['GET'])
def userdownload_api():
    try:
        data = testcollection.find()

        # You can include any additional data processing logic here if needed
        # Construct the response data
        response_data = {
            "data": list(data),  # Convert the data to a list or include your data processing logic
            "status": "success"
        }
        return jsonify(response_data)
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/usersubmitlogin', methods=['GET'])
def usersubmitlogin():
    try:
        
        return render_template('submitlogin.html')
    except:
        return ("Unable to load page")
    

@app.route('/api/usersubmitlogin', methods=['GET'])
def usersubmitlogin_api():
    try:
        # You can include any additional data processing logic here if needed
        # Construct the response data
        response_data = {
            "message": "User submit login page is available",
            "status": "success"
        }
        return jsonify(response_data)
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/usersubmit', methods=['GET'])
def usersubmit():
    try:
        items = organisationcollection.find({"status":"Accepted"})
        print(items)
        data=organisationcollection.find({"status":"Accepted"})
        data1=organisationcollection.find({"status":"Accepted"})
        data2=testcollection.find({})
        return render_template('submit1.html',items=items,data=data,data1=data1,data2=data2)
    except:
        return ("Unable to load page")
@app.route('/api/usersubmit', methods=['GET'])
def usersubmit_api():
    try:
        # You can include any additional data processing logic here if needed
        # Construct the response data
        response_data = {
            "message": "User submit page is available",
            "status": "success"
        }
        return jsonify(response_data)
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/userregister', methods=['GET'])
def userregister():
    try:
        return render_template('register1.html')
    except:
        return ("Unable to load page")
@app.route('/api/userregister', methods=['GET'])
def userregister_api():
    try:
        # You can include any additional data processing logic here if needed
        # Construct the response data
        response_data = {
            "message": "User registration page is available",
            "status": "success"
        }
        return jsonify(response_data)
    except Exception as e:
        return jsonify({"error": str(e)})


@app.route('/signin', methods=['GET'])
def signin():
    try:
        
        return render_template('login.html')
    except:
        return ("Unable to load page")
@app.route('/api/signin', methods=['GET'])
def signin_api():
    try:
        # You can include any additional data processing logic here if needed
        # Construct the response data
        response_data = {
            "message": "Sign-in page is available",
            "status": "success"
        }
        return jsonify(response_data)
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/signout', methods=['GET'])
def signout():
    try:
        items=collection.find({"tasktype":"Translation","status":"published"})
        items1=items.sort("version",-1)        
        return render_template('leaderboard.html',items=items)
        
    except:
        return ("Unable to load page")
@app.route('/api/signout', methods=['GET'])
def signout_api():
    try:
        # You can include any additional data processing logic here if needed
        # For example, retrieve data from the database
        items = collection.find({"tasktype": "Translation", "status": "published"})
        # Process items and construct a response
        response_data = {
            "message": "User has been successfully signed out",
            "items": items,  # You can include data from the database if needed
            "status": "success"
        }
        return jsonify(response_data)
    except Exception as e:
        return jsonify({"error": str(e)})


#main

@app.route('/',methods=['GET','POST'])
def data():
    try:
        return render_template('about.html')
    except:
        return ("Unable to load page")
    
""" @app.route('/', methods=['GET', 'POST'])
def data():
    try:
        # Your data retrieval or processing logic goes here
        if request.method == 'GET':
            # Handle the GET request
            return render_template('about.html')  # Return HTML for GET request
        elif request.method == 'POST':
            # Handle the POST request
            # You can include data processing logic here
            data = {"message": "Data from POST request", "status": "success"}
            return jsonify(data)  # Return JSON response for POST request
    except Exception as e:
        return jsonify({"error": str(e)}) """
    
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        print(username, password)
        data = admincollection.find({})
        print(data)
        names = []
        passwords = []
        for i in data:
            print(i)
            names.append(i['User Name'])
            passwords.append(i['Password'])
        if (username in names) and (password in passwords):
            session['logged_in'] = True
            try:
                items = collection.find({"tasktype": "Translation", "status": "published"})
                items1 = items.sort("version", -1)
                print(items)

                return render_template('leaderboard a.html', items=items)
            except:
                return ("error1")
        else:
            try:
                items = collection.find({"tasktype": "Translation", "status": "published"})
                items1 = items.sort("version", -1)
                print(items)

                return render_template('leaderboard.html', items=items)
            except:
                return ("error2")
    else:
        if 'logged_in' in session:
            return redirect(url_for('protected'))
        else:
            return render_template('login.html')
        
@app.route('/api/login', methods=['POST'])
def api_login():
    try:
        username = request.form['username']
        password = request.form['password']

        # Replace this with your data retrieval logic from the database
        # For example, assume you have a list of user data
        users = [
            {"username": "user1", "password": "password1"},
            {"username": "user2", "password": "password2"}
        ]

        # Check if the provided username and password match any user in your database
        user_match = next((user for user in users if user["username"] == username and user["password"] == password), None)

        if user_match:
            session['logged_in'] = True
            return jsonify({"message": "User successfully logged in.", "status": "success"})
        else:
            return jsonify({"message": "Invalid username or password.", "status": "error"}), 401
    except Exception as e:
        return jsonify({"message": "Error: " + str(e), "status": "error"}), 500

    if request.method == 'POST':
        try:
            # Make an API request to your login endpoint
            api_response = requests.post('http://localhost:5000/api/login', data=request.form)
            if api_response.status_code == 200:
                response_data = api_response.json()
                if response_data["status"] == "success":
                    # User is logged in
                    return redirect(url_for('protected'))
                else:
                    # Show an error message on the login page
                    return render_template('login.html', error_message=response_data["message"])
            elif api_response.status_code == 401:
                return render_template('login.html', error_message="Invalid username or password.")
            else:
                return render_template('login.html', error_message="An error occurred while logging in.")
        except Exception as e:
            return render_template('login.html', error_message="An error occurred while logging in.")

    if 'logged_in' in session:
        return redirect(url_for('protected'))
    else:
        return render_template('login.html')

@app.route('/protected')
def protected():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    else:
        items = collection.find({"tasktype": "Translation", "status": "published"})
        items1 = items.sort("version", -1)
        print(items)

        return render_template('leaderboard.html', items=items)

@app.route('/api/protected')
def api_protected():
    try:
        if 'logged_in' not in session:
            return jsonify({"message": "Unauthorized", "status": "error"}), 401

        # Fetch the data you need for the 'protected' page
        items = collection.find({"tasktype": "Translation", "status": "published"}).sort("version", pymongo.DESCENDING)

        # Convert MongoDB cursor data to a list for serialization
        items_list = []
        for item in items:
            items_list.append({
                "field1": item["field1"],
                "field2": item["field2"],
                # Add more fields as needed
            })

        return jsonify({"items": items_list, "status": "success"})
    except Exception as e:
        return jsonify({"message": "An error occurred: " + str(e), "status": "error"}), 500

""" @app.route('/protected')
def protected():
    try:
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        else:
            # Make an API request to retrieve data
            api_response = requests.get('http://localhost:5000/api/protected')
            if api_response.status_code == 200:
                response_data = api_response.json()
                if response_data["status"] == "success":
                    items = response_data["items"]
                    return render_template('leaderboard.html', items=items)
                else:
                    return render_template('leaderboard.html', error_message=response_data["message"])
            else:
                return render_template('leaderboard.html', error_message="An error occurred while fetching data.")
    except Exception as e:
        return render_template('leaderboard.html', error_message="An error occurred: " + str(e))
 """
#download pages routes

@app.route('/process',methods=['POST'])  #down_test_set data filtering based on language
def process():
    
    
    tasktype = request.form["tasktype"]
    slanguage = request.form["slanguage"]
    tlanguage = request.form["tlanguage"]

    print(tasktype,slanguage,tlanguage)
    print("went")
    data=testcollection.find({"sourcelanguage":slanguage,"targetlanguage":tlanguage,"tasktype":tasktype})
    return render_template('down_test_set.html',data=data)

@app.route('/api/process', methods=['POST'])
def api_process():
    try:
        tasktype = request.form["tasktype"]
        slanguage = request.form["slanguage"]
        tlanguage = request.form["tlanguage"]

        data = testcollection.find({"sourcelanguage": slanguage, "targetlanguage": tlanguage, "tasktype": tasktype})

        # Convert MongoDB cursor data to a list for serialization
        data_list = []
        for item in data:
            data_list.append({
                "field1": item["field1"],
                "field2": item["field2"],
                # Add more fields as needed
            })

        return jsonify({"data": data_list, "status": "success"})
    except Exception as e:
        return jsonify({"message": "An error occurred: " + str(e), "status": "error"}), 500

""" @app.route('/process', methods=['POST'])
def process():
    try:
        tasktype = request.form["tasktype"]
        slanguage = request.form["slanguage"]
        tlanguage = request.form["tlanguage"]

        data = testcollection.find({"sourcelanguage": slanguage, "targetlanguage": tlanguage, "tasktype": tasktype})
        return render_template('down_test_set.html', data=data)
    except Exception as e:
        return ("Unable to load page: " + str(e)) """

@app.route('/process1',methods=['POST'])  #download1 data filtering based on language
def process1():
    
    
    tasktype = request.form["tasktype"]
    slanguage = request.form["slanguage"]
    tlanguage = request.form["tlanguage"]

    print(tasktype,slanguage,tlanguage)
    print("went")
    data=testcollection.find({"sourcelanguage":slanguage,"targetlanguage":tlanguage,"tasktype":tasktype})
    return render_template('download1.html',data=data)

@app.route('/api/process1', methods=['POST'])
def api_process1():
    try:
        tasktype = request.form["tasktype"]
        slanguage = request.form["slanguage"]
        tlanguage = request.form["tlanguage"]

        data = testcollection.find({"sourcelanguage": slanguage, "targetlanguage": tlanguage, "tasktype": tasktype})

        # Convert MongoDB cursor data to a list for serialization
        data_list = []
        for item in data:
            data_list.append({
                "field1": item["field1"],
                "field2": item["field2"],
                # Add more fields as needed
            })

        return jsonify({"data": data_list, "status": "success"})
    except Exception as e:
        return jsonify({"message": "An error occurred: " + str(e), "status": "error"}), 500

""" @app.route('/process1', methods=['POST'])
def process1():
    try:
        tasktype = request.form["tasktype"]
        slanguage = request.form["slanguage"]
        tlanguage = request.form["tlanguage"]

        data = testcollection.find({"sourcelanguage": slanguage, "targetlanguage": tlanguage, "tasktype": tasktype})
        return render_template('download1.html', data=data)
    except Exception as e:
        return ("Unable to load page: " + str(e)) """

@app.route('/tprocess',methods=['POST'])  # down_test_set based on tasktype data filtering  code(not using present)
def tprocess():
    
    
    tasktype = request.form["tasktype"]
    slanguage = request.form["slanguage"]
    tlanguage = request.form["tlanguage"]

    print(tasktype,slanguage,tlanguage)
    print("went")
    data=testcollection.find({"tasktype":tasktype})
    return render_template('down_test_set.html',data=data)
@app.route('/api/tprocess', methods=['POST'])
def api_tprocess():
    try:
        tasktype = request.form["tasktype"]

        data = testcollection.find({"tasktype": tasktype})

        # Convert MongoDB cursor data to a list for serialization
        data_list = []
        for item in data:
            data_list.append({
                "field1": item["field1"],
                "field2": item["field2"],
                # Add more fields as needed
            })

        return jsonify({"data": data_list, "status": "success"})
    except Exception as e:
        return jsonify({"message": "An error occurred: " + str(e), "status": "error"}), 500

""" @app.route('/tprocess', methods=['POST'])
def tprocess():
    try:
        tasktype = request.form["tasktype"]
        data = testcollection.find({"tasktype": tasktype})
        return render_template('down_test_set.html', data=data)
    except Exception as e:
        return ("Unable to load page: " + str(e)) """
@app.route('/process-checkboxes', methods=['POST']) #based on checkboxs selecting files downloading(download pages)
def process_checkboxes():
    tasktype = request.form["tasktype"]
    slanguage = request.form["slanguage"]
    tlanguage = request.form["tlanguage"]
    checkbox_names = request.form.getlist('checkboxes')
    print(checkbox_names)
    split_list = [item.split(',') for item in checkbox_names]
    print(split_list)
    print(split_list[0][0],split_list[0][1],split_list[0][3],split_list[0][4])

    data=testcollection.find({"filename":split_list[0][0],"tasktype":split_list[0][1],"sourcelanguage":split_list[0][3],"targetlanguage":split_list[0][4]})
    print(data)
    l=[]
    for i in data:
        print("data")
        print(i)
        l.append(i['fileurl'])
    print(l)

    if len(l)>0:
        print(l[0])
        response1 = requests.get(l[0])
        print(response1)
    
        # Check if the request was successful
        if response1.status_code == 200:
            # Retrieve the file contents
            file_contents = response1.content
            print(file_contents)
        
            # Create a file object from the file contents
            file = BytesIO(file_contents)
            return send_file(file, download_name='file.txt', as_attachment=True)
        else:
            # Return an error message if the request was not successful
            return 'Error: Could not download file'
    else:
        return ("NO file with selected File Name")
@app.route('/api/process-checkboxes', methods=['POST'])
def api_process_checkboxes():
    try:
        tasktype = request.form["tasktype"]
        slanguage = request.form["slanguage"]
        tlanguage = request.form["tlanguage"]
        checkbox_names = request.form.getlist('checkboxes')
        print(checkbox_names)
        split_list = [item.split(',') for item in checkbox_names]
        print(split_list)
        print(split_list[0][0], split_list[0][1], split_list[0][3], split_list[0][4])

        data = testcollection.find(
            {
                "filename": split_list[0][0],
                "tasktype": split_list[0][1],
                "sourcelanguage": split_list[0][3],
                "targetlanguage": split_list[0][4]
            }
        )
        print(data)
        l = []
        for i in data:
            print("data")
            print(i)
            l.append(i['fileurl'])
        print(l)

        if len(l) > 0:
            print(l[0])
            response1 = requests.get(l[0])
            print(response1)

            # Check if the request was successful
            if response1.status_code == 200:
                # Retrieve the file contents
                file_contents = response1.content
                print(file_contents)

                # Create a file object from the file contents
                file = BytesIO(file_contents)
                return send_file(file, download_name='file.txt', as_attachment=True)
            else:
                # Return an error message if the request was not successful
                return jsonify({"message": "Error: Could not download file", "status": "error"}), 500
        else:
            return jsonify({"message": "No file with the selected File Name", "status": "error"}), 404
    except Exception as e:
        return jsonify({"message": "An error occurred: " + str(e), "status": "error"}), 500

@app.route('/delete-checkboxes', methods=['POST']) #based on checkboxs selecting files downloading(download pages)
def delete_checkboxes():
    row_numbers = request.get_json()['rowNumbers']
    print(row_numbers)
    split_list = [item.split(',') for item in row_numbers]
    print(split_list)

    for number in split_list:
        print(number[0],number[1],number[2],number[3],number[4],number[5],number[6],number[7])
        collection.delete_one({'rowno': number[0],'organisation':number[1],'language':number[2],'module':number[3],'version':number[4],'bleu':number[5],'chrf':number[6],'ter':number[7],'status':'published'})
        print('deleted')

    try:
        items=collection.find({"tasktype":"Translation","status":"published"})
        items1=items.sort("version",-1)
        print(items)   
        return render_template('edit.html',items=items)
    except:
        return ("Unable to load page")
@app.route('/api/delete-checkboxes', methods=['POST'])
def api_delete_checkboxes():
    try:
        row_numbers = request.get_json()['rowNumbers']
        print(row_numbers)
        split_list = [item.split(',') for item in row_numbers]
        print(split_list)

        for number in split_list:
            print(number[0], number[1], number[2], number[3], number[4], number[5], number[6], number[7])
            collection.delete_one({
                'rowno': number[0],
                'organisation': number[1],
                'language': number[2],
                'module': number[3],
                'version': number[4],
                'bleu': number[5],
                'chrf': number[6],
                'ter': number[7],
                'status': 'published'
            })
            print('deleted')

        return jsonify({"message": "Selected rows deleted successfully", "status": "success"})
    except Exception as e:
        return jsonify({"message": "An error occurred: " + str(e), "status": "error"}), 500

@app.route('/submitlogin', methods=['POST','GET'])# user login code for submit result page
def submitlogin():
    username = request.form["username"]
    password = request.form["password"]
    print(username,password)
    data=organisationcollection.find({'status':'Accepted'})
    print(data)
    names=[]
    passwords=[]
    for i in data:
        print(i)
        names.append(i['name'])
        passwords.append(i['password'])
    print(names,passwords)
    if (username in names) and (password in passwords): 

        try:
            items = organisationcollection.find({"status":"Accepted",'name':username,'password':password})
            items1 = organisationcollection.find({"status":"Accepted",'name':username,'password':password})
            print(items)
            data=organisationcollection.find({"status":"Accepted"})
            data1=organisationcollection.find({"status":"Accepted"})
            data2=testcollection.find({})
            return render_template('submit1.html',items=items,items1=items1,data=data,data1=data1,data2=data2)
        except:
            return ("error1")
    else:
        try:
            if (username in names) and (password not in passwords):
                return "password is wrong"
            elif (username not in names) and (password  in passwords):
                return "username is wrong"
            else:    
                return "user is not registered or organisation is accepted by admin"
        except:
            return ("error2")
        
@app.route('/api/submitlogin', methods=['POST', 'GET'])
def api_submitlogin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        print(username, password)
        data = organisationcollection.find({'status': 'Accepted'})
        print(data)
        names = []
        passwords = []
        for i in data:
            print(i)
            names.append(i['name'])
            passwords.append(i['password'])
        print(names, passwords)

        if (username in names) and (password in passwords):
            try:
                items = organisationcollection.find({"status": "Accepted", 'name': username, 'password': password})
                items1 = organisationcollection.find({"status": "Accepted", 'name': username, 'password': password})
                print(items)

                data = organisationcollection.find({"status": "Accepted"})
                data1 = organisationcollection.find({"status": "Accepted"})
                data2 = testcollection.find({})

                return jsonify({
                    "items": [item for item in items],
                    "items1": [item for item in items1],
                    "data": [item for item in data],
                    "data1": [item for item in data1],
                    "data2": [item for item in data2]
                })
            except Exception as e:
                return jsonify({"message": "An error occurred: " + str(e), "status": "error"}), 500
        else:
            return jsonify({"message": "Invalid credentials or organization not accepted by admin", "status": "error"}), 403
    elif request.method == 'GET':
        try:
            return render_template('submitlogin.html')
        except Exception as e:
            return jsonify({"message": "An error occurred: " + str(e), "status": "error"}), 500

@app.route('/langform', methods=['POST','GET'])#download page data filtering based on selection
def langform():
    global count

    organisation = request.form["organisation"]
    tasktype = request.form["tasktype"]
    slanguage = request.form["slanguage"]
    tlanguage = request.form["tlanguage"]
    print(organisation,tasktype,slanguage,tlanguage)

    items=testcollection.find({"tasktype":tasktype,"sourcelanguage":slanguage,"targetlanguage":tlanguage})
    f_names=[]
    for i in items:
        print(i)
        f_names.append(i['filename'])
    print(f_names)
    k=[]

    return f_names

@app.route('/api/langform', methods=['POST', 'GET'])
def api_langform():
    if request.method == 'POST':
        organisation = request.form["organisation"]
        tasktype = request.form["tasktype"]
        slanguage = request.form["slanguage"]
        tlanguage = request.form["tlanguage"]
        print(organisation, tasktype, slanguage, tlanguage)

        items = testcollection.find({"tasktype": tasktype, "sourcelanguage": slanguage, "targetlanguage": tlanguage})
        f_names = [i['filename'] for i in items]

        return jsonify({"filenames": f_names})
    elif request.method == 'GET':
        try:
            return render_template('langform.html')
        except Exception as e:
            return jsonify({"message": "An error occurred: " + str(e), "status": "error"}), 500

@app.route('/newform', methods=['POST','GET'])#submit result values calculation
def newform():
    global count

    organisation = request.form["organisation"]
    tasktype = request.form["tasktype"]
    slanguage = request.form["slanguage"]
    tlanguage = request.form["tlanguage"]
    testsetname = request.form["testsetname"]
    module = request.form["module"]
    version = request.form["version"]
    file = request.files["file"]
    print(organisation)

   
    file_data = file.read()
    f = io.BytesIO(file_data)
    file_size=len(file_data)
    print(file_size)

    try:
        minio_client = Minio('canvas.iiit.ac.in', access_key='minioadmin', secret_key='Minio@0710', secure=True)   
        
        minio_client.put_object('leaderboard', "Submit Files/file.txt", f,file_size)
        print("UPLOADED")
        image_url = minio_client.presigned_get_object('leaderboard', 'Submit Files/file.txt')
        print(image_url)
        response = requests.get(image_url)

        # Save the file to the desired location on the local server
        with open('C:/Users/LENOVO/Downloads/submit/sf.txt', 'wb') as f:
            f.write(response.content)

        ref=testcollection.find({"sourcelanguage":slanguage,"targetlanguage":tlanguage,"tasktype":tasktype,"filename":testsetname})
        print(ref)
        ref_url=[]
        for i in ref:
           ref_url.append(i['targetfileurl'])
        print(ref_url)
        response1 = requests.get(ref_url[0])

        # Save the file to the desired location on the local server
        with open('C:/Users/LENOVO/Downloads/upload/uf.txt', 'wb') as f:
            f.write(response1.content)
        
        reference_text = "C:/Users/LENOVO/Downloads/upload/uf.txt"
        hypothesis_text = "C:/Users/LENOVO/Downloads/submit/sf.txt"
        hypothesis_text_list = hypothesis_text.split("\n")
        reference_text_list = reference_text.split("\n")

        bleu = BLEU()
        r = bleu.corpus_score(hypothesis_text_list, [reference_text_list])
        print(r)
        text=str(r)
        parts = text.split()
        bleuscore= parts[2]
        print(bleuscore)
        s = bleu.get_signature()
        print(s)

        hypothesis_text = "\n".join(hypothesis_text_list)
        reference_text = "\n".join(reference_text_list)

        chrf = CHRF()
        c = chrf.corpus_score(hypothesis_text, reference_text)
        print(c)
        text1=str(c)
        parts1 = text1.split()
        chrfscore= parts1[2]
        print(chrfscore)
        s1 = chrf.get_signature()
        print(s1)

        ter = TER()
        t = ter.corpus_score(hypothesis_text_list, reference_text_list)
        print(t)
        text2=str(t)
        parts2 = text2.split()
        terscore= parts2[2]
        print(terscore)
        s2 = ter.get_signature()
        print(s2)

        print("complete")


        #bleu_score = raw_corpus_bleu(hypothesis_text, [reference_text])
        #print(bleu_score)
        #print(type(bleu_score))
        #text=str(bleu_score)
        #parts = text.split()

        # Extract the first element of the list (the BLEU score) and assign it to a variable
        #bleu= parts[2]

        # Print the BLEU score
        #print(bleu)
        #print("done")
        #command = f'sacrebleu -m chrf --chrf-word-order 2 {reference_text} < {hypothesis_text}'
        #result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        #print(result)
        #output = result.stdout
        #output_dict = json.loads(output)  # Parse the JSON object
        ##score = output_dict['score']    # Extract the chrF score
        #print(score)
        #print("chrf")

        print(count)
        data1=chrfscore
        data=bleuscore
        data2=terscore
        document = {"rowno":str(count),"organisation": organisation, "tasktype": tasktype, "language":slanguage+'-'+tlanguage,"sourcelanguage": slanguage ,"targetlanguage":tlanguage ,"testsetname":testsetname ,"module":module,"version":version ,"fileurl":image_url,"bleu":data,"chrf":str(data1),"ter":str(data2),"bleu_sign":str(s),"chrf_sign":str(s1),"ter_sign":str(s2),"status":"draft"}
        collection.insert_one(document)
        count=count+1
        print(count)
        print("stored")
        d=[]
        d.append(data)
        d.append(data1)
        d.append(data2)
        print(d)


        
        #items = organisationcollection.find({"status":"Accepted"})
        #data2=testcollection.find({})
        return  d
    except:
        return ("error")
    
@app.route('/api/newform', methods=['POST'])
def api_newform():
    try:
        organisation = request.form["organisation"]
        tasktype = request.form["tasktype"]
        slanguage = request.form["slanguage"]
        tlanguage = request.form["tlanguage"]
        testsetname = request.form["testsetname"]
        file = request.files["file"]

        # Read file data
        file_data = file.read()
        file_size = len(file_data)

        # Upload the file to Minio
        file_name = f"Submit Files/{organisation}/{testsetname}/file.txt"
        minio_client.put_object('leaderboard', file_name, io.BytesIO(file_data), file_size)

        # Get presigned URL for the uploaded file
        file_url = minio_client.presigned_get_object('leaderboard', file_name)

        # Fetch the reference text
        ref_url = f"{your_reference_url}/{slanguage}-{tlanguage}/{testsetname}/reference.txt"  # Replace with your actual reference URL
        ref_response = requests.get(ref_url)

        if ref_response.status_code == 200:
            reference_text = ref_response.text
        else:
            return jsonify({"error": "Failed to fetch reference text"})

        # Extract hypothesis text from the uploaded file
        hypothesis_text = file_data.decode('utf-8')

        # Calculate BLEU, CHRF, and TER scores
        bleu = BLEU()
        chrf = CHRF()
        ter = TER()

        bleu_score = bleu.corpus_score([hypothesis_text], [[reference_text]])
        chrf_score = chrf.corpus_score(hypothesis_text, reference_text)
        ter_score = ter.corpus_score([hypothesis_text], [reference_text])

        # Retrieve the scores from the computed scores object
        bleu_score = bleu_score.score
        chrf_score = chrf_score.score
        ter_score = ter_score.score

        # Create a response dictionary
        response_data = {
            "bleu_score": bleu_score,
            "chrf_score": chrf_score,
            "ter_score": ter_score,
            "file_url": file_url,
        }

        return jsonify(response_data)

    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/publish', methods=['POST','GET'])# to publish in the main leaderboard
def publish():
    global count

    organisation = request.form["organisation"]
    tasktype = request.form["tasktype"]
    slanguage = request.form["slanguage"]
    tlanguage = request.form["tlanguage"]
    testsetname = request.form["testsetname"]
    module = request.form["module"]
    version = request.form["version"]
    file = request.files["file"]
    #bleu = request.form["bleu"]
    #chrf = request.form["chrf"]
    #gleu = request.form["gleu"]
    #print(bleu,chrf,gleu)
   
    file_data = file.read()
    f = io.BytesIO(file_data)
    file_size=len(file_data)
    print(file_size)

    try:
        minio_client = Minio('canvas.iiit.ac.in', access_key='minioadmin', secret_key='Minio@0710', secure=True)   
        
        minio_client.put_object('leaderboard', "Publish Files/file.txt", f,file_size)
        print("UPLOADED")
        image_url = minio_client.presigned_get_object('leaderboard', 'Publish Files/file.txt')
        print(image_url)
        #document = {"id":count,"organisation": organisation, "tasktype": tasktype, "language":slanguage+'-'+tlanguage,"sourcelanguage": slanguage ,"targetlanguage":tlanguage ,"testsetname":testsetname ,"module":module,"version":version ,"fileurl":image_url,"status":"Published"}
        #collection.insert_one(document)

        #print(document)
        collection.update_one(
    {'organisation':organisation,'tasktype':tasktype,'sourcelanguage':slanguage,'targetlanguage':tlanguage,'testsetname':testsetname,'module':module,'version':version},
    {'$set': {'status':"published"}}
)
        print("published")
        count += 1
        #items = organisationcollection.find({"status":"Accepted"})
        #data2=testcollection.find({})
        #return  render_template('submit_result.html',items=items,data=data,data2=data2)
        items=collection.find({"tasktype":"Translation","status":"published"})
        items1=items.sort("version",-1)
        print(items)
        
        return render_template('leaderboard a.html',items=items)
    except:
        return ("error")
    
@app.route('/api/publish', methods=['POST'])
def api_publish():
    try:
        organisation = request.form["organisation"]
        tasktype = request.form["tasktype"]
        slanguage = request.form["slanguage"]
        tlanguage = request.form["tlanguage"]
        testsetname = request.form["testsetname"]
        module = request.form["module"]
        version = request.form["version"]
        file = request.files["file"]

        # Read the file data
        file_data = file.read()
        file_size = len(file_data)

        # Upload the file to Minio
        file_name = f"Publish Files/{organisation}/{testsetname}/file.txt"
        minio_client.put_object('leaderboard', file_name, file_data, file_size)

        # Get presigned URL for the uploaded file
        image_url = minio_client.presigned_get_object('leaderboard', file_name)

        # Update the status of the record in the database to "published"
        collection.update_one(
            {
                'organisation': organisation,
                'tasktype': tasktype,
                'sourcelanguage': slanguage,
                'targetlanguage': tlanguage,
                'testsetname': testsetname,
                'module': module,
                'version': version
            },
            {'$set': {'status': "published"}}
        )

        return jsonify({"message": "Results published successfully"})

    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/publish1', methods=['POST','GET'])#to publish in the user leaderboard
def publish1():
    global count

    organisation = request.form["organisation"]
    tasktype = request.form["tasktype"]
    slanguage = request.form["slanguage"]
    tlanguage = request.form["tlanguage"]
    testsetname = request.form["testsetname"]
    module = request.form["module"]
    version = request.form["version"]
    file = request.files["file"]
    #bleu = request.form["bleu"]
    #chrf = request.form["chrf"]
    #gleu = request.form["gleu"]
    #print(bleu,chrf,gleu)
   
    file_data = file.read()
    f = io.BytesIO(file_data)
    file_size=len(file_data)
    print(file_size)

    try:
        minio_client = Minio('canvas.iiit.ac.in', access_key='minioadmin', secret_key='Minio@0710', secure=True)   
        
        minio_client.put_object('leaderboard', "Publish Files/file.txt", f,file_size)
        print("UPLOADED")
        image_url = minio_client.presigned_get_object('leaderboard', 'Publish Files/file.txt')
        print(image_url)
        #document = {"id":count,"organisation": organisation, "tasktype": tasktype, "language":slanguage+'-'+tlanguage,"sourcelanguage": slanguage ,"targetlanguage":tlanguage ,"testsetname":testsetname ,"module":module,"version":version ,"fileurl":image_url,"bleu":bleu,"chrf":chrf,"gleu":gleu,"status":"Published"}
        #collection.insert_one(document)

        #print(document)
        collection.update_one(
    {'organisation':organisation,'tasktype':tasktype,'sourcelanguage':slanguage,'targetlanguage':tlanguage,'testsetname':testsetname,'module':module,'version':version},
    {'$set': {'status':"published"}}
)
        print("published")
        count += 1
        #items = organisationcollection.find({"status":"Accepted"})
        #data2=testcollection.find({})
        #return  render_template('submit1.html',items=items,data=data,data2=data2)
        items=collection.find({"tasktype":"Translation","status":"published"})
        items1=items.sort("version",-1)
        
        return render_template('leaderboard.html',items=items)
    except:
        return ("error")
    
@app.route('/api/publish1', methods=['POST'])
def api_publish1():
    try:
        organisation = request.form["organisation"]
        tasktype = request.form["tasktype"]
        slanguage = request.form["slanguage"]
        tlanguage = request.form["tlanguage"]
        testsetname = request.form["testsetname"]
        module = request.form["module"]
        version = request.form["version"]
        file = request.files["file"]

        # Read the file data
        file_data = file.read()
        file_size = len(file_data)

        # Upload the file to Minio
        file_name = f"Publish Files/{organisation}/{testsetname}/file.txt"
        minio_client.put_object('leaderboard', file_name, file_data, file_size)

        # Get presigned URL for the uploaded file
        image_url = minio_client.presigned_get_object('leaderboard', file_name)

        # Update the status of the record in the database to "published"
        collection.update_one(
            {
                'organisation': organisation,
                'tasktype': tasktype,
                'sourcelanguage': slanguage,
                'targetlanguage': tlanguage,
                'testsetname': testsetname,
                'module': module,
                'version': version
            },
            {'$set': {'status': "published"}}
        )

        return jsonify({"message": "Results published successfully"})

    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/create', methods=['POST','GET'])# user registeration data storing
def create():
    global counter

    organisation = request.form["organisation"]
    email = request.form["email"]
    name = request.form["name"]
    password = request.form["password"]
    correctpassword = request.form["correctpassword"]

    try:
        
        document = {"id":str(counter),"organisation": organisation, "email":email, "name": name,"password":password,"correctpassword":correctpassword,"status":""}
        organisationcollection.insert_one(document)

        print(document)
        print("registered")
        counter += 1
        data ="Your request has been successfully sent to the admin for approval"
        return data

       # return render_template("register.html")
    except:
        data ="Your request has  unable sent to the admin for approval"
        return data
        #return ("error")

@app.route('/api/create', methods=['POST'])
def api_create():
    try:
        organisation = request.form["organisation"]
        email = request.form["email"]
        name = request.form["name"]
        password = request.form["password"]
        correctpassword = request.form["correctpassword"]

        document = {
            "organisation": organisation,
            "email": email,
            "name": name,
            "password": password,
            "correctpassword": correctpassword,
            "status": "pending"  # You can set the initial status as "pending"
        }

        organisationcollection.insert_one(document)
        print("User registration data stored:", document)

        response_data = {
            "message": "Your request has been successfully sent to the admin for approval"
        }
        return jsonify(response_data), 200

    except Exception as e:
        error_message = str(e)
        response_data = {
            "error": f"Registration failed. {error_message}"
        }
        return jsonify(response_data), 400

@app.route('/approved', methods=['POST','GET'])#accepting the organisation in approval page
def approved():
    organisation = request.form["organisation"]
    name = request.form["name"]

    print(organisation,name)
    organisationcollection.update_one(
    {'organisation':organisation,'name':name},
    {'$set': {'status':"Accepted"}}
    )
    print("Accepted")

    items = organisationcollection.find({})
    try:

        return render_template('approval.html',items=items)
    except:
        return ("error")
    
@app.route('/api/approved', methods=['POST'])
def api_approved():
    try:
        organisation = request.form["organisation"]
        name = request.form["name"]

        print(f"Approving {name} from {organisation}")
        organisationcollection.update_one(
            {'organisation': organisation, 'name': name},
            {'$set': {'status': "Accepted"}}
        )
        print(f"{name} has been accepted")

        response_data = {
            "message": f"{name} from {organisation} has been accepted"
        }

        return jsonify(response_data), 200

    except Exception as e:
        error_message = str(e)
        response_data = {
            "error": f"Approval failed. {error_message}"
        }
        return jsonify(response_data), 400
    
@app.route('/form2', methods=['POST','GET'])# upload test data storing
def form2():
    global ucount

    #organisation = request.form["organization"]
    #domain = request.form["domain"]
    tasktype = request.form["tasktype"]
    slanguage = request.form["slanguage"]
    tlanguage = request.form["tlanguage"]
    size= request.form["size"]
    filetype = request.form["filetype"]
    filename = request.form["filename"]
    file = request.files["file"]
    tfile = request.files["file1"]
    print(tfile)
    name=file.filename
    print(name)
    tname=tfile.filename
    print(tname)
    if filetype=="CSV file":
        file_name = "Test Set Files/" + filename+".csv"
    else:
        file_name = "Test Set Files/" + filename+".txt"

    print(file_name)

    target_file_name="Target Files/"+tname
    print(target_file_name)


   
    file_data = file.read()
    f = io.BytesIO(file_data)
    file_size=len(file_data)
    print(file_size)

    tfile_data = tfile.read()
    tf = io.BytesIO(tfile_data)
    tfile_size=len(tfile_data)
    print(tfile_size)

    try:
        minio_client = Minio('canvas.iiit.ac.in', access_key='minioadmin', secret_key='Minio@0710', secure=True)   
        
        minio_client.put_object('leaderboard', file_name, f,file_size)
        print("UPLOADED source file")
        image_url = minio_client.presigned_get_object('leaderboard', file_name)
        print(image_url)
        minio_client = Minio('canvas.iiit.ac.in', access_key='minioadmin', secret_key='Minio@0710', secure=True)   
        
        minio_client.put_object('leaderboard', target_file_name, tf,tfile_size)
        print("UPLOADED target file")
        target_image_url = minio_client.presigned_get_object('leaderboard', target_file_name)
        print(target_image_url) 
        print(counter)
        
        document = {"id":str(ucount),"tasktype": tasktype,"language":slanguage+'-'+tlanguage, "sourcelanguage": slanguage ,"targetlanguage":tlanguage ,"filesize":size ,"filetype":filetype ,"filename":filename,"fileurl":image_url,"targetfileurl":target_image_url,"status":"In review"}
        testcollection.insert_one(document)
        ucount=ucount+1

        print(document)
        
        #items = organisationcollection.find({"status":"Accepted"})
        #return render_template("upload.html",items=items)
        items=collection.find({"tasktype":"Translation","status":"published"})
        items1=items.sort("version",-1)
        print(items)
        
        return render_template('leaderboard a.html',items=items)
    except:
        return ("error")
    
@app.route('/api/form2', methods=['POST'])
def api_form2():
    try:
        # Extract the data from the request
        tasktype = request.form["tasktype"]
        slanguage = request.form["slanguage"]
        tlanguage = request.form["tlanguage"]
        size = request.form["size"]
        filetype = request.form["filetype"]
        filename = request.form["filename"]
        file = request.files["file"]
        tfile = request.files["file1"]

        # Generate unique file names for source and target files
        file_name = f"Test Set Files/{filename}.{filetype.lower()}"
        target_file_name = f"Target Files/{tfile.filename}"

        # Read file data and file sizes
        file_data = file.read()
        file_size = len(file_data)
        tfile_data = tfile.read()
        tfile_size = len(tfile_data)

        # Upload source file
        minio_client = Minio('canvas.iiit.ac.in', access_key='minioadmin', secret_key='Minio@0710', secure=True)
        minio_client.put_object('leaderboard', file_name, file_data, file_size)
        image_url = minio_client.presigned_get_object('leaderboard', file_name)

        # Upload target file
        minio_client.put_object('leaderboard', target_file_name, tfile_data, tfile_size)
        target_image_url = minio_client.presigned_get_object('leaderboard', target_file_name)

        # Store the data in your database or collection
        document = {
            "tasktype": tasktype,
            "language": f"{slanguage}-{tlanguage}",
            "sourcelanguage": slanguage,
            "targetlanguage": tlanguage,
            "filesize": size,
            "filetype": filetype,
            "filename": filename,
            "fileurl": image_url,
            "targetfileurl": target_image_url,
            "status": "In review"
        }

        testcollection.insert_one(document)

        # Update the counter or ID for unique entries
        global ucount
        ucount += 1

        response_data = {
            "message": "Test data has been uploaded and is in review"
        }

        return jsonify(response_data), 200

    except Exception as e:
        error_message = str(e)
        response_data = {
            "error": f"Upload failed. {error_message}"
        }
        return jsonify(response_data), 400

@app.route('/toolsform', methods=['POST','GET'])# upload test data storing
def Toolsform():
    global ucount

    product_name = request.form["productname"]
    language = request.form["language"]
    product_url = request.form["producturl"]
    github_url = request.form["githuburl"]
    description = request.form["description"]
    tfile = request.files["image"]
    print(tfile)
    tname=tfile.filename
    print(tname)

    target_file_name=tname

    if tfile.filename == '':
        return "No selected file"
    print(target_file_name)

    tfile_data = tfile.read()
    tf = io.BytesIO(tfile_data)
    tfile_size=len(tfile_data)
    print(tfile_size)

    try:
        s3 = boto3.client('s3',aws_access_key_id=AWS_ACCESS_KEY_ID,aws_secret_access_key=AWS_ACCESS_KEY_SECRET)
        object_name = target_file_name
        s3.upload_fileobj(tf, AWS_S3_BUCKET, object_name)
        # s3.upload_fileobj(fo, bucket, key)
        s3_url = f"https://{AWS_S3_BUCKET}.s3.amazonaws.com/{target_file_name}"
        print(s3_url)

        # return f"Image uploaded successfully. S3 URL: {s3_url}"
        # except botocore.exceptions.NoCredentialsError:
        # return "AWS credentials not found. Please configure your AWS credentials."


        document = {"id":str(ucount),"product_name": product_name,"product_url":product_url ,"language":language, "github_url": github_url ,"description":description ,"fileurl":s3_url,"status":"published"}
        toolcollection.insert_one(document)
        ucount=ucount+1
        print(document)
        
        #items = organisationcollection.find({"status":"Accepted"})
        #return render_template("upload.html",items=items)
        items=toolcollection.find({"status":"published"})
        # items1=items.sort("version",-1)
        print(items)
        print("thanks for submmiting")
        
        return  redirect(url_for('tools'))

    except:
        return ("error")
@app.route('/api/toolsform', methods=['POST'])
def api_toolsform():
    try:
        # Extract the data from the request
        product_name = request.form["productname"]
        language = request.form["language"]
        product_url = request.form["producturl"]
        github_url = request.form["githuburl"]
        description = request.form["description"]
        tfile = request.files["image"]

        if tfile.filename == '':
            return jsonify({"error": "No selected file"}), 400

        tname = tfile.filename
        tfile_data = tfile.read()

        # Upload the image to an AWS S3 bucket
        s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_ACCESS_KEY_SECRET)
        object_name = tname
        s3.upload_fileobj(io.BytesIO(tfile_data), AWS_S3_BUCKET, object_name)
        s3_url = f"https://{AWS_S3_BUCKET}.s3.amazonaws.com/{object_name}"

        # Store the data in your database or collection
        document = {
            "product_name": product_name,
            "language": language,
            "product_url": product_url,
            "github_url": github_url,
            "description": description,
            "fileurl": s3_url,
            "status": "published"
        }
        toolcollection.insert_one(document)

        # Update the counter or ID for unique entries
        global ucount
        ucount += 1

        response_data = {
            "message": "Tool information has been uploaded and is published"
        }

        return jsonify(response_data), 200

    except Exception as e:
        error_message = str(e)
        response_data = {
            "error": f"Upload failed. {error_message}"
        }
        return jsonify(response_data), 400


@app.route('/update', methods=['POST','GET'])#edited data updating in backend
def update():
    data = request.get_json()
    print(data)
    all_rows_data = data["rows"]
    print(all_rows_data)

    for row in all_rows_data:
        rowno = row["rowno"]
        organization = row["organization"]
        language = row["language"]
        module = row["module"]
        version = row["version"]
        bleu = row["bleu"]
        chrf = row["chrf"]
        ter = row["ter"]

        # Update the data in the collection based on the "rowno" field
        collection.update_one({"rowno": rowno,"bleu":bleu,"chrf":chrf,"ter":ter}, {"$set": {
            "organization": organization,
            "language": language,
            "module": module,
            "version": version,
        }})
        print("updated")

    return jsonify({"message": "Data updated successfully"})





@app.route('/route/to/flask/endpoint', methods=['POST','GET'])
def handle_selected_option():
  selectedOption = request.get_json()['option']
  print(selectedOption)
  if(selectedOption=='None'):
    items=mycol.find({}).sort("Version",-1)
    
    print(items)
    l=[]
    for i in items:
      k=[]
      print(i)
      k.append(i['Id'])
      k.append(i['Organisation'])
      k.append(i['Language'])
      k.append(i['Module'])
      k.append(i['Version'])
      k.append(i['bleu'])
      k.append(i['chrf'])
      k.append(i[' gleu'])
      l.append(k)
  else:
    items=mycol.find({"task":selectedOption})
    items1=items.sort("Version",-1)
  
    print(items1)
    l=[]
    for i in items:
      k=[] 
      print(i)
      k.append(i['Id'])
      k.append(i['Organisation'])
      k.append(i['Language'])
      k.append(i['Module'])
      k.append(i['Version'])
      k.append(i['bleu'])
      k.append(i['chrf'])
      k.append(i[' gleu'])
      l.append(k)
  response=json.dumps(l)
  return response



if __name__=='__main__':
    app.run(debug=True)









