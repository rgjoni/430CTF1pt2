# importing flask module in the project is mandatory
# an object of flask class is our wsgi application
from flask import Flask, request, render_template, redirect, g, make_response
import sqlite3
from passlib.hash import sha256_crypt




hostname = "localhost"
port = 5001
address = "http://" + hostname + ":" + str(port)

# start the flask app. the name of this program is passed to the constructor
app = Flask(__name__)




# base page (if no path is specified. this is just a backup)
@app.route("/")
# "/" URL is bound with hello_world() function.
def base():
    return "base page\n"




# similar to the base page above. this should not be called
@app.route("/blue", methods=["GET"])
def handle_main():
    return "main page\n"




# register a new user
@app.route("/blue/register", methods=["GET"])
def handle_register():
    # get username and password
    user = request.args.get("user")
    password = request.args.get("pass")
    password = sha256_crypt.hash(password)

    # check for duplicates
    users = conn.execute("SELECT balance AS id, * FROM users WHERE username = ?;", (user,)).fetchone()
    if users is not None:
        return "error: duplicate entry\n"

    # create a new user
    conn.execute("INSERT INTO users (username, password, balance) VALUES (?, ?, ?)", (user, password, 0))
    conn.commit()
    resp = make_response()
    return resp




# log in as an existing user
@app.route("/blue/login", methods=["GET"])
def handle_login():
    # get username and password
    user = request.args.get("user")
    password = request.args.get("pass")
    users = conn.execute("SELECT password, * FROM users WHERE username = ?;", (user,)).fetchone()

    if users is None:
        return "user not found\n"

    # attempt to log in the user
    if sha256_crypt.verify(password, users[0]):     # valid user
        resp = make_response()
        resp.set_cookie("username", user)
        return resp
    else:                                           # invalid user
        resp = make_response()
        return resp




# do transactions and whatnot
@app.route("/blue/manage", methods=["GET"])
def action_handler():
    action = request.args.get("action")
    amount = request.args.get("amount")

    # add funds
    if action == "deposit":
        print(request.cookies.get("username"))
        users = conn.execute("SELECT balance AS id, * FROM users WHERE username = ?;", (request.cookies.get("username"),)).fetchone()
        if users is None:
            return "err"
        new_amount = users[0]
        new_amount = new_amount + int(amount)
        conn.execute("UPDATE users SET balance = ? WHERE username = ?;", (new_amount, request.cookies.get("username")))
        conn.commit()
        return str(new_amount)

    # withdraw funds
    elif action == "withdraw":
        users = conn.execute("SELECT balance AS id, * FROM users WHERE username = ?;", (request.cookies.get("username"),)).fetchone()
        if users is None:
            return "err"
        new_amount = users[0]
        new_amount = new_amount - int(amount)
        conn.execute("UPDATE users SET balance = ? WHERE username = ?;", (new_amount, request.cookies.get("username")))
        conn.commit()
        return str(new_amount)

    # check the current balance
    elif action == "balance":
        users = conn.execute("SELECT balance AS id, * FROM users WHERE username = ?;", (request.cookies.get("username"),)).fetchone()
        if users is None:
            return "err"
        new_amount = users[0]
        print(new_amount)
        return str(new_amount)

    # close the account (delete the user from the database)
    elif action == "close":
        conn.execute("DELETE FROM users WHERE username = ?", (request.cookies.get("username"),))
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

    app.run(host=hostname, port=port)
