# from datetime import datetime
# from werkzeug.utils import secure_filename
# import os
# from flask import Flask, render_template, request, redirect, url_for, session
# from flask_pymongo import PyMongo
# from gridfs import GridFS
# from bson.objectid import ObjectId

# app = Flask(__name__)
# app.secret_key = 'your_secret_key'

# # Configure MongoDB URI
# app.config['MONGO_URI'] = 'mongodb://localhost:27017/your_database_name'

# mongo = PyMongo(app)
# grid_fs = GridFS(mongo.db)

# @app.route('/')
# def index():
#     posts = mongo.db.posts.find()
#     return render_template('index.html', posts=posts)

# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     if 'email' in session:
#         # If user is already logged in, redirect to dashboard
#         return redirect(url_for('dashboard'))

#     elif request.method == 'POST':
        
#         fullname = request.form['fullname']
#         email = request.form['email']
#         rollno = request.form['rollno']
#         course = request.form['course']
#         branch = request.form['branch']
#         passout_year = request.form['passout_year']
#         country_code = request.form['country_code']
#         phone = request.form['phone']
#         password = request.form['password']

#         # Insert data into MongoDB
#         mongo.db.users.insert_one({
#             'fullname': fullname,
#             'email': email,
#             'rollno': rollno,
#             'course': course,
#             'branch': branch,
#             'passout_year': passout_year,
#             'country_code': country_code,
#             'phone': phone,
#             'password': password
#         })

#         # Redirect to homepage or login page
#         return redirect(url_for('index'))

#     return render_template('register.html')

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if 'email' in session:
#         # If user is already logged in, redirect to dashboard
#         return redirect(url_for('dashboard'))

#     if request.method == 'POST':
#         email = request.form['email']
#         password = request.form['password']

#         user = mongo.db.users.find_one({'email': email, 'password': password})

#         if user:
#             # Set session variables
#             session['email'] = email
#             session['fullname'] = user['fullname']
#             # Redirect to dashboard
#             return redirect(url_for('dashboard'))
#         else:
#             # Login failed, redirect back to login page with an error message
#             return render_template('login.html', error='Invalid email or password.')

#     return render_template('login.html')

# @app.route('/dashboard')
# def dashboard():
#     if 'email' in session:
#         return render_template('index.html', fullname=session['fullname'])
#     else:
#         return redirect(url_for('login'))

# @app.route('/logout')
# def logout():
#     # Clear the session variables
#     session.pop('email', None)
#     session.pop('fullname', None)
#     # Redirect to the login page
#     return redirect(url_for('login'))

# @app.route('/sell', methods=['GET', 'POST'])
# def sell():
#     if request.method == 'POST':
#         # Get form data
#         description = request.form['description']
#         image_file = request.files['product-image']

#         # Check if the file is uploaded
#         if image_file:
#             # Store the image file in GridFS
#             image_id = grid_fs.put(image_file, filename=image_file.filename)

#             # Insert data into MongoDB
#             mongo.db.posts.insert_one({
#                 'description': description,
#                 'image_id': image_id,
#                 'datetime': datetime.now()
#             })

#             # Redirect to homepage or any other page
#             return redirect(url_for('index'))

#     return render_template('sell.html')

# @app.route('/buy/<post_id>')
# def buy(post_id):
#     if 'email' not in session:
#         # Redirect to login page if the user is not logged in
#         return redirect(url_for('login'))
    
#     # Fetch the post details from MongoDB
#     post = mongo.db.posts.find_one({'_id': ObjectId(post_id)})
#     if post:
#         return render_template('buy.html', post=post)
#     else:
#         return 'Post not found', 404









# @app.route('/profile')
# def profile():
#     return render_template('profile.html')
# if __name__ == '__main__':
#     app.run(debug=True)


# -----------------------------------------------------------------------------------------------------------
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
from bson.objectid import ObjectId
import os
import uuid
from flask_pymongo import PyMongo, GridFS

UPLOAD_FOLDER = 'static/uploads'  # Folder to store uploaded images
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}  # Allowed image file extensions

app = Flask(__name__)
app.secret_key = "hello"

# Configure the upload folder
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config["MONGO_URI"] = "mongodb://localhost:27017/myDatabase"
mongo = PyMongo(app)
fs = GridFS(mongo.db)

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_unique_filename(filename):
    ext = filename.rsplit('.', 1)[1]
    unique_filename = f"{uuid.uuid4().hex}.{ext}"
    return unique_filename

def login_check(email, password):
    return mongo.db.users.find_one({"email": email, "password": password})

def model(name, email, rollno, course, branch, passoutYear, phone, password):
    mongo.db.users.insert_one({
        'fullname': name,
        'email': email,
        'rollno': rollno,
        'course': course,
        'branch': branch,
        'passout_year': passoutYear,
        'phone': phone,
        'password': password,
        'file_url' : ''
    })

def update(obj_id, name, email, rollno, course, branch, passoutYear, phone, password, file_url):
    update_data = {
        "fullname": name,
        "email": email,
        "rollno": rollno,
        "course": course,
        "branch": branch,
        "passout_year": passoutYear,
        "phone": phone,
        "password": password
    }
    if file_url:
        update_data["file_url"] = file_url

    # print("Updating user with data:", update_data)
    result = mongo.db.users.update_one({"_id": ObjectId(obj_id)}, {"$set": update_data})
    # print("Update result:", result.raw_result)

@app.route('/')
def dashboard():
    if 'user' not in session:
        return render_template('login.html')
    posts = mongo.db.images.find({})
    actual_user = session['user']
    user_data1 = mongo.db.users.find_one({'email': actual_user}, {'_id': 0, 'fullname': 1})
    dashboard_data = []
    print(user_data1)
    for post in posts:
        user = mongo.db.users.find_one({'email': post['user_email']}, {'_id': 0, 'email': 1, 'file_url': 1})
        # print(user)
        if user:
            dashboard_data.append({
                '_id' : post['_id'],
                'owner_email': user['email'],
                'owner_photo': user['file_url'],
                'product_image': post['unique_name'],
                'product_name': post['post_name'],
                'product_price': post['post_price'],
                'product_description': post['post_description'],
                
            })
            
            
    return render_template('index.html', user_data1 = user_data1,posts=dashboard_data , actual_user = actual_user )
    

# @app.route('/')
# def dashboard():
#     if 'user' in session:
#         user = session['user']
#         user_data = mongo.db.users.find_one({"email": user})
#         result = mongo.db.images.find({})
#         return render_template('index.html', user=user, dict=user_data,result = result)
#     else:
#         return render_template('index.html')


@app.route('/mypost')
def pypost():
    if 'user' in session:
        user = session['user']
        print(user)
        user_data = mongo.db.users.find_one({"email": user})
        result = mongo.db.images.find({"user_email":user})
        
        return render_template('pypost.html', user=user, dict=user_data, result = result)
    else:
        return render_template('pypost.html')
    



@app.route('/delete/<sno>', methods= ['GET','POST'])
def delete(sno):
    if 'user' in session:
        print(sno)
        mongo.db.images.delete_one({'_id': ObjectId(sno)})
    return redirect(url_for('pypost'))
    
    

@app.route('/buy/<sno>')
def buy(sno):
    print(sno)
    post = mongo.db.images.find_one({'_id': ObjectId(sno)})
    # if request.form == 'POST:
    print(post)  
    return render_template('buy.html',post = post)

    

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user' in session:
        user1 = session['user']
        user = mongo.db.users.find_one({"email": user1})

        obj_id = user['_id']
        # print("User ObjectId:", obj_id)

        file_url = user.get('file_url')  # Get existing file URL from user data if available

        if request.method == "POST":
            # print("Inside request")
            name = request.form.get('fullname')
            email = request.form.get('email')
            rollno = request.form.get('rollno')
            course = request.form.get('course')
            branch = request.form.get('branch')
            passoutYear = request.form.get('passout_year')
            phone = request.form.get('phone')
            password = request.form.get('password')

            # print("Form data received:")
            # print(f"Name: {name}, Email: {email}, Roll No: {rollno}, Course: {course}, Branch: {branch}, Passout Year: {passoutYear}, Phone: {phone}, Password: {password}")

            if 'file' in request.files:
                file = request.files['file']
                if file.filename != '' and allowed_file(file.filename):
                    original_filename = secure_filename(file.filename)
                    unique_filename = generate_unique_filename(original_filename)
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                    file.save(file_path)
                    file_url = os.path.join('uploads', unique_filename)
                    # print("File uploaded and saved as:", file_url)

            # Update user information with file URL if a new file was uploaded
            update(obj_id, name, email, rollno, course, branch, passoutYear, phone, password, file_url)

            return redirect(url_for('profile'))

        return render_template('profile.html',  dict=user, file_url=file_url)
    return render_template('profile.html', user=None, dict=None)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        if login_check(email, password):
            session['user'] = email
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid credentials", "error")
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/register', methods=['POST', 'GET'])
def register():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        name = request.form.get('fullname')
        email = request.form.get('email')
        rollno = request.form.get('rollno')
        course = request.form.get('course')
        branch = request.form.get('branch')
        passoutYear = request.form.get('passout_year')
        phone = request.form.get('phone')
        password = request.form.get('password')
        try:
            model(name, email, rollno, course, branch, passoutYear, phone, password)
            message = "Successfully Registered"
            return redirect(url_for('login', error=message))
        except:
            message = 'Failed to Register'
    return render_template('register.html')















@app.route('/sell', methods = ['GET', 'POST'])
def sell():
    if "user" not in session:
        return redirect(url_for('login'))
    user_email = session['user']
    fullname = mongo.db.users.find_one({'email': user_email}, {'_id': 0, 'fullname': 1})
    
  
    message = ''
    if request.method == 'POST':
        product_name = request.form.get('product_name')
        price = request.form.get('price')
        description = request.form.get('description')
        if 'file' not in request.files:
            return 'No file p'
        file = request.files['file']
        if file.filename == '':
            return 'No selected file'
        if file and allowed_file(file.filename):
            
            original_filename = secure_filename(file.filename)
            unique_filename = generate_unique_filename(original_filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
   
        image_document = {
            "unique_name": unique_filename,
            "post_name": product_name,
            "user_email": user_email,
            "post_price": price,
            "post_description": description
        }
        result1 = mongo.db.images.insert_one(image_document)
        
        message = "Post successfully uploaded"

    return render_template('sell.html',  message=message, user_email = user_email,fullname = fullname)













@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)
    # app.run(debug=True, host='192.168.1.3')
