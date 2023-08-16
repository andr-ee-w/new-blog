from flask import Flask, render_template, flash, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    SubmitField,
    PasswordField,
    BooleanField,
    ValidationError,
)
from wtforms.validators import DataRequired, EqualTo, Length
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date
from wtforms.widgets import TextArea
from flask_login import (
    UserMixin,
    login_user,
    LoginManager,
    login_required,
    logout_user,
    current_user,
)
from webforms import LoginForm, PostForm, UserForm, PasswordForm, NamerForm, SearchForm
from flask_ckeditor import CKEditor
from werkzeug.utils import secure_filename
import uuid as uuid
import os

# Flask Instance
app = Flask(__name__)

# add CK Editor
ckeditor = CKEditor(app)
# OLD SQLite DB
# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"

# NEW MySQL DB
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "mysql+pymysql://root:Testing123@localhost/ourusers"

# Secret Key
app.config["SECRET_KEY"] = "MajorKey"

# Initialize Database
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# Flask_login Stuff
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# Save images
UPLOAD_FOLDER = "static/images/"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


# Create Login Page
@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user:
            # Check hash
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                flash("Login successful!")
                return redirect(url_for("dashboard"))
            else:
                flash("Incorrect Password - Try again...")
        else:
            flash("That user doesn't exist. try again.")
    return render_template("login.html", form=form)


# Create Dashboard Page
@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    return render_template("dashboard.html")


# Create Logout
@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    flash("You have been logged out.")
    return redirect(url_for("login"))


# All Blog Posts Page
@app.route("/posts")
def posts():
    # Grab all the posts from the database
    posts = Posts.query.order_by(Posts.date_posted)

    return render_template("posts.html", posts=posts)


# Individual Post Page
@app.route("/posts/<int:id>")
def post(id):
    post = Posts.query.get_or_404(id)
    return render_template("post.html", post=post)


# Edit Blog Post
@app.route("/posts/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_post(id):
    post = Posts.query.get_or_404(id)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        # post.author = form.author.data
        post.slug = form.slug.data
        post.content = form.content.data

        # Update Database
        db.session.add(post)
        db.session.commit()
        flash("Post Updated Successfully!")
        return redirect(url_for("post", id=post.id))

    if current_user.id == post.poster_id:
        form.title.data = post.title
        # form.author.data = post.author
        form.slug.data = post.slug
        form.content.data = post.content
        return render_template("edit_post.html", form=form)
    else:
        flash("You cannot edit this post!")

        posts = Posts.query.order_by(Posts.date_posted)
        return render_template("posts.html", posts=posts)


# Add Post Page
@app.route("/add-post", methods=["GET", "POST"])
# @login_required
def add_post():
    form = PostForm()

    if form.validate_on_submit():
        poster = current_user.id
        post = Posts(
            title=form.title.data,
            content=form.content.data,
            poster_id=poster,
            slug=form.slug.data,
        )
        # Clear the form
        form.title.data = ""
        form.content.data = ""
        # form.author.data = ""
        form.slug.data = ""

        # Add post to database
        db.session.add(post)
        db.session.commit()

        # Return a message
        flash("Post Submitted Successfully!")

    # Redirect to the webpage
    return render_template("add_post.html", form=form)


# Delete Blog Post
@app.route("/post/delete/<int:id>")
@login_required
def delete_post(id):
    post_to_delete = Posts.query.get_or_404(id)
    id = current_user.id
    if id == post_to_delete.poster.id:
        try:
            db.session.delete(post_to_delete)
            db.session.commit()

            flash("Blog Post Successfully Deleted!")
            posts = Posts.query.order_by(Posts.date_posted)
            return render_template("posts.html", posts=posts)
        except:
            flash("There was a problem deleting your post. Please try again.")
            posts = Posts.query.order_by(Posts.date_posted)
            return render_template("posts.html", posts=posts)
    else:
        flash("You cannot delete this post.")
        posts = Posts.query.order_by(Posts.date_posted)
        return render_template("posts.html", posts=posts)


# Pass Stuff to Navbar
@app.context_processor
def base():
    form = SearchForm()
    return dict(form=form)


# Search Function
@app.route("/search", methods=["POST"])
def search():
    form = SearchForm()
    posts = Posts.query
    if form.validate_on_submit():
        post.searched = form.searched.data
        # Query the Database
        posts = posts.filter(Posts.content.like("%" + post.searched + "%"))
        posts = posts.order_by(Posts.title).all()

        return render_template(
            "search.html", form=form, searched=post.searched, posts=posts
        )


# Json Thing
@app.route("/date")
def get_current_date():
    favorite_pizza = {"John": "Pepperoni", "Mary": "Cheese", "Tim": "Mushroom"}
    return favorite_pizza
    # return {"Date": date.today()}


# Delete Database Records
@app.route("/delete/<int:id>")
def delete(id):
    user_to_delete = Users.query.get_or_404(id)
    name = None
    form = UserForm()

    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash("User Deleted Successfully!")

        our_users = Users.query.order_by(Users.date_added)
        return render_template(
            "add_user.html", form=form, name=name, our_users=our_users
        )
    except:
        flash("Whoops! There was an error deleting your user. Try again.")
        return render_template(
            "add_user.html", form=form, name=name, our_users=our_users
        )


# Add User
@app.route("/user/add", methods=["GET", "POST"])
def add_user():
    name = None
    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            # Hashed Password
            hashed_pw = generate_password_hash(form.password_hash.data)
            user = Users(
                username=form.username.data,
                name=form.name.data,
                email=form.email.data,
                favorite_color=form.favorite_color.data,
                password_hash=hashed_pw,
            )
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ""
        form.username.data = ""
        form.email.data = ""
        form.favorite_color.data = ""
        form.password_hash.data = ""

        flash("User Added Successfully!")
    our_users = Users.query.order_by(Users.date_added)

    return render_template("add_user.html", form=form, name=name, our_users=our_users)


# Update Database Record
@app.route("/update/<int:id>", methods=["GET", "POST"])
@login_required
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        name_to_update.name = request.form["name"]
        name_to_update.email = request.form["email"]
        name_to_update.favorite_color = request.form["favorite_color"]
        name_to_update.username = request.form["username"]
        name_to_update.user_bio = request.form["user_bio"]
        name_to_update.profile_pic = request.files["profile_pic"]

        # Grab Image Name
        pic_filename = secure_filename(name_to_update.profile_pic.filename)

        # set uuid
        pic_id = str(uuid.uuid1()) + "_" + pic_filename

        # Save the image
        saver = request.files["profile_pic"]

        name_to_update.profile_pic = pic_id
        try:
            db.session.commit()
            saver.save(os.path.join(app.config["UPLOAD_FOLDER"], pic_id))
            flash("User Updated Successfully!")
            return render_template(
                "dashboard.html", form=form, name_to_update=name_to_update
            )
        except:
            flash("Error! There was a problem. Try again.")
            return render_template(
                "update.html", form=form, name_to_update=name_to_update, id=id
            )
    else:
        return render_template(
            "update.html", form=form, name_to_update=name_to_update, id=id
        )


# home route
@app.route("/")
def index():
    first_name = "Andrew"
    stuff = "this is bold text"

    favorite_pizza = ["Cheese", "Pepperoni", "Sausage", "Mushroom", 41]
    return render_template(
        "index.html", first_name=first_name, stuff=stuff, favorite_pizza=favorite_pizza
    )


# Admin Page
@app.route("/admin")
@login_required
def admin():
    id = current_user.id
    if id == 15:
        return render_template("admin.html")
    else:
        flash("You must be an admin to see that page...")
        return redirect(url_for("dashboard"))


# localhost:5000/user/john
@app.route("/user/<name>")
@login_required
def user(name):
    return render_template("user.html", user_name=name)


# Custom Error Pages
# Invalid URL
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


# Invalid Server Error
@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html"), 500


# Create Name Page
@app.route("/name", methods=["GET", "POST"])
def name():
    name = None
    form = NamerForm()
    # Validate Form
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ""
        flash("Form Submitted Successfully!")
    return render_template("name.html", name=name, form=form)


# Create Password Test Page
@app.route("/test_pw", methods=["GET", "POST"])
def test_pw():
    email = None
    password = None
    pw_to_check = None
    passed = None
    form = PasswordForm()

    # Validate Form
    if form.validate_on_submit():
        email = form.email.data
        password = form.password_hash.data

        form.email.data = ""
        form.password_hash.data = ""

        # lookup user by email address
        pw_to_check = Users.query.filter_by(email=email).first()
        # Check hashed password
        passed = check_password_hash(pw_to_check.password_hash, password)

    return render_template(
        "test_pw.html",
        email=email,
        password=password,
        pw_to_check=pw_to_check,
        passed=passed,
        form=form,
    )


# Database Models


# Users Model
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    favorite_color = db.Column(db.String(100))
    user_bio = db.Column(db.Text(500), nullable=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    profile_pic = db.Column(db.String(255), nullable=True)
    # Doing password stuff
    password_hash = db.Column(db.String(128))
    # User can have many posts
    posts = db.relationship("Posts", backref="poster")

    # more password stuff
    @property
    def password(self):
        raise AttributeError("Password is not a readable attribute!")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Create a String
    def __repr__(self):
        return "<Name %r>" % self.name


# BLog Post Model
class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    # author = db.Column(db.String(255))
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    slug = db.Column(db.String(255))
    # Foreign Key to Link Users (refer to primary key of the user)
    poster_id = db.Column(db.Integer, db.ForeignKey("users.id"))


# run app and debug create db
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
