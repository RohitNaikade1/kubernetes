import os
from flask import Flask, request
from flask import Flask, render_template, request, redirect, url_for
from flask_mongoengine import MongoEngine
from datetime import datetime
import mongoengine as me
from mongoengine import *
from flask_pymongo import PyMongo

app = Flask(__name__)
title = "Task-Manager"
heading = "Task-Manager"

# app.config["MONGO_URI"] = "mongodb://mongo:27017/mydb1"

app.config['MONGODB_SETTINGS'] = {  # connection to databse
    'host': 'mongodb://mongo/mydb1'
}

db = MongoEngine()
db.init_app(app)  # creates the object of database connection

count = 1
user = None
admin = None



class Task(me.EmbeddedDocument):  # creating database model
    tid = me.IntField(default=0)
    name = me.StringField(max_length=200, required=True)
    desc = me.StringField(max_length=250, required=True)
    comments = me.StringField(max_length=250, required=True)
    priority = me.StringField(required=True, default=5)
    date = me.DateTimeField(default=datetime.utcnow())
    status = me.BooleanField(default=False)


class User(me.Document):
    Uname = me.StringField(max_length=200, required=True)
    Password = me.StringField(max_length=200, required=True)
    Tasks = me.ListField(EmbeddedDocumentField(Task))


class Admin(me.Document):
    AdminName = me.StringField(max_length=200, required=True)
    AdminPass = me.StringField(max_length=200, required=True)
    Tasks = me.ListField(EmbeddedDocumentField(Task))
    Users = me.ListField(me.ReferenceField(User))


AdminName = "roshan"
AdminPass = "roshan12"
AWS_KEY = "kmdncdvfnjvnfvj"
aws_key = "nhatsfere"
aws_access_key="kmdncdvfnjvnfvj"
AWS_ACCESS_KEY="vdffdfdgfdgfd"
AWS_SECRET_KEY="dfsfdsfdsfs"
aws_secret_key="sdfdsfdsfdsfds"
secret="oursecret"
Password="leakedPass@123"
users = []
tasks = []
new_admin = Admin(AdminName=AdminName, AdminPass=AdminPass, Tasks=tasks, Users=users)
new_admin.save()


def redirect_url():
    return request.args.get('next') or request.referrer or url_for('index')


def getuser():
    global user
    return user


def setuser(u1):
    global user
    user = u1


def getadmin():
    global admin
    return admin


def setadmin(a1):
    global admin
    admin = a1


@app.route('/', methods=['POST', 'GET'])  # default routing function
def login():

    if request.method == 'GET':
        return render_template('login.html')
    else:
        uname = request.form['Uname']
        password = request.form['Pass']
        error = False
        user = User.objects(Uname=uname, Password=password).first()
        admin = Admin.objects(AdminName=uname, AdminPass=password).first()
        setadmin(admin)
        setuser(user)
        if user:
            return redirect('/tasks')
        elif admin:
            return redirect('/admin')
        else:
            error = True
            return render_template('login.html', Error=error)


@app.route('/admin', methods=['POST', 'GET'])
def Admin1():
    if request.method == "GET":
        admin = Admin.objects(AdminName="roshan").first()
        return render_template('adminhome.html', admin=admin, task1=False, all=True)



@app.route('/addmember', methods=['POST', 'GET'])
def Addmember():
    if request.method == "POST":
        admin = getadmin()
        Admin1 = Admin.objects(AdminName="roshan").first()
        Uname = request.form['Uname']
        Pass = request.form['Pass']
        new_user = User(Uname=Uname, Password=Pass)
        new_user.save()
        users = [new_user]
        Admin1.Users.append(new_user)
        Admin1.save()
        return redirect('/admin')
    else:
        return render_template('addmember.html')


@app.route('/addtasks/<id>', methods=['POST', 'GET'])
def AddTasks(id):
    if request.method == "GET":
        admin = getadmin()
        Admin1 = Admin.objects(AdminName="roshan").first()
        return render_template('adminhome.html', admin=Admin1, task1=True, all=False)
    else:
        Admin3 = Admin.objects.get(id=id)
        global count
        task_id = count
        increment()
        task_name = request.form['name']  # get the data from form  and
        task_desc = request.form['desc']
        task_comments = request.form['comments']
        task_priority = request.form['priority']
        new_task = Task(tid=task_id, name=task_name, desc=task_desc, comments=task_comments, priority=task_priority)
        Admin3.Tasks.append(new_task)
        Admin3.save()
        try:
            return render_template('adminhome.html', admin=Admin3, task1=True, all=False)
        except:
            return 'There was an while issue adding your task you messed up bruh!!!'


@app.route("/pendingAdmin/<uname>")
def tasksAdmin(uname):
    admin = Admin.objects.filter(AdminName=uname, Tasks__status=False).first()
    a2 = "active"
    return render_template('adminhome.html', admin=admin, a2=a2)


@app.route("/completedAdmin/<uname>")
def completedAdmin(uname):
    admin = Admin.objects.filter(AdminName=uname, Tasks__status=True).first()
    a3 = "active"
    return render_template('adminhome.html', a3=a3, admin=admin)


@app.route('/doneAdmin/<id>/<uname>')  # updating status of task by id
def doneAdmin(id, uname):
    Admin.objects(AdminName=uname).first()
    Admin.objects(AdminName=uname, Tasks__tid=id).update(set__Tasks__S__status=True)
    try:
        return redirect('/addtasks/id')
    except:
        return 'There was an issue updating your task'


@app.route('/undoAdmin/<id>/<uname>')  # updating status of stored task by id
def undoAdmin(id, uname):
    Admin.objects(AdminName=uname).first()
    Admin.objects(AdminName=uname, Tasks__tid=id).update(set__Tasks__S__status=False)
    try:
        return redirect('/addtasks/id')
    except:
        return 'There was an issue updating your task'


@app.route('/deleteAdmin/<id>/<uname>')  # deleting task by id
def deleteAdmin(id, uname):
    Admin2 = Admin.objects(AdminName=uname).first()
    Admin2.update(pull__Tasks__tid=id)
    try:
        return redirect('/addtasks/id')
    except:
        return 'There was an issue while deleting your task'


@app.route('/updateAdmin/<id>/<uname>', methods=['POST', 'GET'])  # updating stored task by id
def updateAdmin(id, uname):
    Error = False
    Admin2 = Admin.objects(AdminName=uname).first()
    for task in Admin2.Tasks:
        if task.tid == int(id):
            selected_task = task

    if request.method == 'POST':  # if method is POST then
        tname = request.form['name']  # getting new content from form and set into databse
        tdesc = request.form['desc']
        tcomments = request.form['comments']
        tpriority = request.form['priority']
        Admin.objects(AdminName=uname, Tasks__tid=id).update(set__Tasks__S__name=tname)
        Admin.objects(AdminName=uname, Tasks__tid=id).update(set__Tasks__S__desc=tdesc)
        Admin.objects(AdminName=uname, Tasks__tid=id).update(set__Tasks__S__comments=tcomments)
        Admin.objects(AdminName=uname, Tasks__tid=id).update(set__Tasks__S__priority=tpriority)
        try:
            return redirect('/addtasks/id')
        except:
            return 'There was an issue while updating your task'
    else:
        return render_template('updateadmin.html', admin=Admin2, task=selected_task, id=id)


@app.route('/assign/<id>', methods=['POST', 'GET'])  # updating stored task by id
def assign(id):
    admin = getadmin()
    Admin2 = Admin.objects(AdminName="roshan").first()
    if request.method == 'POST':  # if method is POST then
        try:
            return redirect('/addtasks/id')
        except:
            return 'There was an issue while updating your task'
    else:

        return render_template('assign.html', admin=Admin2,
                               tid=id)  # if method is GET then redirect requet to update page to get the new content


@app.route('/assign/<id>/<uname>', methods=['POST', 'GET'])  # updating stored task by id
def assign2(id, uname):
    admin = getadmin()
    Admin2 = Admin.objects(AdminName="roshan").first()
    for task in Admin2.Tasks:
        if task.tid == int(id):
            sel_task = task
    User2 = User.objects(Uname=uname).first()
    setuser(User2)
    new_task = Task(tid=sel_task.tid, name=sel_task.name, desc=sel_task.desc, comments=sel_task.comments,
                    priority=sel_task.priority)
    User2.Tasks.append(new_task)
    User2.save()
    Admin2.update(pull__Tasks__tid=id)
    if request.method == 'POST':  # if method is POST then
        try:
            return redirect('/addtasks/id')
        except:
            return 'There was an issue while updating your task'
    else:
        return redirect('/addtasks/id')  # if method is GET then redirect requet to update page to get the new content


#
# ___________________________________________________________________________________________________________________________
# ----------------------------------------------------------------------------------------------------------------------------
#
# __________________________________________________________________________________________________________________________
# ---------------------------------------------------------------------------------------------------------------------------
# 
#

@app.route('/tasks', methods=['POST', 'GET'])
def Tasks():
    user = getuser()
    user1 = User.objects(Uname=user.Uname).first()
    return render_template('index.html', user=user1, a1="active")


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == "POST":
        uname = request.form['Uname']
        passwd = request.form['Pass']

        new_user = User(Uname=uname, Password=passwd)
        new_user.save()
        return redirect('/')
    else:
        return render_template('register.html')


def increment():
    global count
    count += 1


@app.route('/add/<id>', methods=['POST', 'GET'])  # default routing function
def add(id):
    a1 = "active"
    if request.method == 'POST':  # if method is POST
        User3 = User.objects.get(id=id)
        global count
        task_id = count
        increment()
        task_name = request.form['name']  # get the data from form  and
        task_desc = request.form['desc']
        task_comments = request.form['comments']
        task_priority = request.form['priority']
        new_task = Task(tid=task_id, name=task_name, desc=task_desc, comments=task_comments, priority=task_priority)
        User3.Tasks.append(new_task)
        User3.save()
        try:
            return redirect('/tasks')
        except:
            return 'There was an while issue adding your task you messed up bruh'
    else:
        return render_template('index.html')


@app.route("/pending/<uname>")
def tasks(uname):
    user = User.objects.filter(Uname=uname, Tasks__status=False).first()
    a2 = "active"
    return render_template('index.html', user=user, a2=a2)


@app.route("/completed/<uname>")
def completed(uname):
    user = User.objects.filter(Uname=uname, Tasks__status=True).first()
    a3 = "active"
    return render_template('index.html', a3=a3, user=user)


@app.route('/done/<id>/<uname>')  # updating status of task by id
def done(id, uname):
    User2 = User.objects(Uname=uname).first()
    User3 = User.objects(Uname=uname, Tasks__tid=id).update(set__Tasks__S__status=True)
    try:
        return redirect('/tasks')
    except:
        return 'There was an issue updating your task'


@app.route('/undo/<id>/<uname>')  # updating status of stored task by id
def undo(id, uname):
    User.objects(Uname=uname).first()
    User.objects(Uname=uname, Tasks__tid=id).update(set__Tasks__S__status=False)
    try:
        return redirect('/tasks')
    except:
        return 'There was an issue updating your task'


@app.route('/delete/<id>/<uname>')  # deleting task by id
def delete(id, uname):
    User2 = User.objects(Uname=uname).first()
    User2.update(pull__Tasks__tid=id)
    try:
        return redirect('/tasks')
    except:
        return 'There was an issue while deleting your task'


@app.route('/update/<id>/<uname>', methods=['POST', 'GET'])  # updating stored task by id
def update1(id, uname):
    Error = False
    User2 = User.objects(Uname=uname).first()
    for task in User2.Tasks:
        if task.tid == int(id):
            selected_task = task

    if request.method == 'POST':  # if method is POST then
        tname = request.form['name']  # getting new content from form and set into databse
        tdesc = request.form['desc']
        tcomments = request.form['comments']
        tpriority = request.form['priority']
        User.objects(Uname=uname, Tasks__tid=id).update(set__Tasks__S__name=tname)
        User.objects(Uname=uname, Tasks__tid=id).update(set__Tasks__S__desc=tdesc)
        User.objects(Uname=uname, Tasks__tid=id).update(set__Tasks__S__comments=tcomments)
        User.objects(Uname=uname, Tasks__tid=id).update(set__Tasks__S__priority=tpriority)
        try:
            return redirect('/tasks')
        except:
            return 'There was an issue while updating your task'
    else:
        return render_template('update.html', user=User2, task=selected_task,
                               id=id)  # if method is GET then redirect requet to update page to get the new content


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
