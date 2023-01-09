from flask import Flask, render_template, request, redirect, url_for, session
import hashlib

app = Flask(__name__)

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
    
    return redirect("/home")

@app.route("/add_hour", methods=["POST"])
def add_hour():

    if not logged_in():
        redirect("/login")

    category_name = request.form["name"]
    
    for category in categories:
        if category["name"] == category_name:
            category["hours"].append(0)

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