import random
import time
import pandas as pd

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
                ssn_created = session.write_transaction(self._create_person, random.choice(names),
                                                        random.choice(surnames), "ASFJFWNVWI", "1999-05-17")
                self.people.append(ssn_created)
            # print(greeting1)
            print(ssn_created)

    def create_family(self, names, surnames, towns, addresses, num_family):
        with self.driver.session() as session:
            for i in range(num_family):
                town = random.choice(towns)
                address = random.choice(addresses)
                id_house = session.write_transaction(self._create_house, town, address)
                ssn_family = []
                for j in range(random.randint(1, 6)):
                    ssn_family_member = session.write_transaction(self._create_person, random.choice(names), random.choice(surnames), "ASFJFWNVWI", "1999-05-17")
                    ssn_family.append(ssn_family_member)

                session.write_transaction(self._create_lives, ssn_family, id_house)


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

    def str_time_prop(start, end, time_format, prop):
        """Get a time at a proportion of a range of two formatted times.

        start and end should be strings specifying times formatted in the
        given format (strftime-style), giving an interval [start, end].
        prop specifies how a proportion of the interval to be taken after
        start.  The returned time will be in the specified format.
        """

        stime = time.mktime(time.strptime(start, time_format))
        etime = time.mktime(time.strptime(end, time_format))

        ptime = stime + prop * (etime - stime)

        return time.strftime(time_format, time.localtime(ptime))

    def random_date(start, end, prop):
        return start.str_time_prop(start, end, '%m/%d/%Y %I:%M %p', prop)



if __name__ == "__main__":
    txt_parser = NameParser()
    names = pd.read_csv('nomi.txt', sep='\n')
    surnames = pd.read_csv('cognomi.txt', sep='\n', header=None)
    towns = pd.read_csv('comuni.csv', header=None)
    addresses = pd.read_csv('addresses.csv', header=None)
    populator = PopulateDB("bolt://localhost:7687", "neo4j", "neo4jnew")

    populator.create_family(names.values.tolist(), surnames.values.tolist(), towns.values.tolist(), addresses.values.tolist(), 5)
    populator.close()
