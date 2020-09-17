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

if __name__ == '__main__':
    app.secret_key='DDoS'
    app.run(debug=True)
