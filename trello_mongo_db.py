import pymongo
import certifi
import os
from dotenv import load_dotenv
import datetime


def get_trello_db_name():
    return os.getenv("TRELLO_DB_NAME")

# make user and app name configurable
def get_mongo_client(user = os.getenv("MONGO_USER_NAME"), app = os.getenv("MONGO_APP")):
    return pymongo.MongoClient(f"mongodb+srv://{user}:{app}@cluster0.rx95i.mongodb.net/todoAppDB?w=majority", tlsCAFile=certifi.where())


def get_trello_db():
    client = get_mongo_client()
    #if get_trello_db_name() in client.list_database_names():
    #    return client.get_database(get_trello_db_name())
    return client[get_trello_db_name()]


def get_trello_collection():
    db = get_trello_db()
    return db['TRELLO_COLLECTION']
