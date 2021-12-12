# GUIDELINES

## Requirements
The user must check to have correctly installed, in the virtual environment,
the following packages: 
- Flask
- Flask-PyMongo 
- PyMongo 
- pandas 
- numpy  
- python-codicefiscale
- dnspython
## Notes
Both the db generator and the WebApp use by default the connection string
contained in the following file:
`/data/webapp/connection_string.txt`.

## Generator guidelines
In order to run the generator type the following command in the `data` directory:

`python main.py –uri URI` 

where `URI` is the connection string to use to connect to a specific
db. If the URI is not specified, the generator the default connection string.

## WebAPP guidelines
There are two possible ways to run the demo: the first one is to connect to
the following link https://c19-cert-viewer.herokuapp.com/, that works only on
the default database.
In alternative, it is possible to run in the `/data/webapp/` directory the following command:

`python app.py -uri URI` 

where `URI` is the connection string to use to connect to a specific
db. If the URI is not specified, the server will connect with the default connection string
to default DB.
Then connect to `localhost:port` where `port` is the port number suggested by the
console.
