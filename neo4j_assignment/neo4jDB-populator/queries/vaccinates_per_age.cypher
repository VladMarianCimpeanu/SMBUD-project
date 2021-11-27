MATCH (sample: Person)
WHERE duration.between(date(sample.birthdate), date()).years >= $min_age
      AND
      duration.between(date(sample.birthdate), date()).years <= $max_age
WITH sample AS sizeSample
MATCH (vaccinated:Person)-[:VACCINATES]->(vaccine: Vaccine)
WHERE duration.between(date(vaccinated.birthdate), date()).years >= $min_age
      AND
      duration.between(date(vaccinated.birthdate), date()).years <= $max_age
RETURN
CASE
WHEN COUNT(DISTINCT vaccinated) = 0 THEN 0.0
WHEN COUNT(DISTINCT sizeSample) = 0 THEN 0.0
ELSE (COUNT(DISTINCT vaccinated) * 1.0 / COUNT(DISTINCT sizeSample) * 1.0) * 100.0
END AS Percentage