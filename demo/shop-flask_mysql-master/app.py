from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
#from data import
import pymysql.cursors
from passlib.hash import sha256_crypt
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from functools import wraps

app = Flask(__name__)

# Config MySQL
MYSQL_HOST          = 'localhost'
MYSQL_USER          = 'root'
MYSQL_PASSWORD      = ''
MYSQL_DB            = 'shopfooddb'


#connection MySQL
connection = pymysql.connect(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, db=MYSQL_DB , cursorclass=pymysql.cursors.DictCursor)


# Index
@app.route('/')
def index():
    return render_template('home.html')


@app.route('/review')
def review():
    cur = connection.cursor()
    result = cur.execute("SELECT * FROM data_mess WHERE status = 'review' ")
    data = cur.fetchall()
    return render_template('review.html', data=data, result=result)
    


# history
@app.route('/history')
def history():
    # Create cursor
    cur = connection.cursor()

    # Get history
    result = cur.execute("SELECT * FROM orderdb")

    history = cur.fetchall()

    if result > 0:
        return render_template('history.html', history=history)
    else:
        msg = 'No History Found'
        return render_template('history.html', msg=msg)
    # Close connection
    cur.close()




# Register Form Class
class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    phone = StringField('Phone', [validators.Length(min=10, max=10)])
    city = StringField('City', [validators.Length(min=9, max=100)])
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
        name = form.name.data
        email = form.email.data
        phone = form.phone.data
        city = form.city.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        # Create cursor
        cur = connection.cursor()

        x = cur.execute("SELECT * FROM account WHERE username = %s",(username))

        if int(x) > 0:
            flash("That username is already taken, please choose another", 'danger')
            return render_template('register.html', form=form)

        # Execute query
        cur.execute("INSERT INTO account(name, email, username, password, phone, city) VALUES(%s, %s, %s, %s, %s, %s)", (name, email, username, password, phone, city))

        # Commit to DB
        connection.commit()

        # Close connection
        cur.close()

        flash('You are now registered and can log in', 'success')

        return redirect(url_for('login'))
    return render_template('register.html', form=form)


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
        result = cur.execute("SELECT * FROM account WHERE username = %s", [username])

        if result > 0:
            # Get stored hash
            data = cur.fetchone()
            password = data['password']
            status = data['status']
            city = data['city']
            email = data['email']


            # Compare Passwords
            if sha256_crypt.verify(password_candidate, password):
                # Passed
                session['logged_in'] = True
                session['username'] = username
                session['status'] = status
                session['city'] = city
                session['email'] = email

                flash('You are now logged in', 'success')
                return redirect(url_for('Menu'))
            else:
                error = 'Invalid login'
                return render_template('login.html', error=error)
            # Close connection
            cur.close()
        else:
            error = 'Wrong username or password !!!'
            return render_template('login.html', error=error)

    return render_template('login.html')

# Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Only Member, Please login !!!', 'danger')
            return redirect(url_for('login'))
    return wrap

# Logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))


# Dashboard
@app.route('/dashboard')
@is_logged_in
def dashboard():
    date = ['Wait','Accept','Sending','completed']
    stt_W = []
    stt_Acc = []
    stt_Sd = []
    stt_cp = []
    row = 0
    for status in date:
        row+=1
        cur = connection.cursor()
        result = cur.execute("SELECT * FROM orderdb WHERE status = %s", [status] )
        stt_date = cur.fetchall()
        if row == 1:
            stt_W.append(result)
            stt_W.append(stt_date)
        elif row == 2:
            stt_Acc.append(result)
            stt_Acc.append(stt_date)
        elif row == 3:
            stt_Sd.append(result)
            stt_Sd.append(stt_date)
        elif row == 4:
            stt_cp.append(result)
            stt_cp.append(stt_date)

    acctotal = cur.execute("SELECT * FROM account")
    cmmtotal = cur.execute("SELECT * FROM data_mess")

    innMoney = 0
    for s1 in stt_cp[1]:
        innMoney += s1['price']

    if stt_W[0] > 0:
        msg = 'New order '+str(stt_W[0])
        return render_template('dashboard.html', msg=msg, cmmtotal=cmmtotal, innMoney=innMoney, acctotal=acctotal, stt_W=stt_W, stt_Acc=stt_Acc, stt_Sd=stt_Sd, stt_cp=stt_cp)
    else:
        msg = 'No Order Wait'
        return render_template('dashboard.html', msg=msg, cmmtotal=cmmtotal, innMoney=innMoney, acctotal=acctotal, stt_W=[0], stt_Acc=stt_Acc, stt_Sd=stt_Sd, stt_cp=stt_cp)
    # Close connection
    cur.close()

#show menu
@app.route('/menu/')
@is_logged_in
def Menu():
    return render_template('showmenu.html')


@app.route('/myorder/')
@is_logged_in
def myorder():
    customer = session['username']
    cur = connection.cursor()
    result = cur.execute("SELECT * FROM orderdb WHERE customer = %s And status = %s", [customer,"Wait"] )
    history = cur.fetchall()
    cur.close()
    return render_template('myorder.html', history=history, result=result)


@app.route('/myhistory/')
@is_logged_in
def myhistory():
    customer = session['username']
    cur = connection.cursor()
    result = cur.execute("SELECT * FROM orderdb WHERE customer = %s", [customer] )
    history = cur.fetchall()
    cur.close()
    return render_template('myhistory.html', history=history, result=result)


@app.route('/setting')
@is_logged_in
def setting():
    username = session['username']
    cur = connection.cursor()
    cur.execute("SELECT * FROM account WHERE username = %s", [username])
    data = cur.fetchall()
    cur.close()
    return render_template('setting.html',data=data)


@app.route('/addorder/<string:id>',methods=['GET'])
@is_logged_in
def addorder(id):
    datafood = { '0':["สเต็กหมู",79] }
    customer = session['username']
    city = session['city']
    print(city)
    data = datafood[id]
    cur = connection.cursor()
    sql="Insert into `orderdb` (`customer`,`menu`,`price`,`city`) values(%s,%s,%s,%s)"
    cur.execute(sql,(customer,data[0],data[1],city))
    connection.commit()
    cur.close()
    flash("การสังซื้อสําเร็จ","success")
    return redirect(url_for('myorder'))


@app.route('/upstatus/<string:id_order>',methods=['GET'])
@is_logged_in
def upstatus(id_order):
    cur = connection.cursor()
    cur.execute("SELECT * FROM orderdb WHERE id = %s", [id_order])
    data_id = cur.fetchall()
    data_check = data_id[0]
    if data_check['status'] == "Wait":
        cur.execute("UPDATE orderdb SET status = 'Accept' WHERE id = %s", [data_check['id']])
        connection.commit()
    elif data_check['status'] == "Accept":
        cur.execute("UPDATE orderdb SET status = 'Sending' WHERE id = %s", [data_check['id']])
        connection.commit()
    elif data_check['status'] == "Sending":
        cur.execute("UPDATE orderdb SET status = 'completed' WHERE id = %s", [data_check['id']])
        connection.commit()
    cur.close()
    return redirect(url_for('dashboard'))


@app.route('/delete/<string:id_delete>',methods=['GET'])
@is_logged_in
def delete(id_delete):
    cur = connection.cursor()
    cur.execute("delete FROM orderdb WHERE id = %s",[id_delete])
    connection.commit()
    cur.close()
    return redirect(url_for('dashboard'))


@app.route('/update',methods=['POST'])
@is_logged_in
def update():
    try:
        username = session['username']
        if request.method=="POST":
            name = request.form['name']
            phone = request.form['phone']
            email = request.form['email']
            city = request.form['city']
            #conn db
            cur = connection.cursor()
            sql = "update account set name = %s, email = %s, phone = %s, city = %s where username = %s"
            cur.execute(sql,(name, email, phone, city, username))
            connection.commit
            cur.close
            flash("ข้อมูลได้รับการอัพเดทเรียร้อยแล้ว","success")
            return redirect(url_for('setting'))
    except Exception as Error:
        error = str(Error)
        return render_template('setting.html',error=error)


@app.route('/formreview')
@is_logged_in
def formreview():
    return render_template('addreview.html')


@app.route('/addreview',methods=['POST'])
@is_logged_in
def addreview():
    try:
        status = 'review'
        user = session['username']
        email = session['email']
        if request.method=="POST":
            title = request.form['title']
            mess = request.form['mess']
            star = request.form['star']
            #conn db
            cur = connection.cursor()
            sql="Insert into `data_mess` (`status`,`star`,`user`,`email`,`title`,`messages`) values(%s,%s,%s,%s,%s,%s)"
            cur.execute(sql,(status,star,user,email,title,mess))
            cur.close
            connection.commit()
            flash("คุณได้เขี่ยนรีวิวแล้ว","success")
            return redirect(url_for('review'))
    except Exception as Error:
        error = str(Error)
        return render_template('addreview.html',error=error)


if __name__ == '__main__':
    app.secret_key='DDoS'
    app.run(debug=True)
