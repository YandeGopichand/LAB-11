from flask import Flask, request, render_template
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)


# ==========================================
# DATABASE CONNECTION
# ==========================================

def get_db_connection():

    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="sri789&&",
        database="login_db"
    )

    return connection


# ==========================================
# HOME PAGE
# ==========================================

@app.route("/")
def home():

    return render_template("index.html")


# ==========================================
# REGISTER PAGE
# ==========================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "GET":

        return render_template("register.html")


    username = request.form["username"]
    password = request.form["password"]

    # Hash the password
    hashed_password = generate_password_hash(password)

    connection = get_db_connection()
    cursor = connection.cursor()

    try:

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
            message="Username already exists. Please try another username.",
            color="red",
            link="/register",
            link_text="Try Again"
        )


    finally:

        cursor.close()
        connection.close()


# ==========================================
# LOGIN
# ==========================================

@app.route("/login", methods=["POST"])
def login():

    username = request.form["username"]
    password = request.form["password"]

    connection = get_db_connection()
    cursor = connection.cursor()

    query = """
    SELECT password
    FROM accounts
    WHERE username = %s
    """

    cursor.execute(query, (username,))

    result = cursor.fetchone()

    cursor.close()
    connection.close()


    # Check user credentials

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


    # Invalid credentials

    return render_template(
        "result.html",
        title="Login Failed!",
        message="Invalid username or password.",
        color="red",
        link="/",
        link_text="Try Again"
    )


# ==========================================
# RUN APPLICATION
# ==========================================

if __name__ == "__main__":

    app.run(debug=True)