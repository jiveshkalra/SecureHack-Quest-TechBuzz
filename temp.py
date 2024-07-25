from mysql_db_config import get_db

mydb = get_db()
#  INSERT INTO `blogs` (` `title`, `short description`, `content`, `author_id`, `author_name`, `img_link`, `blog_url`, `timestamp`) VALUES  (title,short_desc,content,author_id, author_name,comments_id,img_link, blog_url, current_timestamp());

mycursor = mydb.cursor()

blog_url = 'typography'
mycursor.execute(f"SELECT * FROM blogs WHERE blog_url = '{blog_url}'")
blog_data = mycursor.fetchone()
print(blog_data[0]) # Sno
print(blog_data[1]) # Title 
print(blog_data[2]) # Short Description
print(blog_data[3]) # Content
print(blog_data[4]) # Author ID
print(blog_data[5]) # Author Name
print(blog_data[6]) # img_link
print(blog_data[7]) # blog_url
print(blog_data[8]) # timestamp