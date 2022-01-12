# SMBUD data project
## Introduction
This is the repository of **Systems and methods for big and unstructured data** project held at Politecnico
di Milano in 2021. The aim of the project is to design and implement NoSQL databases for different scenarios.
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
