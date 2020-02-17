from flask import Flask, render_template,request,redirect,url_for # For flask implementation
from bson import ObjectId # For ObjectId to work
from pymongo import MongoClient
import os
from flask import Flask, render_template, flash, request
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
from time import ctime
from random import randint
from time import strftime
import mongo_geoip_log
import subprocess
import json
from flask import Flask, render_template, flash, request
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField

title = "geo ip application"
heading = "geo ip application "
DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = 'SjdnUends821Jsdlkvxh391ksdODnejdDw'

class ReusableForm(Form):
    name = TextField('IP:', validators=[validators.required()])
    surname = TextField('Surname:', validators=[validators.required()])

client = MongoClient("mongodb://127.0.0.1:27017") #host uri
db = client.newscraper #Select the database
todos = db.ip_logs #Select the collection name

def redirect_url():
    return request.args.get('next') or \
        request.referrer or \
        url_for('index')

@app.route("/list")
def lists ():
    #Display the all Tasks
    todos_l = todos.find()
    a1="active"
    return render_template('index.html',a1=a1,todos=todos_l,t=title,h=heading)

@app.route("/")
@app.route("/action", methods=['GET', 'POST'])
def hello():
    form = ReusableForm(request.form)
    if request.method == 'POST':
        def log_ip(request):
            """ Accepts Flask request object with TextField form entry.
            Logs geoIP, time, and form data. """
            name = request.form['name']
            ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
            geo_ip = subprocess.check_output('curl http://api.ipstack.com/' + name +'?access_key=dce6a31122573ec9cb577a6d6882e6fe', shell=True)
            geo_ip = json.loads(geo_ip.decode('ascii'))
            geo_ip.update({'time': ctime(), 'request': name})
            mongo_geoip_log.insert(geo_ip)

        log_ip(request)
    return redirect("/list")
@app.route("/remove")
def remove ():
    #Deleting a Task with various references
    key=request.values.get("_id")
    todos.remove({"_id":ObjectId(key)})
    return redirect("/")

@app.route("/update")
def update ():
    id=request.values.get("_id")
    task=todos.find({"_id":ObjectId(id)})
    return render_template('update.html',tasks=task,h=heading,t=title)

@app.route("/action3", methods=['POST'])
def action3 ():
    #Updating a Task with various references
    ip=request.values.get("ip")
    city=request.values.get("city")
    time=request.values.get("time")
    id=request.values.get("_id")
    todos.update({"_id":ObjectId(id)}, {'$set':{ "ip":i, "desc":city, "date":time }})
    return redirect("/")

@app.route("/search", methods=['GET'])
def search():
    #Searching a Task with various references
    key=request.values.get("key")
    refer=request.values.get("refer")
    if(key=="_id"):
        todos_l = todos.find({refer:ObjectId(key)})
    else:
        todos_l = todos.find({refer:key})
    return render_template('searchlist.html',todos=todos_l,t=title,h=heading)

if __name__ == "__main__":
    app.run()
