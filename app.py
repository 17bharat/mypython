# Store this code in 'app.py' file
#!/usr/bin/env python

from flask import Flask, render_template, request, redirect, url_for, session

from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import ssl
import time, datetime
import openai
openai.api_key = "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"
#assistant_id = "asst_gZxSXO54CATUchcFfSCB2ODk"
#if request.method == 'POST' :python 
#	assistant_id = request.form['Recruiter']
	
# Configure logging to stdout


#assistant_id = _Recruiter
def health():
    return 'OK'


app = Flask(__name__)
app.run(host="https://skillai.azurewebsites.net", port=8000)

app.secret_key = 'your secret key'
ctx = ssl.create_default_context()
# And in this example we disable validation...
# Please don't do this. Loot at the official Python ``ssl`` module documentation
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

app.config['MYSQL_HOST'] = 'mysql-closemonitor.mysql.database.azure.com'
app.config['MYSQL_USER'] = 'bharat'
app.config['MYSQL_PASSWORD'] = 'Orange*630'
app.config['MYSQL_DB'] = 'closemonitormysql'
app.config['ssl']=ctx
	
mysql = MySQL(app)
SelectAssid=''
SelectInsid=0

@app.route('/')

@app.route('/login', methods =['GET', 'POST'])
def login():
	msg = ''
	if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
		username = request.form['username']
		password = request.form['password']
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM assistant_users WHERE Email = % s AND Password = % s', (username, password, ))
		account = cursor.fetchone()
		if account:
			session['loggedin'] = True
			session['id'] = account['UserId']
			session['username'] = account['UserName']
			mycursor = mysql.connection.cursor()
			mycursor.execute('SELECT AssistantID, AssistantKey, AssistantRecruiter FROM recruiter_assistant') 
			joblist = mycursor.fetchall() 


			return render_template('register.html', joblist = joblist, SelectAssid=SelectAssid, SelectInsid='1')
		else:
			msg = 'Incorrect username / password !'
	return render_template('login.html', msg = msg)

@app.route('/logout')
def logout():
	session.pop('loggedin', None)
	session.pop('id', None)
	session.pop('username', None)
	return redirect(url_for('login'))


# For Interview Question 
@app.route('/GetQuest')
def GetQuest():
	return render_template('Interview.html', msg='Interview Questions')
#-------------------------------------------------

@app.route('/register', methods =['GET', 'POST'])
def register():
	msg = ''
	myResume=''
	myJob=''
	instruction=''
	if request.method == 'POST' and 'txt_Resume' in request.form and 'txt_Job' in request.form :
		txt_Resume = request.form['txt_Resume']
		txt_Job = request.form['txt_Job']
		myResume=txt_Resume
		myJob=txt_Job
		SelectInsid=request.form['Instruction']
		if request.form['Instruction']==1 :
			instruction='Provide answer 3 to 4 lines'
		elif request.form['Instruction']==2:
			instruction='Provide answer 5 to 6 lines'

		assistant_id = request.form['Recruiter'] # AssistId from select Recuriter
		SelectAssid=assistant_id
		def create_thread(ass_id,prompt):
			thread=openai.beta.threads.create()
			my_thread_id=thread.id
			message=openai.beta.threads.messages.create(
				thread_id=my_thread_id,
				role="user",
				content=prompt
    		)
			run=openai.beta.threads.runs.create(
				thread_id=my_thread_id,
				assistant_id=ass_id
   	 		)
			return run.id, thread.id
	
		
		_resume=""
		_resume="You have to act as a IT recruiter and screen below given resume with the job"
		_resume=_resume + " specifications and provide a concise answer if the person is a good match "
		_resume=_resume + " for the job specifications. Also provide percent match. Having experience "
		_resume=_resume + " with major companies or having certifications in required skills is a big plus."
		_resume = _resume + " Check if candidates has primarilly worked on required skills in at least one of "
		_resume =_resume + " the two recent projects.\n "
		_resume = _resume +" Below is the resume \n"
		_resume=_resume + " " + txt_Resume +"\n"
		_resume= _resume + " Below is the job specifications:\n"
		_resume=_resume + txt_Job +"\n"
		_resume=_resume + instruction
		my_run_id, my_thread_id=create_thread(assistant_id,_resume)
		
		def check_status(run_id,thread_id):
			run=openai.beta.threads.runs.retrieve(
			thread_id=thread_id,
			run_id=run_id
    		)
			return run.status
		status= check_status(my_run_id,my_thread_id)
		
		while(status !="completed"):
			status= check_status(my_run_id,my_thread_id)
			time.sleep(2)

		response=openai.beta.threads.messages.list(
			thread_id=my_thread_id
        )
		mycursor = mysql.connection.cursor()
		mycursor.execute('SELECT AssistantID, AssistantKey, AssistantRecruiter FROM recruiter_assistant') 
		joblist = mycursor.fetchall()
		now = datetime.datetime.now()
		mycursor.execute('INSERT INTO Assistant_History VALUES (null, % s, % s,% s,% s,% s,% s,% s)', (session['id'],now,txt_Resume,txt_Job,SelectAssid,SelectInsid, response.data[0].content[0].text.value))
		mysql.connection.commit()	

		msg = 'Summary :- \n'+ response.data[0].content[0].text.value
	elif request.method == 'POST':
		msg = 'Please fill out the form !'
	return render_template('register.html', msg = msg, myResume=myResume, myJob=myJob, joblist=joblist ,SelectAssid=SelectAssid, SelectInsid=SelectInsid)

