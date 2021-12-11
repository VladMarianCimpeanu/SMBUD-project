import sys
import argparse

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


class MongoPopulate:
    def __init__(self, connection_string):
        self.client = MongoClient(connection_string, tls=True, tlsAllowInvalidCertificates=True)
        self.db = self.client.SMBUD
        self.vaccines = None
        self.doctors = []
        self.nurses = []
        self.places = []
        self.recovery_people = []
        self.people = []
        self.UCI = []
        self.vaccinated_people = []
        self.authorized_bodies = {}

    def generate_authorized_bodies(self):
        loaded_data = pd.read_csv("datasets/auth_bodies.csv")
        self.db.authorized_bodies.drop()
        collection = self.db.authorized_bodies
        for index, row in loaded_data.iterrows():
            doc = {
                "name": row["name"],
                "city": row["city"],
                "address": row["address"],
                "civic_number": row["civic number"],
                "department": row["department"]
            }
            result = collection.insert_one(doc)
            self.authorized_bodies[row["city"]] = result.inserted_id

    def get_new_uci(self) -> str:
        while True:
            uci = '01ITA797891BBF264E88B9BB8E' + ''.join(random.choices(string.digits, k=6)) + random.choice(
                string.ascii_uppercase) + random.choice(string.digits) + random.choice(string.ascii_uppercase)
            if uci not in self.UCI:
                self.UCI.append(uci)
                return uci

    def create_people(self, num_doc=25, num_nurse=50, num_people=600, num_rec_people=300):
        for i in range(0, num_doc):
            random_italian_person = RandomItalianPerson()
            self.doctors.append(self.create_sanitary_operator('Doctor', random_italian_person))
        for i in range(0, num_nurse):
            random_italian_person = RandomItalianPerson()
            self.nurses.append(self.create_sanitary_operator('Nurse', random_italian_person))
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
            "tax_code": random_italian_person.tax_code,
            "dob": datetime.datetime.strptime(random_italian_person.birthdate, '%Y-%m-%d'),
            "contact": random_italian_person.phone_number,
            "emergency_name": RandomItalianPerson().name + " " + random_italian_person.surname,
            "emergency_contact": RandomItalianPerson().phone_number
        }
        return person

    def create_places(self):
        '''self.db.places.drop()  # drop places before running
        collection = self.db.places  # alias of collection into the function'''
        places_df = pd.read_csv('datasets/locations.csv')  # read csv with places
        places = []  # initialize places as list
        for index, row in places_df.iterrows():
            city, objectID = random.choice(list(self.authorized_bodies.items()))
            place = {
                "building_name": row.building_name,
                "type": row.type,
                "region": row.region,
                "address" : RandomItalianHouse('Milan').address,
                "gps": str(random.uniform(-90, 90)) + "," + str(random.uniform(-180, 180)),
                "city": city,
                "authorized_by": objectID
            }
            places.append(place)  # append each place in form of dict in places list
        self.places = places

    """ For the vaccinations all the irrelevant information can be randomly generated by this function.
        For sake of simplicity the sn number will be the same for all the certifications, even though in 
        reality it may changes due to mixed vaccinations."""

    def create_vaccination(self, doctor_document: dict, nurse_document: dict, vaccination_place: dict,
                           vaccination_date: datetime, vaccine_name: str, vaccine_dose: int) -> dict:
        if self.vaccines is None:
            self.vaccines = pd.read_csv("datasets/vaccines.csv")
        vaccination_document = {
            "name": vaccine_name,
            "brand": self.vaccines.loc[self.vaccines["name"] == vaccine_name, "brand"].reset_index(drop=True).iloc[0],
            "type": self.vaccines.loc[self.vaccines["name"] == vaccine_name, "type"].reset_index(drop=True).iloc[0],
            "lot": random.randint(200000, 300000),
            "sn": int(self.vaccines.loc[self.vaccines["name"] == vaccine_name, "sn"].reset_index(drop=True).iloc[0]),
            "dn": vaccine_dose,
            "nurse": nurse_document,
            "doctor": doctor_document,
            "place": vaccination_place,
            "date": vaccination_date
        }
        return vaccination_document

    def create_random_vaccinations(self, num_series: int) -> list:
        certificates = []
        if self.vaccines is None:
            self.vaccines = pd.read_csv("datasets/vaccines.csv")
        for element in range(num_series):
            person = random.choice(self.people)
            while person in self.vaccinated_people:
                person = random.choice(self.people)
            self.vaccinated_people.append(person)
            vaccine = str(self.vaccines.name.sample(n=1).reset_index(drop=True).iloc[0])
            sn = int(self.vaccines.loc[self.vaccines["name"] == vaccine, "sn"].reset_index(drop=True).iloc[0]),
            date_vaccination = None
            for dn in range(1, random.choice(sn) + 1):
                if date_vaccination is None:
                    date_vaccination = datetime.datetime.strptime(dg.DateGenerator().
                                                                  random_datetimes_or_dates('date').tolist()[0],
                                                                  '%Y-%m-%d')
                else:
                    delta = random.randint(0, 10)
                    date_vaccination += datetime.timedelta(days=int(self.vaccines.loc[self.vaccines["name"] == vaccine,
                                                                                      "validity" + str(dn - 1)]
                                                                    .reset_index(drop=True).iloc[0]) - delta)
                vaccination_doc = self.create_vaccination(doctor_document=random.choice(self.doctors),
                                                          nurse_document=random.choice(self.nurses),
                                                          vaccination_place=random.choice(self.places),
                                                          vaccination_date=date_vaccination,
                                                          vaccine_name=vaccine,
                                                          vaccine_dose=dn)
                doc = self.create_certificate(person, self.get_new_uci(), "vaccination", vaccination_doc)
                certificates.append(doc)
        return certificates

    """Function used to generate recovery certificates"""

    def create_recovery(self):
        date = datetime.datetime.strptime(dg.DateGenerator().random_datetimes_or_dates('date').tolist()[0],
                                          '%Y-%m-%d')
        # the following while checks that the uci is unique and that it is not already present in the db
        uci = self.get_new_uci()
        recovery = {
            "date": date,
            "uci_swab": uci
        }
        return recovery

    def create_test(self, datetime_attribute, test_type, result, place_document, sanitary_operator_document):
        test_document = {
            "datetime": datetime_attribute,
            "type": test_type,
            "result": result,
            "place": place_document,
            "sanitary_operator": sanitary_operator_document,
        }
        return test_document

    def create_random_test(self, prob_positive=0):
        datetime_attribute = datetime.datetime.strptime(
            dg.DateGenerator().random_datetimes_or_dates('datetime').tolist()[0], "%Y-%m-%d %H:%M:%S")
        test_type = random.choices(['Rapid', 'Molecular'], [0.95, 0.05])[0]
        result = random.choices(['Negative', 'Positive'], [1 - prob_positive, prob_positive])[0]
        test = self.create_test(datetime_attribute=datetime_attribute,
                                test_type=test_type,
                                result=result,
                                place_document=random.choices(self.places)[0],
                                sanitary_operator_document=random.choice(self.nurses)
                                )
        return test

    def create_certificate(self, person: dict, uci, cert_type, cert_type_info: dict):
        certificate = {
            "name": person['name'],
            "surname": person['surname'],
            "dob": person['dob'],
            "tax_code": person['tax_code'],
            "contact": person['contact'],
            "emergency_name": person['emergency_name'],
            "emergency_contact": person['emergency_contact'],
            "uci": uci,
            "issuer": "Italian Ministry of Health",
            "revoked": False
        }
        if cert_type == "test":
            if cert_type_info['result'] == "Negative":
                certificate['valid_from'] = cert_type_info['datetime']
                if cert_type_info['type'] == "Rapid":
                    certificate['expiration_date'] = cert_type_info['datetime'] + datetime.timedelta(hours=48)
                else:
                    certificate['expiration_date'] = cert_type_info['datetime'] + datetime.timedelta(hours=72)
        elif cert_type == "vaccination":
            certificate['valid_from'] = cert_type_info['date'] + datetime.timedelta(days=12)
            certificate['expiration_date'] = cert_type_info['date'] + datetime.timedelta(days=int(self.vaccines
                                                                         .loc[
                                                                             self.vaccines["name"] == cert_type_info['name'],
                                                                             "validity" + str(cert_type_info['dn'])]
                                                                         .reset_index(drop=True).iloc[0]))
        elif cert_type == "recovery":
            certificate['valid_from'] = cert_type_info['date'] + datetime.timedelta(days=random.randrange(10, 21))
            certificate['expiration_date'] = certificate['valid_from'] + datetime.timedelta(days=180)
        else:
            print("Error: certification type non valid!")
        certificate[cert_type] = cert_type_info
        return certificate

    def create_random_certificate(self, cert_type, collection):
        uci = self.get_new_uci()
        if cert_type == 'recovery':
            person = random.choice(self.recovery_people)
            recovery_dict = self.create_recovery()
            certificate_recovery = self.create_certificate(person, uci, 'recovery', recovery_dict)
            collection.insert_one(certificate_recovery)

            test_1 = self.create_test(datetime_attribute=recovery_dict['date'],
                                      test_type='Molecular',
                                      result='Positive',
                                      place_document=random.choice(self.places),
                                      sanitary_operator_document=random.choice(self.nurses))
            certificate_test_1 = self.create_certificate(person,
                                                         self.get_new_uci(),
                                                         'test',
                                                         test_1)
            collection.insert_one(certificate_test_1)

            test_2 = self.create_test(datetime_attribute=certificate_recovery['valid_from'],
                                      test_type='Molecular',
                                      result='Negative',
                                      place_document=random.choice(self.places),
                                      sanitary_operator_document=random.choice(self.nurses))
            certificate_test_2 = self.create_certificate(person,
                                                         recovery_dict['uci_swab'],
                                                         'test',
                                                         test_2)
            collection.insert_one(certificate_test_2)
            pass
        elif cert_type == 'test':
            person = random.choice(self.people)
            certificate = self.create_certificate(person, uci, 'test', self.create_random_test())
            collection.insert_one(certificate)
        elif cert_type == 'vaccination':
            certifications = self.create_random_vaccinations(1)
            for certificate in certifications:
                collection.insert_one(certificate)
        else:
            print('Error')
        return

    """num_rec is the number of recovery documents to generate. 
       This will also generate the tests necessary to make the recovery document consistent;
       num_test is the number of test documents to generate; 
       num_vacc is the number of people to vaccinate."""
    def create_certificates(self, num_rec, num_test, num_vacc):
        print("Creation of certificates in progress...")
        self.db.certificates.drop()  # recovery cleaning from db
        collection = self.db.certificates
        for i in range(0, num_rec):
            self.create_random_certificate('recovery', collection)
        for i in range(0, num_test):
            self.create_random_certificate('test', collection)
        for i in range(0, num_vacc):
            self.create_random_certificate('vaccination', collection)
        print("Certificates created!")
        return

    def add_indexes_to_certificates(self):
        self.db.certificates.create_index("tax_code")
        self.db.certificates.create_index("uci")


if __name__ == "__main__":
    with open("connection_string.txt", "r") as connection_string_reader:

        parser = argparse.ArgumentParser(description="Generator of random C19 certificates to store in a MongoDB database")
        parser.add_argument('--uri', dest='uri', default=connection_string_reader.readline().split()[0], help="URI for connection to MongoDB Atlas")
        args = parser.parse_args()
        connection_string = args.uri

        mongo_populate = MongoPopulate(connection_string)
        # places contains the list of all the places
        mongo_populate.generate_authorized_bodies()
        mongo_populate.create_places()
        mongo_populate.create_people()
        """
        the first parameter is the number of recovery documents to generate. 
            This will also generate the tests necessary to make the recovery document consistent;
        the second parameter is the number of test documents to generate; 
        the third parameter is the number of people to vaccinate.
        """
        mongo_populate.create_certificates(50, 450, 450)
        mongo_populate.add_indexes_to_certificates()
