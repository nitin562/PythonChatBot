from Bot import app
from Bot.User.helper import token_verify
from .controller import addRoom, updateRoom, getRooms,deleteRoom,chat
from flask import request
import asyncio
@app.route("/room",methods=["GET","POST","PATCH","DELETE"])
@token_verify
def rooms(user):
    print(user)
    if request.method=="POST":
        # json body
        return addRoom(user)
    elif request.method=="PATCH":
        return updateRoom(user)

    elif request.method=="GET":
        return getRooms(user)
    elif request.method=="DELETE":
        return deleteRoom(user)

@app.route("/chat",methods=["POST"])
@token_verify
def chat_controller(user):
    print(user)
    if request.method=="POST":
        return asyncio.run(chat(user))