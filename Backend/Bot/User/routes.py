from Bot import app
from flask import request
from .controller import register_controller,login_controller

@app.route("/",methods=['POST'])
@app.route("/login",methods=['POST'])
def login():
    if request.method=="POST":
     return login_controller()


@app.route("/register",methods=["POST"])
def register():
    if request.method=="POST":
     return register_controller()