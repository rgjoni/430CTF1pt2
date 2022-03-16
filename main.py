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

# start the flask app. the name of this program is passed to the constructor
app = Flask(__name__)




# base page (if no path is specified. this is just a backup)
@app.route("/")
# "/" URL is bound with hello_world() function.
def base():
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
    users = conn.execute("SELECT balance AS id, * FROM users WHERE username = ?;", (username, )).fetchone()
    if users is not None:
        return make_response(f"error: user <i>{username}</i> already exists. no new user was created", 400)

    # create a new user
    conn.execute("INSERT INTO users (username, password, balance) VALUES (?, ?, ?)", (username, password, 0))
    conn.commit()
    return f"user {username} was created"




# log in as an existing user
@app.route("/blue/login", methods=["GET"])
def handle_login():
    # get username and password
    username = request.args.get("user")
    password = request.args.get("pass")
    users = conn.execute("SELECT password, * FROM users WHERE username = ?;", (username, )).fetchone()

    if users is None:
        return "user not found"

    # attempt to log in the user
    if sha256_crypt.verify(password, users[0]):     # valid user
        resp = make_response(f"logged in as {username}")
        resp.set_cookie("username", username)
        return resp
    else:                                           # invalid user
        return make_response("invalid login attempt", 400)




# do transactions and whatnot
@app.route("/blue/manage", methods=["GET"])
def action_handler():
    action = request.args.get("action")
    amount = request.args.get("amount")

    username = request.cookies.get("username")
    # todo if invalid?

    # add funds
    if action == "deposit":
        print(request.cookies.get("username"))
        users = conn.execute("SELECT balance AS id, * FROM users WHERE username = ?;", (request.cookies.get("username"), )).fetchone()
        if users is None:
            return "err"
        new_amount = users[0]
        new_amount = new_amount + int(amount)
        conn.execute("UPDATE users SET balance = ? WHERE username = ?;", (new_amount, request.cookies.get("username")))
        conn.commit()
        return str(new_amount)

    # withdraw funds
    elif action == "withdraw":
        users = conn.execute("SELECT balance AS id, * FROM users WHERE username = ?;", (request.cookies.get("username"), )).fetchone()
        if users is None:
            return "err"
        new_amount = users[0]
        new_amount = new_amount - int(amount)
        conn.execute("UPDATE users SET balance = ? WHERE username = ?;", (new_amount, request.cookies.get("username")))
        conn.commit()
        return str(new_amount)

    # check the current balance
    elif action == "balance":
        users = conn.execute("SELECT balance AS id, * FROM users WHERE username = ?;", (request.cookies.get("username"), )).fetchone()
        if users is None:
            return "err"
        new_amount = users[0]
        print(new_amount)
        return str(new_amount)

    # close the account (delete the user from the database)
    elif action == "close":
        conn.execute("DELETE FROM users WHERE username = ?", (request.cookies.get("username"), ))
        conn.commit()
        resp = make_response()
        resp.set_cookie("username", "", expires=0)
        return resp




# let the user log out
@app.route("/blue/logout", methods=["GET"])
def handle_logout():
    resp = make_response()
    resp.set_cookie("username", "", expires=0)
    return resp







# main driver function
if __name__ == "__main__":
    # connect to the database
    conn = sqlite3.connect("database.db", check_same_thread=False)
    with open("database.sql") as f:
        conn.executescript(f.read())

    cur = conn.cursor()
    conn.commit()

    # port is an optional command line argument
    if len(sys.argv) > 1:
        port = int(sys.argv[1])

    app.run(host=hostname, port=port)
