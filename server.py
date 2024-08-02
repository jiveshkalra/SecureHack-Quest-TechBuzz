from flask import Flask, redirect, render_template,request ,jsonify
from voluptuous import Schema, Required
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

@app.route('/api/login', methods=['GET'])
def api_login(): 
    email = request.args.get('email')
    password = request.args.get('password')
    if email is None or password is None:
        return {"message":"Email and Password are required","success":False} , 400
    else:
        with mysql.connector.connect(**mysql_config) as mydb:
            mycursor = mydb.cursor() 
            mycursor.execute(f"SELECT * FROM users WHERE email = '{email}' AND password = '{password}'")
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
                query = f"INSERT INTO `users` (`username`,`uuid`,`email`, `password`) VALUES ('{name}','{user_uuid}','{email}', '{password}')"  
                mycursor.execute(query)
                mydb.commit()
                
                return jsonify({"message":"Signup Success","success":True,"uuid":user_uuid}) ,200 
            

@app.route('/api/create_blog', methods=['POST'])
def api_create_blog():  
    blog_schema = Schema({
        Required('title'): All(str, Length(min=1)),
        Required('content'): All(str, Length(min=1)),
        Required('blog_url'): All(str, Length(min=1)),
        Required('short_desc'): All(str, Length(min=1)),
        Required('image_url'): All(str, Length(min=1)),
        Required('author_uuid'): All(str, Length(min=1)),
        Required('author_name'): All(str, Length(min=1))
    })

    try:
        data = request.json
        validated_data = blog_schema(data)
        title = validated_data['title']
        content = validated_data['content']
        blog_url = validated_data['blog_url']
        short_desc = validated_data['short_desc']
        image_url = validated_data['image_url']
        author_uuid = validated_data['author_uuid']
        author_name = validated_data['author_name']
    except Exception as e:
        return jsonify({"message": str(e), "success": False}), 400

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
    blog_schema = Schema({
        Required('sno'): All(int),
        Required('title'): All(str, Length(min=1)),
        Required('content'): All(str, Length(min=1)),
        Required('blog_url'): All(str, Length(min=1)),
        Required('short_desc'): All(str, Length(min=1)),
        Required('image_url'): All(str, Length(min=1)),
        Required('author_name'): All(str, Length(min=1))
    })

    try:
        data = request.json
        validated_data = blog_schema(data)
        sno = validated_data['sno']
        title = validated_data['title']
        content = validated_data['content']
        blog_url = validated_data['blog_url']
        short_desc = validated_data['short_desc']
        image_url = validated_data['image_url']
        author_name = validated_data['author_name']
    except Exception as e:
        return jsonify({"message": str(e), "success": False}), 400

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
