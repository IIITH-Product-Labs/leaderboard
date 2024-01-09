from flask import Flask, render_template, request, redirect, url_for, jsonify, session, send_file
from flask_pymongo import PyMongo
from werkzeug.utils import secure_filename
from flask_restful import Resource, Api
from flask_cors import CORS, cross_origin
import os
import io
from io import StringIO
from io import BytesIO
import pymongo
from minio import Minio
from flask import send_file, make_response
import requests
from bson import ObjectId
import pandas as pd
from sacrebleu import corpus_bleu
from sacrebleu.metrics import BLEU, CHRF, TER
import evaluate
from evaluate import * 
import subprocess
from pymongo import MongoClient
import boto3
import botocore
import json
from bson import ObjectId, json_util
from botocore.exceptions import NoCredentialsError
from functools import wraps
import logging
import traceback
from flask_session import Session
import random
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from random import randint
from flask_mail import Mail, Message

# Initialize the logging configuration
logging.basicConfig(filename='error.log', level=logging.ERROR)

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['SESSION_TYPE'] = 'filesystem'  # Use the filesystem for session storage
app.config['SESSION_PERMANENT'] = True
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
mail= Mail(app)

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'shashankn7261@gmail.com'
app.config['MAIL_PASSWORD'] = 'zcbt nupd ajkj cyoe'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

AWS_ACCESS_KEY_ID = "AKIA3BOLL3RQYEWKMV4B"
AWS_ACCESS_KEY_SECRET = "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"
AWS_S3_REGION = "ap-south-1"
AWS_S3_BUCKET = "tto-asset"

myclient = pymongo.MongoClient("mongodb+srv://Developer:Bahubhashak@bahubhashaak-project.ascwu.mongodb.net")
mydb = myclient["leaderboard"]  # database
mycol = mydb['details'] 
collection = mydb["submitresult"]
testcollection = mydb["UploadedTests"]
admincollection = mydb["admindetails"]
usercollection = mydb["userdetails"]
organisationcollection = mydb["approved"]
toolcollection = mydb["tools"]
campaigncollection = mydb["Campaign"]

counter = 1
count = 1
ucount = 1

admins = [admin['User Name'] for admin in admincollection.find({}, {"User Name": 1})]
users = [users['name'] for users in organisationcollection.find({}, {"name": 1})]

# pages rendering
def admin_required(view_func):
    @wraps(view_func)
    def decorated_view(*args, **kwargs):
        if 'username' in session and session['username'] in admins:
            return view_func(*args, **kwargs)
        else:
            return "You are not authorized to access this page."
    return decorated_view

def user_required(view_func):
    @wraps(view_func)
    def decorated_view(*args, **kwargs):
        if 'username' in session and session['username'] in users:
            return view_func(*args, **kwargs)
        else:
            return "You are not authorized to access this page."
    return decorated_view

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    username = data['username']
    password = data['password']

    # Check for the user in both admin details and approved collections
    admin_data = admincollection.find_one({'User Name': username, 'Password': password})
    organisation_data = organisationcollection.find_one({
        'status': 'Accepted',
        'name': username,
        'password': password
    })

    if admin_data:
        user_role = 'admin'
        user_id = str(admin_data['_id'])

        # No organization or campaign for admin
        organization = ''
        campaign_id = ''  # Change this line to set campaign_id to an empty string
        campaign_name = ''

        session["user_id"] = user_id

    elif organisation_data:
        user_role = 'normal'
        user_id = str(organisation_data['_id'])

        # Fetch additional user information, such as organization and campaign
        organization = organisation_data.get('organisation', '') if organisation_data else ''
        campaign_id = str(organisation_data.get('campaign', ''))  # Ensure campaign_id is set to an empty string if not found

        # If campaign_id is not empty, convert ObjectId to string
        campaign_id_str = campaign_id if campaign_id else ''

        # Set the campaignId in the session
        session['campaign'] = campaign_id_str
        print(f"Session after login: {dict(session)}")

        # Query the Campaigns collection to get the campaign details if campaign_id is not empty
        if campaign_id:
            campaign_data = campaigncollection.find_one({'_id': ObjectId(campaign_id)})
            campaign_name = campaign_data.get('campaign', '') if campaign_data else ''
        else:
            campaign_name = ''

    else:
        return jsonify({'status': 'error', 'message': 'Invalid credentials'})

    session['logged_in'] = True
    session['username'] = username
    session['organisation'] = organization
    session['campaignId'] = campaign_id
    session['campaign'] = campaign_name

    print(f"{user_role.capitalize()} User Logged In: {username}, ID: {user_id}, Organization: {organization}, CampaignId: {campaign_id}, Campaign:{campaign_name}")
    print("Session after login:", dict(session))

    # Update the organization and campaign dynamically in the frontend
    session['login_response'] = {
        'status': 'success',
        'message': 'Login successful',
        'role': user_role,
        'user_id': user_id,
        'username': username,
        'organisation': organization,
        'campaignId': campaign_id,
        'campaign': campaign_name
    }

    return jsonify(session['login_response'])
   
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
    

@app.route('/about_a.html')
@admin_required
def adminabout_data():
    data = {
        "title": "HIMANGY",
        "description": "HIMANGY (HIndustani Machini ANuvaad TechnoloGY) is an Indian Language to Indian Language Machine Translation project. It is a consortium based project under BHASHINI and is funded by Ministry of Electronics and Information Technology (Meity), Government of India. IIIT-Hyderabad is the lead institute of the project.",
        # Add more data as needed
    }
    return jsonify(data)


@app.route('/objective_a.html')
@admin_required
def adminobjective_api():
    data = {
        "title": "Our Objective",
        "content": "This is our objective content in JSON format."
    }
    return jsonify(data)


@app.route('/consortium_a.html')
@admin_required
def adminconsortium_api():
    data = {
        "title": "Our Consortium",
        "content": "This is our consortium content in JSON format.",
        "details": "You can include additional data here."
    }
    return jsonify(data)

@app.route('/documents_a.html')
@admin_required
def admindocuments_api():
    data = {
        "title": "Documents",
        "content": "This is the documents content in JSON format.",
        "details": "You can include additional data here."
    }
    return jsonify(data)
   
@app.route('/tools', methods=['GET'])
def tools_api():
    try:
        # Assuming you have a MongoDB collection named 'toolcollection'
        items = toolcollection.find({"status": "published"})

        # Convert MongoDB cursor to a list of dictionaries
        tool_list = []
        for item in items:
            item["_id"] = str(item["_id"])  # Convert ObjectId to string
            tool_list.append(item)

        # Return the data as JSON
        response_data = {
            "tools": tool_list
        }

        return jsonify(response_data)

    except Exception as e:
        return jsonify({"error": str(e)})


@app.route('/api/tasktype', methods=['GET'])
def tasktype_api():
    try:
        # Get the selected campaign from the query parameters
        selected_campaign = request.args.get('campaign')

        # Define a filter based on the selected campaign
        filter = {}
        if selected_campaign:
            filter["_id"] = ObjectId(selected_campaign)

        # Retrieve data from the database with the specified filter
        items = campaigncollection.find(filter)

        # Convert MongoDB cursor to a list of dictionaries, convert ObjectId to string
        items_list = []
        for item in items:
            item_dict = dict(item)
            item_dict['_id'] = str(item_dict['_id'])
            items_list.append(item_dict)

        # Construct the response data
        response_data = {
            "campaign": items_list,
        }
        return jsonify(response_data)
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/tasktypes/<campaign_id>', methods=['GET'])
def get_tasktypes_for_campaign(campaign_id):
    try:
        # Find the campaign based on the provided campaign_id
        campaign = campaigncollection.find_one({"_id": ObjectId(campaign_id)})

        if campaign:
            tasktypes = campaign.get("tasktypes", [])
            return jsonify({"campaign": campaign["campaign"], "tasktypes": tasktypes})
        else:
            return jsonify({"error": "Campaign not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)})

# Updated endpoint to get scores for a specific task type
    
@app.route('/api/leaderboard/<campaign_id>/<task_type>', methods=['GET'])
def get_leaderboard_data(campaign_id, task_type):
    try:
        leaderboard_data = list(collection.find({
            "campaignId": campaign_id,
            "tasktype": task_type
        }))
        return jsonify({"items": json_util.dumps(leaderboard_data)})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/leaderboard/<campaign_id>/<task_type>/<user_id>', methods=['GET'])
def get_leaderboard_data_user(campaign_id, task_type):

    # Read the saved login response from the file
    with open('./login_response.json', 'r') as file:
        login_response = json.load(file)
        role = login_response.get('role', '')
        user_id = login_response.get('user_id', 'Unknown')
        username = login_response.get('username', '')
        organisation = login_response.get('organisation', '')
        campaign_id = login_response.get('campaignId', '')  # Extract campaignId
        campaign = login_response.get('campaign', '')

        # Set the session data
        session['role'] = role
        session['user_id'] = user_id
        session['username'] = username
        session['organisation'] = organisation
        session['campaignId'] = campaign_id
        session['campaign'] = campaign

    try:
        with open('./login_response.json', 'r') as file:
                login_response = json.load(file)
                user_id = login_response["user_id"]
        if user_id:
            leaderboard_data = list(collection.find({
                "campaignId": campaign_id,
                "tasktype": task_type,
                "userId": user_id
            }))
            return jsonify({"items": json_util.dumps(leaderboard_data)})
        else:
            return jsonify({"error": "User not authenticated"})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/', methods=['GET'])
def campaign_api():

    # Fetch user details from login_response.json
    with open('login_response.json', 'r') as login_file:
        user_details = json.load(login_file)

    # Log the user details to the console
    print("User Details:", user_details)

    # Get the user's registered campaign
    user_campaign = user_details.get('campaign')

    try:
        # Retrieve all campaigns from the collection
        all_campaigns = list(campaigncollection.find({}))

        # Separate campaigns into two lists: user's registered campaign and others
        user_campaign_tools = [tool for tool in all_campaigns if tool['campaign'] == user_campaign]
        other_campaign_tools = [tool for tool in all_campaigns if tool['campaign'] != user_campaign]

        # Convert MongoDB cursor to a list of dictionaries
        tool_list = user_campaign_tools + other_campaign_tools

        # Convert ObjectId to string
        for tool in tool_list:
            tool["_id"] = str(tool["_id"])

        # Return the data as JSON including user status and role
        response_data = {
            "tools": tool_list,
        }

        return jsonify(response_data)

    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/leaderboard', methods=['GET'])
def leaderboard_api():
    try:
        # Get the selected campaign and tasktype from the query parameters
        selected_campaign = request.args.get('campaign')
        selected_tasktype = request.args.get('tasktype')
        sort_param = request.args.get('sort', 'bleu')  # Default sorting by "bleu" if not provided

        # Define a filter based on the selected campaign and tasktype
        filter = {"status": "published"}
        if selected_campaign:
            filter["campaignId"] = selected_campaign
        if selected_tasktype:
            filter["tasktype"] = selected_tasktype

        items = collection.find(filter).sort(sort_param, -1)


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
  
@app.route('/api/download', methods=['GET'])
def download_api():
    try:
        session.clear()

        # Read the saved login response from the file
        with open('./login_response.json', 'r') as file:
            login_response = json.load(file)
            user_id = login_response.get('user_id', 'Unknown')
            username = login_response.get('username', '')
            organisation = login_response.get('organisation', '')
            campaign_id = login_response.get('campaignId', '')  # Extract campaignId
            campaign = login_response.get('campaign','')

            # Set the session data
            session['user_id'] = user_id
            session['username'] = username
            session['organisation'] = organisation
            session['campaignId'] = campaign_id
            session['campaign'] = campaign

        task_type = request.args.get('tasktype', None)  # Get the tasktype query parameter

        if task_type:
            data = testcollection.find({'tasktype': task_type})  # Filter the data based on the task type
        else:
            data = testcollection.find()

        # Convert MongoDB cursor to a list of dictionaries
        download_list = []
        for item in data:
            item["_id"] = str(item["_id"])  # Convert ObjectId to string
            download_list.append(item)

        # Return the data as JSON along with additional user information
        response_data = {
            "data": download_list,
            "user_info": {
                "user_id": user_id,
                "username": username,
                "organisation": organisation,
                "campaignId": campaign_id,
                "campaign": campaign
            }
        }

        return jsonify(response_data)

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)})

@app.route('/api/benchmarks', methods=['GET'])
def get_benchmarks():
    try:
        # Fetch the benchmark data from your MongoDB collection
        benchmark_data = testcollection.distinct('filename')

        return jsonify(benchmark_data)

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)})


@app.route('/api/myleaderboard', methods=['GET'])
def myleaderboard_api():
    try:
        # Read the saved login response from the file
        with open('./login_response.json', 'r') as file:
            login_response = json.load(file)
            user_id = login_response.get('user_id')

        # Check if user is authenticated
        if user_id:
            # Get the selected campaign and tasktype from the query parameters
            selected_campaign = request.args.get('campaign')
            selected_tasktype = request.args.get('tasktype')
            sort_param = request.args.get('sort', 'bleu')

            # Define a filter based on the selected campaign, tasktype, and userId
            filter = {"status": "published", "userId": user_id}
            if selected_campaign:
                filter["campaignId"] = selected_campaign
            if selected_tasktype:
                filter["tasktype"] = selected_tasktype

            items = collection.find(filter).sort({sort_param: -1})

            # Convert MongoDB cursor to a list of dictionaries
            leaderboard_list = []
            for item in items:
                item_dict = dict(item)
                item_dict["_id"] = str(item_dict["_id"])
                leaderboard_list.append(item_dict)

            # Return the data as JSON, including userId
            response_data = {
                "items": leaderboard_list,
                "userId": user_id
            }

            return jsonify(response_data)
        else:
            # User is not authenticated
            return jsonify({"error": "User not authenticated"})

    except Exception as e:
        return jsonify({"error": str(e)})
       
@app.route('/api/submit', methods=['GET'])
def submit_api():
    try:
        # Clear all existing session data
        session.clear()

        # Read the saved login response from the file
        with open('./login_response.json', 'r') as file:
            login_response = json.load(file)
            user_id = login_response.get('user_id', 'Unknown')
            username = login_response.get('username', '')
            organisation = login_response.get('organisation', '')
            campaign_id = login_response.get('campaignId', '')  # Extract campaignId
            campaign = login_response.get('campaign','')

            # Set the session data
            session['user_id'] = user_id
            session['username'] = username
            session['organisation'] = organisation
            session['campaignId'] = campaign_id
            session['campaign'] = campaign

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
            "data2": data2_list,
            "user_id": user_id,  # Include user_id in the response
            "organization": organisation,  # Include organization in the response
            "username": username,
            "campaignId": campaign_id,  # Include campaignId in the response
            "campaign": campaign
        }

        print(f"User ID: {user_id}, Organization: {organisation}, Campaign ID: {campaign_id}")

        return jsonify(response_data)
    except Exception as e:
        return jsonify({"error": str(e)})
       
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

@app.route('/api/approval', methods=['GET', 'POST'])
def approval_api():
    if request.method == 'GET':
        try:
            # Retrieve data from the database
            items = organisationcollection.find()

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
            return jsonify({"error": f"An error occurred: {str(e)}"})

    elif request.method == 'POST':
        try:
            # Handle the POST request data
            data = request.json
            _id = data.get("_id")
            status = data.get("status")

            # Update the status in the MongoDB collection based on Accept or Decline
            organisationcollection.update_one(
                {'_id': ObjectId(_id)},
                {'$set': {'status': status}}
            )

            # Construct a response indicating success
            response_data = {
                "message": "Data received and processed successfully",
                "status": "success",
                "received_data": data
            }
            return jsonify(response_data)
        except Exception as e:
            return jsonify({"error": f"An error occurred: {str(e)}"})


@app.route('/api/accepted', methods=['POST', 'GET'])
def api_accepted():
    if request.method == 'POST':
        try:
            # Handle the POST request data as JSON
            data = request.json
            organisation = data.get("organisation")
            name = data.get("name")
            email = data.get("email")  # Assuming there's an 'email' field in your data

            organisationcollection.update_one(
                {'organisation': organisation, 'name': name},
                {'$set': {'status': "Accepted"}}
            )
            print("Accepted")

            # Send email notification
            send_email_notification(email, "Accepted")

            items = list(organisationcollection.find({}))
            return jsonify({'status': 'success', 'items': items})

        except Exception as e:
            return jsonify({"error": f"An error occurred: {str(e)}"})

    elif request.method == 'GET':
        return jsonify({'status': 'error', 'message': 'GET method not allowed for this endpoint'})


@app.route('/api/declined', methods=['POST', 'GET'])
def api_declined():
    if request.method == 'POST':
        try:
            # Handle the POST request data as JSON
            data = request.json
            organisation = data.get("organisation")
            name = data.get("name")
            email = data.get("email")  # Assuming there's an 'email' field in your data

            organisationcollection.update_one(
                {'organisation': organisation, 'name': name},
                {'$set': {'status': "Declined"}}
            )
            print("Declined")

            # Send email notification
            send_email_notification(email, "Declined")

            items = list(organisationcollection.find({}))
            return jsonify({'status': 'success', 'items': items})

        except Exception as e:
            return jsonify({"error": f"An error occurred: {str(e)}"})

    elif request.method == 'GET':
        return jsonify({'status': 'error', 'message': 'GET method not allowed for this endpoint'})

def send_email_notification(to_email, status):
    try:
        if to_email is not None:
            # Create a message
            subject = "Request Status"
            body = f"Your request has been {status}."
            recipients = [to_email]  # Change this to the actual recipient's email
            message = Message(subject=subject, sender='shashankn7261@gmail.com', recipients=recipients, body=body)

            # Send the email
            mail.send(message)

            print(f"Email notification sent successfully to {to_email} for status: {status}")
        else:
            print(f"No valid email provided for status: {status}")

    except Exception as e:
        print(f"Error sending email notification: {str(e)}")



            
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

@app.route('/api/edit', methods=['GET', 'POST'])
def edit_api():
    try:
        if request.method == 'POST':
            # Handle POST request data and update the database as needed
            data = request.json
            # ...
            return jsonify({"status": "success"})

        # Handle GET request and return data from the database
        selected_tasktype = request.args.get('tasktype')

        # Define a filter based on the selected tasktype
        filter = {"status": "published"}
        if selected_tasktype:
            filter["tasktype"] = selected_tasktype

        items = collection.find(filter).sort("bleu", -1)

        # Convert MongoDB cursor to a list of dictionaries, convert ObjectId to string
        items_list = []
        for item in items:
            item['_id'] = str(item['_id'])
            items_list.append(item)

        # Construct the response data
        response_data = {
            "items": items_list,  
            "status": "success"
        }
        return jsonify(response_data)
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/editcampaign', methods=['GET', 'POST'])
def editcampaign_api():
    try:
        if request.method == 'POST':
            # Handle POST request data and update the database as needed
            data = request.json
            # ...
            return jsonify({"status": "success"})

        items = campaigncollection.find().sort("bleu", -1)

        # Convert MongoDB cursor to a list of dictionaries, convert ObjectId to string
        items_list = []
        for item in items:
            item['_id'] = str(item['_id'])
            items_list.append(item)

        # Construct the response data
        response_data = {
            "items": items_list,  
            "status": "success"
        }
        return jsonify(response_data)
    except Exception as e:
        return jsonify({"error": str(e)})

    
@app.route('/api/delete-checkboxes', methods=['POST'])
def api_delete_checkboxes():
    try:
        row_numbers = request.get_json()['rowNumbers']
        print(row_numbers)
        split_list = [item.split(',') for item in row_numbers]
        print(split_list)

        for number in split_list:
            print(number[0], number[1], number[2], number[3], number[4], number[5], number[6], number[7], number[8])
            collection.delete_one({
                'rowno': number[0],
                'organisation': number[1],
                'language': number[2],
                'module': number[3],
                'version': number[4],
                'bleu': number[5],
                'chrf': number[6],
                'ter': number[7],
                'score': number[8],
                'status': 'published'
            })
            print('deleted')

        return jsonify({"message": "Selected rows deleted successfully", "status": "success"})
    except Exception as e:
        return jsonify({"message": "An error occurred: " + str(e), "status": "error"}), 500 

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
      k.append(i['ter'])
      k.append(i['score'])
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
      k.append(i['ter'])
      k.append(i['score'])
      l.append(k)
  response=json.dumps(l)
  return response

@app.route('/api/userleaderboard', methods=['GET'])
def userleaderboard_api():
    try:
        # Get the selected campaign and tasktype from the query parameters
        selected_campaign = request.args.get('campaign')
        selected_tasktype = request.args.get('tasktype')

        # Define a filter based on the selected campaign and tasktype
        filter = {"status": "published"}
        if selected_campaign:
            filter["campaignId"] = selected_campaign
        if selected_tasktype:
            filter["tasktype"] = selected_tasktype

        items = collection.find(filter).sort("bleu", -1)

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

@app.route('/api/userdownload', methods=['GET'])
def userdownload_api():
    try:
        data = testcollection.find()

        # Convert MongoDB cursor to a list of dictionaries
        data_list = [dict(item, _id=str(item['_id'])) for item in data]

        # Construct the response data
        response_data = {
            "data": data_list,  # Include your data here
            "status": "success"
        }
        return jsonify(response_data)
    except Exception as e:
        return jsonify({"error": str(e)})
    

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

#main

@app.route('/',methods=['GET','POST'])
def data():
    try:
        return render_template('about.html')
    except:
        return ("Unable to load page")
    
class SignInResource(Resource):
    def get(self):
        try:
            # Replace with any specific logic you need for sign-in
            return jsonify({"message": "Please sign in."})
        except Exception as e:
            return jsonify({"error": str(e)})

@app.route('/api/signout', methods=['GET'])
def api_signout():
    session.clear()
    response = {'status': 'success', 'message': 'User signed out successfully'}

    if 'logged_in' in session:
        username = session.get('username')

        if username:
            # Check if the user is an admin by querying the database
            admin = admincollection.find_one({"username": username})
            if admin:
                print("Admin:", username)
                # Perform any additional admin-specific actions if needed
            else:
                print("Non-admin:", username)

        # Clear session data
        session.pop('logged_in', None)
        session.pop('username', None)
    else:
        response['status'] = 'error'
        response['message'] = 'User is not logged in'

    return jsonify(response)

class ProtectedResource(Resource):
    def get(self):
        if 'logged_in' not in session:
            return jsonify({"error": "You are not logged in."})
        else:
            items = collection.find({"tasktype": "Translation", "status": "published"})
            items1 = items.sort("bleu", -1)
            items_list = []

            for item in items:
                item_dict = item
                item_dict['_id'] = str(item['_id'])  # Convert ObjectId to string
                items_list.append(item_dict)

            # Use bson.json_util to serialize ObjectId to JSON
            json_items = json.loads(json_util.dumps(items_list))
            
            return jsonify({"items": json_items})

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

@app.route('/process-checkboxes', methods=['POST'])
def process_checkboxes():
    tasktype = request.form["tasktype"]
    slanguage = request.form["slanguage"]
    tlanguage = request.form["tlanguage"]
    checkbox_names = request.form.getlist('checkboxes')
    
    if not checkbox_names:
        return "No checkboxes selected"

    split_list = [item.split(',') for item in checkbox_names]

    if not split_list or len(split_list[0]) < 5:
        return "Invalid checkbox data format"

    print(split_list)
    
    try:
        filename = split_list[0][0]
        task_type = split_list[0][1]
        source_language = split_list[0][3]
        target_language = split_list[0][4]

        data = testcollection.find({
            "filename": filename,
            "tasktype": task_type,
            "sourcelanguage": source_language,
            "targetlanguage": target_language
        })

        l = []
        for i in data:
            print("data")
            print(i)
            l.append(i['fileurl'])
        print(l)

        if l:
            print(l[0])
            response1 = requests.get(l[0])
            print(response1)
        
            if response1.status_code == 200:
                file_contents = response1.content
                print(file_contents)
            
                file = BytesIO(file_contents)
                return send_file(file, download_name='file.txt', as_attachment=True)
            else:
                return 'Error: Could not download file'
        else:
            return "No file with the selected File Name"
    except Exception as e:
        return f"An error occurred: {str(e)}"

s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_ACCESS_KEY_SECRET, region_name=AWS_S3_REGION)

@app.route('/api/download/<filename>', methods=['GET'])
def download_file(filename):
    try:
        # Assuming you have a collection named 'testcollection' in your MongoDB
        data = testcollection.find_one({"filename": filename})

        if data:
            file_url = data.get('fileurl')

            if file_url:
                # Retrieve file from S3
                s3_response = s3.get_object(Bucket='tto-asset', Key=filename)
                file_contents = s3_response['Body'].read()

                # Create BytesIO object
                file = BytesIO(file_contents)

                # Set the Content-Disposition header
                response = send_file(
                    file,
                    download_name=filename,
                    as_attachment=True
                )
                response.headers["Content-Disposition"] = f"attachment; filename={filename}"

                return response
            else:
                return 'Error: File URL not found'
        else:
            return 'Error: File not found'
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    
@app.route('/delete-checkboxes', methods=['POST']) #based on checkboxs selecting files downloading(download pages)
def delete_checkboxes():
    row_numbers = request.get_json()['rowNumbers']
    print(row_numbers)
    split_list = [item.split(',') for item in row_numbers]
    print(split_list)

    for number in split_list:
        print(number[0],number[1],number[2],number[3],number[4],number[5],number[6],number[7])
        collection.delete_one(
            {'rowno': number[0],
             'organisation':number[1],
             'language':number[2],
             'module':number[3],
             'version':number[4],
             'bleu':number[5],
             'chrf':number[6],
             'ter':number[7],
             'score': number[8],
             'status':'published'})
        print('deleted')

    try:
        items=collection.find({"tasktype":"Translation","status":"published"})
        items1=items.sort("bleu",-1)
        print(items)   
        return render_template('edit.html',items=items)
    except:
        return ("Unable to load page")
        
@app.route('/api/submitlogin', methods=['POST'])
def api_submitlogin():
    data = request.get_json()
    username = data['username']
    password = data['password']

    # Check for the user in organisationcollection
    user_data = organisationcollection.find_one({
        'status': 'Accepted',
        'name': username,
        'password': password
    })

    if user_data:
        try:
            items = organisationcollection.find({"status": "Accepted", 'name': username, 'password': password})
            items1 = organisationcollection.find({"status": "Accepted", 'name': username, 'password': password})
            data = organisationcollection.find({"status": "Accepted"})
            data1 = organisationcollection.find({"status": "Accepted"})
            data2 = testcollection.find({})

            # Convert MongoDB cursor to a list of dictionaries
            items_list = []
            for item in items:
                item_dict = dict(item)
                item_dict["_id"] = str(item_dict["_id"])
                items_list.append(item_dict)

            items1_list = []
            for item in items1:
                item_dict = dict(item)
                item_dict["_id"] = str(item_dict["_id"])
                items1_list.append(item_dict)

            data_list = []
            for item in data:
                item_dict = dict(item)
                item_dict["_id"] = str(item_dict["_id"])
                data_list.append(item_dict)

            data1_list = []
            for item in data1:
                item_dict = dict(item)
                item_dict["_id"] = str(item_dict["_id"])
                data1_list.append(item_dict)

            data2_list = []
            for item in data2:
                item_dict = dict(item)
                item_dict["_id"] = str(item_dict["_id"])
                data2_list.append(item_dict)

            response_data = {
                "items": items_list,
                "items1": items1_list,
                "data": data_list,
                "data1": data1_list,
                "data2": data2_list
            }

            return jsonify({'status': 'success', 'data': response_data})
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)})
    else:
        return jsonify({'status': 'error', 'message': 'Invalid credentials'})

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
  
s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_ACCESS_KEY_SECRET, region_name=AWS_S3_REGION)

count = 0

def evaluate_metrics(hypotheses, references, sources):
    cer_score, wer_score, chrf_score, ter_score, bert_score, comet_score = cer_wer_chrf_ter_metrics(hypotheses, references, sources)
    precision, recall, f1 = calculate_precision_recall_f1(bert_score)
    return cer_score, wer_score, chrf_score, ter_score, bert_score, precision, recall, f1, comet_score

def calculate_precision_recall_f1(bert_score):
    # Check if precision, recall, and f1 scores are available
    if 'precision' in bert_score and 'recall' in bert_score and 'f1' in bert_score:
        precision_scores = bert_score['precision']
        recall_scores = bert_score['recall']
        f1_scores = bert_score['f1']

        # Calculate averages
        avg_precision = sum(precision_scores) / len(precision_scores)
        avg_precision = round(avg_precision* 100, 2)
        avg_recall = sum(recall_scores) / len(recall_scores)
        avg_recall = round(avg_recall* 100, 2)
        avg_f1 = sum(f1_scores) / len(f1_scores)
        avg_f1 = round(avg_f1 * 100, 2 )

        return avg_precision, avg_recall, avg_f1

    return None, None, None

def cer_wer_chrf_ter_metrics(hypotheses, references, sources):
    cer_score = cer(hypotheses, references)
    wer_score = wer(hypotheses, references)
    chrf_score = chrf(hypotheses, references)
    ter_score = ter(hypotheses, references)
    bert_score = bertscore(hypotheses, references)
    comet_score = comet(hypotheses, references, sources)
    return cer_score, wer_score, chrf_score, ter_score, bert_score, comet_score

def comet(hypotheses, references, sources):
    metric = evaluate.load('comet')
    comet_results = metric.compute(predictions=hypotheses, references=references, sources=sources)

    # Check if scores are available and not empty
    if "scores" in comet_results and comet_results["scores"]:
        scores = comet_results["scores"]
        
        # Calculate the average of the scores
        avg_comet_score = sum(scores) / len(scores)
        avg_comet_score = round(avg_comet_score * 100, 2) 
        return f'{avg_comet_score:.2f}'

    return "No scores available"


def bertscore(hypotheses, references):
    metric = evaluate.load('bertscore')
    bert_score = metric.compute(predictions=hypotheses, references=references, model_type="distilbert-base-uncased")
    return bert_score

def cer(hypotheses, references):
    metric = evaluate.load('cer')
    cer_score = metric.compute(predictions=hypotheses, references=references) * 100
    return f'{cer_score:.2f}'

def wer(hypotheses, references):
    metric = evaluate.load('wer')
    wer_score = metric.compute(predictions=hypotheses, references=references) * 100
    return f'{wer_score:.2f}'

def chrf(hypotheses, references):
    metric = evaluate.load('chrf')
    chrf_result = metric.compute(predictions=hypotheses, references=references)
    chrf_score = chrf_result['score'] 
    return f'{chrf_score:.2f}'

def ter(hypotheses, references):
    metric = evaluate.load('ter')
    ter_result = metric.compute(predictions=hypotheses,references=references,normalized=True,ignore_punct=True,case_sensitive=True)
    ter_score = ter_result['score']
    return f'{ter_score:.2f}'

def read_fixed_lines(file_path, num_lines):
    lines = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for _ in range(num_lines):
            line = f.readline().strip()
            if not line:
                break  # Break if there are no more lines in the file
            lines.append(line)
    return lines

@app.route('/api/newform', methods=['POST', 'GET'])
def newform_api():
    count = collection.count_documents({})

    # Increment count to get the next rowno
    count += 1

    # Read the saved login response from the file
    with open('./login_response.json', 'r') as file:
        login_response = json.load(file)
        role = login_response.get('role', '')
        user_id = login_response.get('user_id', 'Unknown')
        username = login_response.get('username', '')
        organisation = login_response.get('organisation', '')
        campaign_id = login_response.get('campaignId', '')  # Extract campaignId
        campaign = login_response.get('campaign', '')

        # Set the session data
        session['role'] = role
        session['user_id'] = user_id
        session['username'] = username
        session['organisation'] = organisation
        session['campaignId'] = campaign_id
        session['campaign'] = campaign

    try:
        # Extract data based on user role
        if role == "admin":
            organisation = request.form["organisation"]
            campaign_id = request.form["campaign"]
            tasktype = request.form["tasktype"]
            slanguage = request.form["slanguage"]
            tlanguage = request.form["tlanguage"] 
            testsetname = request.form["testsetname"]
            module = request.form["module"]
            version = request.form["version"]
            file = request.files["file"]
            with open('./login_response.json','r') as file:
                login_response = json.load(file)
                userId = login_response["user_id"]
        else:
            with open('./login_response.json', 'r') as file:
                login_response = json.load(file)
                organisation = login_response["organisation"]
                campaign = login_response["campaign"]
                userId = login_response["user_id"]
            tasktype = request.form["tasktype"]
            slanguage = request.form["slanguage"]
            tlanguage = request.form["tlanguage"]
            testsetname = request.form["testsetname"]
            module = request.form["module"]
            version = request.form["version"]
            file = request.files["file"]

        print(f"Organisation: {organisation}")

        file_data = file.read()
        file_size = len(file_data)
        print(f"The size of the file is: {file_size} bytes")

        # Upload file to AWS S3
        s3.upload_fileobj(io.BytesIO(file_data), AWS_S3_BUCKET, f"SubmitFiles/{tlanguage}_usr.txt")
        print("File UPLOADED to S3")

        # Get public URL for the uploaded file
        file_url = f"https://{AWS_S3_BUCKET}.s3.amazonaws.com/SubmitFiles/{tlanguage}_usr.txt"
        print(f"File URL: {file_url}")

        # Download the submitted file and save it to the local desktop
        local_hypothesis_path = './hypothesis.txt'  # Specify the path where you want to save the hypothesis file locally
        with open(local_hypothesis_path, 'wb') as local_hypothesis_file:
            local_hypothesis_file.write(file_data.strip())

        print("Hypothesis file saved to local desktop:", local_hypothesis_path)

        ref_cursor = testcollection.find({
            "sourcelanguage": slanguage,
            "targetlanguage": tlanguage,
            "tasktype": tasktype,
            "filename": testsetname
        })

        # Convert the cursor to a list
        ref = list(ref_cursor)

        print("Query criteria:")
        print(f"sourcelanguage: {slanguage}, targetlanguage: {tlanguage}, tasktype: {tasktype}, filename: {testsetname}")

        ref_count = len(ref)
        print(f"Number of matching documents: {ref_count}")

        if ref_count > 0:
            print("Reference file found.")
            matching_document = ref[0]
            sor_url = matching_document.get('fileurl')
            ref_url = matching_document.get('targetfileurl')
            print("Reference URL:", ref_url)
            print("Source URL:", sor_url)

            if ref_url:
                response1 = requests.get(ref_url)
                response2 = requests.get(sor_url)

                # Save the reference file to the desired location on the local server
                with open('./rf.txt', 'w', encoding='utf-8') as f:
                    f.write(response1.text.strip())

                print("Reference file saved to local directory")

                with open('./sf.txt', 'w', encoding='utf-8') as f:
                    f.write(response2.text.strip())

                print("Source file saved to local directory")

                # Get the contents of the hypothesis file
                with open(local_hypothesis_path, 'r', encoding='utf-8') as f:
                    hypothesis_text = f.read()

                # Reference file is already saved to ./rf.txt, so read from this file
                with open('./rf.txt', 'r', encoding='utf-8') as f:
                    reference_text = f.read()

                # Reference file is already saved to ./rf.txt, so read from this file
                with open('./sf.txt', 'r', encoding='utf-8') as f:
                    source_text = f.read()

                hypothesis_text_list = hypothesis_text.split("\n")
                reference_text_list = reference_text.split("\n")
                source_text_list = source_text.split("\n")

                print(len(hypothesis_text_list), len(reference_text_list), len(source_text_list))


                bleu = BLEU()
                r = bleu.corpus_score(hypothesis_text_list, [reference_text_list])
                print(r)
                text = str(r)
                parts = text.split()
                bleuscore = parts[2]
                print(bleuscore)
                """ s = bleu.get_signature()
                print(s) """

                hypothesis_text = "\n".join(hypothesis_text_list)
                reference_text = "\n".join(reference_text_list)
                source_text = "\n".join(source_text_list)

                # Call evaluate_metrics function to get scores
                cer_score, wer_score, chrf_score, ter_score, bert_score, precision, recall, f1, comet_score = evaluate_metrics(hypothesis_text_list, reference_text_list, source_text_list)

                print(f"CER Score: {cer_score}")
                print(f"WER Score: {wer_score}")
                print(f"TER Score: {ter_score}")
                print(f"CHRF Score: {chrf_score}")
                print(f"BLEU Score: {bleuscore}")
                print(f"BERT Score: {bert_score}")
                print(f"PRECISION: {precision}")
                print(f"RECALL: {recall}")
                print(f"F1: {f1}")
                print(f"COMET Score: {comet_score}")

                # Save scores to a file
                scores_file_path = './scores.txt'
                with open(scores_file_path, 'w') as scores_file:
                    scores_file.write(f"CER Score: {cer_score}\n")
                    scores_file.write(f"WER Score: {wer_score}\n")
                    scores_file.write(f"TER Score: {ter_score}\n")
                    scores_file.write(f"CHRF Score: {chrf_score}\n")
                    scores_file.write(f"BLEU Score: {bleuscore}\n")
                    scores_file.write(f"PRECISION: {precision}\n")
                    scores_file.write(f"RECALL: {recall}\n")
                    scores_file.write(f"F1: {f1}\n")    
                    scores_file.write(f"COMET Score: {comet_score}\n")


                print("Complete")

                data1 = chrf_score
                data = bleuscore
                data2 = ter_score
                data3 = cer_score
                data4 = wer_score
                data5 = precision
                data6 = recall
                data7 = f1
                data8 = comet_score

                # Update the document with campaignId
                document = {
                    "rowno": str(count),
                    "organisation": organisation,
                    "tasktype": tasktype,
                    "language": slanguage + '-' + tlanguage,
                    "sourcelanguage": slanguage,
                    "targetlanguage": tlanguage,
                    "testsetname": testsetname,
                    "module": module,
                    "version": version,
                    "fileurl": file_url,
                    "bleu": str(data),
                    "chrf": str(data1),
                    "ter": str(data2),
                    "cer": str(data3),
                    "wer": str(data4),
                    "precision" : str(data5),
                    "recall": str(data6),
                    "f1": str(data7),
                    "comet": str(data8),
                    "status": "in review",
                    "campaignId": campaign_id,  # Add campaignId to the document
                    "userId":user_id
                }

                # Your existing MongoDB insertion code...
                collection.insert_one(document)
                count = count + 1
                print(f"Stored document with count: {count}")

                scores_response = {"data": [data, data1, data2, data3, data4, data5, data6, data7, data8], "message": "Scores calculated and stored successfully"}
                scores_response["scores_file_path"] = scores_file_path
                return jsonify(scores_response)

        else:
            # No reference file found, return an error message
            error_message = "No Reference File found. Please re-check the required fields along with the Tasktypes."
            return jsonify({"error": error_message}), 400  # Use a 400 status code for client-side errors
    except ValueError as ve:
    # Handle specific error: Mismatch in the number of predictions and references
        error_message = str(ve)
        return jsonify({"error": error_message, "type": "ValueError"}), 400

    except NoCredentialsError:
        return jsonify({"error": "AWS credentials not available", "type": "AWSCredentialsError"}), 400

    except Exception as e:
        print(f"Unexpected Error: {e}")
        traceback.print_exc()
        return jsonify({"error": f"Unexpected Error: {e}", "type": "UnexpectedError"}), 500

@app.route('/api/get_scores', methods=['GET'])
def api_get_scores():
    try:
        # Read scores from the file
        with open('./scores.txt', 'r') as scores_file:
            scores = scores_file.read()

        return jsonify({"scores": scores, "message": "Scores fetched successfully"})

    except Exception as e:
        return jsonify({"error": f"Failed to fetch scores: {str(e)}"}), 500
    
@app.route('/api/publish', methods=['POST', 'GET'])
def api_publish():
    global count

    if request.method == 'POST':
        try:
            with open('./login_response.json', 'r') as file:
                login_response = json.load(file)
                organisation = login_response["organisation"]
            tasktype = request.form["tasktype"]
            slanguage = request.form["slanguage"]
            tlanguage = request.form["tlanguage"]
            testsetname = request.form["testsetname"]
            module = request.form["module"]
            version = request.form["version"]
            file = request.files["file"]

            file_data = file.read()
            f = io.BytesIO(file_data)

            # Your existing S3 and MongoDB update code...

             # Query the MongoDB collection for the updated items with status "in review"
            items_to_publish = collection.find({
                "status": "in review",
                "organisation": organisation,  # Adjust this based on your data model
                "tasktype": tasktype,  # Adjust this based on your data model
                "sourcelanguage": slanguage,
                "targetlanguage": tlanguage,
                "testsetname": testsetname,
                "module": module,
                "version": version,
                # Add more criteria if needed to uniquely identify the items to publish
            })

            # Update the status to "published" for the selected items
            for item in items_to_publish:
                collection.update_one(
                    {"_id": item["_id"]},
                    {"$set": {"status": "published"}}
                )

            return jsonify({"status": "success", "message": "Item(s) published successfully"})

        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})

    elif request.method == 'GET':
        try:
            # Query the MongoDB collection for the items with status "in review"
            items = collection.find({"status": "in review"})
            items1 = items.sort("version", -1)

            # Convert MongoDB cursor to a list of dictionaries
            items_list = list(items1)

            return jsonify({"status": "success", "items": items_list})

        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})

@app.route('/api/reject', methods=['POST', 'GET'])
def api_reject():
    global count

    if request.method == 'POST':
        try:
            with open('./login_response.json', 'r') as file:
                login_response = json.load(file)
                organisation = login_response["organisation"]
            tasktype = request.form["tasktype"]
            slanguage = request.form["slanguage"]
            tlanguage = request.form["tlanguage"]
            testsetname = request.form["testsetname"]
            module = request.form["module"]
            version = request.form["version"]
            file = request.files["file"]

            file_data = file.read()
            f = io.BytesIO(file_data)

            # Your existing S3 and MongoDB update code...

             # Query the MongoDB collection for the updated items with status "in review"
            items_to_publish = collection.find({
                "status": "in review",
                "organisation": organisation,  # Adjust this based on your data model
                "tasktype": tasktype,  # Adjust this based on your data model
                "sourcelanguage": slanguage,
                "targetlanguage": tlanguage,
                "testsetname": testsetname,
                "module": module,
                "version": version,
                # Add more criteria if needed to uniquely identify the items to publish
            })

            # Update the status to "published" for the selected items
            for item in items_to_publish:
                collection.update_one(
                    {"_id": item["_id"]},
                    {"$set": {"status": "rejected"}}
                )

            return jsonify({"status": "success", "message": "Item not published"})

        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})

    elif request.method == 'GET':
        try:
            # Query the MongoDB collection for the items with status "in review"
            items = collection.find({"status": "in review"})
            items1 = items.sort("version", -1)

            # Convert MongoDB cursor to a list of dictionaries
            items_list = list(items1)

            return jsonify({"status": "success", "items": items_list})

        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})
        
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


# Add a new Flask route for OTP generation and email sending
@app.route('/send-otp', methods=['POST'])
@cross_origin(supports_credentials=True)
def send_otp():

    global generated_otp  
    
    data = request.get_json()
    email = data.get('email')

    if not email:
        return jsonify({'error': 'Email is required'}), 400

    generated_otp = str(randint(1000, 9999))

    # Use your email server settings
    sender_email = 'shashankn7261@gmail.com'  # replace with your email
    sender_password = 'zcbt nupd ajkj cyoe'  # replace with your email password

    try:
        # Setup the MIME
        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = email
        message['Subject'] = 'Your OTP Code'

        # Add the body to the message
        message.attach(MIMEText(f'Your OTP code is: {generated_otp}', 'plain'))

        # Connect to the server and send the email
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, email, message.as_string())

        return jsonify({'message': 'OTP sent successfully'}), 200
    except Exception as e:
        print(f'Error: {e}')
        return jsonify({'error': 'Failed to send OTP email'}), 500

@app.route('/validate-otp', methods=['POST'])
@cross_origin(supports_credentials=True)
def validate_otp():
    data = request.get_json()
    entered_otp = data.get('enteredOTP')

    if not entered_otp:
        return jsonify({'error': 'Entered OTP is required'}), 400

    # Compare entered OTP with the generated OTP
    is_valid = entered_otp == generated_otp

    return jsonify({'isValid': is_valid}), 200

@app.route('/api/create/<string:campaign_id>', methods=['POST'])
def api_create(campaign_id):
    try:
        organisation = request.form["organisation"]
        email = request.form["email"]
        name = request.form["name"]
        password = request.form["password"]
        correctpassword = request.form["correctpassword"]

        # Convert campaign_id to ObjectId
        campaign_object_id = ObjectId(campaign_id)

        # Fetch campaign details from the Campaign collection
        campaign_details = campaigncollection.find_one({"_id": campaign_object_id})
        if not campaign_details:
            raise Exception("Invalid campaign ID")

        # Extract campaign name from the fetched details
        campaign_name = campaign_details["campaign"]

        document = {
            "organisation": organisation,
            "email": email,
            "name": name,
            "password": password,
            "correctpassword": correctpassword,
            "status": "pending",
            "campaign": campaign_id,
            "campaignName": campaign_name
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
    
@app.route('/api/register_campaign', methods=['GET'])
def register_campaign_api():
    try:
        # You can include any data retrieval or processing logic here if needed
        # Construct the response data
        response_data = {
            "message": "Register Campaign API is under development",
            "status": "success"
        }
        return jsonify(response_data)
    except Exception as e:
        return jsonify({"error": str(e)})

        
@app.route('/api/create_campaign', methods=['POST'])
def create_campaign():
    try:
        # Assuming you are sending campaign details in the request body as FormData
        campaign_name = request.form.get("campaign")
        task_types = json.loads(request.form.get("tasktypes"))

        # Extracting and saving the uploaded thumbnail file
        thumbnail_file = request.files['thumbnail']
        if thumbnail_file.filename == '':
            return jsonify({"error": "No selected file"}), 400

        tname = secure_filename(thumbnail_file.filename)
        tfile_data = thumbnail_file.read()

        # Upload the image to an AWS S3 bucket
        s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_ACCESS_KEY_SECRET)
        object_name = tname
        s3.upload_fileobj(io.BytesIO(tfile_data), AWS_S3_BUCKET, object_name)
        s3_url = f"https://{AWS_S3_BUCKET}.s3.amazonaws.com/{object_name}"

        # Updating the tasktypes structure
        tasktypes = [{"name": task["name"], "metrics": task["metrics"]} for task in task_types]

        # Creating a document for the new campaign
        campaign_document = {
            "campaign": campaign_name,
            "tasktypes": tasktypes,
            "fileurl": s3_url  # Use the S3 URL for the thumbnail
        }

        # Inserting the new campaign document into the campaign collection
        campaigncollection.insert_one(campaign_document)
        print("Campaign created:", campaign_document)

        response_data = {
            "message": "Campaign created successfully"
        }
        return jsonify(response_data), 200

    except Exception as e:
        error_message = str(e)
        response_data = {
            "error": f"Failed to create campaign. {error_message}"
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


@app.route('/api/upload', methods=['GET'])
def upload_api():
    try:
        items = organisationcollection.find({"status": "Accepted"})
        data = organisationcollection.find({"status": "Accepted"})
        data1 = organisationcollection.find({"status": "Accepted"})

        # Convert MongoDB cursor to a list of dictionaries
        items_list = [dict(item, _id=str(item['_id'])) for item in items]
        data_list = [dict(item, _id=str(item['_id'])) for item in data]
        data1_list = [dict(item, _id=str(item['_id'])) for item in data1]

        # Construct the response data
        response_data = {
            "items": items_list,
            "data": data_list,
            "data1": data1_list,
            "status": "success"
        }

        return jsonify(response_data)

    except Exception as e:
        return jsonify({"error": str(e)})


@app.route('/api/form2', methods=['POST'])
def api_form2():
    global ucount

    try:
        # Extract the data from the request
        datatype = request.form["datatype"]
        tasktype = request.form["tasktype"]
        campaign = request.form["campaign"]
        slanguage = request.form["slanguage"]
        tlanguage = request.form["tlanguage"]
        filename = request.form["filename"]
        file = request.files["sourceFile"]
        tfile = request.files["targetFile"]

        # Generate unique file names for source and target files
        file_name = f"TestSetFiles/{file.filename}"
        target_file_name = f"TargetFiles/{tfile.filename}"

        # Read file data
        file_data = file.read()
        tfile_data = tfile.read()

        # Create an S3 client
        s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_ACCESS_KEY_SECRET, region_name=AWS_S3_REGION)

        # Upload the source file to AWS S3
        s3.upload_fileobj(io.BytesIO(file_data), AWS_S3_BUCKET, file_name)

        # Get the public URL for the source file
        image_url = f"https://{AWS_S3_BUCKET}.s3.amazonaws.com/{file_name}"

        # Upload the target file to AWS S3
        s3.upload_fileobj(io.BytesIO(tfile_data), AWS_S3_BUCKET, target_file_name)

        # Get the public URL for the target file
        target_image_url = f"https://{AWS_S3_BUCKET}.s3.amazonaws.com/{target_file_name}"

        # Create a document for MongoDB
        document = {
            "id": str(ucount),
            "datatype": datatype,
            "tasktype": tasktype,
            "language": slanguage + '-' + tlanguage,
            "sourcelanguage": slanguage,
            "targetlanguage": tlanguage,
            "filename": filename,
            "fileurl": image_url,
            "targetfileurl": target_image_url,
            "status": "In review",
            "campaign": campaign,  # Add this line to store the selected campaign
        }

        # Convert ObjectId to string for JSON serialization
        document_str = {str(key): str(value) if isinstance(value, ObjectId) else value for key, value in document.items()}

        testcollection.insert_one(document)
        ucount += 1

        response_data = {
            "message": "Test data has been uploaded and is in review",
            "document": document_str,
        }

        return jsonify(response_data), 200

    except NoCredentialsError:
        return jsonify({"error": "AWS credentials not available"}), 400
    except KeyError as e:
        return jsonify({"error": f"KeyError: {str(e)}"}), 400
    except Exception as e:
        # Capture the traceback and log it
        traceback_str = traceback.format_exc()

        # Log the request data
        request_data = {
            "datatype": datatype,
            "tasktype": tasktype,
            "slanguage": slanguage,
            "tlanguage": tlanguage,
            "filename": filename,
            "file1": tfile.filename if tfile else None,
            "error_traceback": traceback_str,
        }
        logging.error(f"Error in request data: {request_data}")

        return jsonify({"error": f"Error: {str(e)}"}), 400
        
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
            "status": "published",
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
        organisation = row["organisation"]
        language = row["language"]
        module = row["module"]
        version = row["version"]
        bleu = row["bleu"]
        chrf = row["chrf"]
        ter = row["ter"]
        score = row["score"]

        # Update the data in the collection based on the "rowno" field
        collection.update_one({"rowno": rowno,"organisation": organisation,"language": language}, {"$set": {            
            "module": module,
            "version": version,
            "bleu":bleu,
            "chrf":chrf,
            "ter":ter,
            "score":score
        }})
        print("updated")

    return jsonify({"message": "Data updated successfully"})

@app.route('/updatecampaign', methods=['POST','GET'])#edited data updating in backend
def update_campaign():
    data = request.get_json()
    print(data)
    all_rows_data = data["rows"]
    print(all_rows_data)

    for row in all_rows_data:
        campaign = row["campaign"]
        tasktypes = row["tasktypes"]
        fileurl = row["fileurl"]

        # Update the data in the collection based on the "rowno" field
        collection.update_one({"campaign": campaign}, {"$set": {
            "tasktypes": tasktypes,
            "fileurl": fileurl,
        }})
        print("updated")

    return jsonify({"message": "Data updated successfully"})

if __name__ == "__main__":
    app.run(host='ec2-13-233-215-141.ap-south-1.compute.amazonaws.com', port=5000)









