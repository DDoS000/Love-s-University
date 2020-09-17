from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from functools import wraps
import pyrebase

app = Flask(__name__)


configuse = {
    "type": "service_account",
    "project_id": "foodmanage-e63a1",
    "private_key_id": "bda07ba57843d1e3fa3219f8549607b357a24c02",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCm3BIxzSU7nd0h\nYdiL8mqmCB1+RwDGrBjtXALzBOfGUKpxU0nKdlk05gPbT0S4vHP5YU3OSWz66nuH\nh9QbOD0VZ/S4XUeu9hOdjRfvp+tYnigTrFekCZeGgOuErKncCnkBdohZEEK2Mvfa\nOb/nUebqMqUWA5SVC26krVmd2Yh5LUkU/fgQJ1zBKQzA/ekVW5AxRb+WZKOuasBb\nYCmMtNz8OcEDMXPyMJ5BMU/ONCC5Mt081K6UqqTSW5psy4Lgp2T9cYb+XL60A6ov\n8UyWbw/9aI1S8+6sqltkRwzt7RURE5DtcoKgKl54XPLMbHV4/n7EJXEBdXAjEi9B\nbtyJFr27AgMBAAECggEAF07hMRkO/RJC3smO45MBWCAEvqxRwhmC1zqQeZH92Qim\nRnOeoywqWeaniJhnaRwqDHPjLSW563LwaTDiwsqgUxUqbMva75MVj7SIhhmsGRI+\nrEDZco3vH1gdjh2bEfmvMt0elBJev0TEtTR2nMF8GCBASfWbaRZ9ENPbk4kyNHrn\nnPiBzUKa/AFNon3D477Dd8Xj3glzSoAji0n8zQPM+da6o7qomVQyp3NcCu/Hirg7\nXAfn108RLr7kNthr9dJS+wrDJQyXYyKl8HaD7w5sFz4Va+FLBM8Y1w5RE1/nOP1P\n6JxMOOMOjXH72ddafzCpuEjrYW3qoicSHtBm89KlAQKBgQDjOC4S1CrN4c9Ku7ma\nlnWx33V9l25BVJgu+Vhvjo7AJZFNy5wFrEx2nOaez1x8bxT4M8S5RqsQU/m6JYab\nhZV02w8q26B8mx1Ils5cW/FwQKGMCJu7edeCW0jkeHlZPHuX2+WCdc1TDsO9k/xS\nJ9Hzq5KrIslOPVJT8ftEpeNjKwKBgQC7/qnmHfXqHGDe7B25dj+GJM9C2wUcqo+V\ndogPQSu5bXwayFNjuL6b8a1AEa0kVNx5wjQqa7U4PJv1S8NL7PpG29RHjz4cOSHI\npFi61FaJIiHZtpUBcEj1WVQiS/auYgBYprkV8bXMiSBxN5pMTAPNb+VecxsN1grB\nRRcdLPsHsQKBgBZ2hF+KKB0oeMTLoEK/Iy2NiOD8qoK86TqjnfGRZ11pmV7WhTsu\nWHTVeBs1JtCKbslG3OjwKpM3qhWUBiWz5B2kVnCHO+t1rkRx3D7XPBw713yvkS3M\nktipS6CCpISE7TcLHzpxiPXwHLvOOICqvR/Y02wlyT754vy3jH6x47P3AoGAGC0L\n1FgOA+laW9CpkewvByU8sjBQW/tjM6lmne+Xm+UEjL0uXCip+ov957teNMnlAJOE\n+d+YEn9Y3xa7Ksxy8yHaDsnRBvgh7BeWgZBFAKWvDLx6NREnkMXIGBEEzDA2MzBd\npQDMjF0mGuk3opAz/Pti196doA3inDAyZMIgFkECgYEAnZLHkcs6CgKMY9Yvgb+q\nOoywreKpeqDXijReA1J551lEwpkyHwbfdVYyuTVFyHto6sMHqn20hLWUxbDlWDsY\nclN8fqSwSZk/Jm81C40e7rEEybIcDUqq0eHgU5dydaB7Y1yVSXPNflm7c65BXc2E\ng/f2ynG/bFcvHPC2N0e44uY=\n-----END PRIVATE KEY-----\n",
    "client_email": "firebase-adminsdk-jvifj@foodmanage-e63a1.iam.gserviceaccount.com",
    "client_id": "103611357675025426296",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-jvifj%40foodmanage-e63a1.iam.gserviceaccount.com"
}

# Use a service account
cred = credentials.Certificate(configuse)
firebase_admin.initialize_app(cred)

db = firestore.client()

fbConfig = {
    "apiKey": "AIzaSyAX5UAWd54SOE-YHO57YWOgMLlJ2bmgcn8",
    "authDomain": "foodmanage-e63a1.firebaseapp.com",
    "databaseURL": "https://foodmanage-e63a1.firebaseio.com",
    "projectId": "foodmanage-e63a1",
    "storageBucket": "foodmanage-e63a1.appspot.com",
    "messagingSenderId": "1024309103110",
    "appId": "1:1024309103110:web:5895822a1b04b8a9ffd187"
}

app.secret_key = '802a10465059f4276f654ab46b8033a2'

firebase = pyrebase.initialize_app(fbConfig)
auth = firebase.auth()
database = firebase.database()


def GetDataUser(uid):
    doc_ref = db.collection(u'users').document(uid)
    doc = doc_ref.get()
    docs = doc.to_dict()
    return docs


# Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('login'))
    return wrap


@app.route('/')
def index():
    if 'logged_in' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')


# Dashboard
@app.route('/dashboard')
@is_logged_in
def dashboard():
    return render_template('dashboard.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'logged_in' in session:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        try:
            user = auth.sign_in_with_email_and_password(email, password)
            # Passed
            docs = GetDataUser(user["localId"])
            print(docs)
            print(docs["acc"]["manage"])
            if docs["acc"]["manage"] == True:
                session['logged_in'] = True
                session['uid'] = user["localId"]
                session['email'] = user["email"]
                session['storename'] = docs["store"]["storename"]
                flash('เข้าสู้ระบบสําเร็จ', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('คุณไม่มีสิทธิ์เข้าถึง', 'success')
                return redirect(url_for('dashboard'))
        except Exception as Error:
            print(Error)
            error = 'อีเมลล์หรือรหัสผ่านไม่ถูกต้อง'
            return render_template('login.html', error=error)
    return render_template('login.html')


@app.route('/manageStore/', methods=['GET', 'POST'])
@is_logged_in
def manageStore():
    docs = GetDataUser(session['uid'])
    try:
        session['storename'] = docs["store"]["storename"]
        storename = docs["store"]["storename"]
        desc = docs["store"]["desc"]
        Open = docs["store"]["time"]["open"]
        close = docs["store"]["time"]["close"]
        lat = docs["store"]["location"]["lat"]
        lng = docs["store"]["location"]["lng"]
    except Exception:
        print(u'No such document!')
        storename = ""
        desc = ""
        Open = ""
        close = ""
        lat = 0
        lng = 0

    if request.method == "POST":
        storename = request.form['storename']
        desc = request.form['desc']
        Open = request.form['open']
        close = request.form['close']
        lat = request.form['lat']
        lng = request.form['lng']
        data = {
            u"store": {
                u"storename": str(storename),
                u"desc": str(desc),
                u"time": {
                    u"open": str(Open),
                    u"close": str(close)
                },
                u"location": {
                    u"lat": float(lat),
                    u"lng": float(lng)
                }
            }
        }
        session['storename'] = storename
        try:
            db.collection(u'users').document(session['uid']).update(data)
            flash('อัพเดทข้อมูลสําเร็จ', 'success')
            return render_template('manageStore.html', storename=storename, desc=desc, Open=Open, close=close, lat=lat, lng=lng)
        except KeyError:
            print(KeyError)
            return render_template('manageStore.html', storename=storename, desc=desc, Open=Open, close=close, lat=lat, lng=lng)
    return render_template('manageStore.html', storename=storename, desc=desc, Open=Open, close=close, lat=lat, lng=lng)


@app.route('/manageFood/', methods=['GET', 'POST'])
@is_logged_in
def manageFood():
    docs = GetDataUser(session['uid'])

    try:
        foods = docs["menu"]
        print("getfoodspass")
    except KeyError:
        print("getfoodsError")
        foods = [{'photourl': '', 'name': 'ยังไม่มีข้อมูลในระบบ',
                  'detail': 'ยังไม่มีข้อมูลในระบบ', 'price': 'ยังไม่มีข้อมูลในระบบ', 'foodId': 'notvalue'}]

    return render_template('manageFood.html', foods=foods)


@app.route('/addfoods/', methods=['GET', 'POST'])
@is_logged_in
def addfoods():
    if request.method == "POST":
        foodname = request.form['foodname']
        detail = request.form['foodedtail']
        price = request.form['foodprice']
        url = request.form['url']
        print("setdata")
        try:
            counts = GetDataUser(session['uid'])['count']
            counts += 1
        except KeyError:
            try:
                print("UP0")
                counts = 0
                db.collection(u'users').document(
                    session['uid']).update({u"count": 0})
            except KeyError:
                print("upcountna")
            print("Error Get data count")
        print(counts)
        data = {
            u"foodId": counts,
            u"name": foodname,
            u"detail": detail,
            u"price": price,
            u"photourl": url
        }
        try:
            db.collection(u'users').document(
                session['uid']).update({u"count": counts})
            print("upcountpass")
            db.collection(u'users').document(session['uid']).update(
                {u'menu': firestore.ArrayUnion([data])})
        except KeyError:
            print(KeyError)

    return redirect(url_for('manageFood'))


@app.route('/manageSeat')
@is_logged_in
def manageSeat():
    return render_template('manageSeat.html')


@app.route('/ar')
def ar():
    return render_template('ar.html')

@app.route('/ar2')
def ar2():
    return render_template('ar2.html')


# Logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('ออกจากระบบสําเร็จ', 'success')
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.secret_key = '802a10465059f4276f654ab46b8033a2'
    app.config['SESSION_TYPE'] = 'filesystem'

    app.run(debug=True)
