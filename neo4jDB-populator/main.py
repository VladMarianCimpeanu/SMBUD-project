import random
import time
import numpy as np
import pandas as pd
from neo4j import GraphDatabase
from random_italian_things import RandomItalianPerson, RandomItalianHouse


class PopulateDB:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.people = []

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
                house = RandomItalianHouse()
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

                session.write_transaction(self._create_lives, ssn_family, id_house)

    def clear_db(self):
        with self.driver.session() as session:
            session.write_transaction(self._clear_db)
    
    def create_vaccines(self):
        with self.driver.session() as session:
            names = ['Moderna', 'Pfizer', 'AstraZeneca', 'Jensen']
            for name in names:
                session.write_transaction(self._create_vaccine, name)
            
    @staticmethod
    def _create_vaccine(tx,name):
        result = tx.run("CREATE (a:Vaccine{"
                       "name :$name"
                        "})", name = name)

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
    def _clear_db(tx):
        result = tx.run("MATCH (n) DETACH DELETE n")
        result_summary = result.consume()
        print("Deleted " + str(result_summary.counters.nodes_deleted) + " nodes")


if __name__ == "__main__":
    populator = PopulateDB("bolt://localhost:7687", "neo4j", "garden-civil-karate-bonjour-size-620")
    populator.clear_db()
    populator.create_family(10)
    populator.create_vaccines()
    populator.close()
