import os
import secrets
from PIL import Image
from flask import flash, render_template, redirect, url_for, request, abort #importing IoT_Web module and creating IoT_Web web server from the IoT_Web module
from IoT_Web import app, db, bcrypt
from IoT_Web.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm, CreateIntance
from IoT_Web.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required

@app.route("/") #specifies the default page
@app.route("/home")
def home(): #when the user goes to the default page they will be representded with the home page if they go to the login or register page
    page = request.args.get('page', 1, type=int) #start at page 1, setting the type to int prevents anyone from changing the value of the page number in the url to anything other than an integer
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5) #order posts by the latest to the oldest, maximum of 5 posts per page
    return render_template('home.html', posts=posts)

@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/register", methods=['GET', 'POST'])
@login_required
def register():
    form = RegistrationForm()
    if form.validate_on_submit(): #after submiting a register form
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8') #hash the password and decode it into string
        user = User(username=form.username.data, email=form.email.data, password=hashed_password) #username and email will remain in plaintext format, password will be hashed
        db.session.add(user) #adding new user to the database
        db.session.commit() #commiting this change to the database
        flash('Your account was successfully created', 'success') #show message Account created for + username of the account created if successful (success category)
        return redirect(url_for('login')) #after successfully creating an account redirect the user to the login page
    return render_template('register.html', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated: #if the current user is authenticated then redirect them to the home page
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit(): #after logging in
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data): #if the user exists and the password that they entered is valid and checks with the password in the db then the user can login
            login_user(user, remember=form.remember.data) #log the user in, and allow the remember the user option
            next_page = request.args.get('next') #if the user is not logged in and is trying to access a page that you must be logged in for, the user will be redirected to the login page and after they successfully login they will be directed to the page they were trying to go instead of the default home page
            return redirect(next_page) if next_page else redirect(url_for('home')) #redirect the user to the next_page url parameter if the next_page parameter exists, else redirect to the home page, this is known as a turnary conditional
        else:
         flash('Unsuccessful login!', 'danger') #danger bootstrap category
    return render_template('login.html', form=form)

@app.route("/logout") #logout the user and return them to the home page
def logout():
    logout_user()
    return redirect(url_for('home'))

def save_picture(form_picture):
    random_hex = secrets.token_hex(8) #changing the uploaded images name to a random generated name
    _, f_ext = os.path.splitext(form_picture.filename) #discarding the original image file name and holding on to the file extension for the purpose of storing it in the db
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/images', picture_fn)

    output_size = (200, 200) # image resizing, resize the image that the user uploads, saves space on the filesystem and speeds up the websites loading time
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

@app.route("/account", methods=['GET', 'POST'])
@login_required #need to login to access this page
def account():
    form = UpdateAccountForm() #creating an instance of UpdateAccountForm
    if form.validate_on_submit():
        if form.picture.data:
           picture_file = save_picture(form.picture.data)
           current_user.image_file = picture_file
        current_user.username = form.username.data #updating users username
        current_user.email = form.email.data #updating users email
        db.session.commit() #commiting these changes to the db
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username #populating the users field with their current username
        form.email.data = current_user.email #populating the users field with their current email
    image_file = url_for('static', filename='images/' + current_user.image_file) #specifying where the default user profile picture is located,
    return render_template('account.html', image_file=image_file, form=form) #passing the image file and form to the account.html file

#CRUD
@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content =form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post have been created', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', form=form, legend='New Post')

@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', post=post)

@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit() #dont need to do db.session.add, because the information is already in the db, its just being updated
        flash('Your post has been updated', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title #populating forms field with the current title
        form.content.data = post.content #populating forms field with the current content
    return render_template('create_post.html', form=form, legend='Update Post')

@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted', 'success')
    return redirect(url_for('home'))

@app.route("/create_instance")
@login_required
def create_instance():
    form = CreateIntance()
    return render_template('create_instance.html', form=form)

