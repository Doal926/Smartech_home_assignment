import logging

from flask import Flask, abort, jsonify, request
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import check_password_hash, generate_password_hash

from models import User, db

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# Initialize the Flask application
app = Flask(__name__)

# Configure the SQLite database URI
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)


# Initialize HTTP Basic Authentication
auth = HTTPBasicAuth()


# Create the database and tables if they don't exist
with app.app_context():
    db.create_all()

# In-memory store for storing user credentials (admin user for authentication)
users = {"admin": generate_password_hash("admin")}


@auth.verify_password
def verify_password(username, password):
    # Verify the user's password using the stored hash
    if username in users and check_password_hash(users.get(username), password):
        return username
    return None


# Endpoint to create a new user
@app.route("/users", methods=["POST"])
@auth.login_required
def create_user():
    data = request.json
    # Validate the incoming request data
    if "username" not in data or "password" not in data:
        abort(400, "Missing username or password")
    # Hash the user's password for security
    hashed_password = generate_password_hash(data["password"])
    new_user = User(username=data["username"], password_hash=hashed_password)
    # Add the new user to the database
    db.session.add(new_user)
    db.session.commit()
    # Return the created user data with a 201 Created status
    logger.info(f"User - {new_user.username} was created")
    return jsonify(new_user.to_dict()), 201


# Endpoint to retrieve all users
@app.route("/users", methods=["GET"])
@auth.login_required
def get_users():
    # Query all users from the database
    users = User.query.all()
    # Return the list of users as a JSON response
    return jsonify([user.to_dict() for user in users]), 200


# Endpoint to update an existing user
@app.route("/users/<int:user_id>", methods=["PUT"])
@auth.login_required
def update_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        abort(404, "User not found")
    data = request.json
    # Update the username and/or password if provided in the request
    if "username" in data:
        logger.info(f"User - {user.username} was updated to {data['username']}")
        user.username = data["username"]
    if "password" in data:
        logger.info(f"User - {user.username} password was updated")
        user.password_hash = generate_password_hash(data["password"])
    db.session.commit()

    # Return the updated user data
    return jsonify(user.to_dict()), 200


# Endpoint to delete a user
@app.route("/users/<int:user_id>", methods=["DELETE"])
@auth.login_required
def delete_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        abort(404, "User not found")
    # Delete the user from the database
    user_name = user.username
    db.session.delete(user)
    db.session.commit()
    logger.info(f"User - {user_name} was deleted")
    # Return a 204 No Content status
    return "", 204


# Run the Flask application
if __name__ == "__main__":
    app.run(debug=True)
