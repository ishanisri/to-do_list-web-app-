from flask import render_template,redirect, request, flash,g,session,url_for,Flask

import sqlite3 as sql
from werkzeug import generate_password_hash, check_password_hash


app = Flask(__name__)
app.secret_key="why would i tell my secret key?"


from flask import g

DATABASE = '/path/to/database.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sql.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()




@app.route("/")
def main():
    return render_template('index.html')
@app.route('/showSignUp')
def showSignUp():
    return render_template('signup.html') 
@app.route('/showSignIn')
def showSignIn():
    return render_template('signin.html') 

@app.route('/showCreateNotes')
def showCreateNotes():
    return render_template('createNotes.html') 
   

@app.route('/signUp',methods=['GET','POST'])
def signedUp():
    if(request.method=='POST'):
        username= request.form.get('inputName')
        email = request.form.get('inputEmail')
        password=request.form.get('inputPassword')
        
        print(username+" "+email+" "+password)
        hashed_password = generate_password_hash(password)
        
        print("hi")	
        
        with sql.connect("database.db") as con:
            cur = con.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS account_holder( user_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,user_email TEXT DEFAULT NULL,username TEXT DEFAULT NULL,password TEXT DEFAULT NULL)")
            cur.execute("INSERT INTO account_holder (user_email,username,password) VALUES (?,?,?)", (email,username,password))
            
            
            
            
            cur.execute("SELECT user_id FROM account_holder where username=?",(username,))
            data=cur.fetchall()
            print(data)
            con.commit()

        
        session['user']=username

        
 
           
    return redirect('/userHome') 
      
@app.route('/userHome')
def userHome():
	if session.get('user'):
	    conn = sql.connect("database.db")
	    cursor = conn.cursor()
	    _user=session.get('user')
	    cursor.execute("SELECT * FROM NOTES where notes_username=(?)",(_user,))
	    result = cursor.fetchall()
	    print(result)
	    result_dict=[]

	    i=1
	    for data in result:
	        data_dict= {
	                    'No':i,
	                    'Title':data[2],
	                    'Description':data[3]}
                     
	        result_dict.append(data_dict)
	        i=i+1

	            #if len(data) is 0:
	    cursor.execute("SELECT * FROM toDoList where username=?",(_user,))
           
	    List=cursor.fetchall()
	    print(List)

	    conn.commit()
            #toDoList = cursor.fetchall()
	     
	    lists_dict = []
	    j=1
	    for work in List:
	        list_dict = {
	                'id':j,
	                'checked':work[3], 
	                'Task': work[2]}
	        if((request.args.get(work[2])=='on') or (list_dict['checked']=='on')):
	                 list_dict['checked']='on' 
	                 print(list_dict.get('id'))
	                 cursor.execute("UPDATE toDoList SET checked='on' WHERE task=? ",(work[2],))
	                 conn.commit()
	        else:
	                 cursor.execute("UPDATE toDoList SET checked=0 where task=?",(work[2],)) 
	                 conn.commit()              
     #   'Date': work[4]}

	        lists_dict.append(list_dict)

	        j=j+1
	    print(lists_dict)
	    return render_template('userHome.html',result_dict=result_dict,lists_dict=lists_dict)
	else:
	    return render_template('error.html',error = 'Unauthorized Access')



@app.route('/logout')
def logout():
    session.pop('user',None)
    return redirect('/')

@app.route('/getList')
def getList():
	
    try:
        if session.get('user'):
            _user = session.get('user')
 
            print(request.form.getList('input'))
 
            return redirect('/userHome')
        else:
            return render_template('error.html', error = 'Unauthorized Access')
    except Exception as e:
        return render_template('error.html', error = str(e))






  
@app.route('/createNotes',methods=['GET','POST'])
def addWish():
    if(request.method=='POST'):
	    conn = sql.connect("database.db")
	    cursor = conn.cursor()
	    print(session.get('user'))
	    try:
	        if session.get('user'):
	            _title = request.form['inputTitle']
	            _description = request.form['inputDescription']
	            _user = session.get('user')
	            print(_user)
	 
	            
	            cursor.execute("CREATE TABLE IF NOT EXISTS NOTES(notes_id INTEGER  NOT NULL PRIMARY KEY AUTOINCREMENT,notes_username TEXT  ,title TEXT DEFAULT NULL,description TEXT DEFAULT NULL)")
	            cursor.execute("INSERT INTO NOTES(title,description,notes_username) VALUES(?,?,?)",(_title,_description,_user))
	            

	            #if len(data) is 0:
	            conn.commit()
	            print("user in session"+_user)
	            
	            
	           # else:
	            #    return render_template('error.html',error = 'An error occurred!')
	 
	        
	           
	        else:
	           return render_template('error.html',error = 'An error occurred!')
	    except Exception as e:
	        return render_template('error.html',error = str(e))
	    finally:
	        cursor.close()
	        conn.close()       
    return redirect('/userHome')  



@app.route('/validateLogin',methods=['GET','POST'])
def validateLogin():
	if(request.method=='POST'):
	    con = sql.connect("database.db")
	    cur=con.cursor()
	    
	    try:
	        
	        username = request.form['inputName']
	        password = request.form['inputPassword']
	        cur.execute("SELECT * FROM account_holder where username=?",(username,))

	        data = cur.fetchall()
	        print(data)
	        if len(data) > 0:
	            if check_password_hash(str(data[0][3]),password):
	                session['user'] = data[0][2]
	                
	            else:
	                return render_template('error.html',error = 'Wrong Email address or Password.')
	        else:
	            return render_template('error.html',error = 'Wrong Email address or Password!!!!')                  

	 
	    except Exception as e:
	        return render_template('error.html',error = str(e))
	    finally:
	        cur.close()
	        con.close()
	return redirect('/userHome')  


@app.route('/toDoList',methods=['POST','GET'])
def toDo():

  if(request.method=='POST'):
   
    try:
        if session.get('user'):
            _user = session.get('user')
            task=request.form['toDo']

            con = sql.connect("database.db")
            cursor = con.cursor()
            
   
            cursor.execute("CREATE TABLE IF NOT EXISTS toDoList (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,username TEXT DEFAULT NULL,task TEXT DEFAULT NULL,checked  TEXT DEFAULT NULL)")
            print("hi")
            cursor.execute("INSERT INTO toDoList (task,username) VALUES(?,?)",(task,_user))
            print("hello")
            con.commit()


            #selected_users = request.form.getlist('toDo')
            
        else:
            return render_template('error.html', error = 'Unauthorized Access')
    except Exception as e:
        return render_template('error.html', error = str(e))
  return redirect('/userHome')



@app.route('/getList')
def getCheckedList():
	
	return redirect('/userHome')  

if __name__ == "__main__":
     app.run(debug=True)  											