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

app.config['IMAGE_UPLOAD'] = "static/image/"
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
    cur = connection.cursor()
    cur.execute("SELECT * FROM residents")
    datas = cur.fetchall()
    cur.close()

    cur = connection.cursor()
    cur.execute("SELECT * FROM all_location")
    all = cur.fetchall()
    cur.close()


    cur = connection.cursor()
    cur.execute("SELECT * FROM reviews ORDER BY rating DESC")
    top = cur.fetchall()
    cur.close()
    
    return render_template('map.html', datas=datas, all=all, top=top)

@app.route('/index')
def index():

    cur = connection.cursor()
    cur.execute("SELECT * FROM residents")
    datas = cur.fetchall()
    cur.close()

    
    cur = connection.cursor()
    cur.execute("SELECT * FROM all_location")
    all = cur.fetchall()
    cur.close()

    cur = connection.cursor()
    cur.execute("SELECT * FROM reviews ORDER BY rating DESC")
    top = cur.fetchall()
    cur.close()

    return render_template('map.html', datas=datas, all=all, top=top)

@app.route('/admin', methods=['GET', 'POST'])
def Addmin():
    cur = connection.cursor()
    cur.execute("SELECT * FROM members")
    members = cur.fetchall()
    cur.close()

    cur = connection.cursor()
    cur.execute("SELECT * FROM residents")
    residents = cur.fetchall()
    cur.close()

    cur = connection.cursor()
    cur.execute("SELECT * FROM all_location")
    all = cur.fetchall()
    cur.close()

    cur = connection.cursor()
    cur.execute("SELECT * FROM reviews")
    reviews = cur.fetchall()
    cur.close()

    cur = connection.cursor()
    total_residents = cur.execute("SELECT * FROM residents")
    cur.close()

    cur = connection.cursor()
    total_comments = cur.execute("SELECT * FROM reviews")
    cur.close()

    cur = connection.cursor()
    total_users = cur.execute("SELECT * FROM members")
    cur.close()
    return render_template('Admin.html',members=members, residents=residents, all=all, reviews=reviews,total_residents=total_residents, total_comments=total_comments ,total_users=total_users)

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

@app.route('/about-team')
def about_team():
    return render_template('landing.html')



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

            
            msg = f"From: under.university.61@gmail.com\r\nTo: {form.email.data}\r\nSubject: OTP: < {OTP} >\r\n"
            server.starttls()
            server.login('under.university.61@gmail.com', 'love@123456')
            server.sendmail('under.university.61@gmail.com', form.email.data, msg)
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

@app.route('/adds/<string:types>', methods=['GET', 'POST'])
def adds(types):
    return render_template("adds.html",types=types)

@app.route('/insert_location', methods=['POST'])
def insert_location():
    if request.method == 'POST':
        user_id = request.form['addformuser']
        names = request.form['name']
        lat = request.form['lat']
        lng = request.form['lng']
        types = request.form['types']

        cur = connection.cursor()
        x = cur.execute("SELECT * FROM all_location WHERE name = %s",[names])
        if int(x) > 0:
            flash("มีคนได้เพิ่มสถานที่นี้ไปแล้วพักนี้ไปแล้ว", 'danger')
            cur.close()
        cur.execute("INSERT INTO all_location(addformuser ,name, lat, lng, types) VALUES(%s, %s, %s, %s, %s)", (user_id ,names, lat, lng, types))
        connection.commit()
        cur.close()
        flash("ได้ทําการเพิ่มข้อมูลเรียบร้อยแล้ว", 'danger')
        
    return redirect(url_for('index'))

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

        cur = connection.cursor()
        x = cur.execute("SELECT * FROM residents WHERE residentName = %s",[residentName])
        if int(x) > 0:
            flash("มีคนได้เพิ่มหอพักนี้ไปแล้ว", 'danger')
            cur.close()
        cur.execute("INSERT INTO residents(addformuser, residentName, lat, lng, roomType, price, details, phoneConnect, OtherConnect, image, air, fan, water_heater, furniture, cable_tv, phone_direct, internet, pet, smoking, parking, elevators, security, keycard, cctv, pool, fitness, laundry, hair_salon) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (user_id, residentName, lat, lng, roomType, price, details, phoneConnect, OtherConnect, filename, air, fan, water_heater, furniture, cable_tv, phone_direct, internet, pet, smoking, parking, elevators, security, keycard, cctv, pool, fitness, laundry, hair_salon))
        connection.commit()
        cur.close()
        flash('resident saved', 'success')

        connection.commit()
        cur.close()

    return render_template("add.html")

@app.route('/resident/<string:id>',methods=['GET', 'POST'])
def resident(id):
    cur = connection.cursor()
    result = cur.execute("SELECT * FROM residents WHERE residentId = %s", [id])
    datas = cur.fetchall()
    cur.close()

    cur = connection.cursor()
    result = cur.execute("SELECT * FROM reviews")
    reviews = cur.fetchall()
    cur.close()

    if request.method == 'POST':
        print(request.form)
        cur = connection.cursor()
        cur.execute("INSERT INTO reviews(comments, rating, userId, residentId) VALUES(%s, %s, %s, %s)", (request.form['comments'], request.form['rating'], request.form['userId'], request.form['residentId']))
        connection.commit()
        cur.close()
        
    return render_template("resident.html",datas=datas ,id=id,reviews=reviews)


@app.route('/delete/<string:path>/<string:id_delete>',methods=['GET'])
@is_logged_in
def delete(path,id_delete):
    cur = connection.cursor()
    if path == "members":
        cur.execute("delete FROM members WHERE userId = %s",[id_delete])
    elif path == "all_location":
        cur.execute("delete FROM all_location WHERE id = %s",[id_delete])
    elif path == "residents":
        cur.execute("delete FROM residents WHERE residentId = %s",[id_delete])
    elif path == "reviews":
        cur.execute("delete FROM reviews WHERE reviewId = %s",[id_delete])

    connection.commit()
    cur.close()
    return redirect(url_for('Addmin'))

@app.route('/setting')
@is_logged_in
def setting():
    username = session['userId']
    cur = connection.cursor()
    cur.execute("SELECT * FROM members WHERE userId = %s", [username])
    data = cur.fetchall()
    cur.close()
    return render_template('setting.html',data=data)

@app.route('/update',methods=['POST'])
@is_logged_in
def update():
    try:
        userId = session['userId']
        if request.method=="POST":
            firstName = request.form['firstName']
            lastName = request.form['lastName']
            email = request.form['email']

            #conn db
            cur = connection.cursor()
            sql = "update members set firstName = %s, lastName = %s, email = %s where userId = %s"
            cur.execute(sql,(firstName, lastName, email, userId))
            connection.commit
            cur.close
            flash("ข้อมูลได้รับการอัพเดทเรียร้อยแล้ว","success")
            return redirect(url_for('setting'))
    except Exception as Error:
        error = str(Error)
        print(error)
        return redirect(url_for('setting'))

if __name__ == '__main__':
    app.secret_key='kmasdfp[mf[pbn[dnfbpndp[b'
    app.run(debug=True, host="128.199.113.206")
    