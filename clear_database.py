import pymongo

print("IMPORTANT: make sure the flask server is not running!")

mongo_client = pymongo.MongoClient("mongodb://localhost:27017")
database = mongo_client["hour_tracker"]
records = database["records"]

records.drop()
print("Successfully removed records!")