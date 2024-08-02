from flask import Flask, redirect, render_template,request ,jsonify
import mysql.connector
import uuid

app = Flask(__name__) 
mysql_config = { 
    "host":"localhost",
    "user":" root",
    "password":"",
    "database":"secure_hack_quest",
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
    
    return render_template('admin/index.html',blogs_data=blogs_data)
 

@app.route("/blogs/<blog_url>")
def blog(blog_url): 
    try:  
        with mysql.connector.connect(**mysql_config) as mydb:
            mycursor = mydb.cursor() 
            mycursor.execute(f"SELECT * FROM blogs WHERE blog_url = '{blog_url}'")
            blog_data = mycursor.fetchone()  
            print(blog_data[9])
            new_views = blog_data[9] +1
            mycursor.execute(f"UPDATE `blogs` SET `views` = {new_views} WHERE blog_url = '{blog_url}'")
            mydb.commit()
            
        if blog_data is None:
            return redirect('/?error_code=blog_not_found')
        else:
            return render_template('blogs.html', blog_data=blog_data )
    except Exception as e:
        print(e) 
        return redirect('/?error_code=serverdown')
    
@app.route("/")
def index():   
    with mysql.connector.connect(**mysql_config) as mydb:
        mycursor = mydb.cursor()
        mycursor.execute("SELECT * FROM blogs") 
        blogs_data = mycursor.fetchall() 
    return render_template('index.html', blogs_data=blogs_data)

            
def compute_hash(string):
    p = 53
    m = 10**9 + 9
    hash_value = 0
    p_pow = 1
    for c in string:
        hash_value = (hash_value + ((ord(c) - ord('a')) + 1) * p_pow) % m
        p_pow = (p_pow * p) % m
    return hash_value

@app.route('/api/login', methods=['GET'])
def api_login(): 
    email = request.args.get('email')
    password = request.args.get('password')
    if email is None or password is None:
        return {"message":"Email and Password are required","success":False} , 400
    else:
        with mysql.connector.connect(**mysql_config) as mydb:
            mycursor = mydb.cursor() 
            password_hash = compute_hash(password)
            mycursor.execute(f"SELECT * FROM users WHERE email = '{email}' AND password_hash = '{password_hash}'")
            user_data = mycursor.fetchone()
            if user_data is None:
                return jsonify({"message":"Invalid Email or Password","success":False}) , 400
            else: 
                return jsonify({"message":"Login Success","success":True,"user_data":user_data}) , 200 

@app.route('/api/signup', methods=['GET'])
def api_signup():
    email = request.args.get('email')
    name = request.args.get('name')
    password = request.args.get('password') 
    if len(name) ==0 or len(email) == 0 or len(password) ==0:
        return {"message":"Name , Email and Password are required","success":False} , 400
    else:
        user_uuid = str(uuid.uuid4())
        with mysql.connector.connect(**mysql_config) as mydb:
            mycursor = mydb.cursor()
            mycursor.execute(f"SELECT * FROM `users` WHERE email = '{email}'")
            user_data = mycursor.fetchone()
            if user_data is not None:
                return jsonify({"message":"Email Already Exists","success":False}) , 400
            else:
                password_hash = compute_hash(password) 
                query = f"INSERT INTO `users` (`username`,`uuid`,`email`, `password_hash`) VALUES ('{name}','{user_uuid}','{email}', '{password_hash}')"  
                mycursor.execute(query)
                mydb.commit()
                
                return jsonify({"message":"Signup Success","success":True,"uuid":user_uuid}) ,200 
            

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
    if len(title) ==0 or len(content) == 0 or len(blog_url) ==0 or len(short_desc) ==0 or len(image_url) ==0 or len(author_uuid) ==0 or len(author_name) ==0:
        return jsonify({"message":"All fields are required","success":False}) , 400
    else:
        with mysql.connector.connect(**mysql_config) as mydb:
            mycursor = mydb.cursor()
            query = f"INSERT INTO `blogs` (`title`,`content`,`blog_url`, `short_desc`, `img_link`, `author_uuid`, `author_name`) VALUES ('{title}','{content}','{blog_url}', '{short_desc}', '{image_url}', '{author_uuid}', '{author_name}')"    
            mycursor.execute(query)
            mydb.commit()
            return jsonify({"message":"Blog Created Successfully","success":True}) ,200

@app.route('/api/admin/delete_blog', methods=['GET'])
def api_delete_blog():
    try:
        blog_id = request.args.get('blog_id')
        with mysql.connector.connect(**mysql_config) as mydb:
            mycursor = mydb.cursor()
            mycursor.execute(f"DELETE FROM blogs WHERE `s.no` = {blog_id}")
            mydb.commit()
            return jsonify({"message":"Blog Deleted Successfully","success":True}) ,200
    except Exception as e:
        return jsonify({"message":str(e),"success":False}) ,400

@app.route('/api/admin/fetch_blog_data_per_sno', methods=['GET'])
def api_fetch_blog_data_per_sno():
    try:
        sno = request.args.get('sno')
        with mysql.connector.connect(**mysql_config) as mydb:
            mycursor = mydb.cursor()
            mycursor.execute(f"SELECT * FROM blogs WHERE `s.no` = {sno}")
            blog_data = mycursor.fetchone()
            return jsonify({"message":"Blog Data Fetched Successfully","success":True,"blog_data":blog_data} ),200
    except Exception as e:
        return jsonify({"message":str(e),"success":False}) ,400
 
@app.route('/api/admin/update_blog', methods=['POST'])
def api_update_blog():
    sno = request.json.get('sno')
    title = request.json.get('title')
    content = request.json.get('content')
    blog_url = request.json.get('blog_url')
    short_desc = request.json.get('short_desc')
    image_url = request.json.get('image_url') 
    author_name = request.json.get('author_name')
    print(sno,title,content,blog_url,short_desc,image_url,author_name)
    try:
        with mysql.connector.connect(**mysql_config) as mydb:
            mycursor = mydb.cursor() 
            query = f"UPDATE `blogs` SET `title` = '{title}', `content` = '{content}', `blog_url` = '{blog_url}', `short_desc` = '{short_desc}', `img_link` = '{image_url}', `author_name` = '{author_name}' WHERE `s.no` = {sno}"
            mycursor.execute(query)
            mydb.commit()
            return jsonify({"message":"Blog Updated Successfully","success":True}) ,200
    except Exception as e:
        return jsonify({"message":str(e),"success":False}) ,400  



if __name__ == "__main__":
    app.run(debug=True)
