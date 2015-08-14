#  Open-Event Organiser Server

[![Join the chat at https://gitter.im/fossasia/open-event-orga-server](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/fossasia/open-event-orga-server?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)
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

## Demo version

[Go to demo version](http://open-event.herokuapp.com/admin/)

## Chat open event orga-server
[![Join the chat at https://gitter.im/fossasia/open-event-orga-server](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/fossasia/open-event-orga-server?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)


##License
This project is currently licensed under the GNU General Public License v3. A copy of LICENSE.md should be present along with the source code. To obtain the software under a different license, please contact FOSSASIA.
