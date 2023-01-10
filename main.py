from flask import Flask, render_template, request, redirect, url_for, session
import hashlib
import pymongo
from datetime import date

app = Flask(__name__)

# connect to database
mongo_client = pymongo.MongoClient("mongodb://localhost:27017/")
database = mongo_client["hour_tracker"]
records = database["records"]

with open("secret_key.txt", "r") as f:
    secret_key = f.read().replace("\n", "")
    app.secret_key = secret_key

categories = []

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/")
@app.route("/home")
def home():
    if not logged_in():
        return redirect("/login")
    
    get_from_db()
    return render_template("index.html", categories=categories)

@app.route("/add_category", methods=["POST"])
def add_category():

    if not logged_in():
        redirect("/login")

    data = request.form
    
    if data["name"] != "":
        categories.append({
            "name": data["name"],
            "hours": []
        })
    
    write_to_db()
    return redirect("/home")

@app.route("/add_hour", methods=["POST"])
def add_hour():

    if not logged_in():
        redirect("/login")

    category_name = request.form["name"]
    
    for category in categories:
        if category["name"] == category_name:
            category["hours"].append(0)

    write_to_db()
    return redirect("/")


@app.route("/seek_authorization", methods=["POST"])
def seek_authorization():

    data = request.form

    # TODO: credentials get sent unhashed (man in the middle attack possible!)
    if "username" in data.keys() and "password" in data.keys() and \
        credentials_valid(data["username"], data["password"]):

            session["logged_in"] = True
            return redirect("/")
    
    return redirect("/login")

# for authentification
def credentials_valid(username, password):

    f = open("users.txt", "r")

    lines = f.read().replace("\n", " ").split(" ")
    f.close()

    username_stored = lines[0]
    hash_stored = lines[1]

    hash_of_sent = hashlib.md5(password.encode()).hexdigest()

    return username == username_stored and hash_stored == hash_of_sent

def logged_in():
    return "logged_in" in session.keys() and session["logged_in"]

def date_query():
    today = date.today().strftime("%d/%m/%Y")
    query = {"date": today}
    return query

@app.route("/set_hour", methods=["POST"])
def set_hour():

    data = request.form

    # agreement that only one key gets sent with post request
    key = list(data.keys())[0]
    value = 1 if list(data.values())[0] == "on" else 0

    # TODO: exclude : character as part of name
    category_name, hour_index = key.split(":")

    print(value)
    
    for category in categories:
        if category["name"] == category_name:
            category["hours"][int(hour_index)] = value

    write_to_db()
    return redirect("/home")

def write_to_db():

    # if no entry for today, insert
    if records.count_documents(date_query()) == 0:
        records.insert_one({
            "date": date.today().strftime("%d/%m/%Y"),
            "categories": categories
        })
        print("inserted")
    else:
        records.update_one(date_query(), {
            "$set": {"categories": categories}
        })
        print("updated")

# loads in categories from db
def get_from_db():
    
    # only if available
    if records.count_documents(date_query()) == 1:
        x = records.find(date_query())[0]

        # global keyword needed to write to a variable outside a function
        global categories
        categories = x["categories"]