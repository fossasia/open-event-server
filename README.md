#  Open-Event Server

[![Build Status](https://travis-ci.org/fossasia/open-event-orga-server.svg?branch=master)](https://travis-ci.org/fossasia/open-event-orga-server)
[![Dependency Status](https://gemnasium.com/badges/github.com/fossasia/open-event-orga-server.svg)](https://gemnasium.com/github.com/fossasia/open-event-orga-server)
[![Codacy Badge](https://api.codacy.com/project/badge/grade/645630f8334b40dd93ba804956908a42)](https://www.codacy.com/app/triplez/open-event-orga-server)
[![Issue Count](https://codeclimate.com/github/fossasia/open-event-orga-server/badges/issue_count.svg)](https://codeclimate.com/github/fossasia/open-event-orga-server)
[![Test Coverage](https://codeclimate.com/github/fossasia/open-event-orga-server/badges/coverage.svg)](https://codeclimate.com/github/fossasia/open-event-orga-server/coverage)
[![Coverage Status](https://coveralls.io/repos/github/fossasia/open-event-orga-server/badge.svg?branch=master)](https://coveralls.io/github/fossasia/open-event-orga-server?branch=master)
[![codecov](https://codecov.io/gh/fossasia/open-event-orga-server/branch/master/graph/badge.svg)](https://codecov.io/gh/fossasia/open-event-orga-server)
[![Gitter](https://badges.gitter.im/fossasia/open-event-orga-server.svg)](https://gitter.im/fossasia/open-event-orga-server?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge)

This server which will manage all the data of the event. Backed by a database,
it provides API endpoints to fetch the data, and also to modify/update it.

The database can be a sqlite db file or saved in json itself.

The schema for the database is provided [here](https://github.com/fossasia/open-event/blob/master/DATABASE.md)

The data is provided over the API endpoints as described [here](https://github.com/fossasia/open-event/blob/master/API.md)

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

# Communication
Please join our mailing list to discuss questions regarding the project: https://groups.google.com/forum/#!forum/open-event

# Getting Started

## How do I install Open-Event Server with Docker?:
To install Open-Event Server with Docker please refer to [Docker installation](docs/DOCKER.md)


## How do I install Open-Event Server with Vagrant?:
For installation steps on how to deploy Open-Event Server using vagrant please refer to [Vagrant installation](docs/VAGRANT.md)


## How to configure Bower? :
In order to install and configure bower please refer to [Bower installation](docs/BOWER.md)


### Development Mode

To enable development mode (development Flask config), set `APP_CONFIG` environment variable to "config.DevelopmentConfig".

```
export APP_CONFIG=config.DevelopmentConfig
```

## Model updates

When writing changes to models. Use migrations.

 ```
 # To generate a migration after doing a model update
 python manage.py db migrate

 # To sync Database
 python manage.py db upgrade

 # To rollback
 python manage.py db downgrade

 ```

When checking in code for models, please update migrations as well.


##How to run tests for Open-Event Server?:
For steps regarding how to run tests please refer to [How to run tests](docs/TESTS.md)

## Stack

* Database - Postgres
* Webserver - Nginx
* App server - uwsgi
* Web framework - flask (particularly flask-admin)

## How do I deploy Open-Event Server to Heroku?:
For steps regarding how to deploy your version of the Open-Event Server to Heroku, please refer [Heroku deployment](docs/HEROKU.md)

## Demo version

[Go to demo version](http://open-event.herokuapp.com/admin/)

## License

This project is currently licensed under the GNU General Public License v3. A
copy of LICENSE.md should be present along with the source code. To obtain the
software under a different license, please contact FOSSASIA.

[1]: https://www.virtualbox.org/wiki/Downloads
[2]: http://www.vagrantup.com/downloads.html
[3]: https://blog.engineyard.com/2014/building-a-vagrant-box
[4]: https://docs.vagrantup.com/v2/getting-started
