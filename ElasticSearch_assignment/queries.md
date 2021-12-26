## queries
- Increment of vaccinated people per region (per age range) fatto
- Trend of vaccines per day (per region) fatto
- Rank regions per vaccinations for a given day Andrea
- Percentages or absolute number of people who completed the vaccination cycle fatto
- Percentages or absolute numbers of brand of vaccine per period Giovanni
- Percentage of boosted people with respect to people that completed vaccine cycle at least 5 months ago (https://www.governo.it/it/cscovid19/report-vaccini/) Andrea
- Given a specific day, rank the age ranges per vaccinations Giovanni
- Percentages of first dose / second dose / booster administrations for a given period Giovanni
- ~~Percentages about second / booster dose compared to first dose / second dose (watch out for mixed doses)~~

## additional queries
- We could integrate ISTAT data per region and get percentage of vaccinated people over total inhabitants / difference for sex
- We could integrate delivered doses and get the percentage of administred doses over delivered ones

## commands
- Modify the number of administrations for a given day and a region
- Insert an entry for a new day for a given day, age range and region

## interesting datasets
 https://github.com/pcm-dpc/COVID-19/blob/master/dati-statistici-riferimento/popolazione-istat-regione-range.csv
 https://github.com/pcm-dpc/COVID-19/blob/master/dati-andamento-nazionale/dpc-covid19-ita-andamento-nazionale.csv
 

## about the data set -**IMPORTANT**
It should be better to keep all the codes as **keywords** instead of **numbers** for the following reason:


codice_regione_ISTAT are numbers but for compatibility reasons they should be considered as keywords. In Kibana, there 
is the possibility to associate data to regions according to ISTAT code convention, by the way, the format used by kibana
  is the following "01, 02, 03, 04, ...", thus, if ISTAT codes are imported as numbers they will not be compatible with that
  convention as kibana will find the following codes "1, 2, 3, 4, ...".
  As the origina dataset does not follow the kibana convention, it has to be adapted through the script 
  `dataset_cleaner.py`