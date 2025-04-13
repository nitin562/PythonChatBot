from Bot import db
import asyncio
from flask import request,jsonify
from bson.objectid import ObjectId
from bson.json_util import dumps, loads
from datetime import datetime,timezone
from Bot.responses import error,success
from Bot.Scaping.helper import embedd_a_chunk
from Bot.Scaping.pinecone_utils import query
from .groqChat import askToGroq
User=db.get_collection("User")
Rooms=db.get_collection("Rooms")
scraped_collection = db.get_collection("Scraped")
def addRoom(user):
    if request.content_type!="application/json":
        return error(400,"type","Payload must be JSON")
    payload=request.json
    # currently it will only have name
    name=payload["name"]
    if not name or len(name)<2:
        return error(400,"client",{"name":["Name must be present with atleast 3 letters"]})
    doc={
        "user":ObjectId(user["id"]),
        "name":name,
        "urls":[],
        "created":datetime.now(tz=timezone.utc),
        "updated":datetime.now(tz=timezone.utc)
    }
    id=Rooms.insert_one(doc).inserted_id
    del doc["user"]
    doc["_id"]=str(doc["_id"])
    doc["created"]=doc["created"].isoformat()
    doc["updated"]=doc["updated"].isoformat()

    return success(200,"Room Created",doc)

def updateRoom(user):
    if request.content_type!="application/json":
        return error(400,"type","Payload must be JSON")
    body=request.json
   
    if not body["id"]:
        return error(400,"client",{"id":["Id must be present."]})
    try:
        id=ObjectId(body["id"])
    except:
        return error("400","client",{"id":["Id must be valid"]})
    del body["id"]
    # make sure the fields have same keys
    keys=["name","urls"]
    for key in body:
        if key not in keys:
            return error(400,"client",{key:[f"{key} is not valid field. Field names can be {', '.join(keys)}"]})
    print(body,id)
    doc=Rooms.update_one({"_id":id},{"$set":body,"$currentDate":{"updated":True}})
    return success(200,"Room Updated",doc.modified_count)

# get
def getRooms(user):
    user_id=ObjectId(user["id"])
    rooms=Rooms.find({"user":user_id})
    result=[]
    for room in rooms:
        print(room)
        curr={
            "id":str(room["_id"]),
            "name":room["name"],
            "urls":room["urls"],
            "created":room["created"].isoformat(),
            "updated":room["updated"].isoformat()
        }
        result.append(curr)
    return success(200,"Fetched",result)

# delete
def deleteRoom(user):
    roomId=request.args.get("id")
    if not roomId:
        return error(400,"client",{"id":["Id must be present."]})
    try:
        id=ObjectId(roomId)
    except:
        return error("400","client",{"id":["Id must be valid"]})
    ack=Rooms.delete_one({"_id":id})
    if ack.deleted_count==0:
        return error("400","client",{"id":["Id is not Found"]})
    return success(200,"Deleted","Room is trashed.")

# chatting
async def chat(user):
    try:
        if request.content_type!="application/json":
            return error(400,"type","Payload must be JSON")
        payload=request.json
        room=payload["roomId"]
        user_query=payload["query"]
        emebedding_chunk=await asyncio.to_thread(embedd_a_chunk,user_query)
        success,data=await asyncio.to_thread(query,emebedding_chunk,room)
        print(data)
        if not success:
            return error(500,"server",data)
        scrapedContent=scraped_collection.find_one({"room":ObjectId(room)})["data"]
        if not scrapedContent:
            return error(400,"Scraping","Scraped Data is not Found")
        content=""
        for result in data["matches"]:
            idx=int(result["metadata"]["index"])
            if idx>0:
                content=content+scrapedContent[idx-1]
            content=content+scrapedContent[idx]
            if idx<len(scrapedContent)-1:
                content=content+scrapedContent[idx+1]
            content=content+scrapedContent[idx]
        return await asyncio.to_thread(askToGroq,content,user_query)
        
    except Exception as e:
        print(e)
        return error(500,"server","server error occured")

