from flask import Flask, render_template
import mysql.connector

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="12345678",
    database="secure_hack"
)


app = Flask(__name__)


@app.route("/")
def index():

    mycursor = mydb.cursor()

    mycursor.execute("SELECT * FROM blogs")

    blogs_data = mycursor.fetchall()

    return render_template('index.html', blogs_data=blogs_data)


if __name__ == "__main__":
    app.run(debug=True)
