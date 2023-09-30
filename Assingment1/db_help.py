import pymongo

class DB:
    def __init__(self) -> None:
        self.mongo_url = "mongodb+srv://Jyothi:<password>@cluster0.t5qddp4.mongodb.net/?retryWrites=true&w=majority"
        self.client = pymongo.MongoClient(self.mongo_url)
        self.mydb = self.client["blockchain"]
        self.mycol = self.mydb["blocks"]
    
    def insert_into_db(self,data: dict):
        x = self.mycol.insert_one(data)
        
    def insert_chain(self,data: list):
        x = self.mycol.insert_many(data)
        
    def get_all_data(self):
        # myresults = list(mydb.mycollection.find())
        x = list(self.mycol.find().sort("index"))
        # for _ in x:
        #     del _['_id']
        return x

    def delete_all_data(self):
        x = self.mycol.delete_many({})
        print(x.deleted_count,"deleted")