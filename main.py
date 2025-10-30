from flask import Flask, render_template, request, session, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

from flask_mail import Mail
import json
import os
import math 
from datetime import datetime
import pymysql
pymysql.install_as_MySQLdb()

with open('config.json', 'r') as c:
    params = json.load(c)["params"]

local_server = True   
app = Flask(__name__)
app.secret_key = 'super-secret-key'
app.config['UPLOAD_FOLDER'] = params['upload_location']
app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = '465',
    MAIL_USE_SSL = True,
    MAIL_USERNAME = params['gmail-user'],
    MAIL_PASSWORD=  params['gmail-password']
)
mail = Mail(app)
if(local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']
db = SQLAlchemy(app)


class Contacts(db.Model):
    '''
    sno, name phone_num, msg, date, email
    '''
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    phone_num = db.Column(db.String(12), nullable=False)
    msg = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    email = db.Column(db.String(20), nullable=False)

class Posts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    slug = db.Column(db.String(21), nullable=False)
    content = db.Column(db.String(120), nullable=False)
    tagline = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    img_file = db.Column(db.String(12), nullable=True)  
    author = db.Column(db.String(50), nullable=False)


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum('admin', 'author', 'reader', name='user_roles'), nullable=False)


@app.route("/")
def home():
    flash("Welcome to Blog Hub", "success")
    flash("Like the video", "warning")
    posts = Posts.query.filter_by().all()
    last = math.ceil(len(posts)/int(params['no_of_posts']))
    page = request.args.get('page')
    if (not str(page).isnumeric()):
        page = 1
    page = int(page)
    posts = posts[(page-1)*int(params['no_of_posts']):(page-1)*int(params['no_of_posts'])+ int(params['no_of_posts'])]
    if page==1:
        prev = "#"
        next = "/?page="+ str(page+1)
    elif page==last:
        prev = "/?page="+ str(page-1)
        next = "#"
    else:
        prev = "/?page="+ str(page-1)
        next = "/?page="+ str(page+1)
    
    return render_template('index.html', params=params, posts=posts, prev=prev, next=next)


@app.route("/about")
def about():
    return render_template('about.html', params=params)

@app.route("/login", methods=['GET', 'POST'])
def login():
    # If already logged in, redirect based on role
    if 'user' in session:
        role = session.get('role')
        if role == 'admin':
            return redirect('/admin_dashboard')
        elif role == 'author':
            return redirect('/author_dashboard')
        elif role == 'reader':
            return redirect('/reader')

    # Handle login submission
    if request.method == "POST":
        username = request.form.get('uname')
        password = request.form.get('pass')
        role = request.form.get('role')

        # Check user in DB
        user = Users.query.filter_by(username=username, password=password, role=role).first()

        if user:
            # ✅ Valid credentials
            session['user'] = user.username
            session['role'] = user.role

            # Redirect by role
            if user.role == 'admin':
                return redirect('/admin_dashboard')
            elif user.role == 'author':
                return redirect('/author_dashboard')
            elif user.role == 'reader':
                return redirect('/reader')
        else:
            flash("Invalid username, password, or role!", "danger")

    return render_template("login.html", params=params)


@app.route("/admin_dashboard", methods=['GET', 'POST']) 
def admin_dashboard():
    return render_template('dashboard.html', params=params, posts=Posts.query.all())

@app.route("/author_dashboard", methods=['GET', 'POST']) 
def author_dashboard():
    if 'user' not in session:
        return redirect('/login')

    author_name = session['user']
    posts = Posts.query.filter_by(author=author_name).all() 
    return render_template('dashboard_author.html', params=params, posts=Posts.query.all())

@app.route("/reader", methods = ['GET', 'POST'])
def reader():
    posts = Posts.query.filter_by().all()
    last = math.ceil(len(posts)/int(params['no_of_posts']))
    page = request.args.get('page')
    if (not str(page).isnumeric()):
        page = 1
    page = int(page)
    posts = posts[(page-1)*int(params['no_of_posts']):(page-1)*int(params['no_of_posts'])+ int(params['no_of_posts'])]
    if page==1:
        prev = "#"
        next = "/reader?page="+ str(page+1)
    elif page==last:
        prev = "/reader?page="+ str(page-1)
        next = "#"
    else:
        prev = "/reader?page="+ str(page-1)
        next = "/reader?page="+ str(page+1)

    return render_template("dashboard_reader.html", params=params, posts=posts, prev=prev, next=next)

def editinfo(sno):
    if request.method=="POST":
        box_title = request.form.get('title')
        tline = request.form.get('tline')
        slug = request.form.get('slug')
        content = request.form.get('content')
        img_file = request.form.get('img_file')
        date = datetime.now()
        author = request.form.get('author')  



        if sno=='0':
            post = Posts(title=box_title, slug=slug, content=content, tagline=tline, img_file=img_file, date=date, author=author)
            db.session.add(post)
            db.session.commit()
        else:
            post = Posts.query.filter_by(sno=sno).first()
            if post is None:
                return f"Post with sno {sno} not found"

            post.title = box_title
            post.tagline = tline
            post.slug = slug
            post.content = content
            post.img_file = img_file
            post.date = date
            db.session.commit()

            # Only allow the same author or admin to edit
            if post.author == author or session.get('role') == 'admin':
                post.title = box_title
                post.tagline = tline
                post.slug = slug
                post.content = content
                post.img_file = img_file
                post.date = date
                db.session.commit()
            else:
                return "Unauthorized action!"

            return redirect('/edit/' + sno)
        
        

    post = Posts.query.filter_by(sno=sno).first()
    return render_template('edit.html', params=params, sno=sno, post=post)

@app.route("/edit/<string:sno>", methods = ['GET', 'POST'])
def edit(sno):
    if 'user' in session and session['user']==params['admin_user']:
        return editinfo(sno)
    else:
        return editinfo(sno)



@app.route("/post/<string:post_slug>", methods=['GET'])
def post_route(post_slug):
    post = Posts.query.filter_by(slug=post_slug).first()
    if post is None:
        return render_template('404.html', message=f"No post found for slug '{post_slug}'"), 404
    return render_template('post.html', params=params, post=post)

@app.route("/uploader", methods = ['GET', 'POST'])
def uploader():
    if 'user' in session and session['user']==params['admin_user']:
        if(request.method=='POST'):
            f = request.files['file1']
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename) ))    
            return "Uploaded successfully"
    else:
        if(request.method=='POST'):
            f = request.files['file1']
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename) ))    
            return "Uploaded successfully"
        
@app.route("/logout")
def logout():
    session.pop('user')
    return redirect('/') 

@app.route("/delete/<string:sno>", methods = ['GET', 'POST'])
def delete(sno):
    if 'user' in session and session['user']==params['admin_user']:  
        post = Posts.query.filter_by(sno=sno).first()
        if post is None:
            return f"Post with sno {sno} not found"
        db.session.delete(post)
        db.session.commit()     
        return redirect('/dashboard')

@app.route("/contact", methods = ['GET', 'POST'])
def contact():
    if(request.method=='POST'):
        '''Add entry to the database'''
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        entry = Contacts(name=name, phone_num = phone, msg = message, date= datetime.now(),email = email )
        db.session.add(entry)
        db.session.commit()
        mail.send_message('New message from ' + name,
                          sender=email,
                          recipients = [params['gmail-user']],
                          body = message + "\n" + phone
                          )
        flash("Thanks for submitting your details. We will get back to you soon!", "success")
    if 'user' in session and session['role']=='author':
        return render_template('author_contact_dashboard.html', params=params)
    else:     
        return render_template('contact.html', params=params)
    return render_template('contact.html', params=params)   


app.run(debug=True)


