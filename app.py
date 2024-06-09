import os
from os.path import join, dirname
from dotenv import load_dotenv
from flask import Flask, request, render_template, redirect, url_for, jsonify
from pymongo import MongoClient
import jwt
import datetime
import hashlib
from werkzeug.utils import secure_filename
from bson import ObjectId

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)


MONGODB_URI = os.environ.get("MONGODB_URI")
DB_NAME =  os.environ.get("DB_NAME")

client = MongoClient(MONGODB_URI)
db = client[DB_NAME]

app = Flask(__name__)

SECRET_KEY = "ecommerce"

def is_logged_in():
    token_receive = request.cookies.get("mytoken")
    if token_receive:
        try:
            payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
            user_info = db.user.find_one({"username": payload["id"]})
            if user_info:
                return True
        except jwt.ExpiredSignatureError:
            return False
        except jwt.exceptions.DecodeError:
            return False
    return False

@app.route('/')
def index():
    logged_in = is_logged_in()
    user_info = None
    is_admin = False

    if logged_in:
        token_receive = request.cookies.get("mytoken")
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_info = db.user.find_one({"username": payload["id"]})
        if user_info:
            is_admin = user_info.get("role") == "admin"

    return render_template("index.html", user_info=user_info, is_admin=is_admin, logged_in=logged_in)

@app.route('/shop')
def shop():
    logged_in = is_logged_in()
    user_info = None
    is_admin = False

    if logged_in:
        token_receive = request.cookies.get("mytoken")
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_info = db.user.find_one({"username": payload["id"]})
        if user_info:
            is_admin = user_info.get("role") == "admin"

    product_list = db.product.find()


    return render_template("shop.html", user_info=user_info, is_admin=is_admin, logged_in=logged_in, product_list = product_list)

@app.route('/detail/<id_product>', methods=['GET'])
def detail(id_product):
    logged_in = is_logged_in()
    user_info = None
    is_admin = False

    if logged_in:
        token_receive = request.cookies.get("mytoken")
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_info = db.user.find_one({"username": payload["id"]})
        if user_info:
            is_admin = user_info.get("role") == "admin"

    info_product = db.product.find_one({'_id' : ObjectId(id_product)})


    return render_template("detail.html", user_info=user_info, is_admin=is_admin, logged_in=logged_in, info_product = info_product)

@app.route('/contact')
def contact():
    logged_in = is_logged_in()
    user_info = None
    is_admin = False

    if logged_in:
        token_receive = request.cookies.get("mytoken")
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_info = db.user.find_one({"username": payload["id"]})
        if user_info:
            is_admin = user_info.get("role") == "admin"

    return render_template("contact.html", user_info=user_info, is_admin=is_admin, logged_in=logged_in)

@app.route('/manageproduct', methods = ['GET'])
def manageproduct():
    token_receive = request.cookies.get("mytoken")
    try:
        if token_receive:
            payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
            user_info = db.user.find_one({"username": payload["id"]})
            if user_info:
                is_admin = user_info.get("role") == "admin"
                logged_in = True
                role = user_info.get("role")
            else:
                is_admin = False
                logged_in = False
        else:
            user_info = None
            is_admin = False
            logged_in = False

        if not is_logged_in():
            return redirect(url_for("index"))

        if role not in ["admin"]:
            return redirect(url_for("index"))
        
        product_list = db.product.find()

        return render_template("manageproduct.html", 
                               user_info = user_info,
                               is_admin = is_admin,
                               logged_in = logged_in,
                               product_list = product_list)
    
    except jwt.ExpiredSignatureError:
        return redirect(url_for("index"))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("index"))
    
@app.route('/addproduct', methods = ['GET'])
def addproduct():
    token_receive = request.cookies.get("mytoken")
    try:
        if token_receive:
            payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
            user_info = db.user.find_one({"username": payload["id"]})
            if user_info:
                is_admin = user_info.get("role") == "admin"
                logged_in = True
                role = user_info.get("role")
            else:
                is_admin = False
                logged_in = False
        else:
            user_info = None
            is_admin = False
            logged_in = False
            
        if not is_logged_in():
            return redirect(url_for("index"))

        if role not in ["admin"]:
            return redirect(url_for("index"))
        
        return render_template("addproduct.html", 
                               user_info = user_info,
                               is_admin = is_admin,
                               logged_in = logged_in)
    
    except jwt.ExpiredSignatureError:
        return redirect(url_for("index"))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("index"))
    
@app.route('/add_product', methods=['POST'])
def posting():
    from datetime import datetime
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=['HS256']
        )

        name_receive = request.form.get('name_give')
        price_receive = int(request.form.get('price_give'))
        stock_receive = int(request.form.get('stock_give'))
        link_receive = request.form.get('link_give')
        deskripsi_receive = request.form.get('deskripsi_give')

        today = datetime.now()
        mytime = today.strftime("%Y-%m-%d-%H-%M-%S")

        if 'file_give' in request.files:
            file = request.files.get('file_give')
            file_name = secure_filename(file.filename)
            picture_name= file_name.split(".")[0]
            ekstensi = file_name.split(".")[1]
            picture_name = f"{picture_name}[{name_receive}]-{mytime}.{ekstensi}"
            file_path = f'./static/product_pics/{picture_name}'
            file.save(file_path)
        else: picture_name =f"default.jpg"

        doc = {
            'product_name' : name_receive,
            'product_price' : price_receive,
            'product_stock' : stock_receive,
            'link' : link_receive,
            'image' : picture_name,
            'description' : deskripsi_receive,
            'like_counts' : 0
        }
        db.product.insert_one(doc)
        return jsonify({
            'result' : 'success',
            'msg' : 'Product added!'
        })
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for('index'))
    
@app.route('/editproduct/<id_product>', methods = ['GET'])
def editproduct(id_product):
    token_receive = request.cookies.get("mytoken")
    try:
        if token_receive:
            payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
            user_info = db.user.find_one({"username": payload["id"]})
            if user_info:
                is_admin = user_info.get("role") == "admin"
                logged_in = True
                role = user_info.get("role")
            else:
                is_admin = False
                logged_in = False
        else:
            user_info = None
            is_admin = False
            logged_in = False
            
        if not is_logged_in():
            return redirect(url_for("index"))

        if role not in ["admin"]:
            return redirect(url_for("index"))
        
        info_product = db.product.find_one({'_id' : ObjectId(id_product)})
        return render_template("editproduct.html", 
                               user_info = user_info,
                               is_admin = is_admin,
                               logged_in = logged_in, 
                               info_product = info_product)
    
    except jwt.ExpiredSignatureError:
        return redirect(url_for("index"))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("index"))

@app.route('/edit_product/<id_product>', methods=['PUT'])
def edit(id_product):
    from datetime import datetime
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=['HS256']
        )

        name_receive = request.form.get('name_give')
        price_receive = int(request.form.get('price_give'))
        stock_receive = int(request.form.get('stock_give'))
        link_receive = request.form.get('link_give')
        deskripsi_receive = request.form.get('deskripsi_give')

        today = datetime.now()
        mytime = today.strftime("%Y-%m-%d-%H-%M-%S")

        if 'file_give' in request.files:
            data_lama = db.product.find_one({'_id' : ObjectId(id_product)})
            gambar_lama = data_lama['image']
            if gambar_lama != "default.jpg" :
                os.remove(f'./static/product_pics/{gambar_lama}')

            file = request.files.get('file_give')
            file_name = secure_filename(file.filename)
            picture_name= file_name.split(".")[0]
            ekstensi = file_name.split(".")[1]
            picture_name = f"{picture_name}[{name_receive}]-{mytime}.{ekstensi}"
            file_path = f'./static/product_pics/{picture_name}'
            file.save(file_path)

            doc = {
                'product_name' : name_receive,
                'product_price' : price_receive,
                'product_stock' : stock_receive,
                'link' : link_receive,
                'image' : picture_name,
                'description' : deskripsi_receive,
            }

        else :
            doc = {
                'product_name' : name_receive,
                'product_price' : price_receive,
                'product_stock' : stock_receive,
                'link' : link_receive,
                'description' : deskripsi_receive,
            }
        db.product.update_one({'_id' : ObjectId(id_product)},{'$set': doc})
        return jsonify({
            'result' : 'success',
            'msg' : 'Product updated'
        })
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for('index'))
    
@app.route('/delete_product/<string:id_delete>', methods=['DELETE'])
def delete_product(id_delete):
    token_receive = request.cookies.get("mytoken")

    try:
        info_product = db.product.find_one({'_id' : ObjectId(id_delete)})
        image = info_product['image']
        if image != "default.jpg":
            os.remove(f'./static/product_pics/{image}')

        db.product.delete_one({'_id': ObjectId(id_delete)})
        return jsonify({ 'result' : 'success' , 'msg' : 'Product Deleted'})

    except(jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for('home'))
    
@app.route('/cart')
def cart():
    logged_in = is_logged_in()
    user_info = None
    is_admin = False
    cart_items = []

    if logged_in:
        token_receive = request.cookies.get("mytoken")
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_info = db.user.find_one({"username": payload["id"]})
        if user_info:
            is_admin = user_info.get("role") == "admin"
            # Fetch the cart items for the logged-in user
            cart_items = list(db.cart.find({"user_id": user_info["_id"]}))
            total_payment = sum(item["product_price"] * item["quantity"] for item in cart_items)
    return render_template("cart.html", user_info=user_info, is_admin=is_admin, logged_in=logged_in, cart_items=cart_items, total_payment=total_payment)

@app.route('/checkout')
def checkout():
    logged_in = is_logged_in()
    user_info = None
    is_admin = False
    cart_items = []

    if logged_in:
        token_receive = request.cookies.get("mytoken")
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_info = db.user.find_one({"username": payload["id"]})
        if user_info:
            is_admin = user_info.get("role") == "admin"
            # Fetch the cart items for the logged-in user
            cart_items = list(db.cart.find({"user_id": user_info["_id"]}))
            total_checkout = sum(item["product_price"] * item["quantity"] for item in cart_items)
    return render_template("checkout.html", user_info=user_info, is_admin=is_admin, logged_in=logged_in, cart_items=cart_items, total_checkout=total_checkout)

@app.route('/register')
def register():
    if is_logged_in():
        return redirect('/')
    return render_template("register.html")

@app.route('/login')
def login():
    if is_logged_in():
        return redirect('/')
    return render_template("login.html")

@app.route("/api/register", methods=["POST"])
def api_register():
    username_receive = request.form["username_give"]

    existing_user = db.user.find_one({"username": username_receive})
    if existing_user:
        msg = f"An account with id {username_receive} already exists!"
        return jsonify({"result": "failure", "msg": msg})

    password_receive = request.form["password_give"]
    role_receive = request.form.get("role_give")

    password_hash = hashlib.sha256(password_receive.encode("utf-8")).hexdigest()

    db.user.insert_one({
        "username": username_receive, 
        "password": password_hash, 
        "role": role_receive
    })

    return jsonify({"result": "success"})

@app.route("/api/login", methods=["POST"])
def api_login():
    username_receive = request.form["username_give"]
    password_receive = request.form["password_give"]

    pw_hash = hashlib.sha256(password_receive.encode("utf-8")).hexdigest()

    result = db.user.find_one({
        "username": username_receive, 
        "password": pw_hash
    }, {"role": 1})

    if result:
        role_user = result.get("role", None)

        payload = {
            "id": username_receive,
            "role": role_user,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=60*60),
        }

        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

        return jsonify({
            "result": "success",
            "token": token
        })
    else:
        return jsonify({
            "result": "fail", 
            "msg": "your username or password is incorrect"
        })
    
@app.route('/api/cart/mine/items', methods=['POST'])
def add_to_cart():
    from datetime import datetime
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.user.find_one({"username": payload["id"]})
        if user_info:
            product_id = request.form.get('product_id')
            product_name = request.form.get('product_name')
            product_price = int(request.form.get('product_price'))
            product_image = request.form.get('product_image')
            qty = int(request.form.get('qty'))

            # Get the product from the database
            product = db.product.find_one({"_id": ObjectId(product_id)})

            if not product:
                return jsonify({"result": "fail", "msg": "Product not found"})
            
            # Calculate the total quantity in the cart for this product
            existing_cart_item = db.cart.find_one({
                "user_id": user_info["_id"],
                "product_id": product_id
            })
            if existing_cart_item:
                new_qty = existing_cart_item["quantity"] + qty
            else:
                new_qty = qty

            # Check if the requested quantity exceeds the available stock
            if new_qty > product["product_stock"]:
                return jsonify({"result": "fail", "msg": "Quantity exceeds available stock"})

            today = datetime.now()
            mytime = today.strftime("%Y-%m-%d-%H-%M-%S")

            if existing_cart_item:
                # Update the quantity of the existing product in the cart
                db.cart.update_one(
                    {"_id": existing_cart_item["_id"]},
                    {"$set": {"quantity": new_qty, "timestamp": mytime}}
                )
            else:
                # Add the new product to the cart
                db.cart.insert_one({
                    "user_id": user_info["_id"],
                    "product_id": product_id,
                    "product_name": product_name,
                    "product_price": product_price,
                    "product_image": product_image,
                    "quantity": qty,
                    "timestamp": mytime
                })
            return redirect(url_for('cart'))
        else:
            return jsonify({"result": "fail", "msg": "User not found"})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return jsonify({"result": "fail", "msg": "Token invalid"})
    
@app.route('/delete_cart_item/<string:item_id>', methods=['DELETE'])
def delete_cart_item(item_id):
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.user.find_one({"username": payload["id"]})
        if user_info:
            db.cart.delete_one({"_id": ObjectId(item_id), "user_id": user_info["_id"]})
            return jsonify({"result": "success", "msg": "Item deleted from cart"})
        else:
            return jsonify({"result": "fail", "msg": "User not found"})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return jsonify({"result": "fail", "msg": "Token invalid"})


@app.route('/search', methods=['GET'])
def search():
    logged_in = is_logged_in()
    user_info = None
    is_admin = False

    if logged_in:
        token_receive = request.cookies.get("mytoken")
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_info = db.user.find_one({"username": payload["id"]})
        if user_info:
            is_admin = user_info.get("role") == "admin"

    query = request.args.get('q')
    product_list = db.product.find({"product_name": {"$regex": query, "$options": "i"}})

    return render_template("shop.html", user_info=user_info, is_admin=is_admin, logged_in=logged_in, product_list=product_list, query=query)

@app.route('/logout')
def logout():
    response = redirect('/')
    response.set_cookie('mytoken', expires=0)
    return response


if __name__ == "__main__":
    app.run("0.0.0.0", port=5000, debug=True)