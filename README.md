#  Open-Event Organiser Server
This server which will manage all the data of the event. Backed by a database, it provides API endpoints to fetch the data, and also to modify/update it.

The database can be a sqlite db file or saved in json itself.  

The schema for the database is provided [here](https://github.com/fossasia/open-event/blob/master/DATABASE.md)

The data is provided over the API endpoints as described [here](https://github.com/fossasia/open-event/blob/master/API.md)

# Getting Started

Type ```vagrant up``` to start a new virtual machine running the server. This requires having Vagrant installed.

## Proposed Stack

* Database - Postgres
* Webserver - Nginx
* App server - uwsgi
* Web framework - flask (particularly flask-admin)


