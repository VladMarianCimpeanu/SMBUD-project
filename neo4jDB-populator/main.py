import random
import os
import time
import numpy as np
import pandas as pd
from neo4j import GraphDatabase
from random import choices
from random_italian_things import RandomItalianPerson, RandomItalianHouse
import date_generator as dg


class PopulateDB:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.people = []
        self.cities = {}  # dictionary which keys are cities and values are their citizens.
        self.names_city = []  # list with the keys of self.cities
        # read 'datasets_to_read' that contains as keys the name of the available city
        configuration_file = pd.read_csv("{}/random_italian_things/datasets/datasets_to_read.txt".format(os.path.dirname(os.path.abspath(__file__))))
        for index, row in configuration_file.iterrows():
            self.cities[row['key']] = []
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

    def create_family(self, num_family):
        with self.driver.session() as session:
            for i in range(num_family):
                city = random.choice(self.names_city)
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

    def create_swabs(self):
        with self.driver.session() as session:
            session.write_transaction(self._create_swab)

    def create_tests(self):
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

    def clear_db(self):
        with self.driver.session() as session:
            session.write_transaction(self._clear_db)

    def create_vaccines(self):
        with self.driver.session() as session:
            names = ['Moderna', 'Pfizer', 'AstraZeneca', 'Jensen']
            for name in names:
                session.write_transaction(self._create_vaccine, name)
                            
    def _create_vaccinates_relationship(self,tx,person_id,vaccine_name,lotto,date):
        result = tx.run("MATCH (a:Vaccine),(b:Person) WHERE a.name = $vaccine_name AND ID(b) = $person_id "
                           "CREATE (b)-[v:VACCINATES{lotto : $lotto, date: $date}] -> (a)", person_id = person_id,
                        vaccine_name = vaccine_name, lotto = lotto,date = date)

    def _get_people_id(self,tx):
        people_ids = []
        result = tx.run("MATCH (a:Person) RETURN ID(a)")
        for id in result:
            people_ids.append(id.values())
        return people_ids
    
    def _get_vaccines_id(self,tx):
        vaccine_ids = []
        result = tx.run("MATCH (a:Vaccine) RETURN ID(a), a.name")
        for tuple in result:
            vaccine_ids.append(tuple.values())
        return vaccine_ids


    #create vaccinates relationship
    
    def _create_vaccinates(self):
        with self.driver.session() as session:
            person_ids = session.read_transaction(self._get_people_id) #get people ids
            vaccine_name_id = session.read_transaction(self._get_vaccines_id) #get vaccines id and name
            lottos = pd.read_csv('vaccine_lotto.csv', sep = ';')
            for id in person_ids:
                prob = random.random() #with some probability a person has one, two or three vaccinates relationships
                if prob > 0.3:
                    v_name = random.choice(vaccine_name_id)[1]
                    lotto = random.choice(lottos[v_name])
                    random_date = dg.DateGenerator().random_datetimes_or_dates()
                    session.write_transaction(self._create_vaccinates_relationship,id[0],v_name,lotto,random_date.tolist()[0])
                    if prob > 0.6:
                        lotto = random.choice(lottos[v_name])
                        date2 = dg.DateGenerator().random_datetimes_or_dates()
                        #can't vaccinate twice in the same day, other temporal constraints are out of scope
                        while (date2 == random_date): date2 = dg.DateGenerator().random_datetimes_or_dates()
                        session.write_transaction(self._create_vaccinates_relationship,id[0],v_name,lotto,date2.tolist()[0])
                        if prob > 0.95:
                            lotto = random.choice(lottos[v_name])
                            while (date2 == random_date): date2 = dg.DateGenerator().random_datetimes_or_dates()
                            session.write_transaction(self._create_vaccinates_relationship,id[0],v_name,lotto,date2.tolist()[0])

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
                            "CREATE (a)-[r:LIVES]->(b)"
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


if __name__ == "__main__":
    with open("password.txt", "r") as pass_reader:
        neo4j_password = pass_reader.readline().split()[0]
        populator = PopulateDB("bolt://localhost:7687", "neo4j", neo4j_password)
        populator.clear_db()
        #populator.create_people()
        populator.create_family(10)
        populator.create_vaccines()
        populator._create_vaccinates()
        populator.create_swabs()
        populator.create_tests()
        populator.close()
