//#########################################################################COMMANDS###########################################################################
// command: create person
CREATE (p:Person{
  name:      'Mario',
  surname:   'Rossi',
  ssn:       'RSSMRA90C07F205U',
  birthdate: '1990-06-12'
})

// command: create relation MEETS
//EDITED BY Pasquale : changed MEETS attribute from timestamp to date
MATCH (a: Person),
      (b: Person)
WHERE a.ssn = 'FRRLCU94C07F205O' AND b.ssn = 'RSSMRA90C07F205U'
CREATE (a)-[m1:MEETS {date: '2020-10-01'}]->(b),
       (b)-[m2:MEETS {date: '2020-10-01'}]->(a)

// command: create a new domicile
//EDITED BY Pasquale : added LIVES relationship attribute livesFrom                                      
MATCH (a: Person)
//-[l:LIVES] - > (h)
WHERE a.ssn = 'FRRLCU94C07F205O'
CREATE (a)-[:LIVES{livesFrom:'date_of_moving_house'}]->(new_house: House)
//DELETE l
//CREATE (a)-[:LIVES{livesFrom: l.livesFrom, movingDate : 'date_of_moving_house'}]->(h)
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

                      
//Command: changing all the LIVES relations of the people who live in the same house (this command could be useful in case of moving family)
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
WHERE duration.between(date(sample.birthdate), date()).years >= X
      AND
      duration.between(date(sample.birthdate), date()).years <= Y
WITH sample AS sizeSample
MATCH (vaccinated:Person)-[:VACCINATES]->(vaccine: Vaccine)
WHERE duration.between(date(vaccinated.birthdate), date()).years >= X
      AND
      duration.between(date(vaccinated.birthdate), date()).years <= Y
RETURN
CASE
WHEN COUNT(DISTINCT vaccinated) = 0 THEN 0.0
WHEN COUNT(DISTINCT sizeSample) = 0 THEN 0.0
ELSE (COUNT(DISTINCT vaccinated) * 1.0 / COUNT(DISTINCT sizeSample) * 1.0) * 100.0
END AS Percentage

//query: find all the people living with a given person
//WORKS!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
MATCH (p1)-[l1:LIVES]->()
MATCH (p2)-[l2:LIVES]->()
WHERE p1.ssn = 'CMPGRG77T03E532G'
  AND l1.livesFrom < '2021-06-19'
  AND l2.livesFrom < '2021-06-19'
WITH max(l1.livesFrom) AS max1, max(l2.livesFrom) AS max2, p1 AS p1, p2 AS p2
MATCH (p1)-[l3:LIVES]->(h)<-[l4:LIVES]-(p2)
WHERE l3.livesFrom = max1
    AND l4.livesFrom = max2
RETURN p2, l4, h

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
// the date '2021-06-19'. In this case the starting date is '2021-06-19' due the fact data are loaded between 2020-06-19 and 2021-06-19
// in the demo db.
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

//Query that returns the percentage of infected people over all visits for every place by month and city
//This query could be useful to study which places could be more related to infections than others and in this way
// discover the most unsafe places in a desired month and city
//WORKS!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!                                                                                                                           
MATCH (p1:Person)-[v:VISITS]->(ps:PublicSpace)
WHERE date(v.date).month = 10 AND date(v.date).year = 2021 AND ps.city = 'Milano'
WITH ps.name AS space_name, v AS total_visits, p1 AS total_people
OPTIONAL MATCH (p:Person)-[t:TESTS]->()
WHERE p.ssn IN total_people.ssn AND t.res = 'Positive' AND duration.inDays(date(total_visits.date), date(apoc.date.format(apoc.date.parse(t.timestamp, 'ms', 'yyyy-MM-dd'), 'ms', 'yyyy-MM-dd'))).days >= 0 AND duration.inDays(date(total_visits.date), date(apoc.date.format(apoc.date.parse(t.timestamp, 'ms', 'yyyy-MM-dd'), 'ms', 'yyyy-MM-dd'))).days <= 7
RETURN
CASE
WHEN COUNT(DISTINCT p) = 0 THEN 0.0
ELSE (COUNT(DISTINCT p)*1.0 / COUNT(DISTINCT total_people)*1.0)*100.0
END AS percentage, space_name
                                                                                                                                                 
                                                                    
//Query that returns the infection ratio among all the tested people for each month
//TESTED: WORKS but does not return 0 for months without positives
MATCH ()-[t:TESTS]->()
WITH date(apoc.date.format(apoc.date.parse(t.timestamp, 'ms', 'yyyy-MM-dd'), 'ms', 'yyyy-MM-dd')).month AS month,
     date(apoc.date.format(apoc.date.parse(t.timestamp, 'ms', 'yyyy-MM-dd'), 'ms', 'yyyy-MM-dd')).year AS year, count(t) as all_tests
OPTIONAL MATCH ()-[t:TESTS]->()
WHERE date(apoc.date.format(apoc.date.parse(t.timestamp, 'ms', 'yyyy-MM-dd'), 'ms', 'yyyy-MM-dd')).month = month AND
      date(apoc.date.format(apoc.date.parse(t.timestamp, 'ms', 'yyyy-MM-dd'), 'ms', 'yyyy-MM-dd')).year = year AND
      t.res = 'Positive'
RETURN round((count(t) * 1.0 / all_tests * 1.0) * 100.0 * 100.0) / 100.0 AS ratio, month, year
ORDER BY year DESC, month DESC

//QUERY to study the vaccines efficacy over relationship meets between vaccinated and infected. relationships lives and visits omitted for brevity 
MATCH (infected)-[t1:TESTS{res:'Positive'}]->()
MATCH (infected)-[m:MEETS]->(vaccinated)
MATCH (p)-[:VACCINATES]->()
MATCH (vaccinated)-[v:VACCINATES]->(vaccine)
MATCH (vaccinated)-[t2:TESTS{res:'Positive'}]->()
WITH vaccinated, infected, date(apoc.date.format(apoc.date.parse(t1.timestamp, 'ms', 'yyyy-MM-dd'), 'ms', 'yyyy-MM-dd')) AS t1_date, date(apoc.date.format(apoc.date.parse(t2.timestamp, 'ms', 'yyyy-MM-dd'), 'ms', 'yyyy-MM-dd')) AS t2_date,date(m.date) AS m_date, date(v.date) AS v_date, toFloat(COUNT(DISTINCT p)) AS total_vaccinated, toFloat(COUNT(DISTINCT vaccinated)) AS infected_vaccinated
WHERE date(m_date) > date(v_date) //meets with infected person after vaccine
    AND v_date < t1_date //vaccinated before infected has been tested positive
    AND v_date < t2_date //and before being tested positive
    AND abs(duration.inDays(t1_date, m_date).days) <= 7 //vaccinated tested positive within +/- 7 days meets  
    AND abs(duration.inDays(m_date, t2_date).days) <= 7 //infected tested positive within +/- 7 days meets
    AND abs(duration.inDays(t1_date, t2_date).days) <= 7 //infected tested positive within reasonable temporal window
RETURN (infected_vaccinated/total_vaccinated)*100 AS InfectedVaccinatedRatioInMeets

//QUERY: Vaccine efficacy computed as sum(vaccinated_positive)/sum(vaccinated)
MATCH (p1:Person)-[:VACCINATES]->(v1:Vaccine {name: 'AstraZeneca'})
MATCH (p2:Person)-[:VACCINATES]->(v2:Vaccine {name: 'Moderna'})
MATCH (p3:Person)-[:VACCINATES]->(v3:Vaccine {name: 'Pfizer'})
MATCH (p4:Person)-[:VACCINATES]->(v4:Vaccine {name: 'Jensen'})
WITH count(DISTINCT p1) AS vaccinated_astrazeneca,count(DISTINCT p2) AS vaccinated_moderna,count(DISTINCT p3) AS vaccinated_pfizer,count(DISTINCT p4) AS vaccinated_jensen
OPTIONAL MATCH ()<-[t1:TESTS]-(p1:Person)-[v1:VACCINATES]->(vacc1:Vaccine {name: 'AstraZeneca'})
WHERE t1.res = 'Positive'
    AND date(apoc.date.format(apoc.date.parse(t1.timestamp, 'ms', 'yyyy-MM-dd'), 'ms', 'yyyy-MM-dd')) > date(v1.date)
OPTIONAL MATCH ()<-[t2:TESTS]-(p2:Person)-[v2:VACCINATES]->(vacc2:Vaccine {name: 'Moderna'})
WHERE t2.res = 'Positive'
    AND date(apoc.date.format(apoc.date.parse(t2.timestamp, 'ms', 'yyyy-MM-dd'), 'ms', 'yyyy-MM-dd')) > date(v2.date)                                       
OPTIONAL MATCH ()<-[t3:TESTS]-(p3:Person)-[v3:VACCINATES]->(vacc3:Vaccine {name: 'Pfizer'})
WHERE t3.res = 'Positive'
    AND date(apoc.date.format(apoc.date.parse(t3.timestamp, 'ms', 'yyyy-MM-dd'), 'ms', 'yyyy-MM-dd')) > date(v3.date)
OPTIONAL MATCH ()<-[t4:TESTS]-(p4:Person)-[v4:VACCINATES]->(vacc4:Vaccine {name: 'Jensen'})
WHERE t4.res = 'Positive'
    AND date(apoc.date.format(apoc.date.parse(t4.timestamp, 'ms', 'yyyy-MM-dd'), 'ms', 'yyyy-MM-dd')) > date(v4.date)
WITH vaccinated_astrazeneca,vaccinated_moderna,vaccinated_pfizer,vaccinated_jensen,count(DISTINCT p1) AS vaccinated_infected_astra,count(DISTINCT p2) AS vaccinated_infected_moderna,count(DISTINCT p3) AS vaccinated_infected_pfizer,count(DISTINCT p4) AS vaccinated_infected_jensen
RETURN (1- (toFloat(vaccinated_infected_astra)/toFloat(vaccinated_astrazeneca)))*100 AS AstraZenecaEfficacy,
(1- (toFloat(vaccinated_infected_moderna)/toFloat(vaccinated_moderna)))*100 AS ModernaEfficacy,(1- (toFloat(vaccinated_infected_pfizer)/toFloat(vaccinated_pfizer)))*100 AS PfizerEfficacy,(1- (toFloat(vaccinated_infected_jensen)/toFloat(vaccinated_jensen)))*100 AS JensenEfficacy


//finds false negatives; for false positive switch pre with post
match (p: Person)-[pre: TESTS]->()<-[post:TESTS]-(p)
where duration.between(datetime({ epochMillis: apoc.date.parse(pre.timestamp, 'ms', 'yyyy-MM-dd HH:mm:ss')}), datetime({ epochMillis: apoc.date.parse(post.timestamp, 'ms', 'yyyy-MM-dd HH:mm:ss')})).hours < 24
and duration.between(datetime({ epochMillis: apoc.date.parse(pre.timestamp, 'ms', 'yyyy-MM-dd HH:mm:ss')}), datetime({ epochMillis: apoc.date.parse(post.timestamp, 'ms', 'yyyy-MM-dd HH:mm:ss')})).hours > 0
and pre.res="Negative"
and post.res="Positive"
return p, pre, post