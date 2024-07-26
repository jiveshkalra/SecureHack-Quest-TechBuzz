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

@app.route("/login")
def login():
    return render_template('login.html')

@app.route("/signup")
def signup():
    return render_template('signup.html')

@app.route("/adminPageDontComeHereImWarningYou")
def adminPageDontComeHereImWarningYou():
    return render_template('admin.html')

@app.route("/adminPage", method=["POST"])
def adminPage():
    if request.form.passcode == "Priyanshu is the best coder!!!":
        return render_template("actualAdmin.html")
    else:
        return redirect('/adminPageDontComeHereImWarningYou')

@app.route("/blogs/<blog_url>")
def blog(blog_url): 
    mycursor = mydb.cursor()
    # SELECT * FROM `blogs` WHERE `blog_url` = "typography" 
    mycursor.execute(f"SELECT * FROM blogs WHERE blog_url = '{blog_url}'")
    blog_data = mycursor.fetchone()   
    return render_template('blogs.html', blog_data=blog_data ) 

if __name__ == "__main__":
    app.run(debug=True)
