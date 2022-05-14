from flask import Flask,render_template,request,redirect,url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_manager, login_user, current_user
from flask_login.utils import login_required
from datetime import date
import matplotlib.pyplot as plt
import numpy as np

plt.switch_backend('agg')


app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///todo.sqlite3'
app.config['SECRET_KEY'] = 'xyz'
db=SQLAlchemy()
db.init_app(app)
app.app_context().push()



class User(db.Model):
  __tablename__ = 'user'
  userid = db.Column(db.Integer, primary_key=True,autoincrement=True)
  username = db.Column(db.String, unique=True, nullable=False)
  password = db.Column(db.String, nullable=False)
  email = db.Column(db.String, nullable=False, unique=True)

  def is_active(self):   
      return True                 

  def get_id(self):         
      return str(self.userid)

  def is_authenticated(self):
    return True

class Todo(db.Model):
    __tablename__ = 'todo'
    sno=db.Column(db.Integer,primary_key=True,autoincrement=True)
    title=db.Column(db.String(200),nullable=False) 
    desc=db.Column(db.String(500), nullable=False)
    userid = db.Column(db.Integer, db.ForeignKey('user.userid'))
    due_date=db.Column(db.String, nullable=False)
    sect=db.Column(db.String,nullable=False)
    completed=db.Column(db.Boolean,nullable=False)



db.create_all()




login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(userid=user_id).first()

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == "GET":
      return render_template("login.html",x=1)
    else:
      username = request.form["username"]
      password = request.form["password"]

      user = User.query.filter(User.username==username, User.password==password).first()
      if user:
        login_user(user)
        task_date = str(date.today().strftime("%d-%m-%Y"))
        return redirect(url_for('home',dt = task_date))
      else:
        return render_template("login.html",x=0)

@app.route("/signup",methods=["GET","POST"])
def sign():
  if request.method == "GET":
    return render_template("signup.html",x=1)
  else:
    username = request.form["username"]
    password = request.form["password"]
    email = request.form["email"]    
    user = User(username=username,password=password,email=email)
    try:
      db.session.add(user)
      db.session.commit()
      login_user(user)
      task_date = str(date.today().strftime("%d-%m-%Y"))
      return redirect(url_for('home',dt = task_date))
    except:
      return render_template("signup.html",x=0)

@app.route("/home/<dt>")
@login_required
def home(dt):
  id = current_user.get_id()
  sects = ["work","personal","education", "health"]  
  for i in sects:
    todolist1 = Todo.query.filter(Todo.userid == id, Todo.sect == i, Todo.completed == False, Todo.due_date == dt).all()
    todolist2 = Todo.query.filter(Todo.userid == id, Todo.sect == i, Todo.completed == True, Todo.due_date == dt).all()
    l1 = len(todolist1)
    l2 = len(todolist2)
    if (l1+l2 == 0):
      x = 0
    else:
      x = (l1/(l1+l2))*100
    y = np.array([x, 100 - x])
    if (i=='work'):
      colors=['#f8f9fa','#17a2b8',]
    elif (i=='personal'):
      colors=['#f8f9fa','#ffc107',]
    elif (i=='education'):
      colors=['#f8f9fa','#28a745',]
    else:
      colors=['#f8f9fa','#dc3545',]
    labels = ['',"{:.0f}%".format(100-x)]
    plt.clf()
    plt.pie(y,colors=colors,labels=labels,textprops={'fontsize': 25},startangle=90)    
    plt.savefig("static/progress"+i+".png")
  return render_template("home.html",dt=dt)

  
@app.route('/home/<section>/<dt>', methods=["GET","POST"])
@login_required
def sect(section,dt):
  id = current_user.get_id()
  if request.method == "GET":
    todolist = Todo.query.filter(Todo.due_date == dt,Todo.userid == id, Todo.sect==section, Todo.completed==False).all()
    comptodo = Todo.query.filter(Todo.due_date == dt,Todo.userid == id, Todo.sect==section, Todo.completed==True).all()
    return render_template("section.html",dt = dt, todolist = todolist, sect=section,comptodo=comptodo)
  elif request.method=="POST":
    task_name = request.form["title"]
    task_desc = request.form["desc"]
    tasks = Todo(title=task_name, desc=task_desc, due_date=dt, sect=section, userid=id, completed = False)
    db.session.add(tasks)
    db.session.commit()
    return redirect(url_for('sect',section=section,dt=dt))
    

@app.route("/edit/<int:sno>/<dt>",methods=['POST'])
@login_required
def update(sno,dt):
  if request.method=='POST':
    title=request.form['title']
    desc=request.form['desc']
    task=Todo.query.filter_by(sno=sno).first()
    task.title=title
    task.desc=desc
    section=task.sect
    db.session.add(task)
    db.session.commit()
    return redirect(url_for('sect',section=section,dt=dt))

@app.route("/remove/<int:sno>/<dt>")
@login_required
def delete(sno,dt):
    task=Todo.query.filter_by(sno=sno).first()
    section=task.sect
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('sect',section=section,dt=dt))

@app.route("/comp/<int:sno>/<dt>")
@login_required
def comp(sno,dt):
  task = Todo.query.filter_by(sno=sno).first()
  task.completed = True
  db.session.commit()
  return redirect(url_for('sect',section=task.sect,dt=dt))

def give():
  return("Hello")



  
  


  
  
     