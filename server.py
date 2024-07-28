from flask import Flask, redirect, render_template,request
import mysql.connector
  
app = Flask(__name__) 
mysql_config = { 
    "host":"sql12.freesqldatabase.com",
    "user":"sql12722127",
    "password":"kKVN6xFhI9",
    "database":"sql12722127",
    "raise_on_warnings": True
}
@app.route("/")
def index():   
    with mysql.connector.connect(**mysql_config) as mydb:
        mycursor = mydb.cursor()
        mycursor.execute("SELECT * FROM blogs") 
        blogs_data = mycursor.fetchall() 
    return render_template('index.html', blogs_data=blogs_data)

@app.route('/api/login', methods=['GET'])
def api_login(): 
    username = request.args.get('username')
    password = request.args.get('password')
    if username is None or password is None:
        return {"message":"Username and Password are required","success":False}
    else:
        with mysql.connector.connect(**mysql_config) as mydb:
            mycursor = mydb.cursor()
            mycursor.execute(f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'")
            user_data = mycursor.fetchone()
            if user_data is None:
                return {"message":"Invalid Username or Password","success":False}
            else:
                return {"message":"Login Success","success":True}
            
@app.route("/login")
def login():
    return render_template('login.html')

@app.route("/signup")
def signup():
    return render_template('signup.html')
  
@app.route("/admin/login")
def admin_login(): 
    return render_template('admin/login.html')

@app.route("/admin/")
@app.route("/admin/index")
def admin(): 
    return render_template('admin/index.html')
 

@app.route("/blogs/<blog_url>")
def blog(blog_url): 
    try:  
        with mysql.connector.connect(**mysql_config) as mydb:
            mycursor = mydb.cursor() 
            mycursor.execute(f"SELECT * FROM blogs WHERE blog_url = '{blog_url}'")
            blog_data = mycursor.fetchone() 
        if blog_data is None:
            return redirect('/?error_code=blog_not_found')
        else:
            return render_template('blogs.html', blog_data=blog_data )
    except Exception as e:
        print(e) 
        return redirect('/?error_code=serverdown')


if __name__ == "__main__":
    app.run(debug=True)
