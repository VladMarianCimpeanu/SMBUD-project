MATCH (node) DETACH DELETE node
// command: create person
CREATE (p:Person{
  name: "Mario",
  surname: "Rossi",
  SSN: "RSSMRA90C07F205U",
  dateOfBirth: "1990-06-12"
})

// command: create relation MEETS
//TODO: we are assigning a date to the timestamp attribute. We shall change the type attribute or the assignment.
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
WHERE infected.SSN = "FRRLCU94C07F205O" AND v1.date = v2.date AND duration.inDays(date(v1.date), date()).days <= 10 AND AND duration.inDays(date(v1.date), date()).days >= 0
RETURN otherVisitor
UNION
MATCH (infected: Person)-[m: meets]->(personMet: Person)
WHERE infected.SSN = "FRRLCU94C07F205O" AND duration.inDays(date(m.date), date()).days <= 10 AND duration.inDays(date(m.date), date()).days >= 0
RETURN personMet
//TODO: I have to test it because I changed duration.between in duration.inDays (the first one as Andrea said doesn't work properly)

//Query that returns the most visited places by infected people during the X days before getting positive at a covid test
//(in this esample X is equal to ten)
//This query could be useful to study which places could be more related to infections than others and in this way
// discover the most unsafe places type
MATCH (p:Person)-[t:TESTS]->()
WHERE t.result = 'positive'
WITH p AS people, t.date AS dat
MATCH (people)-[v:VISITS]->(ps:PublicSpace)
WHERE duration.inDays(date(v.date), dat).days <= 10 AND duration.inDays(date(v.date), dat).days >= 0
RETURN ps.type, COUNT(ps.type)

//Command: changing all the LIVES relation of the people who live in the same house (this command could be useful in case of moving family)
MATCH (p:Person)-[l:LIVES]->(h:House)
WHERE h.address = 'from'
    WITH p as people, l AS lived
MATCH (new_house:House)
WHERE new_house.address = 'to'
    CREATE (people)-[liv:LIVES]->(new_house)
    DELETE lived


//TODO: write a query to study the vaccines efficacy (for example by taking all the vaccinated people and see how
//many of them get infected by a meets with a person who discovered to be infected in the past X days - for example 10 -)