from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
#from data import
import pymysql.cursors
from passlib.hash import sha256_crypt
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from functools import wraps

app = Flask(__name__)

# Config MySQL
MYSQL_HOST          = '128.199.153.21'
MYSQL_USER          = 'master'
MYSQL_PASSWORD      = 'Cloud2_Space'
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
    return render_template('map.html')

@app.route('/maps')
def maps():
    return render_template('maps.html')

# Register Form Class
class RegisterForm(Form):
    usernamae = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validtors.Length(min=6, max=50)])
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
                return redirect(url_for('index'))
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

if __name__ == '__main__':
    app.secret_key='kmasdfp[mf[pbn[dnfbpndp[b'
    app.run(debug=True)
