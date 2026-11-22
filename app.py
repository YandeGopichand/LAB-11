from flask import Flask, request, render_template
import mysql.connector
import os

from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# ==========================================
# DATABASE CONNECTION
# ==========================================

def get_db_connection():

    connection = mysql.connector.connect(
        host=os.environ.get("MYSQLHOST"),
        port=int(os.environ.get("MYSQLPORT", 3306)),
        user=os.environ.get("MYSQLUSER"),
        password=os.environ.get("MYSQLPASSWORD"),
        database=os.environ.get("MYSQLDATABASE"),
        connection_timeout=10
    )

    return connection


# ==========================================
# HEALTH CHECK
# ==========================================

@app.route("/health")
def health():

    return "Application is running successfully!", 200


# ==========================================
# HOME PAGE
# ==========================================

@app.route("/")
def home():

    return render_template("index.html")


# ==========================================
# REGISTER
# ==========================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "GET":
        return render_template("register.html")

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    if not username or not password:

        return render_template(
            "result.html",
            title="Registration Failed!",
            message="Username and password are required.",
            color="red",
            link="/register",
            link_text="Try Again"
        )

    if len(password) < 8:

        return render_template(
            "result.html",
            title="Registration Failed!",
            message="Password must contain at least 8 characters.",
            color="red",
            link="/register",
            link_text="Try Again"
        )

    hashed_password = generate_password_hash(password)

    connection = None
    cursor = None

    try:

        connection = get_db_connection()
        cursor = connection.cursor()

        query = """
            INSERT INTO accounts (username, password)
            VALUES (%s, %s)
        """

        cursor.execute(query, (username, hashed_password))
        connection.commit()

        return render_template(
            "result.html",
            title="Registration Successful!",
            message="Your account has been created successfully.",
            color="green",
            link="/",
            link_text="Login Now"
        )

    except mysql.connector.IntegrityError:

        return render_template(
            "result.html",
            title="Registration Failed!",
            message="Username already exists. Please choose another username.",
            color="red",
            link="/register",
            link_text="Try Again"
        )

    except mysql.connector.Error as error:

        print("Database Error:", error)

        return render_template(
            "result.html",
            title="Database Error",
            message="Unable to connect to the database.",
            color="red",
            link="/register",
            link_text="Try Again"
        )

    except Exception as error:

        print("Registration Error:", error)

        return render_template(
            "result.html",
            title="Server Error",
            message="Unable to register currently. Please try again later.",
            color="red",
            link="/register",
            link_text="Try Again"
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ==========================================
# LOGIN
# ==========================================

@app.route("/login", methods=["POST"])
def login():

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    if not username or not password:

        return render_template(
            "result.html",
            title="Login Failed!",
            message="Username and password are required.",
            color="red",
            link="/",
            link_text="Try Again"
        )

    connection = None
    cursor = None

    try:

        connection = get_db_connection()
        cursor = connection.cursor()

        query = """
            SELECT password
            FROM accounts
            WHERE username = %s
        """

        cursor.execute(query, (username,))
        result = cursor.fetchone()

        if result:

            stored_password = result[0]

            if check_password_hash(stored_password, password):

                return render_template(
                    "result.html",
                    title="Login Successful!",
                    message=f"Welcome, {username}! You have successfully logged in.",
                    color="green",
                    link="/",
                    link_text="Logout"
                )

        return render_template(
            "result.html",
            title="Login Failed!",
            message="Invalid username or password.",
            color="red",
            link="/",
            link_text="Try Again"
        )

    except mysql.connector.Error as error:

        print("Database Error:", error)

        return render_template(
            "result.html",
            title="Database Error",
            message="Unable to connect to the database. Please try again later.",
            color="red",
            link="/",
            link_text="Back to Login"
        )

    except Exception as error:

        print("Login Error:", error)

        return render_template(
            "result.html",
            title="Server Error",
            message="Something went wrong. Please try again later.",
            color="red",
            link="/",
            link_text="Back to Login"
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ==========================================
# APPLICATION START
# ==========================================

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))

    app.run(host="0.0.0.0", port=port, debug=False)