from flask import Flask, render_template, request, redirect, url_for, session, flash
import hashlib
import pymongo
from datetime import date
import time

from create_stats import create_hours_today, create_hours_last_week, create_work_distribution_last_week

app = Flask(__name__)

APP_URL = "hour_tracker"

# connect to database
mongo_client = pymongo.MongoClient("mongodb://mongoservice:27017/")
database = mongo_client["hour_tracker"]
records = database["records"]
category_info = database["category_info"]

with open("secret_key.txt", "r") as f:
    secret_key = f.read().replace("\n", "")
    app.secret_key = secret_key

categories = []
recent_category_names = []

@app.route(f"/{APP_URL}/login")
def login():
    return render_template("login.html")

@app.route(f"/{APP_URL}/")
@app.route(f"/{APP_URL}/home")
def home():
    if not logged_in():
        return redirect(f"/{APP_URL}/login")
    
    get_from_db()
    get_recent_categories_from_db()
    return render_template("index.html", categories=categories, recent_category_names=recent_category_names)

@app.route(f"/{APP_URL}/add_category", methods=["POST"])
def add_category():

    if not logged_in():
        redirect(f"/{APP_URL}/login")

    data = request.form
    
    # make sure that the same category doesnt exist twice for the same day
    if data["name"] == "":
        flash("can't add a nameless category")
        return redirect(f"/{APP_URL}/home")

    elif does_category_already_exist(data["name"]):
        flash("category name already exists (ignoring casing)")
        return redirect(f"/{APP_URL}/home")
    
    else:
        # add lower case version to data base (canonical form)
        categories.append({
            "name": data["name"].lower(),
            "hours": []
        })

        # add or update category info
        write_category_info(category_added={"name": data["name"].lower()})
    
    write_to_db()
    return redirect(f"/{APP_URL}/home")

@app.route("/add_hour", methods=["POST"])
def add_hour():

    if not logged_in():
        redirect(f"/{APP_URL}/login")

    category_name = request.form["name"]
    
    for category in categories:
        if category["name"] == category_name:
            category["hours"].append(0)

    write_to_db()
    return redirect(f"/{APP_URL}/")


@app.route(f"/{APP_URL}/seek_authorization", methods=["POST"])
def seek_authorization():

    data = request.form

    # TODO: credentials get sent unhashed (man in the middle attack possible!)
    if "username" in data.keys() and "password" in data.keys() and \
        credentials_valid(data["username"], data["password"]):

            session["logged_in"] = True
            return redirect(f"/{APP_URL}/")
    
    else:
        flash("username or password incorrect")
        return redirect(f"/{APP_URL}/login")

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

@app.route(f"/{APP_URL}/set_hour", methods=["POST"])
def set_hour():

    if not logged_in():
        redirect(f"/{APP_URL}/login")

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
    return redirect(f"/{APP_URL}/home")

def write_to_db():

    # if no entry for today, insert
    if records.count_documents(date_query()) == 0:
        records.insert_one({
            "date": date.today().strftime("%d/%m/%Y"),
            "categories": categories
        })
        print("inserted")

    # update means entry exists
    # categories not empty and no empty but no delete operation would mean faulty operation
    # hence for a valid update it must hold len(categories) > 0
    elif len(categories) > 0:

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

    # there is no entry for the day yet but we logged in, so create on
    elif records.count_documents(date_query()) == 0:
        # new day so empty categories
        categories = []
        write_to_db()

def does_category_already_exist(name):

    for category in categories:
        if category["name"].lower() == name.lower():
            return True
    return False

@app.route(f"/{APP_URL}/stats")
def stats():

    # generate stats
    create_hours_today(categories, title="Hours worked today")
    create_hours_last_week(records, title="Hours last week")
    create_work_distribution_last_week(records, title="Work distribution last week")

    return render_template("stats.html", categories=categories)

def write_category_info(category_added):

    date_string = date.today().strftime("%d/%m/%Y")

    if category_info.count_documents({"name": category_added["name"]}) == 0:
        category_info.insert_one({
            "name": category_added["name"],
            "last_used": date_string
        })

    else:
        category_info.update_one({"name": category_added["name"]}, {
            "$set": {"last_used": date_string}
        })

def get_recent_categories_from_db():

    # there exists at least one category
    if category_info.count_documents({}) != 0:

        all_category_info = category_info.find({})

        # sort by date and pick 5 most recent results
        sorted_category_info = list(sorted(all_category_info, key=lambda o: time.strptime(o["last_used"], "%d/%m/%Y"), reverse=True))[:5]

        global recent_category_names
        recent_category_names = list(map(lambda i : i["name"], sorted_category_info))