import sys
sys.path.insert(0,'../')
from random_italian_things import RandomItalianPerson, RandomItalianHouse, random_amenity
from random_italian_things.utils import date_generator as dg, date_facilities
from pymongo import MongoClient
from pprint import pprint
import pandas as pd


class MongoPopulate:
    def __init__(self, connection_string):
        self.client = MongoClient(connection_string)
        self.db = self.client.SMBUD

    @staticmethod
    def create_sanitary_operator(sanitary_type):
        random_italian_person = RandomItalianPerson()
        sanitary_operator = {
            "type": sanitary_type,
            "name": random_italian_person.name,
            "surname": random_italian_person.surname,
            "tax_code": random_italian_person.tax_code,
            "contact": random_italian_person.phone_number
        }
        return sanitary_operator

    def create_places(self):
        self.db.places.drop() #drop places before running
        collection = self.db.places #alias of collection into the function
        places_df = pd.read_csv('datasets/locations.csv') #read csv with places
        places = [] #initialize places as list
        for index, row in places_df.iterrows():
            place = {
                "building_name": row.building_name,
                "type": row.type,
                "region": row.region
            }
            places.append(place) #append each place in form of dict in places list
        result = collection.insert_many(places) #bulk insert in db
        print(result)


if __name__ == "__main__":
    with open("connection_string.txt", "r") as connection_string_reader:
        connection_string = connection_string_reader.readline().split()[0]
        mongo_populate = MongoPopulate(connection_string)
        mongo_populate.db.sanitary_operators.insert_one(mongo_populate.create_sanitary_operator("Doctor"))
        mongo_populate.create_places()
