import os
import uuid
import logging
from flask import Flask, redirect, render_template, request, jsonify
import mysql.connector
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
csrf = CSRFProtect()
csrf.init_app(app)
logging.basicConfig(level=logging.ERROR)
mysql_config = { 
    "host": os.environ.get('DB_Host', 'sql12.freesqldatabase.com'),
    "user": os.environ.get('DB_User', 'sql12722127'),
    "password": os.environ.get('DB_Pass', 'kKVN6xFhI9'),
    "database": os.environ.get('DB_Name', 'sql12722127'),
    "raise_on_warnings": True
}

@app.route("/login")
def login():
    return render_template('login.html')

@app.route("/create_blog")
def create_blog():
    return render_template('create_blog.html')

@app.route("/logout")
def logout():
    return render_template('logout.html')

@app.route("/signup")
def signup():
    return render_template('signup.html')
  
@app.route("/admin/login")
def admin_login():
    return render_template('admin/login.html')

@app.route("/admin/")
@app.route("/admin/index")
def admin():
    with mysql.connector.connect(**mysql_config) as mydb:
        mycursor = mydb.cursor()
        mycursor.execute("SELECT * FROM blogs") 
        blogs_data = mycursor.fetchall()
    
    return render_template('admin/index.html', blogs_data=blogs_data)

@app.route('/error')
def error_page():
    return render_template('error.html')

@app.route("/blogs/<blog_url>")
def blog(blog_url):
    try:
        with mysql.connector.connect(**mysql_config) as mydb:
            mycursor = mydb.cursor() 
            mycursor.execute(f"SELECT * FROM blogs WHERE blog_url = '{blog_url}'")
            blog_data = mycursor.fetchone()  
            new_views = blog_data[9] +1
            mycursor.execute(f"UPDATE `blogs` SET `views` = {new_views} WHERE blog_url = '{blog_url}'")
            mydb.commit()
        return render_template('blog.html', blog_data=blog_data)
    except Exception as e:
        logging.error(f"Error: {e}")
        return redirect('/error?code=serverdown')

@app.route("/")
def index():
    try:
        with mysql.connector.connect(**mysql_config) as mydb:
            mycursor = mydb.cursor()
            mycursor.execute("SELECT * FROM blogs")
            blogs_data = mycursor.fetchall()
        return render_template('index.html', blogs_data=blogs_data)
    except Exception as e:
        logging.error(f"Error fetching blogs: {e}")
        return redirect('/error?code=serverdown')

@app.route('/api/login', methods=['POST'])
def api_login():
    email = request.form.get('email')
    password = request.form.get('password')
    if email is None or password is None:
        return {"message": "Email and Password are required", "success": False}, 400
    try:
        with mysql.connector.connect(**mysql_config) as mydb:
            mycursor = mydb.cursor()
            mycursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            user_data = mycursor.fetchone()
            if user_data and check_password_hash(user_data[2], password):
                return jsonify({"message": "Login Success", "success": True, "user_data": user_data}), 200
            else:
                return jsonify({"message": "Invalid Email or Password", "success": False}), 400
    except Exception as e:
        logging.error(f"Error during login: {e}")
        return jsonify({"message": "Server error", "success": False}), 500

@app.route('/api/signup', methods=['GET'])
def api_signup():
    email = request.args.get('email')
    name = request.args.get('name')
    password = request.args.get('password')
    if not all([email, name, password]):
        return {"message": "Name, Email, and Password are required", "success": False}, 400
    else:
        user_uuid = str(uuid.uuid4())
        with mysql.connector.connect(**mysql_config) as mydb:
            mycursor = mydb.cursor()
            mycursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            user_data = mycursor.fetchone()
            if user_data:
                return jsonify({"message": "Email Already Exists", "success": False}), 400
            else:
                query = "INSERT INTO users (username, uuid, email, password) VALUES (%s, %s, %s, %s)"
                mycursor.execute(query, (name, user_uuid, email, generate_password_hash(password)))
                mydb.commit()
                return jsonify({"message": "Signup Success", "success": True, "uuid": user_uuid}), 200

@app.route('/api/create_blog', methods=['POST'])
def api_create_blog():
    data = request.json
    required_fields = ['title', 'content', 'blog_url', 'short_desc', 'image_url', 'author_uuid', 'author_name']

    if not all([data.get(field) for field in required_fields]):
        return jsonify({"message": "All fields are required", "success": False}), 400
    else:
        with mysql.connector.connect(**mysql_config) as mydb:
            mycursor = mydb.cursor()
            query = "INSERT INTO `blogs` (`title`, `content`, `blog_url`, `short_desc`, `img_link`, `author_uuid`, `author_name`) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            mycursor.execute(query, (data['title'], data['content'], data['blog_url'], data['short_desc'], data['image_url'], data['author_uuid'], data['author_name']))
            mydb.commit()
            return jsonify({"message": "Blog Created Successfully", "success": True}), 200

@app.route('/api/admin/delete_blog', methods=['GET'])
def api_delete_blog():
    try:
        blog_id = request.args.get('blog_id')
        if not blog_id:
            return jsonify({'message': "Blog ID is required", "success": False}), 400
        with mysql.connector.connect(**mysql_config) as mydb:
            mycursor = mydb.cursor()
            mycursor.execute("DELETE FROM blogs WHERE `s.no` = %s", (blog_id,))
            mydb.commit()
            if mycursor.rowcount == 0:
                return jsonify({'message': 'Blog ID not Found', "success": False}), 404
            return jsonify({"message": "Blog Deleted Successfully", "success": True}), 200
    except Exception as e:
        return jsonify({"message": str(e), "success": False}), 400

@app.route('/api/admin/fetch_blog_data_per_sno', methods=['GET'])
def api_fetch_blog_data_per_sno():
    try:
        sno = request.args.get('sno')
        with mysql.connector.connect(**mysql_config) as mydb:
            mycursor = mydb.cursor()
            mycursor.execute("SELECT * FROM blogs WHERE `s.no` = %s", (sno,))
            blog_data = mycursor.fetchone()
            return jsonify({"message": "Blog Data Fetched Successfully", "success": True, "blog_data": blog_data}), 200
    except Exception as e:
        return jsonify({"message": str(e), "success": False}), 400
 
@app.route('/api/admin/update_blog', methods=['POST'])
def api_update_blog():
    data =request.json
    required_fields = ['sno','title','content','blog_url','short_desc','image_url','author_name']
    if not all([data.get(field) for field in required_fields]):
        return jsonify({"message": "All friends are required", "success": False}), 400
    try:
        with mysql.connector.connect(**mysql_config) as mydb:
            mycursor = mydb.cursor() 
            query = "UPDATE blogs SET title = %s, content = %s, blog_url = %s, short_desc = %s, img_link = %s, author_name = %s WHERE `s.no` = %s"
            mycursor.execute(query, (data['title'], data['content'], data['short_desc'], data['image_url'], data['author_name'], data['sno']))
            mydb.commit()
            return jsonify({"message":"Blog Updated Successfully","success":True}) ,200
    except Exception as e:
        return jsonify({"message":str(e),"success":False}) ,400  



if __name__ == "__main__":
    app.run(debug=True)
