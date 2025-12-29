import pymysql
import pymysql.cursors

import os

db_config = {
    'host': os.environ.get('mysql.railway.internal'),
    
    'user': os.environ.get('root'),
    'password': os.environ.get('OmMcoDBAXzZOrqMNwOwkSmDttpKXuZoY'),
    'database': os.environ.get('railway'),
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor,
}


def get_db_connection():    
    conn = pymysql.connect(**db_config)
    return conn
# def get_db_connection():    
#     conn = pymysql.connect(**db_config)
#     return conn

# def get_db_connection():    
#     conn = pymysql.connect(**db_config)
    
#     return conn
def db_init():
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS VERIFICATION
        (USER_ID INT AUTO_INCREMENT PRIMARY KEY,
        USER_NAME VARCHAR(30) NOT NULL,
        USER_EMAIL VARCHAR(50) NOT NULL UNIQUE,
        USER_PASSWORD VARCHAR(10) NOT NULL,
        USER_OTP VARCHAR(6) NOT NULL            
        ) '''
    ) 
    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS User
        (USER_ID INT AUTO_INCREMENT PRIMARY KEY,
        USER_NAME VARCHAR(30) NOT NULL,
        USER_EMAIL VARCHAR(50) NOT NULL UNIQUE,
        USER_PASSWORD VARCHAR(10) NOT NULL
        )
        '''

    ) 
    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS Notes
        (NOTES_ID INT AUTO_INCREMENT PRIMARY KEY,
        USER_ID INT NOT NULL,
        TITLE VARCHAR(30) NOT NULL,
        CONTENT VARCHAR(200) NOT NULL
        )'''
    )
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS Files
        (
        FILE_ID INT AUTO_INCREMENT PRIMARY KEY,
        USER_ID INT NOT NULL,
        FILE_NAME VARCHAR(100) NOT NULL,
        FILE_PATH VARCHAR(100) NOT NULL
        )'''
    )
    conn.commit()
    cursor.close()
    conn.close()
    
def db_verification_insert(name, email, password, otp):
    conn = get_db_connection()
    cursor = conn.cursor()  
    user_name = name
    user_email = email
    user_password = password
    user_otp = otp  
    cursor.execute(
        '''INSERT INTO VERIFICATION
        (user_name, user_email, user_password, user_otp)
        VALUES
        (%s, %s, %s, %s)
        ''', (user_name, user_email, user_password, user_otp)
    )    
    conn.commit()
    cursor.close()
    conn.close()
    
def db_verifyotp(email, otp):
    conn = get_db_connection()
    cursor = conn.cursor()    
    cursor.execute(
        '''SELECT USER_OTP FROM
           VERIFICATION
           WHERE USER_EMAIL = %s and USER_OTP = %s
        ''', (email, otp)
    )    
    res = cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()
    return bool(res)

def db_insert(email):
    conn = get_db_connection()
    cursor = conn.cursor()    
    cursor.execute('''
        INSERT INTO USER
        SELECT USER_ID, USER_NAME,USER_EMAIL, USER_PASSWORD
        FROM VERIFICATION
        WHERE USER_EMAIL = %s
        ''', (email,)
    )
    cursor.execute(
            '''DELETE FROM VERIFICATION
            WHERE USER_EMAIL = %s
            ''',(email,)
        )
    conn.commit()
    cursor.close()
    conn.close()
    
def db_login(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()    
    cursor.execute(
        '''SELECT * FROM User
        WHERE USER_NAME = %s and USER_PASSWORD = %s
        ''', (username, password)
    )    
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user

def db_checkuser(email):
    conn = get_db_connection()
    cursor = conn.cursor()    
    cursor.execute(
        '''SELECT * FROM USER 
        WHERE USER_EMAIL=%s''',(email,)

    )
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user
def db_updatepassword(email,new_password):
    conn = get_db_connection()
    cursor = conn.cursor()    
    cursor.execute(
        '''UPDATE user set user_password=%s where user_email=%s 
        ''',(new_password,email)
    )
    conn.commit()
    cursor.close()
    conn.close()


def db_notesinsert(user_id,title,content):
    conn = get_db_connection()
    cursor = conn.cursor()    
    cursor.execute('''
        INSERT INTO Notes
        (USER_ID, title,content)
        values
        (%s,%s,%s)
        ''', (user_id,title,content)
    )
    conn.commit()
    cursor.close()
    conn.close()

def db_viewnotes(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()    
    cursor.execute(
        '''SELECT * FROM Notes 
        WHERE user_id=%s''',(user_id)
    )
    user = cursor.fetchall()
    cursor.close()
    conn.close()
    return user


def db_deletenote(nid):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''DELETE FROM Notes
        WHERE NOTES_ID = %s
        ''', (nid,)
    )
    conn.commit()
    cursor.close()
    conn.close()


def db_getnote(nid):
    conn = get_db_connection()
    cursor = conn.cursor()    
    cursor.execute(
        '''SELECT TITLE,CONTENT FROM  Notes 
        WHERE NOTES_ID=%s''',(nid)
    )
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user

def db_updatenote(title,content,nid):
    conn = get_db_connection()
    cursor = conn.cursor()    
    cursor.execute(
        '''UPDATE notes set TITLE=%s,CONTENT=%s WHERE NOTES_ID=%s 
        ''',(title,content,nid)
    )
    conn.commit()
    cursor.close()
    conn.close()

def db_insertfile(user_id,file_name,file_path):
    conn = get_db_connection()
    cursor = conn.cursor()    
    cursor.execute(
        '''INSERT INTO Files
        (USER_ID,FILE_NAME,FILE_PATH)VALUES
        (%s,%s,%s)
    ''',(user_id,file_name,file_path)
    )
    conn.commit()
    cursor.close()
    conn.close()
def db_viewfiles(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()    
    cursor.execute(
        ''' SELECT * FROM Files
        WHERE USER_ID=%s''',(user_id,)
    )
    user = cursor.fetchall()
    cursor.close()
    conn.close()
    return user


def db_getfile(fid):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''
        SELECT * FROM Files
        WHERE FILE_ID = %s
        ''', (fid,)
    )
    file = cursor.fetchone()
    cursor.close()
    conn.close()
    return file

def db_deletefile(fid):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''DELETE FROM Files 
        WHERE FILE_ID = %s
        ''', (fid,)
    )
    conn.commit()
    cursor.close()
    conn.close()
    
def db_search(query, user_id):    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''SELECT * FROM 
        Notes WHERE 
        (TITLE LIKE %s) 
        AND 
        USER_ID = %s
        ''',(f'%{query}%',user_id)
    )    
    notes = cursor.fetchall()
    cursor.close()
    conn.close()
    return notes
