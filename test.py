from flask import Flask,render_template,request,redirect,url_for
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
app=Flask(__name__)



#myclient=pymongo.MongoClient("mongodb://localhost:27017/")
myclient=pymongo.MongoClient("mongodb+srv://Developer:Bahubhashak@bahubhashaak-project.ascwu.mongodb.net")
mydb=myclient["leaderboard"]
mycol=mydb['details']
collection = mydb["submitresult"]
testcollection = mydb["UploadedTests"]
admincollection=mydb["admindetails"]
usercollection=mydb["userdetails"]
organisationcollection=mydb["approved"]
counter = 1
count=1
ucount=1



#pages rendering

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/consortium')
def consortium():
    return render_template('consortium.html')

@app.route('/documents')
def documents():
    return render_template('documents.html')

@app.route('/leaderboard')
def leaderboard():
    try:
        items=collection.find({"tasktype":"Translation","status":"published"})
        items1=items.sort("version",-1)
        print(items)
        
        return render_template('leaderboard.html',items=items)
    except:
        return ("Unable to load page")


@app.route('/download')
def download():
    try:
        data = testcollection.find({})
        return render_template('down_test_set.html',data=data)
    except:
        return ("Unable to load page")

@app.route('/submit')
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

@app.route('/register')
def register():
    try:
        return render_template('register.html')
    except:
        return ("Unable to load page")

@app.route('/approval',methods=['GET','POST'])
def approval():
    try:
        items = organisationcollection.find({})
        print(items)
        return render_template('approval.html',items=items)
    except:
        return ("Unable to load page")

@app.route('/upload')
def upload():
    try:
        items = organisationcollection.find({"status":"Accepted"})
        print(items)
        data=organisationcollection.find({"status":"Accepted"})
        data1=organisationcollection.find({"status":"Accepted"})
        return render_template('upload.html',items=items,data=data,data1=data1)
    except:
        return ("Unable to load page")

@app.route('/edit',methods=['GET','POST'])
def edit():
    try:
        items=collection.find({"tasktype":"Translation","status":"published"})
        items1=items.sort("version",-1)
        print(items)   
        return render_template('edit.html',items=items)
    except:
        return ("Unable to load page")

@app.route('/userleaderboard')
def userleaderboard():
    try:
        items=collection.find({"tasktype":"Translation","status":"published"})
        items1=items.sort("version",-1)
        
        return render_template('leaderboard1.html',items=items)
    except:
        return ("Unable to load page")

@app.route('/userdownload')
def userdownload():
    try:
        data = testcollection.find({})
        return render_template('download1.html',data=data)
    except:
        return ("Unable to load page")

@app.route('/usersubmitlogin')
def usersubmitlogin():
    try:
        
        return render_template('submitlogin.html')
    except:
        return ("Unable to load page")

@app.route('/usersubmit')
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


@app.route('/userregister')
def userregister():
    try:
        return render_template('register1.html')
    except:
        return ("Unable to load page")



@app.route('/signin')
def signin():
    try:
        
        return render_template('login.html')
    except:
        return ("Unable to load page")

@app.route('/signout')
def signout():
    try:
        items=collection.find({"tasktype":"Translation","status":"published"})
        items1=items.sort("version",-1)        
        return render_template('leaderboard1.html',items=items)
        
    except:
        return ("Unable to load page")


#main

@app.route('/',methods=['GET','POST'])
def data():
    try:
        items=collection.find({"tasktype":"Translation","status":"published"})
        items1=items.sort("version",-1)
        
        return render_template('leaderboard1.html',items=items)
    except:
        return ("Unable to load page")

@app.route('/login', methods=['POST','GET'])#sigin page
def login():
    username = request.form["username"]
    password = request.form["password"]
    print(username,password)
    data=admincollection.find({})
    print(data)
    names=[]
    passwords=[]
    for i in data:
        print(i)
        names.append(i['User Name'])
        passwords.append(i['Password'])
    if (username in names) and (password in passwords): 

        try:
            items=collection.find({"tasktype":"Translation","status":"published"})
            items1=items.sort("version",-1)
            print(items)
                
            return render_template('leaderboard.html',items=items)
        except:
            return ("Unable to load admin leaderboard page")
    else:
        try:
            #documnet={"username":username,"password":password}
            #usercollection.insert_one(document)
            #print("credentials stored")
            items=collection.find({"tasktype":"Translation","status":"published"})
            items1=items.sort("version",-1)
            print(items)
                
            return render_template('leaderboard1.html',items=items)
        except:
            return ("Unable to load user leaderboard page")

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

@app.route('/process1',methods=['POST'])  #download1 data filtering based on language
def process1():
    
    
    tasktype = request.form["tasktype"]
    slanguage = request.form["slanguage"]
    tlanguage = request.form["tlanguage"]

    print(tasktype,slanguage,tlanguage)
    print("went")
    data=testcollection.find({"sourcelanguage":slanguage,"targetlanguage":tlanguage,"tasktype":tasktype})
    return render_template('download1.html',data=data)

@app.route('/tprocess',methods=['POST'])  # down_test_set based on tasktype data filtering  code(not using present)
def tprocess():
    
    
    tasktype = request.form["tasktype"]
    slanguage = request.form["slanguage"]
    tlanguage = request.form["tlanguage"]

    print(tasktype,slanguage,tlanguage)
    print("went")
    data=testcollection.find({"tasktype":tasktype})
    return render_template('down_test_set.html',data=data)

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
            print(items)
            data=organisationcollection.find({"status":"Accepted"})
            data1=organisationcollection.find({"status":"Accepted"})
            data2=testcollection.find({})
            return render_template('submit1.html',items=items,data=data,data1=data1,data2=data2)
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
        
        return render_template('leaderboard.html',items=items)
    except:
        return ("error")

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
        
        return render_template('leaderboard1.html',items=items)
    except:
        return ("error")


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
        
        return render_template('leaderboard.html',items=items)
    except:
        return ("error")

@app.route('/update', methods=['POST','GET'])#edited data updating in backend
def update():
    rowno=request.form["rowno"]
    organisation = request.form["organisation"]
    language = request.form["language"]
    module = request.form["module"]
    version = request.form["version"]
    bleu= request.form["bleu"]
    chrf = request.form["chrf"]
    gleu = request.form["gleu"]

    print(rowno,organisation,language,module,version,bleu,chrf,gleu)
    items=collection.find({'rowno':rowno})
    for i in items:
        print(i)
        print("data")
    collection.update_one(
    {'rowno':rowno,'bleu': bleu,'chrf':chrf,'gleu':gleu},
    {'$set': {"organisation":organisation,'language':language,'module':module,'version':version,'status':"published"}}
    )
    print("updated")

    items=collection.find({"tasktype":"Translation","status":"published"})
    items1=items.sort("version",-1)
    print(items)
        
    return render_template('edit.html',items=items)




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









