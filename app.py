from flask import Flask, render_template, request, redirect, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.secret_key = "cybersecurity_secret_key"


# --------------------------------------------------
# DATABASE
# --------------------------------------------------

def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # Quiz results table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS quiz_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            score INTEGER NOT NULL,
            total INTEGER NOT NULL,
            percentage REAL NOT NULL,
            date_taken TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            quiz_name TEXT DEFAULT 'General Cybersecurity Awareness'
        )
    """)

    # Check whether quiz_name exists in an older database
    cursor.execute("PRAGMA table_info(quiz_results)")
    columns = [column[1] for column in cursor.fetchall()]

    # Add quiz_name without deleting existing results
    if "quiz_name" not in columns:
        cursor.execute("""
            ALTER TABLE quiz_results
            ADD COLUMN quiz_name TEXT DEFAULT 'General Cybersecurity Awareness'
        """)

    conn.commit()
    conn.close()


init_db()


# --------------------------------------------------
# HOME PAGE
# --------------------------------------------------

@app.route("/")
def home():
    return render_template("home.html")


# --------------------------------------------------
# TRAINING PAGE
# --------------------------------------------------

@app.route("/training")
def training():
    return render_template("training.html")


# --------------------------------------------------
# REGISTER
# --------------------------------------------------

@app.route("/register", methods=["GET", "POST"])
def register():

    error = None

    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        # Hash password before storing it
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

            return redirect("/login?registered=1")

        except sqlite3.IntegrityError:
            conn.close()
            error = "Username already exists. Please choose another username."

    return render_template(
        "register.html",
        error=error
    )


# --------------------------------------------------
# LOGIN
# --------------------------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():

    error = None
    success = None

    if request.args.get("registered") == "1":
        success = "Account created successfully. Please log in."

    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        )

        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[2], password):
            session["username"] = username
            return redirect("/dashboard")

        error = "Invalid username or password."

    return render_template(
        "login.html",
        error=error,
        success=success
    )


# --------------------------------------------------
# ALL QUIZZES
# --------------------------------------------------

quizzes = {

    # --------------------------------------------------
    # 1. GENERAL CYBERSECURITY AWARENESS
    # --------------------------------------------------

    "general": {
        "name": "General Cybersecurity Awareness",
        "questions": [
            {
                "question": "What is phishing?",
                "options": [
                    "A fake message used to steal personal information",
                    "A type of antivirus software",
                    "A secure password manager",
                    "A computer backup method"
                ],
                "answer": "A fake message used to steal personal information",
                "explanation": (
                    "Phishing is a cyberattack where criminals use fake "
                    "emails, messages or websites to trick people into "
                    "revealing sensitive information."
                )
            },
            {
                "question": "Which password is the strongest?",
                "options": [
                    "password123",
                    "admin2024",
                    "Boryana123",
                    "T!9x#Lm2@Q"
                ],
                "answer": "T!9x#Lm2@Q",
                "explanation": (
                    "Strong passwords are difficult to guess and should avoid "
                    "common words and personal information. A mixture of "
                    "characters can make a password harder to guess."
                )
            },
            {
                "question": "What should you do if you receive a suspicious email link?",
                "options": [
                    "Click it to check where it goes",
                    "Reply with your personal details",
                    "Ignore or report it",
                    "Forward it to friends"
                ],
                "answer": "Ignore or report it",
                "explanation": (
                    "Suspicious links may lead to phishing websites or "
                    "malicious content. Avoid clicking them and report "
                    "suspicious messages when appropriate."
                )
            },
            {
                "question": "What is a common warning sign of a phishing email?",
                "options": [
                    "An unexpected request for personal information",
                    "A message from someone you know",
                    "A correctly spelled company name",
                    "An email received during working hours"
                ],
                "answer": "An unexpected request for personal information",
                "explanation": (
                    "Unexpected requests for passwords, banking details or "
                    "personal information can be warning signs of phishing."
                )
            },
            {
                "question": "Why should you use different passwords for different accounts?",
                "options": [
                    "It makes websites load faster",
                    "It limits the damage if one password is compromised",
                    "It prevents all phishing emails",
                    "It removes the need for account security"
                ],
                "answer": "It limits the damage if one password is compromised",
                "explanation": (
                    "Unique passwords reduce the risk of one stolen password "
                    "being used to access several different accounts."
                )
            },
            {
                "question": "What does multi-factor authentication (MFA) provide?",
                "options": [
                    "An additional layer of account security",
                    "A faster internet connection",
                    "Automatic removal of computer viruses",
                    "A replacement for all passwords"
                ],
                "answer": "An additional layer of account security",
                "explanation": (
                    "MFA requires another form of verification in addition "
                    "to a password, making unauthorised access more difficult."
                )
            },
            {
                "question": "What should you do before entering sensitive information on a website?",
                "options": [
                    "Check that the website address is legitimate",
                    "Disable your antivirus software",
                    "Download files from the website",
                    "Share the website with other people"
                ],
                "answer": "Check that the website address is legitimate",
                "explanation": (
                    "Checking the website address can help identify fake or "
                    "misleading websites before sensitive information is entered."
                )
            },
            {
                "question": "What is social engineering?",
                "options": [
                    "Manipulating people into revealing information or performing unsafe actions",
                    "Designing social media websites",
                    "Installing computer hardware",
                    "Updating an operating system"
                ],
                "answer": "Manipulating people into revealing information or performing unsafe actions",
                "explanation": (
                    "Social engineering uses psychological manipulation such "
                    "as trust, urgency, fear or impersonation to influence people."
                )
            },
            {
                "question": "What is ransomware?",
                "options": [
                    "Malware that can lock or encrypt data and demand payment",
                    "Software used to create strong passwords",
                    "A secure method of backing up files",
                    "A tool for improving internet speed"
                ],
                "answer": "Malware that can lock or encrypt data and demand payment",
                "explanation": (
                    "Ransomware is malicious software that can prevent access "
                    "to files or systems and then demand payment from the victim."
                )
            },
            {
                "question": "What is the safest action when you receive an unexpected attachment?",
                "options": [
                    "Open it immediately",
                    "Download it and send it to someone else",
                    "Verify the sender and the attachment before opening it",
                    "Disable security software before opening it"
                ],
                "answer": "Verify the sender and the attachment before opening it",
                "explanation": (
                    "Unexpected attachments may contain malicious software, "
                    "so the sender and attachment should be verified first."
                )
            }
        ]
    },


    # --------------------------------------------------
    # 2. PHISHING AWARENESS
    # --------------------------------------------------

    "phishing": {
        "name": "Phishing Awareness",
        "questions": [
            {
                "question": "What is the main purpose of a phishing attack?",
                "options": [
                    "To trick people into revealing sensitive information",
                    "To improve account security",
                    "To update a computer automatically",
                    "To increase internet speed"
                ],
                "answer": "To trick people into revealing sensitive information",
                "explanation": (
                    "Phishing attempts to deceive people into revealing "
                    "passwords, account details or other sensitive information."
                )
            },
            {
                "question": "Which is a common warning sign of a phishing message?",
                "options": [
                    "An unexpected request for sensitive information",
                    "A newsletter you deliberately subscribed to",
                    "An email saved in your drafts folder",
                    "A normal message from a friend"
                ],
                "answer": "An unexpected request for sensitive information",
                "explanation": (
                    "Unexpected requests for passwords, payment details or "
                    "personal information should be treated with caution."
                )
            },
            {
                "question": "What should you do if you receive a suspicious link in an email?",
                "options": [
                    "Click it to see whether it is safe",
                    "Avoid clicking it and verify the message independently",
                    "Forward it to another person",
                    "Reply with your password"
                ],
                "answer": "Avoid clicking it and verify the message independently",
                "explanation": (
                    "Suspicious links may lead to fake or malicious websites. "
                    "Verify the request using a trusted method instead."
                )
            },
            {
                "question": "Why might a phishing message create a sense of urgency?",
                "options": [
                    "To pressure the recipient into acting without thinking carefully",
                    "To improve internet speed",
                    "To make the email easier to read",
                    "To protect the recipient's account"
                ],
                "answer": "To pressure the recipient into acting without thinking carefully",
                "explanation": (
                    "Attackers may use urgency or fear to encourage people "
                    "to act before checking whether a message is genuine."
                )
            },
            {
                "question": "What should you do if an email claiming to be from your bank asks you to verify your account through a link?",
                "options": [
                    "Click the link and enter your login details",
                    "Reply with your account information",
                    "Contact the bank using an official website, app or trusted contact method",
                    "Forward the email to friends"
                ],
                "answer": "Contact the bank using an official website, app or trusted contact method",
                "explanation": (
                    "Contact the organisation independently rather than using "
                    "links or contact details contained in a suspicious message."
                )
            }
        ]
    },


    # --------------------------------------------------
    # 3. PASSWORD & ACCOUNT SECURITY
    # --------------------------------------------------

    "password-security": {
        "name": "Password & Account Security",
        "questions": [
            {
                "question": "Why is it important to use a unique password for each account?",
                "options": [
                    "It prevents one stolen password from compromising several accounts",
                    "It makes websites load faster",
                    "It removes the need for software updates",
                    "It prevents every type of cyberattack"
                ],
                "answer": "It prevents one stolen password from compromising several accounts",
                "explanation": (
                    "If passwords are reused, one compromised password may "
                    "allow an attacker to access several accounts."
                )
            },
            {
                "question": "Which password is the most difficult to guess?",
                "options": [
                    "football123",
                    "Password1",
                    "London2026",
                    "R7!qL2#vP9"
                ],
                "answer": "R7!qL2#vP9",
                "explanation": (
                    "Passwords that are difficult to predict and do not contain "
                    "common words or personal information are generally safer."
                )
            },
            {
                "question": "What is the purpose of multi-factor authentication?",
                "options": [
                    "To require an additional form of verification",
                    "To make passwords visible",
                    "To disable account security",
                    "To automatically share login details"
                ],
                "answer": "To require an additional form of verification",
                "explanation": (
                    "MFA adds another verification step, reducing the chance "
                    "that a stolen password alone can be used to access an account."
                )
            },
            {
                "question": "What should you do if you believe one of your passwords has been stolen?",
                "options": [
                    "Continue using it",
                    "Change it as soon as possible",
                    "Post it online",
                    "Use the same password on more accounts"
                ],
                "answer": "Change it as soon as possible",
                "explanation": (
                    "A compromised password should be changed promptly to "
                    "reduce the risk of unauthorised access."
                )
            },
            {
                "question": "What is a password manager designed to do?",
                "options": [
                    "Help store and manage passwords securely",
                    "Remove the need for account authentication",
                    "Send passwords to other users",
                    "Disable multi-factor authentication"
                ],
                "answer": "Help store and manage passwords securely",
                "explanation": (
                    "Password managers can help users store and manage unique "
                    "passwords without needing to remember every password."
                )
            }
        ]
    },


    # --------------------------------------------------
    # 4. SOCIAL ENGINEERING
    # --------------------------------------------------

    "social-engineering": {
        "name": "Social Engineering",
        "questions": [
            {
                "question": "What does social engineering mainly target?",
                "options": [
                    "Human behaviour and decision-making",
                    "Computer screen resolution",
                    "Internet connection speed",
                    "Computer storage capacity"
                ],
                "answer": "Human behaviour and decision-making",
                "explanation": (
                    "Social engineering attempts to manipulate people into "
                    "revealing information or performing unsafe actions."
                )
            },
            {
                "question": "Why might an attacker pretend to be a trusted employee or organisation?",
                "options": [
                    "To make the victim more likely to trust the request",
                    "To improve the victim's computer",
                    "To install legitimate updates",
                    "To increase network speed"
                ],
                "answer": "To make the victim more likely to trust the request",
                "explanation": (
                    "Impersonating a trusted person or organisation can make "
                    "a fraudulent request appear more believable."
                )
            },
            {
                "question": "Which situation could be an example of social engineering?",
                "options": [
                    "Someone pretending to be IT support asks for your password",
                    "Your computer installs an authorised update",
                    "You create a document",
                    "You restart your computer"
                ],
                "answer": "Someone pretending to be IT support asks for your password",
                "explanation": (
                    "Impersonating IT support to obtain confidential information "
                    "is a common example of social engineering."
                )
            },
            {
                "question": "What should you do with an unusual request for confidential information?",
                "options": [
                    "Verify the request using a trusted method",
                    "Provide the information immediately",
                    "Post the information publicly",
                    "Ignore all security procedures"
                ],
                "answer": "Verify the request using a trusted method",
                "explanation": (
                    "Unusual requests should be independently verified before "
                    "sensitive information is disclosed."
                )
            },
            {
                "question": "Which emotion may be deliberately used in a social engineering attack?",
                "options": [
                    "Fear or urgency",
                    "Relaxation only",
                    "Boredom only",
                    "Happiness only"
                ],
                "answer": "Fear or urgency",
                "explanation": (
                    "Attackers may create fear or urgency to reduce the time "
                    "a person takes to question or verify a request."
                )
            }
        ]
    },


    # --------------------------------------------------
    # 5. MALWARE & RANSOMWARE
    # --------------------------------------------------

    "malware-ransomware": {
        "name": "Malware & Ransomware",
        "questions": [
            {
                "question": "What is malware?",
                "options": [
                    "Software designed to cause harm or perform malicious actions",
                    "Software used only for writing documents",
                    "A secure backup method",
                    "A type of computer monitor"
                ],
                "answer": "Software designed to cause harm or perform malicious actions",
                "explanation": (
                    "Malware is malicious software designed to damage systems, "
                    "steal information or perform other unwanted actions."
                )
            },
            {
                "question": "What can ransomware do?",
                "options": [
                    "Encrypt or lock data and demand payment",
                    "Improve computer performance",
                    "Create stronger passwords",
                    "Increase internet speed"
                ],
                "answer": "Encrypt or lock data and demand payment",
                "explanation": (
                    "Ransomware can prevent users from accessing their data "
                    "or systems and demand payment."
                )
            },
            {
                "question": "How can malware sometimes reach a computer?",
                "options": [
                    "Through malicious attachments or downloads",
                    "Only through a computer keyboard",
                    "Only through a printer",
                    "Only when the computer is switched off"
                ],
                "answer": "Through malicious attachments or downloads",
                "explanation": (
                    "Malicious files, attachments and downloads are common "
                    "ways malware can be delivered."
                )
            },
            {
                "question": "Why are software updates important for security?",
                "options": [
                    "They can fix known security vulnerabilities",
                    "They guarantee that phishing cannot happen",
                    "They make every password unnecessary",
                    "They prevent all human mistakes"
                ],
                "answer": "They can fix known security vulnerabilities",
                "explanation": (
                    "Updates often contain security patches that correct "
                    "known weaknesses in software."
                )
            },
            {
                "question": "Which practice can help reduce the impact of ransomware?",
                "options": [
                    "Maintaining appropriate backups of important data",
                    "Opening every unexpected attachment",
                    "Disabling security software",
                    "Sharing passwords with other people"
                ],
                "answer": "Maintaining appropriate backups of important data",
                "explanation": (
                    "Appropriate backups can help recover important information "
                    "if data becomes unavailable or damaged."
                )
            }
        ]
    },


    # --------------------------------------------------
    # 6. SAFE BROWSING & EMAIL SECURITY
    # --------------------------------------------------

    "safe-browsing": {
        "name": "Safe Browsing & Email Security",
        "questions": [
            {
                "question": "What should you check before entering sensitive information on a website?",
                "options": [
                    "That the website address is legitimate",
                    "That the page contains many pictures",
                    "That the website uses large text",
                    "That someone has shared it on social media"
                ],
                "answer": "That the website address is legitimate",
                "explanation": (
                    "Checking the website address can help identify fake "
                    "websites designed to steal information."
                )
            },
            {
                "question": "What should you do with an unexpected email attachment?",
                "options": [
                    "Verify the sender and attachment before opening it",
                    "Open it immediately",
                    "Disable security software first",
                    "Forward it to everyone you know"
                ],
                "answer": "Verify the sender and attachment before opening it",
                "explanation": (
                    "Unexpected attachments may contain malware and should "
                    "be verified before they are opened."
                )
            },
            {
                "question": "Why should shortened or unfamiliar links be treated carefully?",
                "options": [
                    "They may hide the real destination",
                    "They always improve security",
                    "They automatically remove malware",
                    "They cannot lead to websites"
                ],
                "answer": "They may hide the real destination",
                "explanation": (
                    "Some links can disguise their true destination, making "
                    "it harder to identify suspicious websites."
                )
            },
            {
                "question": "What is a safer way to access an organisation's website after receiving a suspicious email?",
                "options": [
                    "Type the known website address yourself or use a trusted bookmark",
                    "Use the suspicious email link",
                    "Reply and ask for your password",
                    "Forward the email to strangers"
                ],
                "answer": "Type the known website address yourself or use a trusted bookmark",
                "explanation": (
                    "Using a known address or trusted bookmark avoids relying "
                    "on potentially malicious links in suspicious messages."
                )
            },
            {
                "question": "What should you do if a website unexpectedly asks for sensitive information?",
                "options": [
                    "Check the website carefully before providing anything",
                    "Provide the information immediately",
                    "Disable your browser security",
                    "Share the request with strangers"
                ],
                "answer": "Check the website carefully before providing anything",
                "explanation": (
                    "Unexpected requests for sensitive information should be "
                    "treated cautiously and verified before responding."
                )
            }
        ]
    },


    # --------------------------------------------------
    # 7. ONLINE PRIVACY & PERSONAL DATA
    # --------------------------------------------------

    "online-privacy": {
        "name": "Online Privacy & Personal Data",
        "questions": [
            {
                "question": "Why should you be careful about sharing personal information online?",
                "options": [
                    "It may be misused by criminals or other people",
                    "It always improves account security",
                    "It automatically creates backups",
                    "It prevents phishing"
                ],
                "answer": "It may be misused by criminals or other people",
                "explanation": (
                    "Personal information can sometimes be used for fraud, "
                    "impersonation or targeted scams."
                )
            },
            {
                "question": "Which information should generally be treated as sensitive?",
                "options": [
                    "Passwords and financial information",
                    "A public weather forecast",
                    "The name of a public website",
                    "A general news headline"
                ],
                "answer": "Passwords and financial information",
                "explanation": (
                    "Passwords and financial information can provide access "
                    "to accounts or be used for fraud."
                )
            },
            {
                "question": "Why is it useful to review privacy settings on online accounts?",
                "options": [
                    "To control who can access information you share",
                    "To make every account public",
                    "To remove all passwords",
                    "To disable account security"
                ],
                "answer": "To control who can access information you share",
                "explanation": (
                    "Privacy settings can help users control the visibility "
                    "of information shared through an online service."
                )
            },
            {
                "question": "What is a safer approach when an unfamiliar website asks for unnecessary personal information?",
                "options": [
                    "Avoid providing information that is not needed",
                    "Provide every detail requested",
                    "Use another person's information",
                    "Post the information publicly"
                ],
                "answer": "Avoid providing information that is not needed",
                "explanation": (
                    "Limiting unnecessary disclosure reduces the amount of "
                    "personal information that could be exposed or misused."
                )
            },
            {
                "question": "Why can information shared on social media create a security risk?",
                "options": [
                    "Attackers may use it to make scams more convincing",
                    "Social media automatically deletes passwords",
                    "It prevents attackers from contacting users",
                    "It guarantees account protection"
                ],
                "answer": "Attackers may use it to make scams more convincing",
                "explanation": (
                    "Public personal information can help attackers create "
                    "more believable and targeted fraudulent messages."
                )
            }
        ]
    },


    # --------------------------------------------------
    # 8. PUBLIC WI-FI & NETWORK SAFETY
    # --------------------------------------------------

    "public-wifi": {
        "name": "Public Wi-Fi & Network Safety",
        "questions": [
            {
                "question": "Why should you be cautious when using public Wi-Fi?",
                "options": [
                    "The network may not always be trustworthy or secure",
                    "Public Wi-Fi always deletes files",
                    "Public Wi-Fi cannot connect to websites",
                    "It automatically changes your passwords"
                ],
                "answer": "The network may not always be trustworthy or secure",
                "explanation": (
                    "Public networks may provide less control and assurance "
                    "than a trusted private network."
                )
            },
            {
                "question": "Which activity is better avoided on an untrusted public Wi-Fi network when possible?",
                "options": [
                    "Accessing highly sensitive accounts or financial services",
                    "Reading an offline document",
                    "Changing the screen brightness",
                    "Using a calculator"
                ],
                "answer": "Accessing highly sensitive accounts or financial services",
                "explanation": (
                    "Sensitive activities should preferably be carried out "
                    "using a network or connection you trust."
                )
            },
            {
                "question": "What should you check before joining a public Wi-Fi network?",
                "options": [
                    "That you are connecting to the intended legitimate network",
                    "That the network has the shortest name",
                    "That your screen brightness is high",
                    "That your computer has several open windows"
                ],
                "answer": "That you are connecting to the intended legitimate network",
                "explanation": (
                    "Attackers can create misleading network names, so users "
                    "should confirm that they are joining the intended network."
                )
            },
            {
                "question": "What should you do when you no longer need a public Wi-Fi connection?",
                "options": [
                    "Disconnect from the network",
                    "Share the network with everyone",
                    "Disable your device password",
                    "Leave every account signed in"
                ],
                "answer": "Disconnect from the network",
                "explanation": (
                    "Disconnecting when the network is no longer needed reduces "
                    "unnecessary exposure to an untrusted connection."
                )
            },
            {
                "question": "Which connection may be preferable for sensitive activity when public Wi-Fi is not trusted?",
                "options": [
                    "A trusted mobile data connection",
                    "Any unknown open Wi-Fi network",
                    "A network with a suspicious duplicate name",
                    "A connection recommended by an unknown message"
                ],
                "answer": "A trusted mobile data connection",
                "explanation": (
                    "A trusted personal connection may be preferable to an "
                    "unknown or untrusted public network for sensitive activity."
                )
            }
        ]
    },


    # --------------------------------------------------
    # 9. DEVICE & SOFTWARE SECURITY
    # --------------------------------------------------

    "device-security": {
        "name": "Device & Software Security",
        "questions": [
            {
                "question": "Why should operating systems and applications be kept updated?",
                "options": [
                    "Updates can fix known security vulnerabilities",
                    "Updates remove the need for passwords",
                    "Updates prevent every phishing email",
                    "Updates make all websites trustworthy"
                ],
                "answer": "Updates can fix known security vulnerabilities",
                "explanation": (
                    "Software updates frequently include patches for security "
                    "weaknesses discovered after software was released."
                )
            },
            {
                "question": "Where should software preferably be downloaded from?",
                "options": [
                    "A trusted or official source",
                    "Any unknown website",
                    "A suspicious email attachment",
                    "An unsolicited pop-up advertisement"
                ],
                "answer": "A trusted or official source",
                "explanation": (
                    "Trusted and official sources reduce the risk of installing "
                    "modified, fake or malicious software."
                )
            },
            {
                "question": "Why is a screen lock useful on a device?",
                "options": [
                    "It helps prevent unauthorised access when the device is unattended",
                    "It increases internet speed",
                    "It automatically backs up every file",
                    "It prevents all malware"
                ],
                "answer": "It helps prevent unauthorised access when the device is unattended",
                "explanation": (
                    "A screen lock helps protect information if another person "
                    "tries to use an unattended device."
                )
            },
            {
                "question": "What should you do if your device displays an unexpected request to install unknown software?",
                "options": [
                    "Do not install it until you verify that it is legitimate",
                    "Install it immediately",
                    "Disable security controls first",
                    "Send it to other people"
                ],
                "answer": "Do not install it until you verify that it is legitimate",
                "explanation": (
                    "Unexpected software installation requests may be unsafe "
                    "and should be verified before proceeding."
                )
            },
            {
                "question": "Why is it important to protect a device with authentication such as a password or PIN?",
                "options": [
                    "It helps prevent unauthorised access to the device",
                    "It guarantees that the device cannot be lost",
                    "It makes every website safe",
                    "It removes the need for software updates"
                ],
                "answer": "It helps prevent unauthorised access to the device",
                "explanation": (
                    "Device authentication provides a barrier against someone "
                    "accessing information without permission."
                )
            }
        ]
    }
}


# --------------------------------------------------
# QUIZ CENTRE
# --------------------------------------------------

@app.route("/quizzes")
def quiz_centre():

    if "username" not in session:
        return redirect("/login")

    return render_template(
        "quizzes.html",
        quizzes=quizzes
    )


# --------------------------------------------------
# REUSABLE QUIZ ROUTE
# --------------------------------------------------

@app.route("/quiz/<quiz_id>", methods=["GET", "POST"])
def take_quiz(quiz_id):

    if "username" not in session:
        return redirect("/login")

    # Check that the requested quiz exists
    if quiz_id not in quizzes:
        return redirect("/quizzes")

    selected_quiz = quizzes[quiz_id]
    questions = selected_quiz["questions"]
    quiz_name = selected_quiz["name"]

    if request.method == "POST":

        score = 0
        feedback = []

        for index, question in enumerate(questions):

            selected_answer = request.form.get(
                f"question_{index}"
            )

            is_correct = selected_answer == question["answer"]

            if is_correct:
                score += 1

            feedback.append({
                "question_number": index + 1,
                "question": question["question"],
                "selected_answer": selected_answer,
                "correct_answer": question["answer"],
                "is_correct": is_correct,
                "explanation": question["explanation"]
            })

        total = len(questions)
        percentage = (score / total) * 100

        # Save quiz result
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO quiz_results
            (username, score, total, percentage, quiz_name)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                session["username"],
                score,
                total,
                percentage,
                quiz_name
            )
        )

        conn.commit()
        conn.close()

        return render_template(
            "results.html",
            score=score,
            total=total,
            percentage=percentage,
            feedback=feedback,
            quiz_name=quiz_name,
            retry_url=f"/quiz/{quiz_id}"
        )

    return render_template(
        "quiz.html",
        questions=questions,
        quiz_name=quiz_name
    )


# --------------------------------------------------
# OLD GENERAL QUIZ ADDRESS
# --------------------------------------------------

@app.route("/quiz")
def old_quiz_route():

    if "username" not in session:
        return redirect("/login")

    return redirect("/quiz/general")


# --------------------------------------------------
# LOGOUT
# --------------------------------------------------

@app.route("/logout")
def logout():

    session.pop("username", None)

    return redirect("/")



# --------------------------------------------------
# DASHBOARD
# --------------------------------------------------

@app.route("/dashboard")
def dashboard():

    if "username" not in session:
        return redirect("/login")

    username = session["username"]

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    # Get all quiz results for the logged-in user
    cursor.execute(
        """
        SELECT quiz_name, score, total, percentage
        FROM quiz_results
        WHERE username = ?
        """,
        (username,)
    )

    results = cursor.fetchall()

    conn.close()

    # Store the best attempt for each quiz
    best_results = {}

    for quiz_name, score, total, percentage in results:

        # Treat older General quiz results as the current General quiz
        if quiz_name == "General Cybersecurity":
            quiz_name = "General Cybersecurity Awareness"

        if quiz_name not in best_results:
            best_results[quiz_name] = {
                "score": score,
                "total": total,
                "percentage": percentage
            }

        elif percentage > best_results[quiz_name]["percentage"]:
            best_results[quiz_name] = {
                "score": score,
                "total": total,
                "percentage": percentage
            }

    # Build Dashboard progress
    quiz_progress = []

    completed_quizzes = 0
    total_best_points = 0
    total_available_points = 0

    for quiz_id, quiz_data in quizzes.items():

        quiz_name = quiz_data["name"]
        quiz_total = len(quiz_data["questions"])

        total_available_points += quiz_total

        best_result = best_results.get(quiz_name)

        if best_result is not None:

            completed_quizzes += 1
            total_best_points += best_result["score"]

            quiz_progress.append({
                "quiz_id": quiz_id,
                "quiz_name": quiz_name,
                "best_score": best_result["score"],
                "total": quiz_total,
                "best_percentage": best_result["percentage"]
            })

        else:

            quiz_progress.append({
                "quiz_id": quiz_id,
                "quiz_name": quiz_name,
                "best_score": None,
                "total": quiz_total,
                "best_percentage": None
            })

    total_quizzes = len(quizzes)

    # Only calculate the final overall result
    # after all quizzes have been completed
    if completed_quizzes == total_quizzes:

        overall_percentage = (
            total_best_points / total_available_points
        ) * 100

    else:
        overall_percentage = None

    return render_template(
        "dashboard.html",
        username=username,
        quiz_progress=quiz_progress,
        completed_quizzes=completed_quizzes,
        total_quizzes=total_quizzes,
        total_best_points=total_best_points,
        total_available_points=total_available_points,
        overall_percentage=overall_percentage
    )

# --------------------------------------------------
# RUN APPLICATION
# --------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)