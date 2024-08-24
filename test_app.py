import json
import unittest

from app import User, app, db


class BasicTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = app
        cls.app.config["TESTING"] = True
        cls.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
        cls.app.config["WTF_CSRF_ENABLED"] = False
        cls.client = cls.app.test_client()

        with cls.app.app_context():
            db.create_all()

    @classmethod
    def tearDownClass(cls):
        with cls.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_create_user(self):
        payload = json.dumps({"username": "testuser", "password": "testpassword"})
        response = self.client.post(
            "/users",
            data=payload,
            content_type="application/json",
            headers={"Authorization": "Basic YWRtaW46YWRtaW4="},  # admin:admin base64
        )
        self.assertEqual(response.status_code, 201)

    def test_get_users(self):
        response = self.client.get(
            "/users", headers={"Authorization": "Basic YWRtaW46YWRtaW4="}
        )
        self.assertEqual(response.status_code, 200)

    def test_update_user(self):
        with self.app.app_context():
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
        response = self.client.put(
            f"/users/{user_id}",
            data=payload,
            content_type="application/json",
            headers={"Authorization": "Basic YWRtaW46YWRtaW4="},
        )
        self.assertEqual(response.status_code, 200)

    def test_delete_user(self):
        with self.app.app_context():
            user = User.query.filter_by(username="updateduser").first()
            if not user:
                user = User(username="updateduser")
                user.set_password(
                    "newpassword123"
                )  # Use the correct method for setting passwords
                db.session.add(user)
                db.session.commit()
            user_id = user.id

        response = self.client.delete(
            f"/users/{user_id}", headers={"Authorization": "Basic YWRtaW46YWRtaW4="}
        )
        self.assertEqual(response.status_code, 204)


if __name__ == "__main__":
    unittest.main()
