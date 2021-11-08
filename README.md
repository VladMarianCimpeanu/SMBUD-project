# SMBUD project

## Neo4J assignment
### Specification
Goal of this project is to design a graph database in Neo4J in order to assist tracking applications and Covid19 spread visualization.
The database must register all the necessary information about the users including vaccines and Covid swabs. The application using this database will be able to exploit all the data coming from tracking applications and from all the facilities.

### Hypothesis
The assumptions taken into account are the following:
- People belonging to the same family live in the same house if not explicitly specified. Using the concept of "house" instead of "family", it is offered the possibility to differentiate domicile from residence.
- All the personal data are verified by an authoritative figure, for instance the governament.
- The domicile declaration is assumed to be truthful.
- All the data coming from public spaces are always considered true and complete.
- People always provide all the necessary information to the staff when they visit a certain public space.

Below the ER diagram is shown. ![ER diagram](https://github.com/VladMarianCimpeanu/SMBUD-project/blob/main/deliverables/Graph_diagram.png)
Below the graph diagram is shown. ![graph diagram](https://github.com/VladMarianCimpeanu/SMBUD-project/blob/main/deliverables/Graph_diagram.png)
### Conclusions
