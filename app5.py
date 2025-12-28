

admin_email="srinivasuluch796@gmail.com"
admin_password="xhgi irfx pkld olms"
from flask import Flask, render_template, request, redirect, url_for,session,send_file,Response
import smtplib
from email.message import EmailMessage
import random
import re
import os


from Database import (db_init, db_verification_insert, 
                      db_verifyotp, db_insert, db_login,db_checkuser,
                      db_updatepassword,db_notesinsert,db_viewnotes,db_deletenote,
                      db_getnote,db_updatenote,db_insertfile,db_viewfiles,db_deletefile
                      ,db_getfile,db_search)
from itsdangerous import URLSafeTimedSerializer

app = Flask(__name__)

app.secret_key="sri"
serializer=URLSafeTimedSerializer(secret_key="sri")
admin_email="srinivasuluch796@gmail.com"
admin_password="xhgi irfx pkld olms"
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Use Render's port or fallback to 5000
    app.run(host="0.0.0.0", port=port, debug=True)

def send_mail(to_email, body):    
    msg = EmailMessage()
    msg.set_content(body)
    msg['To'] = to_email
    msg['From'] = admin_email
    msg['Subject'] = 'OTP verification'
    
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(admin_email, admin_password)
        smtp.send_message(msg)
app.config["UPLOAD_FOLDER"]="uploads"
os.makedirs(app.config["UPLOAD_FOLDER"],exist_ok=True)    
   
@app.route('/')
def home():
    session.clear()  
    return render_template('home.html')

@app.route('/register', methods = ['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not re.match(r'^[\w\.-]+@[\w]+\.[\w]+$', email):
            message = 'Invalid Email'
            message_type = 'error'
            return render_template('register.html', message = message, message_type = message_type)
        
        elif not ((5 <= len(password) <= 8) and (password[0].isupper()) and (not password.isalnum())):
            message = '''Password should have a min of 5 and max of 8 characters.
            First character should be upper case. There should be atleast one 
            character other than alphabets and numbers.            
                      '''
            message_type = 'error'
            return render_template('register.html', message = message, message_type = message_type)
        elif db_checkuser(email):
            message='Email already exists'
            message_type='error'
            return render_template('login.html',message = message, message_type=message_type)
        otp = str(random.randint(100000, 999999))
        body = f'Your OTP for verification is {otp}'
        send_mail(email, body)
        db_verification_insert(username, email, password, otp)
        return redirect(url_for('verify_otp', email = email))
    return render_template('register.html')

@app.route('/verify_otp/<email>',methods = ['POST', 'GET'])
def verify_otp(email):
    message = ''
    msg_type = ''
    
    if request.method == 'POST':
        otp = request.form.get('otp')
        status = db_verifyotp(email,otp)
        if status:
            db_insert(email)
            return redirect(url_for('login'))
        else:
            message = 'Invalid OTP'
            msg_type = 'error' 
               
    return render_template('verify_otp.html',email = email, message = message, message_type = msg_type)

@app.route('/login', methods = ['POST', 'GET'])
def login():
    message = ''
    message_type = ''
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = db_login(username, password)
        # user_id=user["USER_ID"]
        if user:
            user_id=user["USER_ID"]
            session["user_id"]=user_id
            session["username"]=username
            # return redirect(url_for("dashboard"))
            return render_template("dashboard.html")
        else:
            message = 'Invalid credentials'
            message_type = 'error'        
            return render_template('login.html', message = message, message_type = message_type)
    return render_template("login.html")
@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        return render_template('dashboard.html')
    return redirect(url_for('login')) 



@app.route('/forgot_password',methods=['GET','POST'])
def forgot_password():
    if request.method == 'POST':
        email=request.form.get("email")
        if db_checkuser(email):
            token=serializer.dumps(email,salt="password_reset")
            reset_url=url_for("reset_password",token=token,_external=True)
            body=f"please click on the link to reset:{reset_url}"
            send_mail(email,body)
            msg="email sent"
            msg_type="success"
            return render_template("login.html",message=msg,message_type=msg_type)
        else:
            message = 'Not a registered user'
            msg_type = 'error' 
            return render_template('register.html',email = email, message = message, message_type = msg_type)
    return render_template('forgot_password.html')
@app.route('/reset_password/<token>',methods=['GET','POST'])
def reset_password(token):
    email=serializer.loads(token,salt="password_reset")
    if request.method=='POST':
        new_password=request.form.get("password")
        db_updatepassword(email,new_password)
        msg="updated successfully"
        msg_type="success"
        return render_template('login.html', message = msg, message_type = msg_type)
    return render_template("reset_password.html",token=token)


@app.route('/add_note',methods=['GET','POST'])
def add_note():
    if request.method=='POST':
        title=request.form.get("title")
        content=request.form.get("content")
        user_id=session.get("user_id")
        db_notesinsert(user_id,title,content)
        return redirect(url_for("view_notes"))
    return render_template("add_note.html")
@app.route('/view_notes')
def view_notes():
    user_id=session['user_id']
    notes=db_viewnotes(user_id)
    
    return render_template("view_notes.html",notes=notes)

@app.route("/view_note/<nid>")
def view_note(nid):
    note=db_getnote(nid)
    
    return render_template("view_note.html",note=note)


@app.route("/update_note/<nid>", methods=["GET", "POST"])
def update_note(nid):
    note = db_getnote(nid)  # only TITLE, CONTENT

    if request.method == "POST":
        title = request.form.get("title")
        content = request.form.get("content")
        db_updatenote(title, content, nid)
        return render_template("update_note.html",note=note,nid=nid,message='success',message_type='success')

    # explicitly pass nid so template can use it
    return render_template("update_note.html", note=note, nid=nid)


@app.route("/delete_note/<nid>")
def delete_note(nid):  
    db_deletenote(nid)      
    return redirect(url_for('view_notes'))





@app.route('/upload_file',methods=['POST','GET'])
def upload_file():
    if request.method=='POST':
        file=request.files.get('file')
        file_name=file.filename
        file_path=os.path.join(app.config['UPLOAD_FOLDER'],file_name)
        file.save(file_path)
        user_id=session["user_id"]
        db_insertfile(user_id,file_name,file_path)
        return redirect(url_for("view_files"))
    return render_template("upload.html")

@app.route('/view_files')
def view_files():
    user_id=session["user_id"]
    files=db_viewfiles(user_id)
    
    return render_template("view_files.html",files=files)

@app.route('/view_file/<fid>')
def view_file(fid):
    file = db_getfile(fid)
    file_path = file['FILE_PATH']
    return send_file(file_path, as_attachment = False)

@app.route('/dowload_file/<fid>')
def download_file(fid):
    file = db_getfile(fid)
    file_path = file['FILE_PATH']
    return send_file(file_path, as_attachment = True)

@app.route('/delete_file/<fid>')
def delete_file(fid):
    file = db_getfile(fid)
    file_path = file['FILE_PATH']
    os.remove(file_path)
    db_deletefile(fid)
    return redirect(url_for('view_files'))



@app.route('/search', methods = ['POST', 'GET'])
def search():
    if request.method == 'POST':
        query = request.form.get('query')
        user_id = session['user_id']
        notes = db_search(query,user_id)
        return render_template('search.html', notes = notes)
    return render_template('search.html')


@app.route('/export_notes')
def export_notes():
    user_id = session["user_id"]
    notes = db_viewnotes(user_id)   # function should return list of dicts

    if not notes:
        return "No notes to export."

    # Build text content
    export_content = "Your Notes Export\n\n"
    for note in notes:
        export_content += f"Title: {note['TITLE']}\n"
        export_content += f"Content: {note['CONTENT']}\n"
        export_content += "-" * 60 + "\n"

    return Response(
        export_content,
        mimetype="text/plain",
        headers={"Content-Disposition": "attachment;filename=notes_export.txt"}
    )


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for("home"))


# app.run(debug = True)