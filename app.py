from flask import Flask,url_for,session,redirect,render_template,request,flash,send_file,send_from_directory
from flask_session import Session 
from flask_mysqldb import MySQL
from otp import genotp
from cmail import sendmail
import random
import os
from itsdangerous import URLSafeTimedSerializer
from key import secret_key,salt1,salt2
import smtplib
from smtplib import SMTP
from email.message import EmailMessage
from stoken import token
app=Flask(__name__)
app.secret_key = secret_key
app.config['SESSION_TYPE'] = 'filesystem'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Admin'
app.config['MYSQL_DB'] = 'online'
Session(app)
mysql = MySQL(app)
@app.route('/',methods=['GET','POST'])
def home():
     if request.method=="POST":
        name=request.form['name']
        emailid=request.form['emailid']
        phone_number=request.form['phone_number']
        message=request.form['message']
        cursor=mysql.connection.cursor()
        cursor.execute('insert into contactus(name,emailid,phone_number,message) values(%s,%s,%s,%s)',[name,emailid,phone_number,message])
        mysql.connection.commit()
     return render_template('home.html')
#----------------------------admin login---------------------------------------
@app.route('/registration',methods=['GET','POST'])
def aregister():
    if request.method=='POST':
        adminid= request.form['adminid']
        phonenumber= request.form['phonenumber']
        email = request.form['email']
        password= request.form['password']
        cursor=mysql.connection.cursor()
        cursor.execute('select count(*) from admin where adminid=%s',[adminid])
        count=cursor.fetchone()[0]
        cursor.execute('select count(*) from admin where email=%s',[email])
        count1=cursor.fetchone()[0]
        cursor.close()
        if count==1:
            flash('adminid already in use')
            return render_template('admin.html')
        elif count1==1:
            flash('Email already in use')
            return render_template('admin.html')
        data={'adminid':adminid,'phonenumber':phonenumber,'email':email,'password':password}
        subject='Email Confirmation'
        body=f"Thanks for signing up\n\nfollow this link for further steps-{url_for('confirm',token=token(data,salt1),_external=True)}"
        sendmail(to=email,subject=subject,body=body)
        flash('Confirmation link sent to mail')
        return redirect(url_for('alogin'))
    return render_template('admin.html')
@app.route('/confirm/<token>')
def confirm(token):
    try:
        serializer=URLSafeTimedSerializer(secret_key)
        data=serializer.loads(token,salt=salt1,max_age=180)
    except Exception as e:
        #print(e)
        return 'Link Expired register again'
    else:
        cursor=mysql.connection.cursor()
        adminid=data['adminid']
        cursor.execute('select count(*) from admin where adminid=%s',[adminid])
        count=cursor.fetchone()[0]
        if count==1:
            cursor.close()
            flash('You are already registerterd!')
            return redirect(url_for('alogin'))
        else:
            cursor.execute('insert into admin (adminid,phonenumber,EMAIL,PASSWORD) values(%s,%s,%s,%s)',[data['adminid'],data['phonenumber'],data['email'],data['password']])
            mysql.connection.commit()
            cursor.close()
            flash('Details registered!')
            return redirect(url_for('alogin'))
@app.route('/adminlogin', methods=['GET', 'POST'])
def alogin():
    if request.method == 'POST':
        adminid = request.form['adminid']
        # email=request.form['email']
        password = request.form['password']
        cursor=mysql.connection.cursor()
        cursor.execute('SELECT COUNT(*) FROM admin WHERE adminid=%s AND password=%s', [adminid, password])
        count = cursor.fetchone()[0]
        cursor.close()
        if count == 1:
            session['admin'] = adminid
            flash('Only Admin can login here')
            return redirect(url_for('admindashboard'))
        else:
            flash('Invalid username or password')
            return redirect(url_for('alogin'))

    return render_template('alogin.html')

@app.route('/alogout')
def alogout():
    if session.get('admin'):
        session.pop('admin')
        return redirect(url_for('alogin'))
    else:
        flash('u are already logged out!')
        return redirect(url_for('alogin'))
        #return redirect(url_for('loginp'))
# ------------------------------------user login---------------------------
@app.route('/signin',methods=['GET','POST'])
def register():
    if request.method=='POST':
        username = request.form['username']
        email = request.form['email']
        password= request.form['password']
        phno= request.form['phno']
        state=request.form['state']
        address=request.form['address']
        pincode=request.form['pincode']
        cursor=mysql.connection.cursor()
        cursor.execute('select count(*) from user where username=%s',[username])
        count=cursor.fetchone()[0]
        cursor.execute('select count(*) from user where email=%s',[email])
        count1=cursor.fetchone()[0]
        cursor.close()
        if count==1:
            flash('adminid already in use')
            return render_template('usersignin.html')
        elif count1==1:
            flash('Email already in use')
            return render_template('usersignin.html')
        data={'username':username,'email':email,'password':password,'phno':phno,'state':state,'address':address,'pincode':pincode}
        subject='Email Confirmation'
        body=f"Thanks for signing up\n\nfollow this link for further steps-{url_for('uconfirm',token=token(data,salt1),_external=True)}"
        sendmail(to=email,subject=subject,body=body)
        flash('Confirmation link sent to mail')
        return redirect(url_for('login'))
    return render_template('usersignin.html')
@app.route('/uconfirm/<token>')
def uconfirm(token):
    try:
        serializer=URLSafeTimedSerializer(secret_key)
        data=serializer.loads(token,salt=salt1,max_age=180)
    except Exception as e:
        #print(e)
        return 'Link Expired register again'
    else:
        cursor=mysql.connection.cursor()
        username =data['username']
        cursor.execute('select count(*) from user where username=%s',[username])
        count=cursor.fetchone()[0]
        if count==1:
            cursor.close()
            flash('You are already registerterd!')
            return redirect(url_for('login'))
        else:
            cursor.execute('insert into user (username,email,password,phno,state,address,pincode) values(%s,%s,%s,%s,%s,%s,%s)',[data['username'],data['email'],data['password'],data['phno'],data['state'],data['address'],data['pincode']])
            mysql.connection.commit()
            cursor.close()
            flash('Details registered!')
            return redirect(url_for('login'))
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['name']
        # email=request.form['email']
        password = request.form['password']
        cursor=mysql.connection.cursor()
        cursor.execute('SELECT COUNT(*) FROM user WHERE username=%s AND password=%s', [username, password])
        count = cursor.fetchone()[0]
        cursor.close()
        if count == 1:
            session['user'] = username
            flash('Only Admin can login here')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password')
            return redirect(url_for('login'))

    return render_template('userlogin.html')
@app.route('/logout')
def logout():
    if session.get('user'):
        session.pop('user')
        return redirect(url_for('login'))
    else:
        flash('u are already logged out!')
        return redirect(url_for('login'))
        #return redirect(url_for('loginp'))
@app.route('/washroomproblems', methods=['GET', 'POST'])
def washroomproblems():
    if session.get('user'):
        
        if request.method == "POST":
            id1=genotp()
            email = request.form['email']
            problem = request.form['problem']
            address=request.form['address']
            image=request.files['image']
            categorie=request.form['categorie']
            cursor=mysql.connection.cursor()
            filename=id1+'.jpg'
            data=cursor.execute('select * from complaint')
            print(data)
            cursor.execute('INSERT INTO complaint (id,username,email,problem,address,categorie) VALUES (%s,%s,%s,%s,%s,%s)',[id1,session.get('user'),email,problem,address,categorie]) 
            mysql.connection.commit()
            cursor.close()
            path=os.path.dirname(os.path.abspath(__file__))
            static_path=os.path.join(path,'static')
            image.save(os.path.join(static_path,filename))
            subject = 'complaint deatils'
            body = 'complaint are submitted' 
            sendmail(email,subject,body)
            flash('complaint submitted')
            return redirect(url_for('home'))

        return render_template('washroomproblems.html')
    else:
        return redirect(url_for('login'))
        

@app.route('/canteenproblems', methods=['GET', 'POST'])
def canteenproblems():
    if session.get('user'):
        
        if request.method == "POST":
            id1=genotp()
            email = request.form['email']
            problem = request.form['problem']
            address=request.form['address']
            image=request.files['image']
            categorie=request.form['categorie']
            cursor=mysql.connection.cursor()
            filename=id1+'.jpg'
            data=cursor.execute('select * from complaint')
            print(data)
            cursor.execute('INSERT INTO complaint (id,username,email,problem,address,categorie) VALUES (%s,%s,%s,%s,%s,%s)',[id1,session.get('user'),email,problem,address,categorie]) 
            mysql.connection.commit()
            cursor.close()
            path=os.path.dirname(os.path.abspath(__file__))
            static_path=os.path.join(path,'static')
            image.save(os.path.join(static_path,filename))
            subject = 'complaint deatils'
            body = 'complaint are submitted' 
            sendmail(email,subject,body)
            flash('complaint submitted')
            return redirect(url_for('home'))

        return render_template('canteenproblems.html')
    else:
        return redirect(url_for('login'))



@app.route('/classroomproblems')
def classroomproblems():
    if session.get('user'):
        
        if request.method == "POST":
            id1=genotp()
            email = request.form['email']
            problem = request.form['problem']
            address=request.form['address']
            image=request.files['image']
            categorie=request.form['categorie']
            cursor=mysql.connection.cursor()
            filename=id1+'.jpg'
            data=cursor.execute('select * from complaint')
            print(data)
            cursor.execute('INSERT INTO complaint (id,username,email,problem,address,categorie) VALUES (%s,%s,%s,%s,%s,%s)',[id1,session.get('user'),email,problem,address,categorie]) 
            mysql.connection.commit()
            cursor.close()
            path=os.path.dirname(os.path.abspath(__file__))
            static_path=os.path.join(path,'static')
            image.save(os.path.join(static_path,filename))
            subject = 'complaint deatils'
            body = 'complaint are submitted' 
            sendmail(email,subject,body)
            flash('complaint submitted')
            return redirect(url_for('home'))

        return render_template('classroomprolems.html')
    else:
        return redirect(url_for('login'))

@app.route('/groundproblems')
def groundproblems():
    if session.get('user'):
        
        if request.method == "POST":
            id1=genotp()
            email = request.form['email']
            problem = request.form['problem']
            address=request.form['address']
            image=request.files['image']
            categorie=request.form['categorie']
            cursor=mysql.connection.cursor()
            filename=id1+'.jpg'
            data=cursor.execute('select * from complaint')
            print(data)
            cursor.execute('INSERT INTO complaint (id,username,email,problem,address,categorie) VALUES (%s,%s,%s,%s,%s,%s)',[id1,session.get('user'),email,problem,address,categorie]) 
            mysql.connection.commit()
            cursor.close()
            path=os.path.dirname(os.path.abspath(__file__))
            static_path=os.path.join(path,'static')
            image.save(os.path.join(static_path,filename))
            subject = 'complaint deatils'
            body = 'complaint are submitted' 
            sendmail(email,subject,body)
            flash('complaint submitted')
            return redirect(url_for('home'))

        return render_template('groundproblems.html')
    else:
        return redirect(url_for('login'))



@app.route('/admindashboard')
def admindashboard():
    if session.get('admin'):
        cursor=mysql.connection.cursor()
        cursor.execute('select * from complaint')
        details = cursor.fetchall()
        return render_template('admindashboard.html',details=details)
    else:
        return redirect(url_for('alogin'))
@app.route('/notsolved')
def notsolved():
    if session.get('admin'):
        cursor=mysql.connection.cursor()
        cursor.execute('select * from complaint where status="Not Started"')
        details=cursor.fetchall()
        '''if request.method=="POST":
            id1=request.form['id1']
            status=request.form['status']
            cursor.execute('update complaint set status=%s where id=%s',[id1,status])
            cursor.commit()'''
        return render_template('unsolved.html',details=details)
    else:
        return redirect(url_for('alogin'))
@app.route('/update/<id1>',methods=['GET','POST'])
def update(id1):
    if session.get('admin'):
        cursor=mysql.connection.cursor()
        cursor.execute('select * from complaint where id=%s',[id1])
        data=cursor.fetchone()
        cursor.close()
        if request.method=='POST':
            status=request.form['status']
            cursor=mysql.connection.cursor()
            cursor.execute('update complaint set status=%s where id=%s',[status,id1])
            mysql.connection.commit()
            cursor.execute('select email from complaint where id=%s',[id1])
            
            email=cursor.fetchone()[0]
            print(email)
            cursor.close()
            subject = 'complaint deatils'#--------------------
            body = f'the status of the complaint {status}' #-----------------------------
            sendmail(email,subject,body)#-----------------
            flash('updated successfully')
            cursor.close()
            flash('updated successfully')
            return redirect(url_for('notsolved'))
     
    else:
        return redirect(url_for('alogin'))
    return render_template('update.html',data=data)
@app.route('/currently')
def currently():
    if session.get('admin'):
        cursor=mysql.connection.cursor()
        cursor.execute('select * from complaint where status="In Progress"')
        details=cursor.fetchall()
        print(details)
        return render_template('inprogress.html',details=details)
    else:
        return redirect(url_for('alogin'))
@app.route('/oldcomplaint')
def oldcomplaint():
    if session.get('admin'):
        cursor=mysql.connection.cursor()
        cursor.execute('select * from complaint where status="resolved"')
        details=cursor.fetchall()
        return render_template('inprogress.html',details=details)
    else:
        return redirect(url_for('alogin'))
@app.route('/user')
def user():
    if session.get('user'):
        cursor=mysql.connection.cursor()
        cursor.execute('select * from complaint where username=%s',[session.get('user')])
        details=cursor.fetchall()
        return render_template('userstatus.html',details=details)

@app.route('/view/<id1>')
def view(id1):
    path = os.path.dirname(os.path.abspath(__file__))
    static_path = os.path.join(path, 'static')
    return send_from_directory(static_path, f'{id1}.jpg')

@app.route('/viewcontactus')
def contactusview():
    if session.get('admin'):
        cursor=mysql.connection.cursor()
        cursor.execute('select * from contactus order by date desc')
        data=cursor.fetchall()
        return render_template('viewcontactus.html',data=data)
    else:
        return redirect(url_for('login'))


app.run(use_reloader=True,debug=True)

