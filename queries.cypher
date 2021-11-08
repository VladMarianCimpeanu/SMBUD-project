//#########################################################################COMMANDS###########################################################################
// command: create person
CREATE (p:Person{
  name:      'Mario',
  surname:   'Rossi',
  ssn:       'RSSMRA90C07F205U',
  birthdate: '1990-06-12'
})

// command: create relation MEETS
//TODO: we are assigning a date to the timestamp attribute. We shall change the type attribute or the assignment.
//EDITED BY Pasquale : changed MEETS attribute from timestamp to date
MATCH (a: Person),
      (b: Person)
WHERE a.ssn = 'FRRLCU94C07F205O' AND b.ssn = 'RSSMRA90C07F205U'
CREATE (a)-[m1:MEETS {date: '2020-10-01'}]->(b),
       (b)-[m2:MEETS {date: '2020-10-01'}]->(a)

// command: create a new domicile
//EDITED BY Pasquale : added LIVES relationship attribute livesFrom                                      
MATCH (a: Person)
WHERE a.ssn = 'FRRLCU94C07F205O'
CREATE (a)-[:LIVES{livesFrom:'date_of_moving_house'}]->(new_house: House)
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
CREATE (guest)-[:LIVES{livesFrom : 'date_of_moving_house'}]->(h)

// command: create relation VACCINATES
// lotto must be in format AZ##, P##,J##,M## for coherence
MATCH (person_to_vaccinate: Person),
      (vax: Vaccine)
WHERE person_to_vaccinate.ssn = 'FRRLCU94C07F205O' AND vax.name = 'AstraZeneca'
CREATE (person_to_vaccinate)-[:VACCINATES {lot: 'ABV 2856', date: '2021-06-01'}]->(vax)

// command: create relation VISITS
MATCH (restaurant: PublicSpace),
      (guest: Person)
WHERE restaurant.code = 'rest1' AND guest.ssn = 'FRRLCU94C07F205O'
CREATE (guest)-[:VISITS {date: '2021-06-01'}]->(restaurant)

                      
//Command: changing all the LIVES relation of the people who live in the same house (this command could be useful in case of moving family)
MATCH (p:Person)-[l:LIVES]->(h:House)
WHERE h.address = 'address_of_old_house'
    WITH p AS people, l AS lived
MATCH (new_house:House)
WHERE new_house.address = 'address_of_new_house'
    CREATE (people)-[:LIVES{livesFrom: 'date_of_moving_house'}]->(new_house)
    DELETE lived


                                                
//#########################################################################QUERIES###########################################################################
//query: percentage people vaccinated per age range
//WORKS!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
MATCH (sample: Person)
WHERE duration.between(date(sample.birthdate), date()).years >= 30 AND
      duration.between(date(sample.birthdate), date()).years <= 50
WITH count(sample) AS sizeSample
MATCH (vaccinated: Person)-[:VACCINATES]->(vaccine: Vaccine)
WHERE duration.between(date(vaccinated.birthdate), date()).years >= 30 AND
      duration.between(date(vaccinated.birthdate), date()).years <= 50
RETURN (count(vaccinated) * 1.0 / sizeSample * 1.0) * 100.0

//query: find all the people living with a given person
//TODO
MATCH (person: Person)-[:LIVES]->()<-[:LIVES]-(roommate: Person)
WHERE person.ssn = "RSSMRA90C07F205U"
RETURN roommate

// query: find the last date someone discovered to be positive
//WORKS!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
MATCH (infected: Person)-[r:TESTS]->()
WHERE infected.ssn = 'RSSMRA90C07F205U' AND r.res = 'Positive'
WITH r AS test
ORDER BY test.timestamp DESC
LIMIT 1
RETURN head(collect(test.timestamp)) //TODO: I must try it, the goal should be obtain a date instead of a collection

//query: find all the people that met a given person for the last 10 days starting from a given date. For this example, the
// day taken in consideration is the day in which the query is run. When the goal is to get people
// in contact with the given person for the last ten days before he discovered to be positive, it is assumed
// first the last covid swab date is queried and then, the returned date is used as parameter instead of
// the function date().
//TODO : CHANGE QUERY DESCRIPTION! Starting date is not queries date but date in the interval 2020-06-19 and 2021-06-19
//WORKS FINE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
MATCH (infected: Person)-[:LIVES]->()<-[:LIVES]-(person: Person)
WHERE infected.ssn = "FLPRTI37L58A799Z"
RETURN person
UNION
MATCH (infected: Person)-[v1:VISITS]->()<-[v2:VISITS]-(roommate: Person)
WHERE infected.ssn = "FLPRTI37L58A799Z" AND v1.date = v2.date AND duration.inDays(date(v1.date), date('2021-06-19')).days <= 15 AND duration.inDays(date(v1.date), date('2021-06-19')).days >= 0
RETURN person
UNION
MATCH (infected: Person)-[m:MEETS]->(roommate: Person)
WHERE infected.ssn = "FLPRTI37L58A799Z" AND duration.inDays(date(m.date), date('2021-06-19')).days <= 15 AND duration.inDays(date(m.date), date('2021-06-19')).days >= 0
RETURN person

//Query that returns the most visited places by infected people during the X days before getting positive at a covid test
//(in this example X is equal to ten)
//This query could be useful to study which places could be more related to infections than others and in this way
// discover the most unsafe places type
//WORKS!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!                                                                                                                           
MATCH (p:Person)-[t:TESTS]->()
WHERE t.res = 'Positive'
WITH p AS people, date(apoc.date.format(apoc.date.parse(t.timestamp, 'ms', 'yyyy-MM-dd'), 'ms', 'yyyy-MM-dd')) AS dat
MATCH (people)-[v:VISITS]->(ps:PublicSpace)
WHERE duration.inDays(date(v.date), dat).days <= 10 AND duration.inDays(date(v.date), dat).days >= 0
RETURN ps.type, count(ps.type)
                                                                                                                                                 
                                                                    
//Query that returns the infection ratio among all the tested people for each month
//NOT TESTED
MATCH ()-[t:TESTS]->()
WITH date(apoc.date.format(apoc.date.parse(t.timestamp, 'ms', 'yyyy-MM-dd'), 'ms', 'yyyy-MM-dd')).month AS month,
     date(apoc.date.format(apoc.date.parse(t.timestamp, 'ms', 'yyyy-MM-dd'), 'ms', 'yyyy-MM-dd')).year AS year, count(t) as all_tests
MATCH ()-[t:TESTS]->()
WHERE date(apoc.date.format(apoc.date.parse(t.timestamp, 'ms', 'yyyy-MM-dd'), 'ms', 'yyyy-MM-dd')).month = month AND
      date(apoc.date.format(apoc.date.parse(t.timestamp, 'ms', 'yyyy-MM-dd'), 'ms', 'yyyy-MM-dd')).year = year AND
      t.res = 'Positive'
RETURN round((count(t) * 1.0 / all_tests * 1.0) * 100.0 * 100.0) / 100.0 AS ratio, month, year

//TODO: write a query to study the vaccines efficacy over relationship meets between vaccinated and infected. relationships lives and visits omitted for brevity 
MATCH (infected)-[t1:TESTS{res:'Positive'}]->()
MATCH (infected)-[m:MEETS]->(vaccinated)
MATCH vacc = ()-[:VACCINATES]->()
MATCH (vaccinated)-[v:VACCINATES]->(vaccine)
MATCH (vaccinated)-[t2:TESTS{res:'Positive'}]->()
WITH vacc,vaccinated, infected, date(apoc.date.format(apoc.date.parse(t1.timestamp, 'ms', 'yyyy-MM-dd'), 'ms', 'yyyy-MM-dd')) AS t1_date, date(apoc.date.format(apoc.date.parse(t2.timestamp, 'ms', 'yyyy-MM-dd'), 'ms', 'yyyy-MM-dd')) AS t2_date,date(m.date) AS m_date, date(v.date) AS v_date
WHERE date(m_date) > date(v_date) //meets with infected person after vaccine
    AND v_date < t1_date //vaccinated before infected has been tested positive
    AND v_date < t2_date //and before being tested positive
    AND abs(duration.inDays(t1_date, m_date).days) <= 7 //vaccinated tested positive within +/- 7 days meets  
    AND abs(duration.inDays(m_date, t2_date).days) <= 7 //infected tested positive within +/- 7 days meets
    AND abs(duration.inDays(t1_date, t2_date).days) <= 7 //infected tested positive within reasonable temporal window
RETURN (COUNT(DISTINCT vaccinated)*1.0)/(COUNT(vacc)*1.0))*100 AS VaccinatesInfectedPercentage


//TODO : vaccine efficacy computed as sum(vaccinated_positive)/sum(vaccinated)
//FIRST PART : MATCH VACCINATED PEOPLE
MATCH (p1)-[v1:VACCINATES]->(vacc1) WHERE vacc1.name = 'AstraZeneca'
//MATCH (p2)-[v2:VACCINATES]->(vacc2) WHERE vacc2.name = 'Moderna'
//MATCH (p3)-[v3:VACCINATES]->(vacc3) WHERE vacc3.name = 'Pfizer'
//MATCH (p4)-[v4:VACCINATES]->(vacc4) WHERE vacc4.name = 'Jensen'
//SECOND PART : MATCH, AMONG VACCINATED PEOPLE, INFECTED ONES (AFTER VACCINE)
MATCH (i1)-[t1:TESTS]->() WHERE t1.res = 'Positive' AND i1 = p1 AND date(apoc.date.format(apoc.date.parse(t1.timestamp, 'ms', 'yyyy-MM-dd'), 'ms', 'yyyy-MM-dd')) > date(v1.date)
//MATCH (i2)-[t2:TESTS]->() WHERE t2.res = 'Positive' AND i2 = p2 AND date(apoc.date.format(apoc.date.parse(t2.timestamp, 'ms', 'yyyy-MM-dd'), 'ms', 'yyyy-MM-dd')) > date(v2.date)
//MATCH (i3)-[t3:TESTS]->() WHERE t3.res = 'Positive' AND i3 = p3 AND date(apoc.date.format(apoc.date.parse(t3.timestamp, 'ms', 'yyyy-MM-dd'), 'ms', 'yyyy-MM-dd')) > date(v1.date)
//MATCH (i4)-[t4:TESTS]->() WHERE t4.res = 'Positive' AND i4 = p4 AND date(apoc.date.format(apoc.date.parse(t1.timestamp, 'ms', 'yyyy-MM-dd'), 'ms', 'yyyy-MM-dd')) > date(v1.date)
RETURN COUNT(DISTINCT v1), COUNT(DISTINCT i1)

    