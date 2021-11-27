// Setting parameters
// :param ssn => "DRNMJT43R48F220W"
// :param age_min => 20
// :param age_max => 30
// :param month => 12
// :param year => 2020
// :param city => 'Milano'
// :param end_date => "2020-06-13"
// :param incubation => Duration({days: 15})


//Queries
// Vaccination percentage for a given age range

MATCH (sample: Person)
WHERE duration.between(date(sample.birthdate), date()).years >= $age_min
AND
duration.between(date(sample.birthdate), date()).years <= $age_max
WITH sample AS sizeSample
MATCH (vaccinated:Person)-[:VACCINATES]->(vaccine: Vaccine)
WHERE duration.between(date(vaccinated.birthdate), date()).years >=
$age_min
AND
duration.between(date(vaccinated.birthdate), date()).years <=
$age_max
RETURN
CASE
WHEN COUNT(DISTINCT vaccinated) = 0 THEN 0.0
WHEN COUNT(DISTINCT sizeSample) = 0 THEN 0.0
ELSE (COUNT(DISTINCT vaccinated) * 1.0 / COUNT(DISTINCT sizeSample) *
1.0) * 100.0
END AS Percentage

//////////////////////////////////////////////////////////////////////////////
// Infection ratio per month

MATCH ()-[t:TESTS]->()
WITH date(apoc.date.format(apoc.date.parse(t.timestamp, 'ms', 'yyyy-MM-dd'), 'ms', 'yyyy-MM-dd')).month AS month,
     date(apoc.date.format(apoc.date.parse(t.timestamp, 'ms', 'yyyy-MM-dd'), 'ms', 'yyyy-MM-dd')).year AS year, count(t) as all_tests
OPTIONAL MATCH ()-[t:TESTS]->()
WHERE date(apoc.date.format(apoc.date.parse(t.timestamp, 'ms', 'yyyy-MM-dd'), 'ms', 'yyyy-MM-dd')).month = month AND
    date(apoc.date.format(apoc.date.parse(t.timestamp, 'ms', 'yyyy-MM-dd'), 'ms', 'yyyy-MM-dd')).year = year AND
    t.res = 'Positive'
RETURN round((COUNT(t) * 1.0 / all_tests * 1.0) * 100.0 * 100.0) / 100.0 AS ratio, month, year
ORDER BY year DESC, month DESC

//////////////////////////////////////////////////////////////////////////////
// False positives

MATCH (p: Person)-[pre: TESTS]->()<-[post:TESTS]-(p)
WHERE duration.between(datetime({ epochMillis: apoc.date.parse(pre.
timestamp, 'ms', 'yyyy-MM-dd HH:mm:ss')}), datetime({ epochMillis:
apoc.date.parse(post.timestamp, 'ms', 'yyyy-MM-dd HH:mm:ss')})).
hours < 24
AND duration.between(datetime({ epochMillis: apoc.date.parse(pre.
timestamp, 'ms', 'yyyy-MM-dd HH:mm:ss')}), datetime({ epochMillis:
apoc.date.parse(post.timestamp, 'ms', 'yyyy-MM-dd HH:mm:ss')})).
hours > 0
AND post.res="Negative"
AND pre.res="Positive"
RETURN p, pre, post

//////////////////////////////////////////////////////////////////////////////
// Most unsafe public spaces for a given city

MATCH (p1:Person)-[v:VISITS]->(ps:PublicSpace)
WHERE date(v.date).month = $month AND date(v.date).year = $year
      AND ps.city = $city
WITH ps.name AS space_name, v AS total_visits, p1 AS total_people
OPTIONAL MATCH (p:Person)-[t:TESTS]->()
WHERE p.ssn IN total_people.ssn AND t.res = 'Positive' AND duration.inDays(date(total_visits.date), date(apoc.date.format(apoc.date.parse(t.timestamp, 'ms', 'yyyy-MM-dd'), 'ms', 'yyyy-MM-dd'))).days >= 0 AND duration.inDays(date(total_visits.date), date(apoc.date.format(apoc.date.parse(t.timestamp, 'ms', 'yyyy-MM-dd'), 'ms', 'yyyy-MM-dd'))).days <= 15
RETURN
CASE
WHEN COUNT(DISTINCT p) = 0 THEN 0.0
ELSE (COUNT(DISTINCT p)*1.0 / COUNT(DISTINCT total_people)*1.0)*100.0
END AS percentage, space_name ORDER BY percentage DESC

//////////////////////////////////////////////////////////////////////////////
// Vaccine efficacy

MATCH (p1:Person)-[:VACCINATES]->(v1:Vaccine {name: 'AstraZeneca'})
MATCH (p2:Person)-[:VACCINATES]->(v2:Vaccine {name: 'Moderna'})
MATCH (p3:Person)-[:VACCINATES]->(v3:Vaccine {name: 'Pfizer'})
MATCH (p4:Person)-[:VACCINATES]->(v4:Vaccine {name: 'Jensen'})
WITH COUNT(DISTINCT p1) AS vaccinated_astrazeneca, COUNT(DISTINCT p2) AS vaccinated_moderna, COUNT(DISTINCT p3) AS vaccinated_pfizer, COUNT(DISTINCT p4) AS vaccinated_jensen
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
WITH vaccinated_astrazeneca,vaccinated_moderna,vaccinated_pfizer,vaccinated_jensen, COUNT(DISTINCT p1) AS vaccinated_infected_astra, COUNT(DISTINCT p2) AS vaccinated_infected_moderna, COUNT(DISTINCT p3) AS vaccinated_infected_pfizer, COUNT(DISTINCT p4) AS vaccinated_infected_jensen
RETURN (1- (toFloat(vaccinated_infected_astra)/toFloat(vaccinated_astrazeneca)))*100 AS AstraZenecaEfficacy,
    (1- (toFloat(vaccinated_infected_moderna)/toFloat(vaccinated_moderna)))*100 AS ModernaEfficacy,(1- (toFloat(vaccinated_infected_pfizer)/toFloat(vaccinated_pfizer)))*100 AS PfizerEfficacy,(1- (toFloat(vaccinated_infected_jensen)/toFloat(vaccinated_jensen)))*100 AS JensenEfficacy

//////////////////////////////////////////////////////////////////////////////
// People to quarantine
MATCH (infected:Person)-[l1:LIVES]->(h)<-[l2:LIVES]-(person:Person)
WHERE infected.ssn = $ssn
  AND date(l1.livesFrom) <= date($end_date) AND (date(l1.movingDate) >=   
  date($end_date) - $incubation OR l1.movingDate is  NULL)
  AND date(l2.livesFrom) <= date($end_date) AND (date(l2.movingDate) >=   
  date($end_date) - $incubation OR l2.movingDate is NULL)
  AND (date(l2.movingDate) >= date(l1.livesFrom) OR date(l2.livesFrom) <= 
  date(l1.movingDate))
RETURN person
UNION
MATCH (infected: Person)-[v1:VISITS]->()<-[v2:VISITS]-(person: Person)
WHERE infected.ssn = $ssn AND v1.date = v2.date AND duration.inDays(date(v1.date), date($end_date)).days <= 15 AND duration.inDays(date(v1.date), date($end_date)).days >= 0
RETURN person
UNION
MATCH (infected: Person)-[m:MEETS]->(person: Person)
WHERE infected.ssn = $ssn AND duration.inDays(date(m.date), date($end_date)).days <= 15 AND duration.inDays(date(m.date), date($end_date)).days >= 0
RETURN person