import mysql.connector
from datetime import datetime

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="12345678",  
  database="secure_hack"
)
 
#  INSERT INTO `blogs` (` `title`, `short description`, `content`, `author_id`, `author_name`, `comments_id`, `img_link`, `blog_url`, `timestamp`) VALUES  (title,short_desc,content,author_id, author_name,comments_id,img_link, blog_url, current_timestamp());

mycursor = mydb.cursor()

mycursor.execute("SELECT * FROM blogs") 
myresult = mycursor.fetchall()

for i in myresult:
    print(i[9]) 
 