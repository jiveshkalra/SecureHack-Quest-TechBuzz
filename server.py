from flask import Flask, redirect, render_template, request, jsonify
import mysql.connector
import uuid
import os
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

dotenv_path = find_dotenv()

load_dotenv(dotenv_path)

mysql_config = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
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

@app.route("/blogs/<blog_url>")
def blog(blog_url):
    try:
        with mysql.connector.connect(**mysql_config) as mydb:
            mycursor = mydb.cursor()
            mycursor.execute("SELECT * FROM blogs WHERE blog_url = %s", (blog_url,))
            blog_data = mycursor.fetchone()

            if blog_data is None:
                return redirect('/?error_code=blog_not_found')

            new_views = blog_data[9] + 1
            mycursor.execute("UPDATE blogs SET views = %s WHERE blog_url = %s", (new_views, blog_url))
            mydb.commit()

        return render_template('blogs.html', blog_data=blog_data)
    except Exception as e:
        app.logger.error(f"Error occurred: {str(e)}")
        return redirect('/?error_code=serverdown')

@app.route("/")
def index():
    with mysql.connector.connect(**mysql_config) as mydb:
        mycursor = mydb.cursor()
        mycursor.execute("SELECT * FROM blogs")
        blogs_data = mycursor.fetchall()
    return render_template('index.html', blogs_data=blogs_data)

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"message": "Email and Password are required", "success": False}), 400

    with mysql.connector.connect(**mysql_config) as mydb:
        mycursor = mydb.cursor()
        mycursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user_data = mycursor.fetchone()

        if user_data is None or not check_password_hash(user_data[4], password):
            return jsonify({"message": "Invalid Email or Password", "success": False}), 400

        return jsonify({"message": "Login Success", "success": True, "user_data": user_data}), 200

@app.route('/api/signup', methods=['POST'])
def api_signup():
    data = request.json
    email = data.get('email')
    name = data.get('name')
    password = data.get('password')

    if not all([email, name, password]):
        return jsonify({"message": "Name, Email, and Password are required", "success": False}), 400

    hashed_password = generate_password_hash(password)
    user_uuid = str(uuid.uuid4())

    with mysql.connector.connect(**mysql_config) as mydb:
        mycursor = mydb.cursor()
        mycursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        if mycursor.fetchone() is not None:
            return jsonify({"message": "Email Already Exists", "success": False}), 400

        query = "INSERT INTO users (username, uuid, email, password) VALUES (%s, %s, %s, %s)"
        mycursor.execute(query, (name, user_uuid, email, hashed_password))
        mydb.commit()

    return jsonify({"message": "Signup Success", "success": True, "uuid": user_uuid}), 200

@app.route('/api/create_blog', methods=['POST'])
def api_create_blog():
    data = request.json
    title = data.get('title')
    content = data.get('content')
    blog_url = data.get('blog_url')
    short_desc = data.get('short_desc')
    image_url = data.get('image_url')
    author_uuid = data.get('author_uuid')
    author_name = data.get('author_name')

    if not all([title, content, blog_url, short_desc, image_url, author_uuid, author_name]):
        return jsonify({"message": "All fields are required", "success": False}), 400

    with mysql.connector.connect(**mysql_config) as mydb:
        mycursor = mydb.cursor()
        query = ("INSERT INTO blogs (title, content, blog_url, short_desc, img_link, author_uuid, author_name) "
                 "VALUES (%s, %s, %s, %s, %s, %s, %s)")
        mycursor.execute(query, (title, content, blog_url, short_desc, image_url, author_uuid, author_name))
        mydb.commit()

    return jsonify({"message": "Blog Created Successfully", "success": True}), 200

@app.route('/api/admin/delete_blog', methods=['DELETE'])
def api_delete_blog():
    try:
        data = request.json
        blog_id = data.get('blog_id')

        if not blog_id:
            return jsonify({"message": "Blog ID is required", "success": False}), 400

        with mysql.connector.connect(**mysql_config) as mydb:
            mycursor = mydb.cursor()
            mycursor.execute("DELETE FROM blogs WHERE `s.no` = %s", (blog_id,))
            mydb.commit()

            if mycursor.rowcount == 0:
                return jsonify({"message": "Blog not found", "success": False}), 404

            return jsonify({"message": "Blog Deleted Successfully", "success": True}), 200
    except Exception as e:
        app.logger.error(f"Error occurred: {str(e)}")
        return jsonify({"message": "An error occurred", "success": False}), 500

@app.route('/api/admin/fetch_blog_data_per_sno', methods=['GET'])
def api_fetch_blog_data_per_sno():
    try:
        sno = request.args.get('sno')

        if not sno:
            return jsonify({"message": "S.no is required", "success": False}), 400

        with mysql.connector.connect(**mysql_config) as mydb:
            mycursor = mydb.cursor()
            mycursor.execute("SELECT * FROM blogs WHERE `s.no` = %s", (sno,))
            blog_data = mycursor.fetchone()

            if blog_data is None:
                return jsonify({"message": "Blog not found", "success": False}), 404

            return jsonify({"message": "Blog Data Fetched Successfully", "success": True, "blog_data": blog_data}), 200
    except Exception as e:
        app.logger.error(f"Error occurred: {str(e)}")
        return jsonify({"message": "An error occurred", "success": False}), 500

@app.route('/api/admin/update_blog', methods=['POST'])
def api_update_blog():
    try:
        data = request.json
        sno = data.get('sno')
        title = data.get('title')
        content = data.get('content')
        blog_url = data.get('blog_url')
        short_desc = data.get('short_desc')
        image_url = data.get('image_url')
        author_name = data.get('author_name')

        if not all([sno, title, content, blog_url, short_desc, image_url, author_name]):
            return jsonify({"message": "All fields are required", "success": False}), 400

        with mysql.connector.connect(**mysql_config) as mydb:
            mycursor = mydb.cursor()
            query = ("UPDATE blogs SET title = %s, content = %s, blog_url = %s, short_desc = %s, "
                     "img_link = %s, author_name = %s WHERE `s.no` = %s")
            mycursor.execute(query, (title, content, blog_url, short_desc, image_url, author_name, sno))
            mydb.commit()

            if mycursor.rowcount == 0:
                return jsonify({"message": "Blog not found or no changes made", "success": False}), 404

            return jsonify({"message": "Blog Updated Successfully", "success": True}), 200
    except Exception as e:
        app.logger.error(f"Error occurred: {str(e)}")
        return jsonify({"message": "An error occurred", "success": False}), 500

if __name__ == "__main__":
    app.run()
