
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from redis.exceptions import ConnectionError as RedisConnectionError
from werkzeug.security import generate_password_hash

# Configure isolated test services BEFORE importing app.py.
temporary_directory = tempfile.TemporaryDirectory()
database_path = Path(temporary_directory.name) / "fernward_test.db"

os.environ["DATABASE_URL"] = (
    "sqlite:///" + database_path.as_posix()
)
os.environ["REDIS_URL"] = "redis://127.0.0.1:6379/15"

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import application, database, User, redis_client


class TestSessionReplay(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        application.config["TESTING"] = True

        with application.app_context():
            database.create_all()

            user = User(
                username="replay_test_user",
                password_hash=generate_password_hash("TestPassword123!")
            )

            database.session.add(user)
            database.session.commit()

    @classmethod
    def tearDownClass(cls):
        with application.app_context():
            database.session.remove()
            database.drop_all()
            database.engine.dispose()

        temporary_directory.cleanup()

    def test_logout_prevents_cookie_replay(self):
        client = application.test_client()

        login_response = client.post(
            "/login",
            data={
                "username": "replay_test_user",
                "password": "TestPassword123!"
            }
        )

        self.assertEqual(login_response.status_code, 302)

        original_cookie = client.get_cookie("session")
        self.assertIsNotNone(original_cookie)

        # Confirm the cookie works before logout.
        before_logout = client.get("/dashboard")
        self.assertEqual(before_logout.status_code, 200)

        with client.session_transaction() as sess:
            session_id = sess.get("session_id")

        self.assertIsNotNone(session_id)
        session_key = f"fernward:session:{session_id}"

        try:
            logout_response = client.post("/logout")
            self.assertEqual(logout_response.status_code, 302)

            # Replay the original cookie using another client.
            attacker = application.test_client()
            attacker.set_cookie(
                "session",
                original_cookie.value
            )

            replay_response = attacker.get("/dashboard")

            self.assertEqual(replay_response.status_code, 302)
            self.assertIn(
                "/login",
                replay_response.headers["Location"]
            )

            # Verify the Redis session was revoked.
            self.assertIsNone(redis_client.get(session_key))

        finally:
            redis_client.delete(session_key)

    def test_registration_creates_valid_session(self):
        client = application.test_client()
        session_key = None

        try:
            response = client.post(
                "/register",
                data={
                    "username": "register_test",
                    "password": "TestPassword123!"
                }
            )

            self.assertEqual(response.status_code, 302)
            self.assertIn(
                "/dashboard",
                response.headers["Location"]
            )

            with client.session_transaction() as sess:
                session_id = sess.get("session_id")

            self.assertIsNotNone(session_id)
            session_key = f"fernward:session:{session_id}"

            # Registration must create a valid Redis session.
            self.assertIsNotNone(redis_client.get(session_key))

            # Newly registered users should access the dashboard.
            dashboard_response = client.get("/dashboard")
            self.assertEqual(dashboard_response.status_code, 200)

        finally:
            if session_key:
                redis_client.delete(session_key)

    def test_redis_outage_denies_dashboard_access(self):
        client = application.test_client()
        session_key = None

        try:
            login_response = client.post(
                "/login",
                data={
                    "username": "replay_test_user",
                    "password": "TestPassword123!"
                }
            )

            self.assertEqual(login_response.status_code, 302)

            with client.session_transaction() as sess:
                session_id = sess.get("session_id")

            self.assertIsNotNone(session_id)
            session_key = f"fernward:session:{session_id}"

            # Confirm authentication works before simulating an outage.
            self.assertEqual(client.get("/dashboard").status_code, 200)

            # Simulate Redis being unavailable only during validation.
            with patch.object(
                redis_client,
                "get",
                side_effect=RedisConnectionError("Simulated outage")
            ):
                response = client.get("/dashboard")

            self.assertEqual(response.status_code, 503)

        finally:
            if session_key:
                redis_client.delete(session_key)


if __name__ == "__main__":
    unittest.main()
