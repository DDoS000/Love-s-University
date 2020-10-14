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

app.config['IMAGE_UPLOAD'] = "static\image"
app.config['ALLOWED_IMAGE_EXTENTIONS'] = ["PNG", "JPG", "JPEG", "GIF"]

# connection MySQL
connection = pymysql.connect(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, db=MYSQL_DB , cursorclass=pymysql.cursors.DictCursor)

# Index
@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/index')
def index():
    return render_template('landing.html')

@app.route('/OTP')
def OTP():
    return render_template('OTP.html')

@app.route('/map')
def map():
    cur = connection.cursor()
    result = cur.execute("SELECT * FROM residents")
    print(result)
    datas = cur.fetchall()
    cur.close()
    return render_template('map.html', datas=datas)

# @app.route('/add-residents')
# def add():
#     return render_template('addResidents.html')

@app.route('/resident')
def select():
    return render_template('resident.html')


# Register Form Class
class RegisterForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [
        validators.Regexp('@ubu.ac.th', message="กรุณาใช้เมล@ubu.ac.th"),
    ])
    fname = StringField('firstName', [validators.Length(min=6, max=50)])
    lastName = StringField('lastName', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='พาสไม่ตรงกัน')
    ])
    confirm = PasswordField('Confirm Password')

# User Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        email = form.email.data
        password = sha256_crypt.encrypt(str(form.password.data))
        fname = form.fname.data
        lastName = form.lastNam.data

        # Create cursor
        cur = connection.cursor()

        x = cur.execute("SELECT * FROM members WHERE email = %s",(email))

        if int(x) > 0:
            # flash("That username is already taken, please choose another", 'danger')
            return render_template('login.html', form=form)

        # Execute query
        cur.execute("INSERT INTO members(email, username, password, firstName, lastName) VALUES(%s, %s, %s, %s, %s)", (email, username, password, fname, lastName))

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
        email = request.form['username']
        password_candidate = request.form['password']

        # Create cursor
        cur = connection.cursor()

        # Get user by username
        result = cur.execute("SELECT * FROM members WHERE email = %s", [email])

        if result > 0:
            # Get stored hash
            data = cur.fetchone()
            userId = data['userId']
            password = data['password']
            email = data['email']
            firstName = data['firstName']
            lastName = data['lastName']
            permission = data['permission']

            # Compare Passwords
            if sha256_crypt.verify(password_candidate, password):
                # Passed
                session['logged_in'] = True
                session['userId'] = userId
                session['email'] = email
                session['firstName'] = firstName
                session['lastName'] = lastName
                session['permission'] = permission


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

# Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('login'))
    return wrap


# Logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        user_id = request.form['addformuser']
        residentName = request.form['residentName']
        lat = request.form['lat']
        lng = request.form['lng']
        roomType = request.form['roomType']
        price = request.form['price']
        details = request.form['details']
        phoneConnect = request.form['phoneConnect']
        OtherConnect = request.form['OtherConnect']
        image = request.files['image']
        air = request.form['air']
        fan = request.form['fan']
        water_heater = request.form['water_heater']
        furniture = request.form['furniture']
        cable_tv = request.form['cable_tv']
        phone_direct = request.form['phone_direct']
        internet = request.form['internet']
        pet = request.form['pet']
        smoking = request.form['smoking']
        parking = request.form['parking']
        elevators = request.form['elevators']
        security = request.form['security']
        keycard = request.form['keycard']
        cctv = request.form['cctv']
        pool = request.form['pool']
        fitness = request.form['fitness']
        laundry = request.form['laundry']
        hair_salon = request.form['hair_salon']

        filename = secure_filename(image.filename)
        image.save(os.path.join(app.config["IMAGE_UPLOAD"], filename))
        # Create cursor
        cur = connection.cursor()
        x = cur.execute("SELECT * FROM residents WHERE residentName = %s",(residentName))
        if int(x) > 0:
            flash("มีคนได้เพิ่มหอพักนี้ไปแล้ว", 'danger')
        cur.execute("INSERT INTO residents(addformuser, residentName, lat, lng, roomType, price, details, phoneConnect, OtherConnect, image, air, fan, water_heater, furniture, cable_tv, phone_direct, internet, pet, smoking, parking, elevators, security, keycard, cctv, pool, fitness, laundry, hair_salon) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (user_id, residentName, lat, lng, roomType, price, details, phoneConnect, OtherConnect, filename, air, fan, water_heater, furniture, cable_tv, phone_direct, internet, pet, smoking, parking, elevators, security, keycard, cctv, pool, fitness, laundry, hair_salon))

         # Commit to DB
        connection.commit()

        # Close connection
        cur.close()

        flash('You are now registered and can log in', 'success')
        # return redirect(url_for('register'))
    return render_template("add.html")


if __name__ == '__main__':
    app.secret_key='kmasdfp[mf[pbn[dnfbpndp[b'
    app.run(debug=True)
    