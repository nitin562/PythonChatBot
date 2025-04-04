from Bot import app
from flask import request
from Bot.User.helper import token_verify
from .controller import scraping_controller
@app.route("/scrape",methods=["POST"])
@token_verify
def scraping(user):
    print(user)
    if request.method=="POST":
        return scraping_controller()
        