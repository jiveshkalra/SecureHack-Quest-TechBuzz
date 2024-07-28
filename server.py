from flask import Flask, redirect, render_template,request
from mysql_db_config import get_db 
 
mydb = get_db()
app = Flask(__name__) 
 
@app.route("/")
def index(): 
    mycursor = mydb.cursor()   
    mycursor.execute("SELECT * FROM blogs") 
    blogs_data = mycursor.fetchall() 
    return render_template('index.html', blogs_data=blogs_data)
  
@app.route("/admin/login")
def admin_login():
    # Sessions setup
    return render_template('admin/login.html')

@app.route("/admin/")
def admin(): 
    # Sessions setup
    return render_template('admin/index.html')


@app.route("/login")
def login():
    return render_template('login.html')

@app.route("/signup")
def signup():
    return render_template('signup.html')

@app.route("/adminPage")
def adminPage():
    return render_template('admin/login.html')

@app.route("/adminPageDontComeHereImWarningYou")
def adminPageDontComeHereImWarningYou():
    mycursor = mydb.cursor()   
    mycursor.execute("SELECT * FROM blogs") 
    blogs_data = mycursor.fetchall() 
    return render_template("admin/index.html", blogs_data=blogs_data)  

@app.route("/blogs/<blog_url>")
def blog(blog_url): 
    mycursor = mydb.cursor() 
    mycursor.execute(f"SELECT * FROM blogs WHERE blog_url = '{blog_url}'")
    blog_data = mycursor.fetchone()   
    return render_template('blogs.html', blog_data=blog_data ) 


if __name__ == "__main__":
    app.run(debug=True)
