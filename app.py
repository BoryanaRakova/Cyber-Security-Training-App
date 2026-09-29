from flask import Flask, render_template, request, redirect, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.secret_key = "cybersecurity_secret_key"


# Create the users database table
def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


init_db()


# Home page
@app.route("/")
def home():
    return render_template("home.html")


# Training page
@app.route("/training")
def training():
    return render_template("training.html")


# Register page
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Hash the password before saving it to the database
        hashed_password = generate_password_hash(password)

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, hashed_password)
            )

            conn.commit()
            conn.close()

            # Send a registration confirmation to the login page
            return render_template(
                "login.html",
                success="Account created successfully. Please log in."
            )

        except sqlite3.IntegrityError:
            conn.close()

            return render_template(
                "register.html",
                error="Username already exists. Please choose another username."
            )

    return render_template("register.html")


# Login page
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        )

        user = cursor.fetchone()
        conn.close()

        # Check the entered password against the stored password hash
        if user and check_password_hash(user[2], password):
            session["username"] = username
            return redirect("/dashboard")

        else:
            return render_template(
                "login.html",
                error="Invalid username or password."
            )

    return render_template("login.html")


# Quiz questions
quiz_questions = [
    {
        "question": "What is phishing?",
        "options": [
            "A fake message used to steal personal information",
            "A type of antivirus software",
            "A secure password manager",
            "A computer backup method"
        ],
        "answer": "A fake message used to steal personal information"
    },
    {
        "question": "Which password is the strongest?",
        "options": [
            "password123",
            "admin2024",
            "Boryana123",
            "T!9x#Lm2@Q"
        ],
        "answer": "T!9x#Lm2@Q"
    },
    {
        "question": "What should you do if you receive a suspicious email link?",
        "options": [
            "Click it to check",
            "Reply with personal details",
            "Ignore or report it",
            "Forward it to friends"
        ],
        "answer": "Ignore or report it"
    }
]


# Quiz page
@app.route("/quiz", methods=["GET", "POST"])
def quiz():

    if request.method == "POST":
        score = 0

        for index, question in enumerate(quiz_questions):
            selected_answer = request.form.get(f"question_{index}")

            if selected_answer == question["answer"]:
                score += 1

        return render_template(
            "results.html",
            score=score,
            total=len(quiz_questions)
        )

    return render_template(
        "quiz.html",
        questions=quiz_questions
    )


# Logout
@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect("/")


# Dashboard
@app.route("/dashboard")
def dashboard():

    if "username" in session:
        return render_template(
            "dashboard.html",
            username=session["username"]
        )

    return redirect("/login")


if __name__ == "__main__":
    app.run(debug=True)