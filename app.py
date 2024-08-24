import logging

from flask import Flask, abort, jsonify, request
from flask_httpauth import HTTPBasicAuth
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# Initialize the Flask application
app = Flask(__name__)

# Configure the SQLite database URI
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the SQLAlchemy ORM
db = SQLAlchemy(app)

# Initialize HTTP Basic Authentication
auth = HTTPBasicAuth()


# Define a User model for the database
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        # Convert the User object to a dictionary format
        return {
            "id": self.id,
            "username": self.username,
        }


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


# Endpoint to update an existing user (bonus)
@app.route("/users/<int:user_id>", methods=["PUT"])
@auth.login_required
def update_user(user_id):
    user = User.query.get(user_id)
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


# Endpoint to delete a user (bonus)
@app.route("/users/<int:user_id>", methods=["DELETE"])
@auth.login_required
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        abort(404, "User not found")
    # Delete the user from the database
    logger.info(f"User - {user.username} was deleted")
    db.session.delete(user)
    db.session.commit()
    # Return a 204 No Content status
    return "", 204


# Run the Flask application
if __name__ == "__main__":
    app.run(debug=True)
