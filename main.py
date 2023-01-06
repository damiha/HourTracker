from flask import Flask, render_template, request, redirect

app = Flask(__name__)

categories = []

@app.route("/")
def hello_world():
    return render_template("index.html", categories=categories)

@app.route("/add_category", methods=["POST"])
def add_category():
    data = request.form 
    
    if data["name"] != "":
        categories.append({
            "name": data["name"],
            "hours": []
        })
    
    print(categories)
    # redirect to front page
    return redirect("/")

@app.route("/add_hour", methods=["POST"])
def add_hour():

    category_name = request.form["name"]
    
    for category in categories:
        if category["name"] == category_name:
            category["hours"].append(0)

    return redirect("/")

