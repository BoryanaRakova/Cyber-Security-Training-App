import os
import sqlite3
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, session, url_for
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()
app = Flask(__name__)
app.secret_key = os.environ["FLASK_SECRET_KEY"]
RESEARCHER_USER_ID = int(os.environ.get("RESEARCHER_USER_ID", "8"))


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
    cursor.execute("PRAGMA table_info(quiz_results)")
    columns = [column[1] for column in cursor.fetchall()]
    if "quiz_name" not in columns:
        cursor.execute("""
            ALTER TABLE quiz_results
            ADD COLUMN quiz_name TEXT DEFAULT 'General Cybersecurity Awareness'
        """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS evaluation_feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            q1 INTEGER NOT NULL,
            q2 INTEGER NOT NULL,
            q3 INTEGER NOT NULL,
            q4 INTEGER NOT NULL,
            q5 INTEGER NOT NULL,
            q6 INTEGER NOT NULL,
            q7 INTEGER NOT NULL,
            q8 INTEGER NOT NULL,
            q9 INTEGER NOT NULL,
            q10 INTEGER NOT NULL,
            positive_feedback TEXT,
            improvement_feedback TEXT,
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

init_db()

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/training")
def training():
    return render_template("training.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    error = None
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
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

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    success = None
    message = None
    if request.args.get("registered") == "1":
        success = "Account created successfully. Please log in."
    if request.args.get("next") == "quizzes":
        message = "Please log in to access the quizzes."
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
            session.clear()
            session["username"] = user[1]
            session["user_id"] = user[0]
            if request.args.get("next") == "quizzes":
                return redirect("/quizzes")
            return redirect("/dashboard")
        error = "Invalid username or password."
    return render_template(
        "login.html",
        error=error,
        success=success,
        message=message
    )

# Nine quizzes and their answer explanations
def make_questions(items):
    return [
        {
            "question": question,
            "options": options,
            "answer": options[correct],
            "explanation": explanation
        }
        for question, options, correct, explanation in items
    ]

quizzes = {
    # 1. GENERAL CYBERSECURITY AWARENESS
    "general": {
        "name": "General Cybersecurity Awareness",
        "questions": make_questions([
            (
                "A colleague receives an unexpected login approval request on their phone. What should they do?",
                [
                    "Approve it in case it is a system test",
                    "Deny it and report the unexpected request",
                    "Turn off notifications for the day",
                    "Send their password to IT for checking"
                ],
                1,
                "An unexpected authentication prompt may mean someone is trying to access the account."
            ),
            (
                "A website displays a padlock icon but its domain name is slightly different from the organisation you intended. What does this suggest?",
                [
                    "The padlock proves the organisation owns the site",
                    "The site must be safe because it uses encryption",
                    "The domain may be an impersonation and should be checked",
                    "The difference is harmless if the page looks familiar"
                ],
                2,
                "HTTPS encrypts the connection but does not guarantee that the website is legitimate."
            ),
            (
                "You discover that an online service you use has suffered a data breach. What is the most useful first response?",
                [
                    "Wait until someone accesses your account",
                    "Change the affected password and any reused passwords",
                    "Delete all browser bookmarks",
                    "Turn off your device for a week"
                ],
                1,
                "Changing compromised and reused passwords helps prevent account takeover."
            ),
            (
                "Why should important files be backed up separately from the main device?",
                [
                    "Backups make all malware impossible",
                    "Backups automatically stop phishing",
                    "Backups remove the need for security updates",
                    "Backups can help restore data after loss or ransomware"
                ],
                3,
                "Separate, tested backups support recovery when original files are lost or damaged."
            ),
            (
                "A mobile app requests access to your contacts even though it only provides a calculator. What is the best response?",
                [
                    "Question the permission and deny unnecessary access",
                    "Allow it because apps always need every permission",
                    "Share your contact list manually instead",
                    "Disable your screen lock before installing"
                ],
                0,
                "Applications should receive only the permissions necessary for their purpose."
            ),
            (
                "You find a USB drive in a shared office. What should you do?",
                [
                    "Connect it to identify its owner",
                    "Take it home and scan it later",
                    "Give it to the appropriate IT or security team without connecting it",
                    "Use it only on a colleague's computer"
                ],
                2,
                "Unknown USB devices can contain malicious files or hardware."
            ),
            (
                "An online account offers a passkey sign-in option. What is a key security benefit?",
                [
                    "It makes your account public",
                    "It can reduce reliance on passwords and resist many phishing attacks",
                    "It lets you share sign-in details more easily",
                    "It disables all account recovery methods"
                ],
                1,
                "Passkeys use cryptographic authentication designed to resist credential phishing."
            ),
            (
                "What is the best way to confirm that a software update notification is genuine?",
                [
                    "Install from the operating system or application's trusted update settings",
                    "Use the first download link in a pop-up advertisement",
                    "Ask an unknown social media account for the installer",
                    "Ignore every update notification permanently"
                ],
                0,
                "Trusted update mechanisms reduce the risk of installing fake software updates."
            ),
            (
                "You accidentally send a confidential document to the wrong recipient. What should you do?",
                [
                    "Assume the recipient will delete it",
                    "Post a warning on social media",
                    "Wait until the recipient complains",
                    "Report the incident promptly using the organisation's procedure"
                ],
                3,
                "Prompt incident reporting helps limit the consequences of accidental disclosure."
            ),
            (
                "Which statement best describes cybersecurity awareness?",
                [
                    "It is only the responsibility of technical staff",
                    "It is a one-time activity completed after training",
                    "It involves recognising risks and making safer everyday decisions",
                    "It means avoiding all internet services"
                ],
                2,
                "Cybersecurity awareness means recognising threats and applying safe practices consistently."
            )
        ])
    },
    # 2. PHISHING AWARENESS
    "phishing": {
        "name": "Phishing Awareness",
        "questions": make_questions([
            (
                "An email says your university account will be suspended in 30 minutes unless you sign in using its link. What should you do?",
                [
                    "Use the link quickly to avoid suspension",
                    "Open the university website independently to check your account",
                    "Reply with your password to verify the sender",
                    "Forward the link to classmates for testing"
                ],
                1,
                "Account warnings should be checked through an independently accessed official website."
            ),
            (
                "A message appears to come from your manager, asking you to buy gift cards immediately. What is the strongest warning sign?",
                [
                    "The message uses your manager's first name",
                    "It arrived during working hours",
                    "It requests an unusual urgent purchase outside normal procedures",
                    "It contains a familiar company logo"
                ],
                2,
                "Unexpected financial requests and urgency are common signs of impersonation."
            ),
            (
                "You hover over a link labelled 'Student Portal' and see a different, unfamiliar domain. What is the safest interpretation?",
                [
                    "The link destination may be deceptive and needs independent verification",
                    "The visible label guarantees the destination",
                    "Hovering over links automatically downloads malware",
                    "An unfamiliar domain always means the message is legitimate"
                ],
                0,
                "The real destination of a link matters more than its displayed label."
            ),
            (
                "A suspicious email contains an attachment labelled 'invoice.pdf.exe'. Why is this concerning?",
                [
                    "PDF files cannot be attached to emails",
                    "The filename is too short",
                    "All invoices are malicious",
                    "The final extension indicates an executable file, not an ordinary PDF"
                ],
                3,
                "A double file extension can disguise an executable program as a document."
            ),
            (
                "You entered your password into a website and then realised it was a phishing page. What should you do?",
                [
                    "Wait to see whether anything happens",
                    "Change the password through the legitimate service and report the incident",
                    "Visit the phishing page again to remove your details",
                    "Use the same password on a different account"
                ],
                1,
                "Secure the legitimate account immediately and report the suspected compromise."
            )
        ])
    },
    # 3. PASSWORD & ACCOUNT SECURITY
    "password-security": {
        "name": "Password & Account Security",
        "questions": make_questions([
            (
                "You use the same password for your email and a shopping website. The shopping website suffers a breach. What is the main risk?",
                [
                    "The email account may also be compromised",
                    "The email account will automatically be deleted",
                    "Your internet connection will stop working",
                    "Your shopping history will be erased"
                ],
                0,
                "Password reuse allows attackers to try stolen credentials on other services."
            ),
            (
                "Which approach is generally best for creating passwords?",
                [
                    "Use your date of birth with a symbol",
                    "Use one memorable password everywhere",
                    "Use long, unique passwords or passphrases, preferably managed securely",
                    "Use the website name followed by 123"
                ],
                2,
                "Long, unique passwords are harder to compromise. Password managers can help."
            ),
            (
                "Your password manager warns that one of your saved passwords has appeared in a breach. What should you do?",
                [
                    "Ignore the warning if you still have access",
                    "Change that password and check whether it was reused elsewhere",
                    "Delete the warning message only",
                    "Turn off password manager notifications"
                ],
                1,
                "Compromised passwords should be replaced and reused passwords should be checked."
            ),
            (
                "Someone repeatedly sends authentication approval requests that you did not initiate. What should you do?",
                [
                    "Approve one request to stop the notifications",
                    "Share your authentication code with the caller",
                    "Disable your account security permanently",
                    "Reject the requests and secure or report the account"
                ],
                3,
                "Unexpected authentication requests may indicate an attempted account compromise."
            ),
            (
                "A website offers account recovery codes after you enable multi-factor authentication. How should you handle them?",
                [
                    "Store them securely somewhere separate from your usual login method",
                    "Publish them in a private social media post",
                    "Email them to everyone in your contacts",
                    "Discard them because recovery is never needed"
                ],
                0,
                "Recovery codes provide account access and must be stored securely."
            )
        ])
    },
    # 4. SOCIAL ENGINEERING
    "social-engineering": {
        "name": "Social Engineering",
        "questions": make_questions([
            (
                "A caller claims to be from IT support and asks you to install remote-access software immediately. What should you do?",
                [
                    "Install it because the caller knows your name",
                    "Provide your password before asking questions",
                    "Verify the request through your organisation's official IT support channel",
                    "Allow remote access for five minutes only"
                ],
                2,
                "Unexpected support requests should be verified through official channels."
            ),
            (
                "Someone wearing a delivery uniform asks you to hold open a secure office door because they forgot their access card. What is the safest response?",
                [
                    "Allow entry because the uniform looks genuine",
                    "Follow the building's visitor and access-control procedures",
                    "Give them your own access card",
                    "Leave the door unlocked for future deliveries"
                ],
                1,
                "Tailgating is a social engineering technique used to bypass physical security."
            ),
            (
                "A person on social media offers you a prize but requires your account recovery code first. What tactic are they using?",
                [
                    "Legitimate account verification",
                    "A routine software update",
                    "A secure payment method",
                    "Manipulation using a reward to obtain sensitive information"
                ],
                3,
                "Attackers sometimes offer rewards to persuade victims to disclose confidential information."
            ),
            (
                "A caller says they are a senior manager and demands confidential employee records immediately. What should you do?",
                [
                    "Verify their identity and authorisation using established procedures",
                    "Send the records because senior managers never need verification",
                    "Upload the records to a public file-sharing website",
                    "Ask the caller to confirm only their first name"
                ],
                0,
                "Claims of authority should not bypass normal identity and access checks."
            ),
            (
                "A stranger begins a friendly conversation and gradually asks detailed questions about your workplace security procedures. What should you consider?",
                [
                    "Friendly people cannot be attackers",
                    "Any information is safe if it is shared verbally",
                    "The person may be gathering information for a later attack",
                    "Security information becomes harmless outside the office"
                ],
                2,
                "Social engineers may build trust gradually to gather information."
            )
        ])
    },
    # 5. MALWARE & RANSOMWARE
    "malware-ransomware": {
        "name": "Malware & Ransomware",
        "questions": make_questions([
            (
                "Your computer suddenly displays a message saying your files have been encrypted and payment is required. What should you do?",
                [
                    "Pay immediately without informing anyone",
                    "Disconnect the affected device from networks where safe and report the incident",
                    "Email the encrypted files to colleagues",
                    "Install random recovery tools from advertisements"
                ],
                1,
                "Prompt isolation and reporting can help contain ransomware."
            ),
            (
                "Why is a backup connected permanently to the same computer sometimes insufficient against ransomware?",
                [
                    "Connected backups may also be encrypted or damaged",
                    "Backups cannot contain documents",
                    "Ransomware only affects internet browsers",
                    "Connected storage automatically blocks malware"
                ],
                0,
                "Ransomware may affect accessible backups as well as the original files."
            ),
            (
                "A free software installer offers an unrelated browser extension that is selected by default. What is the safest approach?",
                [
                    "Install everything because the software is free",
                    "Disable security software before continuing",
                    "Accept all optional components without reading",
                    "Review the installer carefully and decline unnecessary additions"
                ],
                3,
                "Bundled software may introduce unwanted or potentially harmful programs."
            ),
            (
                "Your antivirus software quarantines a suspicious file downloaded from an unknown website. What should you do?",
                [
                    "Restore the file immediately",
                    "Send the file to your friends",
                    "Leave it quarantined and follow the security software's guidance",
                    "Disable antivirus protection permanently"
                ],
                2,
                "Quarantine helps prevent suspicious files from running."
            ),
            (
                "What is a realistic benefit of testing your data backups?",
                [
                    "It guarantees no future cyberattack",
                    "It confirms that important files can actually be restored",
                    "It removes the need for access controls",
                    "It makes antivirus software unnecessary"
                ],
                1,
                "Backups are useful only when the required data can be recovered."
            )
        ])
    },
    # 6. SAFE BROWSING & EMAIL SECURITY
    "safe-browsing": {
        "name": "Safe Browsing & Email Security",
        "questions": make_questions([
            (
                "You are about to enter payment details on an unfamiliar online shop. What should you check first?",
                [
                    "Whether the site has colourful advertisements",
                    "Whether the site offers a large discount",
                    "Whether the website and seller are legitimate and the connection is secure",
                    "Whether the page contains customer photographs"
                ],
                2,
                "Check the seller, website address and connection before providing payment information."
            ),
            (
                "Your browser warns that a website's security certificate is invalid. What should you do?",
                [
                    "Avoid entering sensitive information and investigate the warning",
                    "Ignore the warning because every website has one",
                    "Disable browser security checks permanently",
                    "Enter your password to remove the warning"
                ],
                0,
                "Certificate warnings can indicate problems with a site's identity or secure connection."
            ),
            (
                "You receive an email addressed to many recipients, and you need to reply only to the sender. What should you check?",
                [
                    "Whether the message has a colourful signature",
                    "Whether the email was sent in the morning",
                    "Whether your browser is in dark mode",
                    "Whether you selected Reply rather than Reply All"
                ],
                3,
                "Checking recipients prevents accidental disclosure to unnecessary recipients."
            ),
            (
                "A browser pop-up claims your computer is infected and gives a telephone number for urgent technical support. What should you do?",
                [
                    "Call the number and provide remote access",
                    "Close the suspicious page and use trusted security tools if needed",
                    "Enter payment details to remove the warning",
                    "Install the software offered by the pop-up"
                ],
                1,
                "Fake security alerts may attempt to trick users into contacting scammers."
            ),
            (
                "An email includes a shortened URL that hides its destination. What is the safest approach?",
                [
                    "Assume shortened links are always safe",
                    "Click it because it is easier to read",
                    "Verify the destination or access the intended website independently",
                    "Forward it to others to check"
                ],
                2,
                "Shortened links can conceal deceptive or malicious destinations."
            )
        ])
    },
    # 7. ONLINE PRIVACY & PERSONAL DATA
    "online-privacy": {
        "name": "Online Privacy & Personal Data",
        "questions": make_questions([
            (
                "A social media app makes your profile publicly visible by default. What should you do if you want to limit who sees your posts?",
                [
                    "Review and adjust the account's privacy settings",
                    "Post your password to warn other users",
                    "Delete your device's security updates",
                    "Accept every new follower automatically"
                ],
                0,
                "Privacy settings help control who can view your shared information."
            ),
            (
                "A shopping website asks for your home address when you are only subscribing to a newsletter. What should you consider?",
                [
                    "Every website needs your full address",
                    "The information is automatically anonymous",
                    "Giving extra information always improves security",
                    "Whether the information is genuinely necessary for the service"
                ],
                3,
                "Avoid providing personal information that is not needed for the service."
            ),
            (
                "A navigation app requests permanent access to your location, but it only needs location for a single search. What is the better choice?",
                [
                    "Allow permanent access to avoid prompts",
                    "Choose access only while using the app, or only when needed",
                    "Share your location publicly instead",
                    "Disable every other privacy setting"
                ],
                1,
                "Limiting location permissions reduces unnecessary collection of sensitive information."
            ),
            (
                "Why might combining your birthday, school and pet's name in public posts be risky?",
                [
                    "It prevents account recovery",
                    "It automatically publishes your passwords",
                    "It makes your internet connection less secure",
                    "It can help attackers guess security answers or craft convincing scams"
                ],
                3,
                "Public personal details may help attackers impersonate you or target you."
            ),
            (
                "What is data minimisation when signing up for an online service?",
                [
                    "Using the same password for every service",
                    "Making every profile public",
                    "Providing only the personal information genuinely required",
                    "Giving a false identity in every situation"
                ],
                2,
                "Data minimisation limits collection and disclosure to necessary information."
            )
        ])
    },
    # 8. PUBLIC WI-FI & NETWORK SAFETY
    "public-wifi": {
        "name": "Public Wi-Fi & Network Safety",
        "questions": make_questions([
            (
                "You see two cafe Wi-Fi networks with nearly identical names. What should you do before connecting?",
                [
                    "Choose the one with the strongest signal",
                    "Connect to both and compare speeds",
                    "Ask another customer for their password",
                    "Confirm the official network name with cafe staff"
                ],
                3,
                "Attackers may create lookalike hotspots to impersonate legitimate networks."
            ),
            (
                "Your laptop automatically connects to an open hotspot you used months ago. What is the best security improvement?",
                [
                    "Disable automatic joining for untrusted networks",
                    "Turn off the laptop's screen lock",
                    "Share files with nearby devices",
                    "Use the hotspot for banking immediately"
                ],
                0,
                "Disabling automatic connections reduces exposure to untrusted networks."
            ),
            (
                "You need to access a sensitive work system while travelling. Which option is generally preferable?",
                [
                    "Any open network without a password",
                    "A trusted connection using your organisation's approved security controls",
                    "A hotspot advertised by an unknown pop-up",
                    "The first Wi-Fi name that contains 'secure'"
                ],
                1,
                "Use trusted connections and follow organisational security policies."
            ),
            (
                "What is the main risk of leaving file sharing enabled on an untrusted public network?",
                [
                    "It makes your battery charge faster",
                    "It automatically backs up all files",
                    "Other devices may be able to discover or access shared resources",
                    "It prevents encrypted websites from loading"
                ],
                2,
                "Network sharing may expose files and services to nearby devices."
            ),
            (
                "A public Wi-Fi login page asks for your main email password even though the venue did not mention an account requirement. What should you do?",
                [
                    "Enter the password if the page has a logo",
                    "Try the password twice to confirm the page works",
                    "Send the password to venue staff by email",
                    "Stop and verify the request with venue staff before entering credentials"
                ],
                3,
                "Unexpected password requests may indicate a deceptive hotspot or login page."
            )
        ])
    },
    # 9. DEVICE & SOFTWARE SECURITY
    "device-security": {
        "name": "Device & Software Security",
        "questions": make_questions([
            (
                "Your phone is lost while signed in to several important accounts. What should you do first?",
                [
                    "Use available device-location or remote-lock tools and secure affected accounts",
                    "Wait for someone to return it before taking action",
                    "Post your unlock PIN online to help the finder",
                    "Turn off multi-factor authentication on all accounts"
                ],
                0,
                "Remote locking and account protection help limit exposure after device loss."
            ),
            (
                "Why is enabling automatic security updates often helpful?",
                [
                    "It removes the need for backups",
                    "It ensures every downloaded application is trustworthy",
                    "It reduces the time a device remains exposed to known vulnerabilities",
                    "It prevents all physical theft"
                ],
                2,
                "Automatic security updates help address known vulnerabilities promptly."
            ),
            (
                "A newly installed app requests administrator privileges without explaining why. What should you do?",
                [
                    "Approve because administrator access is always required",
                    "Decline and investigate whether the app genuinely needs those privileges",
                    "Disable antivirus software before approving",
                    "Share the administrator password with the app developer"
                ],
                1,
                "Unnecessary administrator privileges can increase security risks."
            ),
            (
                "What is the main purpose of full-disk encryption on a laptop?",
                [
                    "To prevent the laptop from being stolen",
                    "To improve wireless signal strength",
                    "To guarantee that malware cannot run",
                    "To protect stored data from unauthorised reading if the device is lost"
                ],
                3,
                "Full-disk encryption protects stored data if a device is lost or stolen."
            ),
            (
                "A work computer has been unused for several months. What should you do before using it for sensitive tasks?",
                [
                    "Install approved security updates and check its protection status",
                    "Disable its screen lock for convenience",
                    "Connect unknown USB devices to test the ports",
                    "Ignore all update prompts because it still starts"
                ],
                0,
                "Devices that have missed security updates may contain known vulnerabilities."
            )
        ])
    }
}


@app.route("/quizzes")
def quiz_centre():
    if "username" not in session:
        return redirect(url_for("login", next="quizzes"))
    return render_template(
        "quizzes.html",
        quizzes=quizzes
    )

@app.route("/quiz/<quiz_id>", methods=["GET", "POST"])
def take_quiz(quiz_id):
    if "username" not in session:
        return redirect("/login")
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

@app.route("/quiz")
def old_quiz_route():
    if "username" not in session:
        return redirect("/login")
    return redirect("/quiz/general")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/dashboard")
def dashboard():
    if "username" not in session:
        return redirect("/login")
    username = session["username"]
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
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
    best_results = {}
    for quiz_name, score, total, percentage in results:
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
    certificate_eligible = (
        completed_quizzes == total_quizzes
        and all(
            result["best_percentage"] is not None
            and result["best_percentage"] >= 70
            for result in quiz_progress
        )
    )
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
        overall_percentage=overall_percentage,
        certificate_eligible=certificate_eligible
    )

@app.route("/certificate")
def certificate():
    if "username" not in session:
        return redirect("/login")
    username = session["username"]
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    # Retrieve all quiz attempts in chronological order.
    # The database already stores the date of each attempt.
    cursor.execute(
        """
        SELECT quiz_name, score, total, percentage, date_taken, id
        FROM quiz_results
        WHERE username = ?
        ORDER BY date_taken ASC, id ASC
        """,
        (username,)
    )
    attempts = cursor.fetchall()
    conn.close()
    # Quiz names that count towards the certificate
    required_quizzes = {
        quiz_data["name"]: len(quiz_data["questions"])
        for quiz_data in quizzes.values()
    }
    # Track the highest percentage achieved in each quiz.
    best_percentages = {}
    # The first moment all quizzes reached 70%.
    first_completion_date = None
    for quiz_name, score, total, percentage, date_taken, attempt_id in attempts:
        # Support results saved under the older General quiz name
        if quiz_name == "General Cybersecurity":
            quiz_name = "General Cybersecurity Awareness"
        # Ignore results from quizzes that are no longer part
        # of the application.
        if quiz_name not in required_quizzes:
            continue
        # Keep the best percentage reached so far.
        if quiz_name not in best_percentages:
            best_percentages[quiz_name] = percentage
        else:
            best_percentages[quiz_name] = max(
                best_percentages[quiz_name],
                percentage
            )
        # Check whether the user has qualified at this point.
        qualified = all(
            best_percentages.get(required_name, 0) >= 70
            for required_name in required_quizzes
        )
        if qualified:
            first_completion_date = date_taken
            break
    # Users who have not qualified cannot access the certificate.
    if first_completion_date is None:
        return redirect("/dashboard")
    # Calculate the current best overall achievement using
    # all attempts, including retakes after qualification.
    best_results = {}
    for quiz_name, score, total, percentage, date_taken, attempt_id in attempts:
        if quiz_name == "General Cybersecurity":
            quiz_name = "General Cybersecurity Awareness"
        if quiz_name not in required_quizzes:
            continue
        if (
            quiz_name not in best_results
            or percentage > best_results[quiz_name]["percentage"]
        ):
            best_results[quiz_name] = {
                "score": score,
                "total": total,
                "percentage": percentage
            }
    total_best_points = 0
    total_available_points = 0
    for quiz_name, question_count in required_quizzes.items():
        best_percentage = best_results[quiz_name]["percentage"]
        total_best_points += (
            best_percentage / 100
        ) * question_count
        total_available_points += question_count
    overall_percentage = (
        (total_best_points / total_available_points) * 100
        if total_available_points > 0 else 0
    )
    # Convert the saved SQLite timestamp into a readable date.
    from datetime import datetime
    completion_date = datetime.strptime(
        first_completion_date,
        "%Y-%m-%d %H:%M:%S"
    ).strftime("%d %B %Y")
    return render_template(
        "certificate.html",
        username=username,
        completion_date=completion_date,
        overall_percentage=overall_percentage
    )

@app.route("/feedback", methods=["GET", "POST"])
def feedback():

    
    if request.method == "POST":
        if request.form.get("consent") != "yes":
            return "Please confirm consent before submitting feedback.", 400
        try:
            ratings = [int(request.form[f"q{i}"]) for i in range(1, 11)]
        except (KeyError, ValueError):
            return "Please answer all ten rating questions.", 400
        if any(not 1 <= rating <= 5 for rating in ratings):
            return "Ratings must be between 1 and 5.", 400
        positive = request.form.get("positive_feedback", "").strip()
        improvements = request.form.get("improvement_feedback", "").strip()
        if len(positive) > 1000 or len(improvements) > 1000:
            return "Written feedback must be no longer than 1000 characters.", 400
        columns = [f"q{i}" for i in range(1, 11)] + ["positive_feedback", "improvement_feedback"]
        placeholders = ", ".join("?" for _ in columns)
        with sqlite3.connect("users.db") as conn:
            conn.execute(
                f"INSERT INTO evaluation_feedback ({', '.join(columns)}) VALUES ({placeholders})",
                [*ratings, positive, improvements]
            )
        return redirect(url_for("feedback_success"))
    return render_template("feedback.html")


@app.route("/feedback/success")
def feedback_success():
    return render_template("feedback_success.html")


@app.route("/researcher-dashboard")
def researcher_dashboard():
    if session.get("user_id") != RESEARCHER_USER_ID:
        return "Access denied. Researcher only.", 403
    conn = sqlite3.connect("users.db")
    conn.row_factory = sqlite3.Row
    responses = [
        dict(row)
        for row in conn.execute("""
            SELECT *
            FROM evaluation_feedback
            ORDER BY submitted_at DESC, id DESC
        """).fetchall()
    ]
    conn.close()
    question_averages = []
    for number in range(1, 11):
        values = [response[f"q{number}"] for response in responses]
        average = sum(values) / len(values) if values else 0
        question_averages.append(round(average, 2))
    return render_template(
        "researcher_dashboard.html",
        responses=responses,
        total_responses=len(responses),
        question_averages=question_averages
    )

if __name__ == "__main__":
    app.run(debug=True, port=5001)
