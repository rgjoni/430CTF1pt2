"""
    some notes:
    returning a string (from flask) makes the server send a 200 response.
    technically, the mimetype is incorrect (HTML instead of plaintext), but this
    is just a small CTF project, so it's not a big deal

    also, when you call execute() for sqlite, you need to pass in a tuple. so
    even if there's just one thing being passed in, just pass a tuple with blank
    arguments. there will be an extra comma. it can look like `(username, )`

    another thing to note is that the database resets every time the server is
    restarted. it's just a CTF exercise, so again, not a big deal
"""

# importing flask module in the project is mandatory
# an object of flask class is our wsgi application
from flask import Flask, request, render_template, redirect, g, make_response
import sqlite3
import sys      # to get args (when this program is invoked from command line)
from passlib.hash import sha256_crypt




hostname = "localhost"
port = 5001             # might be overridden
conn = None             # global variable

# start the flask app. the name of this program is passed to the constructor
app = Flask(__name__)




# base page (if no path is specified. this is just a backup)
@app.route("/")
# "/" URL is bound with hello_world() function.
def handle_base():
    return "welcome to the bank"




# similar to the base page above. this should not be called
@app.route("/blue", methods=["GET"])
def handle_main():
    return "welcome to the blue bank"




# register a new user
@app.route("/blue/register", methods=["GET"])
def handle_register():
    # get username and password
    username = request.args.get("user")
    password = request.args.get("pass")

    if not username or not password:
        return make_response("error: missing username and/or password", 400)

    password = sha256_crypt.hash(password)

    # check for duplicates
    global conn
    users = conn.execute("SELECT balance AS id, * FROM users WHERE username = ?;", (username, )).fetchone()
    if users is not None:
        return make_response(f"error: user <i>{username}</i> already exists. no new user was created", 400)

    # create a new user
    conn.execute("INSERT INTO users (username, password, balance) VALUES (?, ?, ?)", (username, password, 0))
    conn.commit()
    return f"user <i>{username}</i> was created"




# log in as an existing user
@app.route("/blue/login", methods=["GET"])
def handle_login():
    # get username and password
    username = request.args.get("user")
    password = request.args.get("pass")

    global conn
    users = conn.execute("SELECT password, * FROM users WHERE username = ?;", (username, )).fetchone()

    if users is None:
        return make_response("user not found", 400)

    # attempt to log in the user
    if sha256_crypt.verify(password, users[0]):     # valid user
        resp = make_response(f"logged in as <i>{username}</i>")
        resp.set_cookie("username", username)
        return resp
    else:                                           # invalid user
        return make_response("invalid login attempt", 400)




def is_valid_amount(amount):
    """
    returns whether or not it's a valid transaction amount. see the README for
    details. dont forget to round the value after checking

    :param amount: the amount to test
    :type amount: str
    :return: True if valid amount. False otherwise
    """
    return amount.replace(".", "", 1).isdecimal()

def convert_amount(amount):
    """
    converts the amount into an integer, or None if invalid
    :param amount: amount to convert
    :type amount: str
    :return: integer form of the amount, or None if invalid
    """
    if not is_valid_amount(amount):
        return None

    return int(round(float(amount)))




# do transactions and whatnot
@app.route("/blue/manage", methods=["GET"])
def action_handler():
    action = request.args.get("action")
    amount = request.args.get("amount")

    # check if the user has a username cookie
    username = request.cookies.get("username")
    if not username:
        return make_response("error: you need to log in to do this", 400)

    # check if the user exists in the database
    global conn  # connection to the sqlite database
    users = conn.execute("SELECT balance AS id, * FROM users WHERE username = ?;", (username, )).fetchone()
    if not users:
        return make_response("error: invalid user", 400)
    balance = users[0]


    # add funds
    if action == "deposit":
        amount = convert_amount(amount)
        if amount is None:
            return make_response("error: invalid amount", 400)

        if amount > 0:      # ignore database if amount == 0
            balance += amount
            conn.execute("UPDATE users SET balance = ? WHERE username = ?;", (balance, username))
            conn.commit()

        return f"deposited {amount}. balance={balance}"


    # withdraw funds
    elif action == "withdraw":
        amount = convert_amount(amount)
        if amount is None:
            return make_response("error: invalid amount", 400)

        if amount > balance:
            return make_response("error: cannot withdraw more than account balance", 400)

        # at this point, we should be good to go make a withdrawal
        if amount > 0:  # ignore database if amount == 0
            balance -= amount
            conn.execute("UPDATE users SET balance = ? WHERE username = ?;", (balance, username))
            conn.commit()

        return f"withdrew {amount}. balance={balance}"


    # check the current balance
    elif action == "balance":
        return f"balance={balance}"


    # close the account (delete the user from the database)
    elif action == "close":
        conn.execute("DELETE FROM users WHERE username = ?", (username, ))
        conn.commit()
        resp = make_response(f"user <i>{username}</i> was deleted")
        resp.set_cookie("username", "", expires=0)
        return resp


    # else, action is invalid
    return make_response("error: invalid action", 400)




# let the user log out
@app.route("/blue/logout", methods=["GET"])
def handle_logout():
    resp = make_response(f"successfully logged out")
    resp.set_cookie("username", "", expires=0)
    return resp








# main driver function
if __name__ == "__main__":
    # connect to the database
    # `conn` is a global variable defined above
    conn = sqlite3.connect("database.db", check_same_thread=False)
    with open("database.sql") as db:
        conn.executescript(db.read())

    cur = conn.cursor()
    conn.commit()

    # port is an optional command line argument
    if len(sys.argv) > 1:
        port = int(sys.argv[1])

    app.run(host=hostname, port=port)

