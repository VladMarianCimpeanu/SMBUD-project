MATCH (node) DETACH DELETE node
// command: create person
CREATE (p:Person{
  name:      'Mario',
  surname:   'Rossi',
  ssn:       'RSSMRA90C07F205U',
  birthdate: '1990-06-12'
})

// command: create relation MEETS
//TODO: we are assigning a date to the timestamp attribute. We shall change the type attribute or the assignment.
MATCH (a: Person),
      (b: Person)
WHERE a.ssn = 'FRRLCU94C07F205O' AND b.ssn = 'RSSMRA90C07F205U'
CREATE (a)-[m1:MEETS {timestamp: date('2019-10-01')}]->(b),
       (b)-[m2:MEETS {timestamp: date('2019-10-01')}]->(a)

// command: create a new domicile
MATCH (a: Person)
WHERE a.ssn = 'FRRLCU94C07F205O'
CREATE (a)-[:LIVES]->(new_house: House)
RETURN new_house

// command: adding roommates
CREATE (:Person {
  name:      'Lucia',
  surname:   'Ferri',
  ssn:       'FRRLCU94C07F205O',
  birthdate: '1995-02-13'
})
MATCH (host: Person)-[:LIVES]->(h: House),
      (guest: Person)
WHERE host.ssn = 'RSSMRA90C07F205U' AND guest.ssn = 'FRRLCU94C07F205O'
CREATE (guest)-[:LIVES]->(h)

// command: create relation VACCINATES
MATCH (person_to_vaccinate: Person),
      (vax: Vaccine)
WHERE person_to_vaccinate.ssn = 'FRRLCU94C07F205O' AND vax.name = 'AstraZeneca'
CREATE (person_to_vaccinate)-[:VACCINATES {lot: 'ABV 2856', date: '2021-06-01'}]->(vax)

//TODO: timestamp or date? discuss
// command: create relation VISITS
MATCH (restaurant: PublicSpace),
      (guest: Person)
WHERE restaurant.code = 'rest1' AND guest.ssn = 'FRRLCU94C07F205O'
CREATE (guest)-[:VISITS {date: '2021-06-01'}]->(restaurant)

//query: percentage people vaccinated per age range
//WORKS!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
MATCH (sample: Person)
<<<<<<< Updated upstream
WHERE duration.between(date(sample.birthdate), date()).years >= 30 AND
      duration.between(date(sample.birthdate), date()).years <= 50
WITH count(sample) AS sizeSample
MATCH (vaccinated: Person)-[:VACCINATES]->(vaccine: Vaccine)
WHERE duration.between(date(vaccinated.birthdate), date()).years >= 30 AND
      duration.between(date(vaccinated.birthdate), date()).years <= 50
RETURN (count(vaccinated) * 1.0 / sizeSample * 1.0) * 100.0

//query: find all the people living with a given person
MATCH (person: Person)-[:LIVES]->(house)<-[:LIVES]-(roommate: Person)
WHERE person.ssn = 'RSSMRA90C07F205U'
=======
WHERE duration.between(date(sample.birthdate), date()).years >= 10 AND
      duration.between(date(sample.birthdate), date()).years <= 100
WITH COUNT(sample) as sizeSample
MATCH (vaccinated: Person)-[:VACCINATES]->(vaccine: Vaccine)
WHERE duration.between(date(vaccinated.birthdate), date()).years >= 10 AND
      duration.between(date(vaccinated.birthdate), date()).years <= 100
RETURN (COUNT(DISTINCT vaccinated) * 1.0 / sizeSample * 1.0) * 100.0

//query: find all the people living with a given person
MATCH (person: Person)-[:LIVES]->()<-[:LIVES]-(roommate: Person)
WHERE person.ssn = "RSSMRA90C07F205U"
>>>>>>> Stashed changes
RETURN roommate

// query: find the last date someone discovered to be positive
MATCH (infected: Person)-[r:TESTS]->()
WHERE infected.ssn = 'RSSMRA90C07F205U' AND r.res = 'positive'
WITH r AS test
ORDER BY test.date DESC
LIMIT 1
RETURN head(collect(test.date)) //TODO: I must try it, the goal should be obtain a date instead of a collection

//query: find all the people that met a given person for the last 10 days starting from a given date. For this example, the
// day taken in consideration is the day in which the query is run. When the goal is to get people
// in contact with the given person for the last ten days before he discovered to be positive, it is assumed
// first the last covid swab date is queried and then, the returned date is used as parameter instead of
// the function date().
<<<<<<< Updated upstream

MATCH (infected: Person)-[:LIVES]->()<-[:LIVES]-(roommate: Person)
WHERE infected.ssn = 'FRRLCU94C07F205O'
RETURN roommate
UNION
MATCH (infected: Person)-[v1:VISITS]->()<-[v2:VISITS]-(otherVisitor: Person)
WHERE infected.ssn = 'FRRLCU94C07F205O' AND v1.date = v2.date AND duration.inDays(date(v1.date), date()).days <= 10 AND duration.inDays(date(v1.date), date()).days >= 0
RETURN otherVisitor
UNION
MATCH (infected: Person)-[m: meets]->(personMet: Person)
WHERE infected.ssn = 'FRRLCU94C07F205O' AND duration.inDays(date(m.date), date()).days <= 10 AND duration.inDays(date(m.date), date()).days >= 0
RETURN personMet
//TODO: I have to test it because I changed duration.between in duration.inDays (the first one as Andrea said doesn't work properly)
=======
//WORKS FINE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
MATCH (infected: Person)-[:LIVES]->()<-[:LIVES]-(roommate: Person)
WHERE infected.ssn = "FLPRTI37L58A799Z"
RETURN roommate
UNION
MATCH (infected: Person)-[v1:VISITS]->()<-[v2:VISITS]-(roommate: Person)
WHERE infected.ssn = "FLPRTI37L58A799Z" AND v1.date = v2.date AND duration.inDays(date(v1.date), date('2021-06-19')).days <= 15 AND duration.inDays(date(v1.date), date('2021-06-19')).days >= 0
RETURN roommate
UNION
MATCH (infected: Person)-[m:MEETS]->(roommate: Person)
WHERE infected.ssn = "FLPRTI37L58A799Z" AND duration.inDays(date(m.date), date('2021-06-19')).days <= 15 AND duration.inDays(date(m.date), date('2021-06-19')).days >= 0
RETURN roommate
>>>>>>> Stashed changes

//Query that returns the most visited places by infected people during the X days before getting positive at a covid test
//(in this example X is equal to ten)
//This query could be useful to study which places could be more related to infections than others and in this way
// discover the most unsafe places type
//WORKS!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!                                                                                                                           
MATCH (p:Person)-[t:TESTS]->()
<<<<<<< Updated upstream
WHERE t.res = 'positive'
WITH p AS people, t.date AS dat
=======
WHERE t.res = 'Positive'
WITH p AS people, date(apoc.date.format(apoc.date.parse(t.timestamp, 'ms', 'yyyy-MM-dd'), 'ms', 'yyyy-MM-dd')) AS dat
>>>>>>> Stashed changes
MATCH (people)-[v:VISITS]->(ps:PublicSpace)
WHERE duration.inDays(date(v.date), dat).days <= 10 AND duration.inDays(date(v.date), dat).days >= 0
RETURN ps.type, count(ps.type)

                      
                      
//Command: changing all the LIVES relation of the people who live in the same house (this command could be useful in case of moving family)
MATCH (p:Person)-[l:LIVES]->(h:House)
WHERE h.address = 'from'
    WITH p AS people, l AS lived
MATCH (new_house:House)
WHERE new_house.address = 'to'
    CREATE (people)-[liv:LIVES]->(new_house)
    DELETE lived


//TODO: write a query to study the vaccines efficacy (for example by taking all the vaccinated people and see how
//many of them get infected by a meets with a person who discovered to be infected in the past X days - for example 10 -)


//Query that returns the infection ratio among all the tested people for each month
MATCH ()-[t:TESTS]->()
WITH date(apoc.date.format(apoc.date.parse(t.timestamp, 'ms', 'yyyy-MM-dd'), 'ms', 'yyyy-MM-dd')).month AS month,
     date(apoc.date.format(apoc.date.parse(t.timestamp, 'ms', 'yyyy-MM-dd'), 'ms', 'yyyy-MM-dd')).year AS year, count(t) as all_tests
MATCH ()-[t:TESTS]->()
WHERE date(apoc.date.format(apoc.date.parse(t.timestamp, 'ms', 'yyyy-MM-dd'), 'ms', 'yyyy-MM-dd')).month = month AND
      date(apoc.date.format(apoc.date.parse(t.timestamp, 'ms', 'yyyy-MM-dd'), 'ms', 'yyyy-MM-dd')).year = year AND
      t.res = 'Positive'
RETURN round((count(t) * 1.0 / all_tests * 1.0) * 100.0 * 100.0) / 100.0 AS ratio, month, year
