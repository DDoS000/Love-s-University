from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
#from data import
import pymysql.cursors
from passlib.hash import sha256_crypt
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from functools import wraps
from werkzeug.utils import secure_filename
import os


app = Flask(__name__)

# Config MySQL
MYSQL_HOST          = '128.199.113.206'
MYSQL_USER          = 'master'
MYSQL_PASSWORD      = 'love@123456'
MYSQL_DB            = 'University'


# connection MySQL
connection = pymysql.connect(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, db=MYSQL_DB , cursorclass=pymysql.cursors.DictCursor)


# Index
@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/index')
def index():
    return render_template('landing.html')

@app.route('/map')
def map():
    cur = connection.cursor()
    result = cur.execute("SELECT * FROM residents")
    residents = cur.fetchall()
    cur.close()
    return render_template('map.html', residents=residents)

# Register Form Class
class RegisterForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')


# User Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        # Create cursor
        cur = connection.cursor()

        x = cur.execute("SELECT * FROM members WHERE username = %s",(username))

        if int(x) > 0:
            # flash("That username is already taken, please choose another", 'danger')
            return render_template('login.html', form=form)

        # Execute query
        cur.execute("INSERT INTO members(email, username, password) VALUES(%s, %s, %s)", (email, username, password))

        # Commit to DB
        connection.commit()

        # Close connection
        cur.close()

        flash('You are now registered and can log in', 'success')

        return redirect(url_for('register'))
    return render_template('login.html', form=form)

# User login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get Form Fields
        username = request.form['username']
        password_candidate = request.form['password']

        # Create cursor
        cur = connection.cursor()

        # Get user by username
        result = cur.execute("SELECT * FROM members WHERE username = %s", [username])

        if result > 0:
            # Get stored hash
            data = cur.fetchone()
            password = data['password']
            email = data['email']


            # Compare Passwords
            if sha256_crypt.verify(password_candidate, password):
                # Passed
                session['logged_in'] = True
                session['username'] = username
                session['email'] = email

                flash('You are now logged in', 'success')
                return redirect(url_for('map'))
            else:
                error = 'Invalid login'
                return redirect(url_for('register', error=error))
            # Close connection
            cur.close()
        else:
            error = 'Wrong username or password !!!'
            return redirect(url_for('register', error=error))

    return redirect(url_for('register'))



# Logout
@app.route('/logout')
# @is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))

 
# Add Location form User

app.config['IMAGE_UPLOAD'] = "static\image"
app.config['ALLOWED_IMAGE_EXTENTIONS'] = ["PNG", "JPG", "JPEG", "GIF"]

def allowed_image(filename):

    if not "." in filename:
        return False

    ext = filename.rsplit(".", 1)[1]

    if ext.upper() in app.config['ALLOWED_IMAGE_EXTENTIONS']:
        return True
    else:
        return False

@app.route('/addlocation', methods=["GET", "POST"])

def addlocation():

    if request.method == "POST" :

        if request.files:

            image = request.files["image"]

            if image.filename == "":
                print("Image must have a filename")
                return redirect(request.url)

            if not allowed_image(image.filename):
                print("That image extention is not allow")
                return redirect(request.url)

            else:
                filename = secure_filename(image.filename)

                image.save(os.path.join(app.config["IMAGE_UPLOAD"], filename))
            print("Image save")

            
            return redirect(request.url)

    return render_template("addlocation.html")




if __name__ == '__main__':
    app.secret_key='kmasdfp[mf[pbn[dnfbpndp[b'
    app.run(debug=True)
    