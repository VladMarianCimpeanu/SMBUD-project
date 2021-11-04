MATCH (node) DETACH DELETE node
// command: create person
CREATE (p:Person{
  name: "Mario",
  surname: "Rossi",
  SSN: "RSSMRA90C07F205U",
  dateOfBirth: "1990-06-12"
})

// command: create relation MEETS
//TODO: we are assigning a date to the timestamp attribute. We shall change the type attribute or the assignement.
MATCH (a: Person),
      (b: Person)
WHERE a.SSN = 'FRRLCU94C07F205O' AND b.SSN = 'RSSMRA90C07F205U'
CREATE (a)-[m1:MEETS {timestamp: date("2019-10-01")}]->(b),
       (b)-[m2:MEETS {timestamp: date("2019-10-01")}]->(a)

// command: create a new domicile
MATCH (a: Person)
WHERE a.SSN = "FRRLCU94C07F205O"
CREATE (a)-[:lives]->(new_house: House)
RETURN new_house

// command: adding roommates
CREATE (:Person {
  name: "Lucia",
  surname: "Ferri",
  SSN: "FRRLCU94C07F205O",
  dateOfBirth: "1995-02-13"
})
MATCH (host: Person)-[:lives]->(h: House),
      (guest: Person)
WHERE host.SSN = "RSSMRA90C07F205U" AND guest.SSN = "FRRLCU94C07F205O"
CREATE (guest)-[:lives]->(h)

// command: create relation VACCINATES
MATCH (person_to_vaccinate: Person),
      (vax: Vaccine)
WHERE person_to_vaccinate.SSN = "FRRLCU94C07F205O" AND vax.name = "AstraZeneca"
CREATE (person_to_vaccinate)-[:vaccinates {lot: "ABV 2856", date: "2021-06-01"}]->(vax)

//TODO: timestamp or date? discuss
// command: create relation VISITS
MATCH (restaurant: PublicSpace),
      (guest: Person)
WHERE restaurant.code = "rest1" and guest.SSN = "FRRLCU94C07F205O"
CREATE (guest)-[:visits {date: "2021-06-01"}]->(restaurant)

//query: percentage people vaccinated per age range
MATCH (sample: Person)
WHERE duration.between(date(sample.dateOfBirth), date()).years >= 30 AND
      duration.between(date(sample.dateOfBirth), date()).years <= 50
WITH COUNT(sample) as sizeSample
MATCH (vaccinated: Person)-[:vaccinates]->(vaccine: Vaccine)
WHERE duration.between(date(vaccinated.dateOfBirth), date()).years >= 30 AND
      duration.between(date(vaccinated.dateOfBirth), date()).years <= 50
RETURN (COUNT(vaccinated) * 1.0 / sizeSample * 1.0) * 100.0

//query: find all the people living with a given person
MATCH (person: Person)-[:lives]->(house)<-[:lives]-(roommate: Person)
WHERE person.SSN = "RSSMRA90C07F205U"
RETURN roommate

// query: find the last date someone discovered to be positive
MATCH (infected: Person)-[r:tests]->()
WHERE infected.SSN = "RSSMRA90C07F205U" and r.result = "positive"
WITH r as test
ORDER BY test.date DESC
LIMIT 1
RETURN head(collect(test.date)) //TODO: I must try it, the goal should be obtain a date instead of a collection

//query: find all the people that met a given person for the last 10 days starting from a given date. For this example, the
// day taken in consideration is the day in which the query is run. When the goal is to get people
// in contact with the given person for the last ten days before he discovered to be positive, it is assumed
// first the last covid swab date is queried and then, the returned date is used as parameter instead of
// the function date().

MATCH (infected: Person)-[:lives]->()<-[:lives]-(roommate: Person)
WHERE infected.SSN = "FRRLCU94C07F205O"
RETURN roommate
UNION
MATCH (infected: Person)-[v1:visits]->()<-[v2:visits]-(otherVisitor: Person)
WHERE infected.SSN = "FRRLCU94C07F205O" AND v1.date = v2.date AND duration.between(date(v1.date), date()).days <= 10
RETURN otherVisitor
UNION
MATCH (infected: Person)-[m: meets]->(personMet: Person)
WHERE infected.SSN = "FRRLCU94C07F205O" AND duration.between(date(m.date), date()).days <= 10
RETURN otherVisitor