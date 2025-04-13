from Bot import app
from flask import request
from Bot.User.helper import token_verify
from .controller import scraping_controller
import asyncio
@app.route("/scrape",methods=["POST"])
@token_verify
def scraping(user):
    print(user)
    if request.method=="POST":
        return asyncio.run(scraping_controller())
    