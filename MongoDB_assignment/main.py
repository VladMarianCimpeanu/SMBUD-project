import sys
sys.path.insert(0, '../')
import random
import string
import datetime
from random_italian_things import RandomItalianPerson, RandomItalianHouse, random_amenity
from random_italian_things.utils import date_generator as dg, date_facilities
from pymongo import MongoClient
from pprint import pprint
import pandas as pd
import numpy as np
import googlemaps

# list of the swab uci generated by create_recovery,
# useful to generate the certification after the generation of the recoveries
swab_uci = []
# list of all the uci created, useful to avoid the random generation of duplicate uci
all_uci = []


class MongoPopulate:
    def __init__(self, connection_string):
        self.client = MongoClient(connection_string)
        self.db = self.client.SMBUD
        self.vaccines = None
        self.sanitary_operators = []
        self.places = []
        self.recovery_people = []
        self.people = []

    def create_people(self, num_doc=25, num_nurse=50, num_people=100, num_rec_people=5):
        for i in range(0, num_doc):
            random_italian_person = RandomItalianPerson()
            self.sanitary_operators.append(self.create_sanitary_operator('Doctor', random_italian_person))
        for i in range(0, num_nurse):
            random_italian_person = RandomItalianPerson()
            self.sanitary_operators.append(self.create_sanitary_operator('Nurse', random_italian_person))
        for i in range(0, num_people):
            random_italian_person = RandomItalianPerson()
            self.people.append(self.create_person(random_italian_person))
        for i in range(0, num_rec_people):
            random_italian_person = RandomItalianPerson()
            self.recovery_people.append(self.create_person(random_italian_person))

    @staticmethod
    def create_sanitary_operator(sanitary_type, random_italian_person):
        sanitary_operator = {
            "type": sanitary_type,
            "name": random_italian_person.name,
            "surname": random_italian_person.surname,
            "tax_code": random_italian_person.tax_code,
            "contact": random_italian_person.phone_number
        }
        return sanitary_operator

    def create_person(self, random_italian_person):
        person = {
            "name": random_italian_person.name,
            "surname": random_italian_person.surname,
            "tax code": random_italian_person.tax_code,
            "dob": random_italian_person.birthdate,
            "emergency name": random_italian_person.name + random_italian_person.surname,
            "emergency contact": random_italian_person.phone_number
        }
        return person

    def create_places(self):
        '''self.db.places.drop()  # drop places before running
        collection = self.db.places  # alias of collection into the function'''
        places_df = pd.read_csv('datasets/locations.csv')  # read csv with places
        places = []  # initialize places as list
        for index, row in places_df.iterrows():
            place = {
                "building_name": row.building_name,
                "type": row.type,
                "region": row.region,
                "gps" : str(random.uniform(-90, 90)) + "," + str(random.uniform(-180, 180))
            }
            places.append(place)  # append each place in form of dict in places list
        self.places=places

    """ For the vaccinations all the irrelevant information can be randomly generated by this function.
        For sake of simplicity the sn number will be the same for all the certifications, even though in 
        reality it may changes due to mixed vaccinations."""

    def create_vaccination(self, doctor_document, nurse_document, vaccination_place, vaccination_date, vaccine_name,
                           vaccine_dose):
        if self.vaccines is None:
            self.vaccines = pd.read_csv("datasets/vaccines.csv")
        vaccination_document = {
            "revoked": False,  # for simplicity sake all the vaccines will be legally valid by default
            "name": vaccine_name,
            "brand": self.vaccines.loc[self.vaccines["name" == vaccine_name], "brand"][0],
            "type": self.vaccines.loc[self.vaccines["name" == vaccine_name], "type"][0],
            "lot": random.randint(200000, 300000),
            "sn": int(self.vaccines.loc[self.vaccines["name" == vaccine_name], "sn"][0]),
            "dn": vaccine_dose,
            "issuer": "Italian Ministry of Health",
            "nurse": nurse_document,
            "doctor": doctor_document,
            "place": vaccination_place,
            "date": vaccination_date,
            "expiration date": vaccination_date + datetime.timedelta(days=int(self.vaccines
                                                                              .loc[
                                                                                  self.vaccines["name"] == vaccine_name,
                                                                                  "validity" + str(vaccine_dose)]))
        }
        return vaccination_document

    """Function used to generate recovery certificates"""

    def create_recovery(self, amount, days_duration):
        print("Creation of recovery certificates in progress...")
        self.db.recovery.drop()  # recovery cleaning from db
        collection = self.db.recovery
        recoveries = []
        for i in range(0, amount):
            date = datetime.datetime.strptime(dg.DateGenerator().random_datetimes_or_dates('date').tolist()[0],
                                              '%Y-%m-%d')
            valid_date = date + datetime.timedelta(days=random.randrange(10, 21))
            # the following while checks that the uci is unique and that it is not already present in the db
            while True:
                uci = '01ITA797891BBF264E88B9BB8E' + ''.join(random.choices(string.digits, k=6)) + random.choice(
                    string.ascii_uppercase) + random.choice(string.digits) + random.choice(string.ascii_uppercase)
                if uci not in all_uci:
                    all_uci.append(uci)
                    swab_uci.append(uci)
                    break
            recovery = {
                "revoked": False,
                "date": date,
                "valid_from": valid_date,
                "expiration_date": valid_date + datetime.timedelta(days=days_duration),
                "uci_swab": uci,
                "issuer": "Italian Ministry of Health"
            }
            recoveries.append(recovery)
        rec = collection.insert_many(recoveries)
        print("Recovery certificates created successfully.")
        return rec

    def create_test(self, revoked, datetime_attribute, test_type, result, place_document, sanitary_operator_document,
                    expiration_date):
        test_document = {
            "revoked": revoked,
            "datetime": datetime_attribute,
            "type": test_type,
            "issuer": "Italian Ministry of Health",
            "result": result,
            "place": place_document,
            "sanitary operator": sanitary_operator_document,
        }
        if result == "Negative":
            test_document['expiration date'] = expiration_date
        return test_document

    def create_random_test(self, hours_duration_rapid=48, hours_duration_molecular=72):
        revoked = False
        datetime_attribute = datetime.datetime.strptime(
            dg.DateGenerator().random_datetimes_or_dates('datetime').tolist()[0], "%Y-%m-%d %H:%M:%S")
        test_type = random.choices(['Rapid', 'Molecular'], [0.95, 0.05])[0]
        result = random.choices(['Negative', 'Positive'], [0.95, 0.05])[0]
        if test_type == 'Rapid':
            expiration_date = datetime_attribute + datetime.timedelta(hours=hours_duration_rapid)
        else:
            expiration_date = datetime_attribute + datetime.timedelta(hours=hours_duration_molecular)
        test = self.create_test(revoked=revoked,
                                datetime_attribute=datetime_attribute,
                                test_type=test_type,
                                result=result,
                                place_document=random.choices(self.places)[0],
                                sanitary_operator_document=random.choice(self.sanitary_operators),
                                expiration_date=expiration_date
                                )
        return test

    def create_random_certificate(self, cert_type):
        person = random.choice(self.people)
        certificate = {
         #   "version": "to-do",
            "name": person['name'],
            "surname": person['surname'],
            "dob": person['dob'],
            "tax code": person['tax code'],
            "emergency contact": person['emergency contact'],
            "emergency name": person['emergency name'],
            "uci": "to-do"
        }
        if cert_type == 'Recovery':
            pass
        elif cert_type == 'Test':
            certificate["test"]=self.create_random_test()
        elif cert_type == 'Vaccination':
            pass
        else:
            print('Error')
        return certificate

    def create_certificates(self, num_rec, num_test, num_vacc):
        print("Creation of certificates in progress...")
        self.db.certificates.drop()  # recovery cleaning from db
        collection = self.db.certificates
        certificates = []
        for i in range(0, num_rec):
            certificates.append(self.create_random_certificate('Recovery'))
        for i in range(0, num_test):
            certificates.append(self.create_random_certificate('Test'))
        for i in range(0, num_vacc):
            certificates.append(self.create_random_certificate('Vaccination'))
        return collection.insert_many(certificates)


if __name__ == "__main__":
    with open("connection_string.txt", "r") as connection_string_reader:
        connection_string = connection_string_reader.readline().split()[0]
        mongo_populate = MongoPopulate(connection_string)
        # places contains the list of all the places
        mongo_populate.create_places()
        mongo_populate.create_people()
        # create_recovery: the first parameter is the amount of certificates that will be created
        # the second one is the duration - in days- of the certification
        # mongo_populate.create_recovery(10, 180)
        mongo_populate.create_certificates(0, 10, 0)
