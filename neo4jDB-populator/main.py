import random
import os
import time
import numpy as np
import pandas as pd
from neo4j import GraphDatabase
from random import choices
from random_italian_things import RandomItalianPerson, RandomItalianHouse, random_amenity
from random_italian_things.utils import date_generator as dg
from random_italian_things.utils import date_facilities


class PopulateDB:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.people = []
        self.cities = {}  # dictionary which keys are cities and values are their citizens.
        self.names_city = []  # list with the keys of self.cities
        self.amenities = {}  # dictionary containing public spaces per each city
        # read 'datasets_to_read' that contains as keys the name of the available city
        configuration_file = pd.read_csv(
            "{}/random_italian_things/datasets/datasets_to_read.txt".format(os.path.dirname(os.path.abspath(__file__))))
        for index, row in configuration_file.iterrows():
            self.cities[row['key']] = []
            self.amenities[row['key']] = []
            self.names_city.append(row['key'])

    def close(self):
        self.driver.close()

    """
    def create_people(self):
        with self.driver.session() as session:
            for i in range(100):
                person = RandomItalianPerson()
                ssn_created = session.write_transaction(self._create_person, person.name, person.surname,
                                                        person.data["codice_fiscale"], person.birthdate, person.sex,
                                                        person.birthplace)
                self.people.append(ssn_created)
                print(ssn_created + " created")
            # print(greeting1)
    """

    def create_family(self, num_family_per_city):
        print("loading families ...")
        with self.driver.session() as session:
            for city in self.names_city:
                for i in range(num_family_per_city):
                    house = RandomItalianHouse(city)
                    family_surname_data = RandomItalianPerson().surname_data  # Picking random family surname
                    id_house = session.write_transaction(self._create_house, house.municipality, house.address)
                    ssn_family = []
                    for j in range(random.randint(1, 6)):
                        person = RandomItalianPerson(surname=family_surname_data)
                        ssn_family_member = session.write_transaction(self._create_person, person.name, person.surname,
                                                                      person.data["codice_fiscale"], person.birthdate,
                                                                      person.sex,
                                                                      person.birthplace)
                        ssn_family.append(ssn_family_member)
                        self.cities[city].append(ssn_family_member)

                    session.write_transaction(self._create_lives, ssn_family, id_house)
        print("families loaded.")

    def create_swabs(self):
        with self.driver.session() as session:
            session.write_transaction(self._create_swab)

    def create_tests(self):
        print("loading covid swabs...")
        range_tests = [0, 1, 2, 3, 4, 5, 6, 7]
        prob_range_tests = [0.3, 0.26, 0.17, 0.12, 0.7, 0.5, 0.02, 0.01]
        results = ['Positive', 'Negative']
        prob_results = [0.05, 0.95]
        with self.driver.session() as session:
            person_ids = session.read_transaction(self._get_people_id)
            for id_person in person_ids:
                for i in range(choices(range_tests, prob_range_tests)[0]):
                    timestamp = dg.DateGenerator().random_datetimes_or_dates('datetime').tolist()[0]
                    res = choices(results, prob_results)[0]
                    session.write_transaction(self._create_test, id_person[0], timestamp, res)
        print("loaded covid swabs.")

    def clear_db(self):
        print("clearing db...")
        with self.driver.session() as session:
            session.write_transaction(self._clear_db)

    def create_amenities(self, num_public_spaces: int):
        print("loading public spaces...")
        with self.driver.session() as session:
            for amenity in range(num_public_spaces):
                city = random.choice(self.names_city)
                amenity = random_amenity.Amenity(city)
                self.amenities[city].append(amenity)
                session.write_transaction(
                    self._create_amenity, amenity.amenity, amenity.city, amenity.name, amenity.street)
        print("public spaces loaded.")

    @staticmethod
    def _create_amenity(tx, amenity_type: str, city: str, name: str, street: str):
        tx.run("CREATE (amenity: PublicSpace {"
               "type: $type,"
               "name: $name,"
               "city: $city,"
               "street: $street"
               "})", type=amenity_type, name=name, city=city, street=street)

    def create_visits_relations(self, min_freq: int, max_freq: int, starting_date: tuple, ending_date: tuple):
        print("loading visits...")
        with self.driver.session() as session:
            for city_name in self.names_city:
                for person in self.cities[city_name]:
                    time_series = date_facilities.random_dates(max_freq, min_freq, starting_date, ending_date)
                    for d in time_series:
                        amenity = random.choice(self.amenities[city_name])
                        session.write_transaction(
                            self._create_visits,
                            amenity.name,
                            amenity.street,
                            amenity.city,
                            person,
                            d
                        )
        print("visits loaded.")

    @staticmethod
    def _create_visits(tx, amenity_name, amenity_street, amenity_city, ssn, date):
        tx.run("MATCH (person: Person), (ps: PublicSpace) "
               "WHERE person.ssn = $ssn AND ps.name = $name AND ps.street = $street AND ps.city = $city "
               "CREATE (person)-[r:VISITS {"
               "date : $date"
               "}]->(ps)", name=amenity_name, street=amenity_street, city=amenity_city, ssn=ssn, date=date)

    def create_meets_relations(self, num_meets: int, starting_date: tuple, ending_date: tuple):
        print("loading meetings...")
        with self.driver.session() as session:
            for n in range(num_meets):
                random_date = date_facilities.random_single_date(starting_date, ending_date)
                if random.random() <= 0.9:  # 90% probability of meeting in the same city
                    same_city = random.choice(self.names_city)
                    two_random_people = random.sample(self.cities[same_city], 2)
                    person1 = two_random_people[0]
                    person2 = two_random_people[1]
                else:
                    two_random_cities = random.sample(self.names_city, 2)  # Picks two random different cities
                    city_1 = two_random_cities[0]
                    city_2 = two_random_cities[1]
                    person1 = random.choice(self.cities[city_1])
                    person2 = random.choice(self.cities[city_2])

                session.write_transaction(self._create_meets, person1, person2, random_date)
        print("meeting loaded.")

    @staticmethod
    def _create_meets(tx, person1, person2, date):
        tx.run("MATCH (person1: Person), (person2: Person) "
               "WHERE person1.ssn = $person1 AND person2.ssn = $person2 "
               "CREATE (person1)-[r1:MEETS {"
               "date : $date"
               "}]->(person2) "
               "CREATE (person2)-[r2:MEETS {"
               "date : $date"
               "}]->(person1) ", person1=person1, person2=person2, date=date)

    def create_vaccines(self):
        print("loading vaccines...")
        with self.driver.session() as session:
            names = ['Moderna', 'Pfizer', 'AstraZeneca', 'Jensen']
            for name in names:
                session.write_transaction(self._create_vaccine, name)
        print("vaccines loaded.")

    @staticmethod
    def _create_vaccinates_relationship(tx, person_id, vaccine_name, lot, date):
        result = tx.run("MATCH (a:Vaccine),(b:Person) WHERE a.name = $vaccine_name AND ID(b) = $person_id "
                        "CREATE (b)-[v:VACCINATES{lot : $lot, date: $date}] -> (a)", person_id=person_id,
                        vaccine_name=vaccine_name, lot=lot, date=date)

    @staticmethod
    def _get_people_id(tx):
        people_ids = []
        result = tx.run("MATCH (a:Person) RETURN ID(a)")
        for id in result:
            people_ids.append(id.values())
        return people_ids

    @staticmethod
    def _get_vaccines_id(tx):
        vaccine_ids = []
        result = tx.run("MATCH (a:Vaccine) RETURN ID(a), a.name")
        for tuple in result:
            vaccine_ids.append(tuple.values())
        return vaccine_ids

    # create vaccinates relationship

    def _create_vaccinates(self):
        print("vaccinating people ...")
        with self.driver.session() as session:
            person_ids = session.read_transaction(self._get_people_id)  # get people ids
            vaccine_name_id = session.read_transaction(self._get_vaccines_id)  # get vaccines id and name
            lots = pd.read_csv('vaccine_lot.csv', sep=';')
            for id in person_ids:
                prob = random.random()  # with some probability a person has one, two or three vaccinates relationships
                if prob > 0.3:
                    v_name = random.choice(vaccine_name_id)[1]
                    lot = random.choice(lots[v_name])
                    random_date = dg.DateGenerator().random_datetimes_or_dates()
                    session.write_transaction(self._create_vaccinates_relationship, id[0], v_name, lot,
                                              random_date.tolist()[0])
                    if prob > 0.6:
                        lot = random.choice(lots[v_name])
                        date2 = dg.DateGenerator().random_datetimes_or_dates()
                        #  can't vaccinate twice in the same day, other temporal constraints are out of scope
                        while date2 == random_date: date2 = dg.DateGenerator().random_datetimes_or_dates()
                        session.write_transaction(self._create_vaccinates_relationship, id[0], v_name, lot,
                                                  date2.tolist()[0])
                        if prob > 0.95:
                            lot = random.choice(lots[v_name])
                            while date2 == random_date: date2 = dg.DateGenerator().random_datetimes_or_dates()
                            session.write_transaction(self._create_vaccinates_relationship, id[0], v_name, lot,
                                                      date2.tolist()[0])
        print("people vaccinated.")

    @staticmethod
    def _create_vaccine(tx, name):
        result = tx.run("CREATE (a:Vaccine{"
                        "name :$name"
                        "})", name=name)

    @staticmethod
    def _create_person(tx, name, surname, ssn, birth, sex, birthplace):
        result = tx.run("CREATE (a:Person {"
                        "name : $name,"
                        "surname : $surname,"
                        "ssn : $ssn, "
                        "birthdate : $birth,"
                        "sex : $sex,"
                        "birthplace : $birthplace"
                        "}) "
                        "RETURN a.ssn", name=name, surname=surname, ssn=ssn, birth=birth, sex=sex,
                        birthplace=birthplace)
        return result.single()[0]

    @staticmethod
    def _create_house(tx, town, address):
        result = tx.run("CREATE (a:House {"
                        "town : $town,"
                        "address : $address"
                        "}) "
                        "RETURN id(a)", town=town, address=address)
        return result.single()[0]

    @staticmethod
    def _create_lives(tx, ssn_family, id_house):
        for ssn in ssn_family:
            result = tx.run("MATCH (a:Person), (b:House) "
                            "WHERE a.ssn = $ssn AND id(b) = $id_house "
                            "CREATE (a)-[r:LIVES{livesFrom: a.birthdate}]->(b)"
                            "RETURN r ", ssn=ssn, id_house=id_house)
        return result.single()[0]

    @staticmethod
    def _create_swab(tx):
        result = tx.run("CREATE (a:Swab {name: 'Covid Swab'})")

    @staticmethod
    def _create_test(tx, id_person, timestamp, res):
        result = tx.run("MATCH (a:Person), (b:Swab) "
                        "WHERE id(a) = $id_person AND b.name='Covid Swab' "
                        "CREATE (a)-[r:TESTS {timestamp : $timestamp, res : $res}]->(b) "
                        "RETURN r ", id_person=id_person, timestamp=timestamp, res=res)
        return 1

    @staticmethod
    def _clear_db(tx):
        result = tx.run("MATCH (n) DETACH DELETE n")
        result_summary = result.consume()
        print("Deleted " + str(result_summary.counters.nodes_deleted) + " nodes")

    @staticmethod
    def _query_one(self):
        with self.driver.session() as session:
            result = session.run("MATCH ()-[t:TESTS]->() "
            "WITH date(apoc.date.format(apoc.date.parse(t.timestamp, 'ms', 'yyyy-MM-dd'), 'ms', 'yyyy-MM-dd')).month AS month, "                                             "date(apoc.date.format(apoc.date.parse(t.timestamp, 'ms', 'yyyy-MM-dd'), 'ms', 'yyyy-MM-dd')).year AS year, count(t) as all_tests "
            "OPTIONAL MATCH ()-[t:TESTS]->() "
            "WHERE date(apoc.date.format(apoc.date.parse(t.timestamp, 'ms', 'yyyy-MM-dd'), 'ms', 'yyyy-MM-dd')).month = month AND "
                  "date(apoc.date.format(apoc.date.parse(t.timestamp, 'ms', 'yyyy-MM-dd'), 'ms', 'yyyy-MM-dd')).year = year AND "
                  "t.res = 'Positive' "
            "RETURN round((count(t) * 1.0 / all_tests * 1.0) * 100.0 * 100.0) / 100.0 AS ratio, month, year "
            "ORDER BY year DESC, month DESC")
            return result.values()

if __name__ == "__main__":
    with open("password.txt", "r") as pass_reader:
        neo4j_password = pass_reader.readline().split()[0]
        populator = PopulateDB("bolt://localhost:7687", "neo4j", neo4j_password)
        populator.clear_db()
        # populator.create_people()
        populator.create_family(5)
        populator.create_meets_relations(50, (2020, 6, 19), (2021, 6, 19))
        populator.create_vaccines()
        populator._create_vaccinates()
        populator.create_swabs()
        populator.create_tests()
        populator.create_amenities(15)
        populator.create_visits_relations(50, 40, (2020, 6, 19), (2021, 6, 19))
        print("all the data have been loaded successfully.")
        #populator._query_one(populator)
        populator.close()