# SMBUD data project
## Introduction
This is the repository of **Systems and methods for big and unstructured data** project held at Politecnico
di Milano in 2021. The aim of the project is to design and implement NoSQL databases for different scenarios.

## Table of contents
* [Grading](https://github.com/VladMarianCimpeanu/SMBUD-project#grading)
* [Neo4J assignment](https://github.com/VladMarianCimpeanu/SMBUD-project#first-assignment---neo4j)
* [MongoDB assignment](https://github.com/VladMarianCimpeanu/SMBUD-project#second-assignment---mongodb)
* [ElasticSearch assignment](https://github.com/VladMarianCimpeanu/SMBUD-project#third-assignment---elasticsearch-&-kibana)
* [Repository structure](https://github.com/VladMarianCimpeanu/SMBUD-project#repository-structure)

## Grading
| Assignment | Grade | Optional part | Total | 
|------|---------|--------|--------|
| Neo4J | 9/10 | :heavy_check_mark: | 10|
| MongoDB | 9.5/10 | :heavy_check_mark: | 10.5 |
| ElasticSearch | 10/10 | :heavy_check_mark: | 11 |

Final score: 31.5/33
## First assignment - Neo4J
Design, store and query graph data structures in a NoSQL DB for supporting a contact tracing application for
COVID-19.

Tasks to perform:
- Design conceptual model 
- Store a sample dataset in Neo4J
- Write basic Queries (minimum 5) and Commands (minimum 3) useful for typical usage scenarios
- Implementation of some application / UI that exploits the Neo4J database.
## Second assignment - MongoDB
Design, store and query data on a NoSQL DB supporting a certification app for COVID-19.
The data storage solution must keep track of people and information about their tests and vaccination status.
In particular, it is required to record in a document-based storage the certificate of vaccination /testing and the
authorized bodies that can deliver them.
Data stored in the deisigned database will be used for checking the validity of the certificate (concerning expiration dates, evolution
of the rules, and so on)

Tasks to perform:
- Design conceptual model
- Store a sample dataset in MongoDB (some hundred nodes at least)
- Write basic Queries (minimum 5) and Commands (minimum 3) useful for typical usage scenarios
- Implementation of some application / UI that interacts with the MongoDB database.


## Third assignment - ElasticSearch & Kibana
Design, store and query data on a NoSQL DB supporting a data analysis scenario over data about
COVID-19 vaccination statistics. The purpose is that of building a comprehensive database of vaccinations.
Data analysis is performed over the dataset that can be found at:
https://raw.githubusercontent.com/italia/covid19-opendata-vaccini/master/dati/somministrazioni-vaccini-latest.csv

Tasks to perform:
- Report the schema of the data, including the types of the different fields. Make sure that the format/schema
is correct and motivate it (even if you use the automatic mapping)
- Store the dataset in ElasticSearch
- Write basic Queries (minimum 8) and data update commands (minimum 2) useful for typical usage
scenarios
- Implement a simple visualization dashboard using Kibana. Exploration, navigation and dynamicity of the
dashboard will be considered a valuable contribution too
- Integrate other datasets

## Repository structure
- **[random_italian_things](https://github.com/VladMarianCimpeanu/SMBUD-project/tree/main/random_italian_things)**: this package is responsible for the random generation of the database's entities such as people, houses (group of people living together) and amenities such as restaurants, pubs and so on. This package is used in the Neo4J and MongoDB assignment.
- **[neo4J assignment](https://github.com/VladMarianCimpeanu/SMBUD-project/tree/main/neo4J_assignment)** content is divided in:
  - [neo4JDB-populator](https://github.com/VladMarianCimpeanu/SMBUD-project/tree/main/neo4j_assignment/neo4jDB-populator): package responsible for the automatic population of the graph database. The main.py file exploits the classes belonging to random_italian_things package.
  - [GUI](https://github.com/VladMarianCimpeanu/SMBUD-project/tree/main/neo4j_assignment/GUI): package containing all the necessary classes to run the python application supported by the Neo4j DB
  - [deliverables](https://github.com/VladMarianCimpeanu/SMBUD-project/tree/main/neo4j_assignment/deliverables) contains the [pdf report file](https://github.com/VladMarianCimpeanu/SMBUD-project/blob/main/neo4j_assignment/deliverables/Project_1_Team_3.pdf) and the [example queries](https://github.com/VladMarianCimpeanu/SMBUD-project/blob/main/neo4j_assignment/deliverables/queries_dump_example.cypher)
- **[MongoDB_assignment](https://github.com/VladMarianCimpeanu/SMBUD-project/tree/main/MongoDB_assignment)** content is divided in:
  - [data](https://github.com/VladMarianCimpeanu/SMBUD-project/tree/main/MongoDB_assignment/data) contains [main.py](https://github.com/VladMarianCimpeanu/SMBUD-project/blob/main/MongoDB_assignment/data/main.py) used to populate the document oriented DB, [webapp](https://github.com/VladMarianCimpeanu/SMBUD-project/tree/main/MongoDB_assignment/data/webapp) package containing all the necessary files to run the webapp application supported by the MongoDB database, finally, [queries and commands.txt](https://github.com/VladMarianCimpeanu/SMBUD-project/blob/main/MongoDB_assignment/data/queries%20and%20commands.txt) is a list of example MongoDB queries.
  - [Report] contains latex and png files to compile the [pdf report](https://github.com/VladMarianCimpeanu/SMBUD-project/blob/main/MongoDB_assignment/Report/Project_2_Team_3.pdf)
- **[ElasticSearch_assignment](https://github.com/VladMarianCimpeanu/SMBUD-project/tree/main/ElasticSearch_assignment)** contains:
  - [kibana dashboard](https://github.com/VladMarianCimpeanu/SMBUD-project/blob/main/ElasticSearch_assignment/dashboard.ndjson) file that can be imported in Kibana. See more details in the [report](https://github.com/VladMarianCimpeanu/SMBUD-project/blob/main/ElasticSearch_assignment/Report/Project_3_Team_3.pdf)
  - [queries.txt](https://github.com/VladMarianCimpeanu/SMBUD-project/blob/main/ElasticSearch_assignment/queries.txt) is an example set of queries for the ElasticSearch DB
  - dataset_cleaner.py and merge dataset.ipynb are used to fix some format code in the csv file.
