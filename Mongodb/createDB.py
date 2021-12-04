import pymongo

myclient=pymongo.MongoClient("mongodb://localhost:27017/")

dblist = myclient.list_database_names()

print(dblist)
if "mydatabase" in dblist:
  print("The database exists.")