from pymongo.mongo_client import MongoClient

from os import getenv


def get_student_collection():
    atlas_conn_url = getenv("ATLAS_CONNECTION_URL")
    print(atlas_conn_url)
    client = MongoClient(atlas_conn_url)
    return client["Cluster0"].students
