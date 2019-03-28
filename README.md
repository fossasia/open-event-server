# Open Event Server

![Open Event Server](/docs/images/open-event-server.png)

[![GitHub release](https://img.shields.io/badge/release-1.0.0--alpha.10-blue.svg?style=flat-square)](https://github.com/fossasia/open-event-server/releases/latest)
[![Build Status](https://travis-ci.org/fossasia/open-event-server.svg?branch=development)](https://travis-ci.org/fossasia/open-event-server)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/1ac554483fac462797ffa5a8b9adf2fa?style=flat-square)](https://www.codacy.com/app/fossasia/open-event-orga-server)
[![Codecov branch](https://codecov.io/gh/fossasia/open-event-server/branch/master/graph/badge.svg?style=flat-square)](https://codecov.io/gh/fossasia/open-event-orga-server)
[![Gitter](https://img.shields.io/badge/chat-on%20gitter-ff006f.svg?style=flat-square)](https://gitter.im/fossasia/open-event-server)
[![Open Source Helpers](https://www.codetriage.com/fossasia/open-event-orga-server/badges/users.svg)](https://www.codetriage.com/fossasia/open-event-orga-server)
[![Reviewed by Hound](https://img.shields.io/badge/Reviewed_by-Hound-8E64B0.svg)](https://houndci.com)

> **The Open Event Server enables organizers to manage events from concerts to conferences and meet-ups.**

It offers features for events with several tracks and venues. Event managers can create invitation forms for speakers and build schedules in a *drag and drop* interface. The event information is stored in a **database**. The system provides **API endpoints** to **fetch** the data, and to **modify** and **update** it. Organizers can import and export event data in a standard compressed file format that includes the event data in **JSON and binary** media files like **images and audio**.

The **Open Event Server** exposes a well documented [JSON:API Spec](http://jsonapi.org/) Compliant `REST API` that can be used by external services *(like the Open Event App generators and the frontend)* to access & manipulate the data.

**API Documentation:**
- Every installation of the project includes **API docs**, (e.g. here on the test install [https://open-event-api.herokuapp.com](https://open-event-api.herokuapp.com)).
-  A hosted version of the **API docs** is available in the `gh-pages` branch of the repository at [http://dev.eventyay.com/api/v1](http://dev.eventyay.com/api/v1)

## Communication

* Please join our **[mailing list](https://groups.google.com/forum/#!forum/open-event)** to discuss questions regarding the project.
> https://groups.google.com/forum/#!forum/open-event

* Our chat channel is on **[Gitter](https://gitter.im/fossasia/open-event-server)**
> [gitter.im/fossasia/open-event-server](https://gitter.im/fossasia/open-event-server)

## Demo Version

A demo version is automatically deployed from our repositories:
* Deployment from the `master` branch - **[open-event-api.herokuapp.com](https://open-event-api.herokuapp.com/)**
* Deployment from the `development` branch - **[open-event-api-dev.herokuapp.com](https://open-event-api-dev.herokuapp.com/)**

## Installation

The Open Event Server can be easily deployed on a variety of platforms. Detailed platform-specific installation instructions have been provided below.

1. [Generic Installation Instructions](/docs/installation/basic.md)
1. [Local Installation](/docs/installation/local.md)
1. [Vagrant Installation](/docs/installation/vagrant.md)
1. [Deployment on Google Compute Engine](/docs/installation/google.md)
1. [Deployment on Google Container Engine (Kubernetes)](/docs/installation/gce-kubernetes.md)
1. [Deployment on AWS EC2](/docs/installation/aws.md)
1. [Deployment on Digital Ocean](/docs/installation/digital-ocean.md)
1. [Deployment with Docker](/docs/installation/docker.md)
1. [Deployment on Heroku](/docs/installation/heroku.md)


One-click Heroku and Docker deployments are also available:

[![Deploy to Docker Cloud](https://files.cloud.docker.com/images/deploy-to-dockercloud.svg)](https://cloud.docker.com/stack/deploy/?repo=https://github.com/fossasia/open-event-server)  [![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)


## Technology Stack

Please get familiar with the components of the project in order to be able to contribute.

### Components

* Database - [PostgreSQL](https://www.postgresql.org)
* Web framework - [Flask](http://flask.pocoo.org)
* App server - [uWSGI](https://github.com/unbit/uwsgi)
* Web Server - [NGINX](https://www.nginx.com)

Note that open-event-server **works with Python 3.6** at the moment.

### External Service Dependencies

#### OAuth Social Authentication

OAuth is used to get information from Facebook and Google accounts, that enables users to sign in with their respective credentials:
 1. Google - https://accounts.google.com/o/oauth2/auth
 2. Facebook - https://graph.facebook.com/oauth

#### Twitter

Twitter feed integration is provided in the public event pages.

Required keys can be obtained from [https://dev.twitter.com/overview/documentation](https://dev.twitter.com/overview/documentation)

#### Instagram

It is possible to extend the functionality and offer images from Instagram in the event service.

Required keys can be obtained from [https://www.instagram.com/developer/authentication/](https://www.instagram.com/developer/authentication/).

#### Google Maps

Google maps is used to get information about location (info about country, city, latitude and longitude).

Required keys can be obtained from [https://developers.google.com/maps/documentation/javascript/get-api-key](https://developers.google.com/maps/documentation/javascript/get-api-key).

#### Media Storage - Local/Amazon S3/Google Cloud

Media (like audio, avatars and logos) can be stored either Locally or on Amazon S3 or on Google Storage.

1. [Amazon S3 Setup Instructions](/docs/general/amazon-s3.md)
1. [Google Cloud Setup Instructions](https://cloud.google.com/storage/docs/migrating#defaultproj)

#### Emails - SMTP/Sendgrid

The server can send emails via SMTP or using the sendgrid API.

1. SMTP can be configured directly at `admin/settings`
2. Obtaining [Sendgrid API Token](https://sendgrid.com/docs/User_Guide/Settings/api_keys.html).

#### Heroku API

If the application is deployed on Heroku, we use the heroku API to obtain the latest release and also to display the heroku.

The required token can be obtained from [https://devcenter.heroku.com/articles/authentication](https://devcenter.heroku.com/articles/authentication).

#### Payment Gateways

For ticket sales the service integrates payment gateways:
 1. Stripe - [Obtaining Keys](https://support.stripe.com/questions/where-do-i-find-my-api-keys).
 2. Paypal - [Obtaining Credentials](https://developer.paypal.com/docs/classic/lifecycle/ug_sandbox/).

## Data Access

#### Import & Export

**Import:**

Open Event server supports multiple formats as a valid source for import.

- A **zip archive** with JSON (matching the API structure) and binary media files. Read more about this [here](/docs/general/import-export.md).
- The **Pentabarf XML** format is also supported as a valid import source. ([Sample file](https://archive.fosdem.org/2016/schedule/xml)).

**Export:**

The event data and the sessions can be exported in various formats.
- A **zip archive** with JSON (matching the API structure) and binary media files. Read more about this [here](/docs/general/import-export.md).
- The **Pentabarf XML** format. ([Sample file](https://archive.fosdem.org/2016/schedule/xml)).
- The **iCal** format. ([Sample file](https://archive.fosdem.org/2016/schedule/ical)).
- The **xCal** format. ([Sample file](https://archive.fosdem.org/2016/schedule/xcal)).


## Roles

The system has two kinds of role type.

1. System roles are related to the Open Event organization and operator of the application.
2. Event Roles are related to the users of the system with their different permissions.

Read more [here](/docs/general/roles.md).

## Development

### Development Mode

To enable development mode (development Flask config), set `APP_CONFIG` environment variable to "config.DevelopmentConfig".

```
export APP_CONFIG=config.DevelopmentConfig
```

### Model updates & migrations

When writing changes to models. Use migrations.

```
 # To generate a migration after doing a model update
 python3 manage.py db migrate

 # To sync Database
 python3 manage.py db upgrade

 # To rollback
 python3 manage.py db downgrade
```

When checking in code for models, please update migrations as well.

### API documentation

The api is documented using [api blueprint](https://apiblueprint.org/). Local changes to [the description](https://github.com/fossasia/open-event-server/blob/development/docs/api/api_blueprint.apib) can be viewed using e.g. the [apiary gem](https://help.apiary.io/tools/apiary-cli/):

```bash
gem install apiaryio # dependency
apiary preview --path docs/api/api_blueprint.apib # opens browser with generated file
```

### Testing

Clone the repo and set up the server according to the steps listed. Make sure you have installed all the dependencies required for testing by running

```
pip3 install -r requirements/tests.txt
```

#### Running unit tests

* Open Event uses Postgres database for testing. So set `DATABASE_URL` as a postgres database. Here is an example.

```sh
export DATABASE_URL=postgresql://test_user:test@127.0.0.1:5432/opev_test
# format is postgresql://USERNAME:PASSWORD@ADDRESS/DATABASE_NAME
export APP_CONFIG=config.TestingConfig
```

* Then go to the project directory and run the following command:
```
python3 -m unittest discover tests/all/
```
* It will run each test one by one.

* You can also use the following command to run tests using nosetests:
```
nosetests tests/all/
```

#### Running robot framework tests
* Make sure you have FireFox installed
* Start your local flask server instance.
* Go to the project directory and Run the tests by using the following command.

```
robot -v SERVER:{server_name} -v SUPERUSER_USERNAME:{super_user_email_here} -v SUPERUSER_PASSWORD:{super_user_password} tests/robot
```

Change all the parameters inside `{}` as per your local server. The final command would look like:
```
robot -v SERVER:localhost:5000 -v SUPERUSER_USERNAME:test@opev.net -v SUPERUSER_PASSWORD:test_password tests/robot
```
* Once the tests are completed, a report and a log would be generated at `report.html` and `log.html` respectively in your root directory.

## Logging

Certain information is being logged and stored in the database for future reference, resolving conflicts in case of hacks and for maintaining an overview of the system. Read more about [logging here](/docs/general/logs.md).

## Internationalization (i18n)

[![Translation status](https://hosted.weblate.org/widgets/open-event/-/multi-blue.svg)](https://hosted.weblate.org/engage/open-event)

Open Event is being translated using Weblate, a web tool designed to ease translating for both developers and translators.

If you would like to contribute to the translation of Open Event, you need to [register on this server](https://hosted.weblate.org/accounts/register/).

Once you have activated your account just proceed to the [translation section](https://hosted.weblate.org/projects/open-event/).


## Contributions, Bug Reports, Feature Requests

This is an Open Source project and we would be happy to see contributors who report bugs and file feature requests submitting pull requests as well. Please report issues here https://github.com/fossasia/open-event-server/issues. It is also recommended to go through the [developer handbook](https://github.com/fossasia/open-event/tree/master/docs/dev-handbook) in order to get a basic understanding of the ecosystem.

## Branch Policy

We have the following branches :
 * **development**
	 All development goes on in this branch. If you're making a contribution, please make a pull request to _development_.
	 All PRs must pass a build check and a unit-test check on Travis (https://open-event-api.herokuapp.com - Is running off the development branch. It is hosted on Heroku.)
	 (https://api.eventyay.com - Is running off the `development` branch. Hosted on Google Cloud Platform (Google Container Engine + Kubernetes).)
 * **master**
   This contains shipped code. After significant features/bug-fixes are accumulated on development, we make a version update and make a release. (https://eventyay.com - Is running off the master branch. (whichever is the latest release.) Hosted on Google Cloud Platform (Google Container Engine + Kubernetes).)
 * **gh-pages**
   This contains the documentation website on http://dev.eventyay.com. The site is built automatically on each commit in the development branch through a script and using travis. It includes the md files of the Readme and /docs folder. It also includes javadocs.

## Release Policy

The tentative release policy, for now (since there is a lot of activity and a lot of bugs), is an alpha release every Monday and Friday (since we see more activity on weekends). So, any bug-fixes will not be reflected at eventyay.com until a new release is made in the master branch.

## Contributions Best Practices

**Commits**
* Write clear meaningful git commit messages (Do read http://chris.beams.io/posts/git-commit/)
* Make sure your PR's description contains GitHub's special keyword references that automatically close the related issue when the PR is merged. (More info at https://github.com/blog/1506-closing-issues-via-pull-requests )
* When you make very minor changes to a PR of yours (like for example fixing a failing travis build or some small style corrections or minor changes requested by reviewers) make sure you squash your commits afterward so that you don't have an absurd number of commits for a very small fix. (Learn how to squash at https://davidwalsh.name/squash-commits-git )
* When you're submitting a PR for a UI-related issue, it would be really awesome if you add a screenshot of your change or a link to a deployment where it can be tested out along with your PR. It makes it very easy for the reviewers and you'll also get reviews quicker.

**Feature Requests and Bug Reports**
* When you file a feature request or when you are submitting a bug report to the [issue tracker](https://github.com/fossasia/open-event-server/issues), make sure you add steps to reproduce it. Especially if that bug is some weird/rare one.

**Join the development**
* Before you join development, please set up the system on your local machine and go through the application completely. Press on any link/button you can find and see where it leads to. Explore. (Don't worry ... Nothing will happen to the app or to you due to the exploring :wink: Only thing that will happen is, you'll be more familiar with what is where and might even get some cool ideas on how to improve various aspects of the app.)
* Test the application on your machine and explore the admin area. The test deployment on Heroku will not give you access to the admin section, where you can switch on/off modules, e.g. ticketing and add keys for services, e.g. storage on S3.
* If you would like to work on an issue, drop in a comment at the issue. If it is already assigned to someone, but there is no sign of any work being done, please free to drop in a comment so that the issue can be assigned to you if the previous assignee has dropped it entirely.

## License

This project is currently licensed under the **[GNU General Public License v3](LICENSE.md)**.

> To obtain the software under a different license, please contact [FOSSASIA](http://blog.fossasia.org/contact/).
