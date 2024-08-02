from flask import Flask, redirect, render_template, request, jsonify, session
import mysql.connector
import uuid
import os
from dotenv import load_dotenv
import logging
from werkzeug.security import generate_password_hash, check_password_hash
from markupsafe import escape  # Updated for Cross-Site Scripting in blogs.html

app = Flask(__name__)

load_dotenv()

mysql_config = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
    "app.secret_key": os.getenv("SECRET_KEY"),
    "raise_on_warnings": True
}

logging.basicConfig(level=logging.ERROR, format='%(asctime)s %(levelname)s %(message)s')

@app.route("/login")
def login():
    return render_template('login.html')

@app.route("/create_blog")
def create_blog():
    return render_template('create_blog.html')

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

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

        # Updated for Cross-Site Scripting in blogs.html
        sanitized_blog_data = [escape(data) for data in blog_data]

        return render_template('blogs.html', blog_data=sanitized_blog_data)
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
    email = escape(request.form.get('email')) # Updated for Cross-Site Scripting in blogs.html
    password = request.form.get('password')

    if not email or not password:
        return jsonify({"message": "Email and Password are required", "success": False}), 400


    try:
        with mysql.connector.connect(**mysql_config) as mydb:
            mycursor = mydb.cursor()
            mycursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            user_data = mycursor.fetchone()
            if user_data is None or not check_password_hash(user_data[3], password):
                return jsonify({"message": "Invalid Email or Password", "success": False}), 400
            return jsonify({"message": "Login Success", "success": True, "user_data": user_data}), 200
    except Exception as e:
        logging.error("Error during login process: %s", e)
        return jsonify({"message": "An error occurred, please try again later", "success": False}), 500


@app.route('/api/signup', methods=['POST'])
def api_signup():
    email = escape(request.form.get('email')) # Updated for Cross-Site Scripting in blogs.html
    name = escape(request.form.get('name')) # Updated for Cross-Site Scripting in blogs.html
    password = request.form.get('password')

    if not name or not email or not password:
        return jsonify({"message": "Name, Email, and Password are required", "success": False}), 400

    try:
        user_uuid = str(uuid.uuid4())
        hashed_password = generate_password_hash(password)
        with mysql.connector.connect(**mysql_config) as mydb:
            mycursor = mydb.cursor()
            mycursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            user_data = mycursor.fetchone()
            if user_data:
                return jsonify({"message": "Email Already Exists", "success": False}), 400
            mycursor.execute("INSERT INTO users (username, uuid, email, password) VALUES (%s, %s, %s, %s)",
                             (name, user_uuid, email, hashed_password))
            mydb.commit()
            return jsonify({"message": "Signup Success", "success": True, "uuid": user_uuid}), 200
    except Exception as e:
        logging.error("Error during signup process: %s", e)
        return jsonify({"message": "An error occurred, please try again later", "success": False}), 500
    
@app.route('/api/create_blog', methods=['POST'])
def api_create_blog():
    data = request.json 
    # Updated for Cross-Site Scripting in blogs.html
    title = escape(data.get('title'))
    content = escape(data.get('content'))
    blog_url = escape(data.get('blog_url'))
    short_desc = escape(data.get('short_desc'))
    image_url = escape(data.get('image_url'))
    author_uuid = escape(data.get('author_uuid'))
    author_name = escape(data.get('author_name'))

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
        # Updated for Cross-Site Scripting in blogs.html
        sno = escape(data.get('sno'))
        title = escape(data.get('title'))
        content = escape(data.get('content'))
        blog_url = escape(data.get('blog_url'))
        short_desc = escape(data.get('short_desc'))
        image_url = escape(data.get('image_url'))
        author_name = escape(data.get('author_name'))

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
