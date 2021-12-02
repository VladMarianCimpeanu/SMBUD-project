#from random_italian_things import RandomItalianPerson, RandomItalianHouse, random_amenity
#from random_italian_things.utils import date_generator as dg, date_facilities
from pymongo import MongoClient
from pprint import pprint
import pandas as pd

class MongoPopulate:
    
    client = None
    db = None
    
    def __init__(self, connection_string):
        global client, db
        client = MongoClient(connection_string)
        db = client.SMBUD

    @staticmethod
    def create_sanitary_operator(self, sanitary_type):
        random_italian_person = RandomItalianPerson()
        sanitary_operator = {
            "type": sanitary_type,
            "name": random_italian_person.name,
            "surname": random_italian_person.surname,
            "tax_code": random_italian_person.tax_code,
        }
    
    @staticmethod
    def create_places():
        collection = db.places
        places_df = pd.read_csv('datasets/locations.csv')
        places = []
        for index,row in places_df.iterrows():
            place = {
                "building_name" : row.building_name,
                "type" : row.type,
                "region" : row.region
            }
            places.append(place)
        result = collection.insert_many(places)
        print(result)
            
            


if __name__ == "__main__":
    with open("connection_string.txt", "r") as connection_string_reader:
        connection_string = connection_string_reader.readline().split()[0]
        mongo_populate = MongoPopulate(connection_string)
        MongoPopulate.create_places()
        