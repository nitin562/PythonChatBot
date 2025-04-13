from flask import Flask
from flask_pymongo import PyMongo
import dotenv
dotenv.load_dotenv()
import os
app=Flask(__name__)
app.config["MONGO_URI"] = os.getenv("db")
mongo=PyMongo(app)
db=mongo.db
print(db)
collections=["User","Rooms","Scraped"]
db_collections=db.list_collection_names()
for collection in collections:
    if collection not in db_collections:
        db.create_collection(collection)

from .routes import *