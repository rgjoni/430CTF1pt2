# Importing flask module in the project is mandatory
# An object of Flask class is our WSGI application.
from flask import Flask, request, render_template, redirect, g, make_response
import sqlite3
from passlib.hash import sha256_crypt

hostname = "localhost"
port = 5001
address = "http://" + hostname + ":" + str(port)

# Flask constructor takes the name of
# current module (__name__) as argument.
app = Flask(__name__)


# The route() function of the Flask class is a decorator,
# which tells the application which URL should call
# the associated function.
@app.route('/')
# ‘/’ URL is bound with hello_world() function.
def base():
    return 'Base page'

@app.route('/blue', methods=['GET'])
def handle_main():
    return 'Main Page'



    
@app.route('/blue/register', methods=['GET'])
def handle_register():
    print("in reg")
    user = request.args.get("user")
    password = request.args.get("pass")
    print(password)
    password = sha256_crypt.encrypt(password)
    print(user)
    print(password)
    users = conn.execute('SELECT balance AS id, * FROM users WHERE username = ?;', (user,)).fetchone()
    if users is not None:
        return "error duplicate entry"
    conn.execute('INSERT INTO users (username, password, balance) VALUES (?, ?, ?)', (user, password, 0))
    conn.commit()
    resp = make_response()
    resp.set_cookie('username', user)
    # return redirect(address + "/blue", code=302)
    return ""


@app.route('/blue/login', methods=['GET'])
def handle_login():
    user = request.args.get("user")
    password = request.args.get("pass")
    password = sha256_crypt.encrypt(password)
    #check db
    users = conn.execute('SELECT balance AS id, * FROM users WHERE username = ? AND password = ?;', (user, password)).fetchone()
    if users is None:
        print('error')
        return ""
    else:
        print('logged in')
        resp = make_response()
        resp.set_cookie('username', user)
        return resp


@app.route('/blue/manage', methods=['GET'])
def action_handler():
    action = request.args.get("action")
    amount = request.args.get("amount")
    if(action == "deposit"):
        print("deposit")
        print(request.cookies.get('username'))
        users = conn.execute('SELECT balance AS id, * FROM users WHERE username = ?;', (request.cookies.get('username'))).fetchone()
        if users is None:
            return "err"
        newAmount = users['balance']
        if newAmount is None:
            newAmount = 0
        newAmount = int(newAmount)
        newAmount = newAmount + amount
        conn.execute('UPDATE users SET balance = ? WHERE username = ?;', (newAmount, request.cookies.get('username')))
        conn.commit()
        return newAmount
    elif(action == "withdraw"):
        users = conn.execute('SELECT balance AS id, * FROM users WHERE username = ?;', (request.cookies.get('username'))).fetchone()
        if users is None:
            return "err"
        newAmount = users['balance']
        if newAmount is None:
            newAmount = 0
        newAmount = int(newAmount)
        newAmount = newAmount - amount
        conn.execute('UPDATE users SET balance = ? WHERE username = ?;', (newAmount, request.cookies.get('username')))
        conn.commit()
        return newAmount
    elif (action == "balance"):
        users = conn.execute('SELECT balance AS id, * FROM users WHERE username = ?;', (request.cookies.get('username'))).fetchone()
        if users is None:
            return "err"
        newAmount = users['balance']

        return newAmount
    elif (action == "close"):
        conn.execute('DELETE FROM posts WHERE username = ?', (request.cookies.get('username')))
        conn.commit()
        return 'Login'

# main driver function
if __name__ == '__main__':
    # run() method of Flask class runs the application
    # on the local development server.
    conn = sqlite3.connect('database.db', check_same_thread=False)
    with open('database.sql') as f:
        conn.executescript(f.read())

    cur = conn.cursor()
    conn.commit()
    
    app.run(host=hostname, port=port)