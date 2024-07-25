from flask import Flask, render_template
from mysql_db_config import get_db

mydb = get_db()
app = Flask(__name__)


@app.route("/")
def index(): 
    mycursor = mydb.cursor()   
    mycursor.execute("SELECT * FROM blogs") 
    blogs_data = mycursor.fetchall() 
    return render_template('index.html', blogs_data=blogs_data)


if __name__ == "__main__":
    app.run(debug=True)
