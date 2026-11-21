from flask import Flask, request, render_template_string
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)


# Database connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="sri789&&",
        database="login_db"
    )


# Home page: Login and Create Account
@app.route("/")
def home():

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>User Authentication System</title>

        <style>
            body {
                font-family: Arial;
                background-color: #f2f2f2;
                text-align: center;
                margin-top: 50px;
            }

            .container {
                background: white;
                width: 350px;
                margin: auto;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 0 10px gray;
            }

            input {
                padding: 10px;
                width: 90%;
                margin: 10px;
            }

            button {
                padding: 10px 20px;
                background-color: blue;
                color: white;
                border: none;
                cursor: pointer;
            }

            a {
                text-decoration: none;
                color: blue;
            }
        </style>
    </head>

    <body>

        <div class="container">

            <h1>User Authentication</h1>

            <h2>Login</h2>

            <form action="/login" method="POST">

                <input type="text"
                       name="username"
                       placeholder="Enter Username"
                       required>

                <input type="password"
                       name="password"
                       placeholder="Enter Password"
                       required>

                <br>

                <button type="submit">Login</button>

            </form>

            <hr>

            <h2>Create Account</h2>

            <p>New user?</p>

            <a href="/register">
                Create a New Account
            </a>

        </div>

    </body>
    </html>
    """)


# Create account page
@app.route("/register")
def register_page():

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Create Account</title>
    </head>

    <body style="text-align:center; font-family:Arial;">

        <h1>Create Account</h1>

        <form action="/register" method="POST">

            <input type="text"
                   name="username"
                   placeholder="Enter Username"
                   required>

            <br><br>

            <input type="password"
                   name="password"
                   placeholder="Enter Password"
                   required>

            <br><br>

            <button type="submit">Create Account</button>

        </form>

        <br>

        <a href="/">Back to Login</a>

    </body>
    </html>
    """)


# Register new account
@app.route("/register", methods=["POST"])
def register():

    username = request.form["username"]
    password = request.form["password"]

    # Encrypt the password
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

        return render_template_string("""
        <html>
        <body style="text-align:center; font-family:Arial;">

            <h1 style="color:green;">
                Account Created Successfully!
            </h1>

            <p>Your account has been registered.</p>

            <a href="/">Login Now</a>

        </body>
        </html>
        """)

    except mysql.connector.IntegrityError:

        return render_template_string("""
        <html>
        <body style="text-align:center; font-family:Arial;">

            <h1 style="color:red;">
                Registration Failed!
            </h1>

            <p>Username already exists.</p>

            <a href="/register">Try Again</a>

        </body>
        </html>
        """)

    finally:

        cursor.close()
        connection.close()


# Login validation
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

    if result:

        stored_password = result[0]

        if check_password_hash(stored_password, password):

            return render_template_string("""
            <html>
            <body style="text-align:center; font-family:Arial;">

                <h1 style="color:green;">
                    Login Successful!
                </h1>

                <h2>Welcome, {{ username }}!</h2>

                <p>You have successfully logged in.</p>

                <a href="/">Logout</a>

            </body>
            </html>
            """, username=username)

    return render_template_string("""
    <html>
    <body style="text-align:center; font-family:Arial;">

        <h1 style="color:red;">
            Login Failed!
        </h1>

        <p>Invalid username or password.</p>

        <a href="/">Try Again</a>

    </body>
    </html>
    """)


# Run application
if __name__ == "__main__":
    app.run(debug=True)