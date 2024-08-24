import json

import pytest

from app import app
from models import User, db


@pytest.fixture(scope="module")
def test_client():
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
    app.config["WTF_CSRF_ENABLED"] = False
    with app.app_context():
        db.create_all()
    with app.test_client() as client:
        yield client
    with app.app_context():
        db.session.remove()
        db.drop_all()


def test_create_user(test_client):
    payload = json.dumps({"username": "testuser", "password": "testpassword"})
    response = test_client.post(
        "/users",
        data=payload,
        content_type="application/json",
        headers={"Authorization": "Basic YWRtaW46YWRtaW4="},  # admin:admin base64
    )
    assert response.status_code == 201
    # Create the same user again
    response = test_client.post(
        "/users",
        data=payload,
        content_type="application/json",
        headers={"Authorization": "Basic YWRtaW46YWRtaW4="},  # admin:admin base64
    )
    assert response.status_code == 409


def test_get_users(test_client):
    response = test_client.get(
        "/users", headers={"Authorization": "Basic YWRtaW46YWRtaW4="}
    )
    assert response.status_code == 200


def test_update_user(test_client):
    with app.app_context():
        user = User.query.filter_by(username="testuser").first()
        if not user:
            user = User(username="testuser")
            user.set_password(
                "testpassword"
            )  # Use the correct method for setting passwords
            db.session.add(user)
            db.session.commit()
        user_id = user.id

    payload = json.dumps({"username": "updateduser", "password": "newpassword123"})
    response = test_client.put(
        f"/users/{user_id}",
        data=payload,
        content_type="application/json",
        headers={"Authorization": "Basic YWRtaW46YWRtaW4="},
    )
    assert response.status_code == 200


def test_delete_user(test_client):
    with app.app_context():
        user = User.query.filter_by(username="updateduser").first()
        if not user:
            user = User(username="updateduser")
            user.set_password(
                "newpassword123"
            )  # Use the correct method for setting passwords
            db.session.add(user)
            db.session.commit()
        user_id = user.id

    response = test_client.delete(
        f"/users/{user_id}", headers={"Authorization": "Basic YWRtaW46YWRtaW4="}
    )
    assert response.status_code == 204


def test_delete_nonexistent_user(test_client):
    # Try to delete a user that does not exist
    response = test_client.delete(
        "/users/999", headers={"Authorization": "Basic YWRtaW46YWRtaW4="}
    )
    assert response.status_code == 404


def test_create_user_unauthorized(test_client):
    payload = json.dumps({"username": "testuser", "password": "testpassword"})
    response = test_client.post(
        "/users",
        data=payload,
        content_type="application/json",
    )
    assert response.status_code == 401


if __name__ == "__main__":
    pytest.main()
