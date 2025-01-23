from app import init_app

app = init_app()

if __name__ == "__main__":
    app.run()








# from flask import Blueprint, request, jsonify
# from app import db, bcrypt
# from app.models import User
# from flask_jwt_extended import create_access_token

# auth_bp = Blueprint("auth_bp", __name__, url_prefix="/auth")

# @auth_bp.route("/register", methods=["POST"])
# def register():
#     data = request.get_json()
#     hashed_password = bcrypt.generate_password_hash(data["password"]).decode("utf-8")
#     user = User(username=data["username"], password=hashed_password)
#     db.session.add(user)
#     db.session.commit()
#     return jsonify({"message": "User registered successfully"}), 201

# @auth_bp.route("/login", methods=["POST"])
# def login():
#     data = request.get_json()
#     user = User.query.filter_by(username=data["username"]).first()
#     if user and bcrypt.check_password_hash(user.password, data["password"]):
#         token = create_access_token(identity=user.id)
#         return jsonify({"access_token": token}), 200
#     return jsonify({"message": "Invalid credentials"}), 401
