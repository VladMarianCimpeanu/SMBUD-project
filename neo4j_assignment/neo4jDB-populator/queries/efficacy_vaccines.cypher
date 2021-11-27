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
