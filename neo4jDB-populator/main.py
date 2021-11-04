import random

from neo4j import GraphDatabase
from name_parser import NameParser
from codicefiscale import codicefiscale


class PopulateDB:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.people = []

    def close(self):
        self.driver.close()

    def create_people(self, names, surnames):
        with self.driver.session() as session:
            for i in range(100):
                ssn_created = session.write_transaction(self._create_person, random.choice(names), random.choice(surnames), "ASFJFWNVWI", "1999-05-17")
                self.people.append(ssn_created)
            # print(greeting1)
            print(ssn_created)

    @staticmethod
    def _create_and_return_greeting(tx, message):
        result = tx.run("CREATE (a:Greeting) "
                        "SET a.message = $message "
                        "RETURN a.message + ', from node ' + id(a)", message=message)
        return result.single()[0]

    @staticmethod
    def _create_person(tx, name, surname, ssn, birth):
        result = tx.run("CREATE (a:Person {"
                        "name : $name,"
                        "surname : $surname,"
                        "ssn : $ssn, "
                        "dateOfBirth : $birth"
                        "}) "
                        "RETURN a.ssn", name=name, surname=surname, ssn=ssn, birth=birth)
        return result.single()[0]


if __name__ == "__main__":
    txt_parser = NameParser()
    names = txt_parser.parse_txt("nomi_italiani.txt")
    surnames = txt_parser.parse_txt("cognomi.txt")
    populator = PopulateDB("bolt://localhost:7687", "neo4j", "neo4jnew")
    populator.create_people(names, surnames)
    populator.close()
