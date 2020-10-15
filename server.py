from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
#from data import
import pymysql.cursors
from passlib.hash import sha256_crypt
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from functools import wraps
from werkzeug.utils import secure_filename
import os
# from flask_mail import Mail, Message
import smtplib
from random import randint

app = Flask(__name__)

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587

# Config MySQL
MYSQL_HOST          = '128.199.113.206'
MYSQL_USER          = 'master'
MYSQL_PASSWORD      = 'love@123456'
MYSQL_DB            = 'University'

app.config['IMAGE_UPLOAD'] = "static\image"
app.config['ALLOWED_IMAGE_EXTENTIONS'] = ["PNG", "JPG", "JPEG", "GIF"]

# mail_settings = {
#     "MAIL_SERVER": 'smtp.gmail.com',
#     "MAIL_PORT": 587,
#     "MAIL_USE_TLS": False,
#     "MAIL_USE_SSL": False,
#     "MAIL_USERNAME": 'gm270624@gmail.com',
#     "MAIL_PASSWORD": '045270624'
# }
# app.config.update(mail_settings)
# mail = Mail(app)

# connection MySQL

connection = pymysql.connect(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, db=MYSQL_DB , cursorclass=pymysql.cursors.DictCursor)

# Index
@app.route('/')
def landing():
    # msg = Message(sender="gm270624@gmail.com" ,recipients = ["chimomonono@gmail.com"])
    # msg.subject = "Hello world"
    # msg.body = "Hello Flask message sent from Flask-Mail"
    # mail.send(msg)
    return render_template('landing.html')

@app.route('/index')
def index():
    return render_template('landing.html')

@app.route('/admin')
def Addmin():
    return render_template('Admin.html')

@app.route('/OTP', methods=['GET', 'POST'])
def OTP():
    if request.method == 'POST':
        cur = connection.cursor()

        checkOTP = cur.execute("SELECT * FROM otp WHERE email = %s AND OTP = %s",(request.form['email'], request.form['OTP']))
        print(checkOTP)
        if int(checkOTP) > 0:
            verify = cur.execute("UPDATE members SET verify = %s WHERE email = %s",("verify",request.form['email']))
            delOTP = cur.execute("DELETE FROM otp WHERE email = %s",(request.form['email']))
            connection.commit()
            flash('Verify Success', 'success')
            cur.close()

            return redirect(url_for('login'))
        else :
            return render_template('OTP',email=request.form['email'])

        


    return render_template('OTP.html')

@app.route('/map')
def map():
    
    cur = connection.cursor()
    cur.execute("SELECT * FROM residents")
    datas = cur.fetchall()
    cur.close()

    cur = connection.cursor()
    cur.execute("SELECT * FROM stores")
    stores = cur.fetchall()
    cur.close()

    cur = connection.cursor()
    cur.execute("SELECT * FROM gas_stations")
    gas = cur.fetchall()
    cur.close()

    cur = connection.cursor()
    cur.execute("SELECT * FROM hospitals")
    hospitals = cur.fetchall()
    cur.close()


    return render_template('map.html', datas=datas, stores=stores , gas=gas , hospitals=hospitals)


@app.route('/resident')
def select():
    return render_template('resident.html')

@app.route('/select')
def selectType():
    return render_template('select.html')

# Register Form Class
class RegisterForm(Form):
    email = StringField('email', [
        validators.Regexp('[\w.+\-]+@ubu.ac\.th$', message="กรุณาใช้เมล@ubu.ac.th"),
    ])
    fname = StringField('firstName', [validators.Length(min=6, max=50)])
    lastName = StringField('lastName', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='พาสไม่ตรงกัน')
    ])
    confirm = PasswordField('Confirm Password')

def random_with_N_digits(n):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return randint(range_start, range_end)

# User Register
@app.route('/register', methods=['GET', 'POST'])
def register():

    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        with smtplib.SMTP(host=SMTP_HOST, port=SMTP_PORT) as server:
            email = form.email.data
            password = sha256_crypt.encrypt(str(form.password.data))
            fname = form.fname.data
            lastName = form.lastName.data
        # Create cursor
            cur = connection.cursor()

            x = cur.execute("SELECT * FROM members WHERE email = %s",(email))
            
            if int(x) > 0:
            # flash("That username is already taken, please choose another", 'danger')
                return render_template('login.html', form=form)

        # Execute query
            cur.execute("INSERT INTO members(email, password, firstName, lastName) VALUES(%s, %s, %s, %s)", (email, password, fname, lastName))

        # Commit to DB
            connection.commit()

        # Close connection
            cur.close()
            flash('You are now registered and can log in', 'success')

            OTP = random_with_N_digits(5)
            cur = connection.cursor()
            cur.execute("INSERT INTO otp(OTP, email) VALUES(%s, %s)", (OTP, email))
            connection.commit()
            cur.close()
            flash('Send OTP Success', 'success')

            
            msg = f"From: worawit.pa.61@ubu.ac.th\r\nTo: {form.email.data}\r\nSubject: OTP: < {OTP} >\r\n"
            server.starttls()
            server.login('worawit.pa.61@ubu.ac.th', 'Vryi4696')
            server.sendmail('worawit.pa.61@ubu.ac.th', form.email.data, msg)
            return render_template('OTP.html',email=form.email.data)
        
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
        data = cur.fetchone()
        if result > 0 and data['verify'] == "verify":
            # Get stored hash
            
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

@app.route('/add/<string:type>', methods=['GET', 'POST'])
def add(type):
    if request.method == 'POST':
        if type == "resident":
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

            cur = connection.cursor()
            x = cur.execute("SELECT * FROM residents WHERE residentName = %s",[residentName])
            if int(x) > 0:
                flash("มีคนได้เพิ่มหอพักนี้ไปแล้ว", 'danger')
            cur.execute("INSERT INTO residents(addformuser, residentName, lat, lng, roomType, price, details, phoneConnect, OtherConnect, image, air, fan, water_heater, furniture, cable_tv, phone_direct, internet, pet, smoking, parking, elevators, security, keycard, cctv, pool, fitness, laundry, hair_salon) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (user_id, residentName, lat, lng, roomType, price, details, phoneConnect, OtherConnect, filename, air, fan, water_heater, furniture, cable_tv, phone_direct, internet, pet, smoking, parking, elevators, security, keycard, cctv, pool, fitness, laundry, hair_salon))

            connection.commit()

            cur.close()

            flash('resident saved', 'success')
        elif type == "store":
            name = request.form['residentName']
            lat = request.form['lat']
            lng = request.form['lng']
            cur = connection.cursor()

            x = cur.execute("SELECT * FROM stores WHERE name = %s",[name])
            if int(x) > 0:
                flash("มีคนได้เพิ่มร้านค้านี้ไปแล้ว", 'danger')
            cur.execute("INSERT INTO stores(name, lat, lng) VALUES(%s, %s, %s)", (name, lat, lng))

            connection.commit()

            cur.close()

            flash('store has saved', 'success')
        
        elif type == "gas":
            name = request.form['residentName']
            lat = request.form['lat']
            lng = request.form['lng']
            cur = connection.cursor()

            x = cur.execute("SELECT * FROM gas_stations WHERE name = %s",[name])
            if int(x) > 0:
                flash("มีคนได้เพิ่มร้านค้านี้ไปแล้ว", 'danger')
            cur.execute("INSERT INTO gas_stations(name, lat, lng) VALUES(%s, %s, %s)", (name, lat, lng))

            connection.commit()

            cur.close()

            flash('gas station has saved', 'success')
        
        elif type == "hospital":
            name = request.form['residentName']
            lat = request.form['lat']
            lng = request.form['lng']
            cur = connection.cursor()

            x = cur.execute("SELECT * FROM hospitals WHERE name = %s",[name])
            if int(x) > 0:
                flash("มีคนได้เพิ่มร้านค้านี้ไปแล้ว", 'danger')
            cur.execute("INSERT INTO hospitals(name, lat, lng) VALUES(%s, %s, %s)", (name, lat, lng))

            connection.commit()

            cur.close()

            flash('hospital station has saved', 'success')

            
    return render_template("add.html",type=type)

@app.route('/resident/<string:id>',methods=['GET'])
def resident(id):
    cur = connection.cursor()
    result = cur.execute("SELECT * FROM residents WHERE residentId = %s", [id])
    datas = cur.fetchall()
    cur.close()
    return render_template("resident.html",datas=datas)


if __name__ == '__main__':
    app.secret_key='kmasdfp[mf[pbn[dnfbpndp[b'
    app.run(debug=True)
    