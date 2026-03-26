from flask import Flask, request, redirect, render_template, session, url_for
import mysql.connector
import re

app = Flask(__name__)
app.secret_key = "2026_campus_incidents_secret_key"#This can be change

#This is a connection helper file for the campus incident reporting system. 
#It includes database connection, input validation, user management, 
#and route handling for login, registration, and dashboard access.

# -----------------------------
# Database Connection Helper
# -----------------------------
def get_db():
    return mysql.connector.connect(
        host="127.0.0.1",
        port=3307,
        user="root",
        password="",
        database="campus_incidents_db",
    )


# -----------------------------
# Input Validation
# -----------------------------
def validate_input(username: str, password: str):
    errors = []

    if not re.match(r"^[a-zA-Z0-9_]{3,50}$", username or ""):
        errors.append("Username must be 3–50 chars and only letters, numbers, underscores.")

    if password is None or len(password) < 4:
        errors.append("Password must be at least 4 characters.")

    return errors


# -----------------------------
# Helpers
# -----------------------------
def user_exists(username: str) -> bool:
    db = None
    cursor = None
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT 1 FROM users WHERE username = %s LIMIT 1", (username,))
        return cursor.fetchone() is not None
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()


def create_user(username: str, password: str):
    """Plain-text registration (NOT secure; for now only)."""
    errors = validate_input(username, password)
    if errors:
        return errors

    if user_exists(username):
        return ["Username already exists. Please choose another."]

    db = None
    cursor = None
    try:
        db = get_db()
        cursor = db.cursor()

        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
            (username, password),
        )
        db.commit()
        return None
    except Exception as e:
        return [f"Database error: {e}"]
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()


# -----------------------------
# Routes
# -----------------------------
@app.route("/")
def home():
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        errors = validate_input(username, password)
        if errors:
            return render_template("index.html", error=errors[0])

        db = None
        cursor = None
        try:
            db = get_db()
            cursor = db.cursor(dictionary=True)

            cursor.execute("""
                SELECT user_id, username, password_hash, role, status
                FROM users
                WHERE username = %s
                LIMIT 1
            """, (username,))

            user = cursor.fetchone()

            if not user:
                return render_template("index.html", error="User not found.")

            if user.get("status") != "ACTIVE":
                return render_template("index.html", error="Account is inactive.")

            
            if password == (user.get("password_hash") or ""):
                session["user_id"] = user["user_id"]
                session["username"] = user["username"]
                session["role"] = user.get("role", "staff")
                return redirect("/dashboard")
            else:
                return render_template("index.html", error="Wrong password.")

        except Exception as e:
            return render_template("index.html", error=f"DB Error: {e}")

        finally:
            if cursor:
                cursor.close()
            if db:
                db.close()

    return render_template("index.html")


@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.json or {}
    username = (data.get("username") or "").strip()
    password = (data.get("password") or "").strip()

    errors = validate_input(username, password)
    if errors:
        return {"error": errors[0]}, 400

    db = None
    cur = None
    try:
        db = get_db()
        cur = db.cursor(dictionary=True)
        cur.execute("SELECT user_id, username, password_hash, role, status FROM users WHERE username=%s LIMIT 1", (username,))
        user = cur.fetchone()

        if not user:
            return {"error": "Unauthorized"}, 401

        if user.get("status") != "ACTIVE":
            return {"error": "Account is inactive"}, 403

        
        if password != (user.get("password_hash") or ""):
            return {"error": "Unauthorized"}, 401

        return {
            "message": "Login success",
            "user_id": user["user_id"],
            "role": user.get("role", "staff")
        }, 200

    finally:
        if cur:
            cur.close()
        if db:
            db.close()


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        errors = create_user(username, password)
        if errors:
            return render_template("register.html", errors=errors, username=username), 400

        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html", username=session.get("username"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/test-db")
def test_db():
    db = None
    cursor = None
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT DATABASE()")
        name = cursor.fetchone()[0]
        return f"Connected ✅ DB: {name}"
    except Exception as e:
        return f"Failed ❌ {e}", 500
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()


if __name__ == "__main__":
    app.run(debug=True)
    
    
