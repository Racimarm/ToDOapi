from flask import jsonify, request, Blueprint
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db_connection
import sqlite3
import jwt
from functools import wraps
import datetime

secret_key ="didou_our_bb_this_is_my_secret_key_for_my_first_project"

auth = Blueprint("auth", __name__)

@auth.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if not name:
        return jsonify({"error": "Name missing, Please enter your Name"}), 400
    if not email:
        return jsonify({"error": "Email missing, Please enter your Email"}), 400
    if not password:
        return jsonify({"error": "Password missing, Please enter your Password"}), 400
    
    hashed_password = generate_password_hash(password)
    
    try:
        conn = get_db_connection()
        cursor = conn.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", (name, email, hashed_password)) 
        conn.commit()
        user_id = cursor.lastrowid
        payload = {
            "user_id": user_id,
            "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=24)
        }
        token = jwt.encode(
            payload,
            secret_key,
            algorithm="HS256"
        )
        
        return jsonify({"message": f"Welcome {name}, you registered successfully, here is your token", "token": token}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "This Email is already registered"}), 409
    finally:
        conn.close()

@auth.route("/login", methods=["POST"])
def login():
    data = request.get_json()  
    email = data.get("email") 
    password = data.get("password")

    if not email:
        return jsonify({"error": "Email missing, Please enter your Email"}), 400
    if not password:
        return jsonify({"error": "Password missing, Please enter your Password"}), 400
    
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    conn.close()

    if not user:
        return jsonify({"error": "Email is not registered"}), 401

    if check_password_hash(user["password"], password):
        payload = {
            "user_id" : user["id"],
            "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=24)   
        }
        token = jwt.encode(
            payload,
            secret_key,
            algorithm="HS256"
        )
        return jsonify({"message": f"Welcome {user['name']}, Here is your token", "token": token}), 200
    else:
        return jsonify({"error": "invalid Email or Password, Check again please"}), 401

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if auth_header:
            token = auth_header.split(" ")[1]
            try:
                payload = jwt.decode(token, secret_key, algorithms="HS256")
                user_id = payload["user_id"]
            except jwt.ExpiredSignatureError:
                return jsonify({"error": "Token expired"}), 401
            except jwt.DecodeError:
                return jsonify({"error": "Token invalid"}), 401
        else:
            return jsonify({"error": "Token missing"}), 401
        return f(user_id, *args, **kwargs)
    return decorated