# Importing flask module in the project is mandatory
# An object of Flask class is our WSGI application.
from flask import Flask, request, render_template, redirect

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
    return 'Registration'

@app.route('/blue/login', methods=['GET'])
def handle_login():
    user = request.args.get("user")
    password = request.args.get("pass")
    #check db
    if(user == "ok"):
        return redirect("http://127.0.0.1:5000/blue ", code=302)
    else:
        return redirect("http://127.0.0.1:5000/blue/login ", code=302)
@app.route('/blue/manage', methods=['GET'])
def action_handler():
    action = request.args.get("action")
    amount = request.args.get("amount")
    if(action == "deposit"):
        #ok
        return 'Login'
    elif(action == "withdraw"):
        #DB code
        return 'Login'
    elif (action == "balance"):
        # DB code
        return 'Login'
    elif (action == "close"):
        # DB code
        return 'Login'

# main driver function
if __name__ == '__main__':
    # run() method of Flask class runs the application
    # on the local development server.
    app.run()
