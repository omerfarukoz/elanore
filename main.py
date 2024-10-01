from flask import Flask, redirect, url_for, request, render_template,session, stream_with_context, Response
import sqlite3
import uuid
import bcrypt
import requests
import json
import time
from datetime import datetime


app = Flask(__name__,static_folder='assets')
app.secret_key = "CHANGE_THIS_APP_SECRET"
database = sqlite3.connect('elanore.db',check_same_thread=False)


## START - TEMPLATE FUNCTIONS - START ##
@app.template_filter('timestamp_to_time')
def timestamp_to_time(value):
    if value:
        try:
            timestamp = int(float(value))
            return datetime.fromtimestamp(timestamp).strftime('%H:%M')
        except ValueError:
            return "Invalid timestamp"
    return ""

@app.template_filter('truncate_string')
def truncate_string(value, max_length=75):
    value = json.loads(value)[-1]["content"]
    if value and len(value) > max_length:
        return value[:max_length] + '...'
    return value
## END --- TEMPLATE FUNCTIONS --- END ##



## START - APP FUNCTIONS - START ##
def get_sessions(user_uuid):
    cursor = database.cursor()
    sql = f"""SELECT * FROM chats WHERE user_uuid='{user_uuid}';"""
    cursor.execute(sql)
    veriler = cursor.fetchall()
    cursor.close()
    return veriler

def insertuser(uuid,username,password,email,firstname,lastname,session):

    cursor = database.cursor()
    sql = f"""INSERT INTO users (uuid,username,password,email,firstname,lastname,sessions) VALUES('{uuid}','{username}','{password}','{email}','{firstname}','{lastname}','{session}');"""
    cursor.execute(sql)
    database.commit()
    cursor.close()
    #print(veriler)
## END --- APP FUNCTIONS --- END ##


## START - APP ROUTES (GET) - START ## 

@app.route('/')
def index():
    return redirect(url_for("home"))

@app.route('/home')
def home():
    if "uuid" not in session:
        return redirect(url_for("login"))
        
    chat_sessions = get_sessions(session["uuid"])
    cursor = database.cursor()
    sql = f"""SELECT * FROM users WHERE uuid='{session['uuid']}';"""
    cursor.execute(sql)
    userdata = cursor.fetchall()

    return render_template('home.html',chat_sessions=chat_sessions,userdata=userdata)

@app.route('/chat/<chatuuid>')
def getchat(chatuuid):
    if "uuid" not in session:
        return redirect(url_for("login"))
    cursor = database.cursor()
    sql = f"""SELECT * FROM chats WHERE uuid='{chatuuid}';"""
    cursor.execute(sql)
    messages = cursor.fetchall()
    cursor.close()
    all_messages_json = json.loads(messages[0][2])
    print(all_messages_json)


    cursor = database.cursor()
    sql = f"""SELECT * FROM users WHERE uuid='{session['uuid']}';"""
    cursor.execute(sql)
    userdata = cursor.fetchall()
    print(userdata)



    chat_sessions = get_sessions(session["uuid"])



    return render_template('chat-direct.html',all_messages_json=all_messages_json, session_key = chatuuid,chat_sessions=chat_sessions,userdata=userdata)

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('signup.html')


@app.route('/quit')
def quitsession():
    session["uuid"] = None
    return redirect(url_for("login"))

## END --- APP ROUTES (GET) --- END ## 




## START - API'S / APP ROUTES (POST) - START ## 

@app.route('/api/chat/<session_key>', methods=["POST"])
def api_getchat(session_key):

    if "uuid" not in session:
        return redirect(url_for("login"))


    data = request.form
    print(data)

    model = "llama3.1"
    prompt = data["prompt"]
    user_uuid = session["uuid"]

    new_message = {
        "role": "user",
        "content": prompt,
        "datatime": time.time()
    }

    cursor = database.cursor()
    sql = f"SELECT * FROM chats WHERE uuid='{session_key}';"
    cursor.execute(sql)
    mesajlar = json.loads(cursor.fetchall()[0][2])
    mesajlar.append(new_message)
    cursor.close()
    print(mesajlar)

    url = "http://localhost:11434/api/chat"
    request_data = {
        "model": model,
        "messages": mesajlar,
        "stream": True
    }

    last_message = ""

    def generate():
        nonlocal last_message

        with requests.post(url, json=request_data, stream=True) as r:
            for line in r.iter_lines():
                if line:
                    b_llama = json.loads(line.decode('utf-8'))
                    print(b_llama)
                    llama_response = b_llama["message"]["content"]
                    llama_done = b_llama["done"]

                    last_message += llama_response
                    yield json.dumps({"session": session_key, "llama_response": llama_response, "llama_done": llama_done}) + "\n"

    def save_last_message():
        nonlocal mesajlar
        cursor = database.cursor()
        sanitized_message = last_message.replace("'", "''")
        ai_message = {
            "role": "assistant",  
            "content": sanitized_message,
            "datatime": time.time()
        }
        mesajlar.append(ai_message)
        mesajlar = json.dumps(mesajlar)

        update_sql = f"""
        UPDATE chats SET messages = ? WHERE uuid = ?
        """
        try:
            print(f"Executing SQL: {update_sql}, Params: {mesajlar}, {session_key}") 
            cursor.execute(update_sql, (mesajlar, session_key)) 
            database.commit()
        except sqlite3.OperationalError as e:
            print(f"SQL error occurred: {e}")
        finally:
            cursor.close()

    response = Response(stream_with_context(generate()), content_type='text/event-stream')
    response.call_on_close(save_last_message)

    return response

@app.route('/api/login', methods = ['POST'])
def api_login():

    data = request.form

    if data["password"] == "" or data["email"] == "":
        res = {"status":False,"message":"Email or password cannot be empty!"}
        return res


    email = data["email"]
    password = data["password"].strip().encode('utf-8')

    cursor = database.cursor()
    sql = f"""SELECT * FROM users WHERE email='{email}';"""
    cursor.execute(sql)
    veriler = cursor.fetchall()
    if(len(veriler) > 0 ):
        db_password = veriler[0][2].encode("utf-8")
        if(bcrypt.checkpw(password, db_password)):
            print("yes")
            session["uuid"] = veriler[0][0]
            #return redirect(url_for("dashboard"))
            res = {"status":True,"message":"You have successfully logged in"}
            return res

    res = {"status":False,"message":"Email or password is incorrect."}
    return res

@app.route('/api/register', methods = ['POST'])
def api_register():

    data = request.form

    if data["firstname"] == "" :
        res = {"status":False,"message":"First Name cannot be empty!"}
        return res
    
    if data["lastname"] == "" :
        res = {"status":False,"message":"Last Name cannot be empty!"}
        return res
    
    if data["username"] == "" :
        res = {"status":False,"message":"Username cannot be empty!"}
        return res
    

    if data["password"] == "":
        res = {"status":False,"message":"Password cannot be empty!"}
        return res
    
    if data["email"] == "":
        res = {"status":False,"message":"Email cannot be empty!"}
        return res


    email = data["email"].strip()
    password = data["password"].strip().encode('utf-8')
    firstname = data["firstname"].strip()
    lastname = data["lastname"].strip()
    username = data["username"].strip()



    cursor = database.cursor()
    sql = f"""SELECT * FROM users WHERE email='{email}';"""
    cursor.execute(sql)
    veriler = cursor.fetchall()
    if(len(veriler) > 0 ):
        res = {"status":False,"message":"Email registered already!"}
        return res
        
    cursor = database.cursor()
    sql = f"""SELECT * FROM users WHERE username='{username}';"""
    cursor.execute(sql)
    veriler = cursor.fetchall()
    if(len(veriler) > 0 ):
        res = {"status":False,"message":"Username registered already!"}
        return res
        
    hashed = bcrypt.hashpw(password,bcrypt.gensalt()).decode("utf-8")
    user_uuid = uuid.uuid4()
    sessiona = "[]"
    session["uuid"] = user_uuid
    insertuser(user_uuid,username,hashed,email,firstname,lastname,sessiona)
    res = {"status":True,"message":"You have successfully registered"}
    return res

@app.route('/api/generate', methods=['POST'])
def generate_conversation():
    if "uuid" not in session:
        return redirect(url_for("login"))
    data = request.form
    print(data)
    model = "llama3.1"
    prompt = data["prompt"]
    user_uuid = session["uuid"]
    session_key = str(uuid.uuid4()) 

    url = "http://localhost:11434/api/generate"
    request_data = {
        "model": model,
        "prompt": prompt,
        "stream": True
    }

    last_message = "" 

    def generate():
        nonlocal last_message 

        with requests.post(url, json=request_data, stream=True) as r:
            for line in r.iter_lines():
                if line:
                    b_llama = json.loads(line.decode('utf-8'))
                    llama_response = b_llama["response"]
                    llama_done = b_llama["done"]

                    last_message += llama_response 
                    yield json.dumps({"session": session_key, "llama_response": llama_response, "llama_done": llama_done}) + "\n"

    first_messages = json.dumps([{
        "role": "user",
        "content": prompt,
        "datatime": time.time()
    }, {
        "role": "assistant",
        "content": last_message,  
        "datatime": time.time()
    }
    ])
    cursor = database.cursor()
    sql = f"INSERT INTO chats (uuid, user_uuid, messages, modelname, cr_time) VALUES('{session_key}', '{user_uuid}', '{first_messages}', '{model}', '{time.time()}');"
    cursor.execute(sql)
    database.commit()
    cursor.close()

    def save_last_message():
        cursor = database.cursor()
        
        sanitized_message = last_message.replace("'", "''")  
        
        update_sql = f"""
            UPDATE chats
            SET messages = JSON_SET(messages, '$[1].content', '{sanitized_message}')
            WHERE uuid = '{session_key}';
        """
        
        try:
            cursor.execute(update_sql)
            database.commit()
        except sqlite3.OperationalError as e:
            print(f"SQL error occurred: {e}")
        finally:
            cursor.close()

    response = Response(stream_with_context(generate()), content_type='text/event-stream')

    response.call_on_close(save_last_message)

    return response

## END --- API'S / APP ROUTES (POST) --- END ## 


## APP DEBUG ## ## APP DEBUG ## ## APP DEBUG ## ## APP DEBUG ## ## APP DEBUG ## ## APP DEBUG #### APP DEBUG ##
#P DEBUG ## ## APP DEBUG ## ## APP DEBUG ## ## APP DEBUG ## ## APP DEBUG #### APP DEBUG #### APP DEBUG #### AP
## APP DEBUG ## ## APP DEBUG ## ## APP DEBUG ## ## APP DEBUG ## ## APP DEBUG ## ## APP DEBUG #### APP DEBUG ##
#P DEBUG ## ## APP DEBUG ## ## APP DEBUG ## ## APP DEBUG ## ## APP DEBUG #### APP DEBUG #### APP DEBUG #### AP


@app.route('/stream/<key>', methods = ['POST','GET'])
def conversation(key):
    session_key = uuid.uuid4()
    print(session_key)
    url = "http://localhost:11434/api/chat"
    data = {
        "model": "llama3.1",
        "messages":[
            {
            "role":"user",
            "content":"Remember this: abcdefgh31!"
            }
        ],
        "stream": True
    }

    def generate():
        with requests.post(url, json=data, stream=True) as r:
            for line in r.iter_lines():
                if line:
                    yield f"data: {line.decode('utf-8')}\n\n"
                    
    return Response(stream_with_context(generate()), content_type='text/event-stream')

@app.route('/testsession')
def sessiona():
    return session["uuid"]

def debug_droptable():
    cursor = database.cursor()
    sql= """DROP TABLE chats;"""
    cursor.execute(sql)
    database.commit()
    cursor.close()

def debug_createusertable():
    cursor = database.cursor()
    sql = """CREATE TABLE IF NOT EXISTS users (
    uuid varchar(255),
    username varchar(255),
    password varchar(255),
    email varchar(255),
    firstname varchar(255),
    lastname varchar(255),
    sessions json
    );"""
    cursor.execute(sql)
    database.commit()
    cursor.close()

def debug_getuserlist():
    cursor = database.cursor()
    sql = """SELECT * FROM chats;"""
    cursor.execute(sql)
    veriler = cursor.fetchall()
    print(veriler)
    cursor.close()

def debug_createchattable():
    cursor = database.cursor()
    sql = """CREATE TABLE IF NOT EXISTS chats (
    uuid varchar(255),
    user_uuid varchar(255),
    messages json,
    modelname varchar(255),
    cr_time varchar(255)
    );"""
    cursor.execute(sql)
    database.commit()
    cursor.close()


#debug_createusertable()
#debug_createchattable()
#createchattable()
#droptable()
#createchattable()
#createtable()
#hash=bcrypt.gensalt()
#print(bcrypt.hashpw("deneme".encode("utf-8"),hash).decode('utf-8'))
#insertuser(uuid.uuid4(),"Admin","$2b$12$zH2wdtZ2A.GW5y7vt.eGQ.XApxrICJ4U098zU3FbIdu8iKI//XUu.","deneme@deneme.com","deneme","deneme","[]")
#getuserlist()



## APP DEBUG ## ## APP DEBUG ## ## APP DEBUG ## ## APP DEBUG ## ## APP DEBUG ## ## APP DEBUG #### APP DEBUG ##
#P DEBUG ## ## APP DEBUG ## ## APP DEBUG ## ## APP DEBUG ## ## APP DEBUG #### APP DEBUG #### APP DEBUG #### AP
## APP DEBUG ## ## APP DEBUG ## ## APP DEBUG ## ## APP DEBUG ## ## APP DEBUG ## ## APP DEBUG #### APP DEBUG ##
#P DEBUG ## ## APP DEBUG ## ## APP DEBUG ## ## APP DEBUG ## ## APP DEBUG #### APP DEBUG #### APP DEBUG #### AP




## START THE APP ##
if __name__ == '__main__':
    app.run(debug=True, threaded=True)
    pass


