import unittest
from app import app


class CyberSecurityAppTestCase(unittest.TestCase):

    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    # TC01 - Home page loads
    def test_home_page(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    # TC02 - Login page loads
    def test_login_page(self):
        response = self.client.get("/login")
        self.assertEqual(response.status_code, 200)

    # TC03 - Register page loads
    def test_register_page(self):
        response = self.client.get("/register")
        self.assertEqual(response.status_code, 200)

    # TC04 - Training page loads
    def test_training_page(self):
        response = self.client.get("/training")
        self.assertEqual(response.status_code, 200)

    # TC05 - Quiz Centre requires login
    def test_quiz_centre_requires_login(self):
        response = self.client.get("/quizzes")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.headers["Location"])

    # TC06 - General quiz requires login
    def test_general_quiz_requires_login(self):
        response = self.client.get("/quiz")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.headers["Location"])

    # TC07 - Dashboard requires login
    def test_dashboard_requires_login(self):
        response = self.client.get("/dashboard")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.headers["Location"])

    # TC08 - Logged-in user can access Quiz Centre
    def test_logged_in_user_can_access_quiz_centre(self):
        with self.client.session_transaction() as session:
            session["username"] = "testuser"

        response = self.client.get("/quizzes")
        self.assertEqual(response.status_code, 200)

    # TC09 - Logged-in user can access General quiz
    def test_logged_in_user_can_access_general_quiz(self):
        with self.client.session_transaction() as session:
            session["username"] = "testuser"

        response = self.client.get("/quiz/general")
        self.assertEqual(response.status_code, 200)

    # TC10 - Logged-in user can access Dashboard
    def test_logged_in_user_can_access_dashboard(self):
        with self.client.session_transaction() as session:
            session["username"] = "testuser"

        response = self.client.get("/dashboard")
        self.assertEqual(response.status_code, 200)

    # TC11 - Logout redirects user
    def test_logout_redirects_user(self):
        with self.client.session_transaction() as session:
            session["username"] = "testuser"

        response = self.client.get("/logout")
        self.assertEqual(response.status_code, 302)

    # TC12 - Logout removes user session
    def test_logout_removes_session(self):
        with self.client.session_transaction() as session:
            session["username"] = "testuser"

        self.client.get("/logout")

        with self.client.session_transaction() as session:
            self.assertNotIn("username", session)


if __name__ == "__main__":
    unittest.main()