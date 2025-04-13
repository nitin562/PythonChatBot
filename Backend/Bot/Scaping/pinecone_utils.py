from pinecone import Pinecone, ServerlessSpec
from pinecone.exceptions import PineconeException
import os
from Bot import db, mongo
from bson.objectid import ObjectId
from uuid import uuid4
from pymongo.errors import PyMongoError
scraped_collection = db.get_collection("Scraped")
room_collection = db.get_collection("Rooms")
pc = Pinecone(api_key=os.getenv("pinecone_api_key"))
index_name = os.getenv("index")
index = None
if not pc.has_index(index_name):
    index = pc.create_index(
        name=index_name,
        vector_type="dense",
        dimension=384,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        deletion_protection="disabled",
        tags={"environment": "development"},
    )
else:
    index = pc.Index(index_name)


def storeEmbeddings(embeddings: dict, roomId, urls):
    for key in embeddings:

        embedding = embeddings[key]["final"]
        text = embeddings[key]["text"]
        client = mongo.cx
        try:
            with client.start_session() as session:
                with session.start_transaction():
                    id = ObjectId(roomId)
                    room_collection.update_one(
                        {"_id": id}, {"$set": {"urls": urls}}, session=session
                    )
                    scraped_collection.insert_one(
                        {"room": id, "data": text}, session=session
                    )
                    try:
                        records = []

                        for i in range(0, len(embedding)):
                            value = embedding[i].tolist()

                            records.append(
                                {
                                    "id": str(uuid4()),
                                    "values": value,
                                    "metadata": {"source": key, "index": i},
                                }
                            )
                        print(records)
                        index.upsert(namespace=roomId, vectors=records)

                    except PineconeException as e:
                        session.abort_transaction()
                        print("pinecone error-", e)
                        return (False,str(e))

        except PyMongoError as e:
            print("Transaction Error-",e)
            return (False,str(e))

    return (True,"")


def query(searchEmbedding, namespace):
    try:
        content = index.query(
            namespace=namespace,
            vector=searchEmbedding.tolist(),
            top_k=2,
            include_metadata=True,
        )
        print(content)
        return (True,content)
    except PineconeException as e:
        print("gew", e)
        return (False,str(e))
