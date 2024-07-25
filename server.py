from flask import Flask , render_template
import mysql.connector
import datetime 

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
    # for index,i in enumerate(blogs_data):
    #     time_stamp = i[9]  
    #     dt_obj = datetime.fromtimestamp(time_stamp)
    #     i[10] = dt_obj.strftime("%d %B, %Y")
    #     # update the new blogs_data with the new timestamp
        
     
    return render_template('index.html',blogs_data=blogs_data)

if __name__ == "__main__":
    app.run(debug=True)
    