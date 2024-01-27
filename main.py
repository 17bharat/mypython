from flask import Flask, render_template, request, redirect, url_for, session
from flask_bootstrap import Bootstrap
import re
import ssl
import time, datetime
import openai
openai.api_key = "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"
#assistant_id = "asst_gZxSXO54CATUchcFfSCB2ODk"
#if request.method == 'POST' :
#	assistant_id = request.form['Recruiter']


#assistant_id = _Recruiter

app = Flask(__name__)


app.secret_key = 'your secret key'
ctx = ssl.create_default_context()
# And in this example we disable validation...
# Please don't do this. Loot at the official Python ``ssl`` module documentation
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
SelectAssid=''
SelectInsid=0

@app.route('/')
@app.route('/login', methods =['GET', 'POST'])
def login():
	msg = ''
	if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
		username = request.form['username']
		password = request.form['password']
		return render_template('register.html',  SelectAssid=SelectAssid, SelectInsid='1')
	else:
			msg = 'Incorrect username / password !'
	return render_template('login.html', msg = msg)