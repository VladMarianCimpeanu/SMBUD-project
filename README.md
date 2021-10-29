# SMBUD project

## Neo4J assignement
### Specification
Goal of this project is to design a graph database in Neo4J in order to assist tracking applications and Covid19 spread visualization.
The database must register all the necessary information about the users including vaccines and Covid swabs. The application using this database will be able to exploit all the data coming from tracking applications and from all the facilities.

### Hipothesis
The assumptions taken into account are the following:
- People belonging to the same family lives in the same home if not explicitly specified. Using the concept of "home" instead of "family", it is offered the possibility to differentiate domicile from residence.
- All the personal data are verified by an authoritative figure, for instance the governament.
- The domicile declaration is assumed to be truthful.
- All the data coming from public spaces are always considered true and complete.
- People always provide all the necessary information to the staff when they visit a certain public space.

Below the ER diagram is shown. ![ER diagram](https://github.com/VladMarianCimpeanu/SMBUD-project/blob/main/er.png)

### Conclusions