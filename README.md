# open-event-server
The Open Event Server enables organizers to manage events from concerts to conferences and meet-ups.

## Intro

This branch is a `v3` rewrite of the backend REST API and a work in progress.
This new version of the API uses [Python]([https://www.python.org),
[Django 5](https://docs.djangoproject.com/en/dev/releases/5.0/), and the [Django REST Framework](https://www.django-rest-framework.org).
Currently, data is stored in SQLite although this might change in the future.

If you want to collaborate feel free to have a look at our
[first issues](https://github.com/fossasia/open-event-server/issues?q=is%3Aissue+is%3Aopen+label%3Aopen-for-all+label%3Av3+).

## Quickstart

We're going to install and configure the latest development build of this API.

### Clone the project

First of all, you need to clone the project on your computer with :

```
git clone https://github.com/fossasia/open-event-server.git
```

You can now move to the newly created folder:

```
cd open_event_server
```

### Check out the development branch

```
git checkout dev-v3
```

### Create a virtual environment

[Virtualenv](https://virtualenv.pypa.io/) provides an isolated Python environment, which is more practical than installing packages system-wide. They also allow packages to be installed without administrator privileges.

1. Create a new virtual environment
```
virtualenv env
```

2. Activate the virtual environment
```
. env/bin/activate
```

You need to ensure the virtual environment is active each time you want to launch the project.

A similar setup can be achieved using pyenv and pyenv/virtualenv.

### Install all requirements

Requirements of the project are stored in the `requirements.txt` file.
You can install them with:

**WARNING**: Make sure your virtual environment is active or you will install the packages system-wide.
```
pip install -r requirements.txt
```
### Configure the database

Django has a versioning system to generate the database called
[migrations](https://docs.djangoproject.com/en/4.2/topics/migrations/).
You first need to apply all existing "migrations" to update your local database.

```
python manage.py migrate
```

**Note:** The project uses a sqlite3 file as a database in development mode,
to simplify development. In production, the environment variable `DATABASE_URL`
can be set to any supported format, eg., a Postgres database.

### Launch the API

You can now launch an instance of the API and visit the built-in admin website.
To log into the admin page, you'll need to create a superuser first:

```
python manage.py createsuperuser
```
Launch a local API instance with:
```
python manage.py runserver
```

You can now visit these links to validate the installation:

- The root of the API: [http://localhost:8000/](http://localhost:8000/),
- Login for users: [http://localhost:8000/api-auth/login/](http://localhost:8000/api-auth/login/),
- The admin site: [http://localhost:8000/admin/](http://localhost:8000/admin),
- The autogenerated documentation: [http://localhost:8000/v2/schema/swagger-ui/](http://localhost:8000/v2/schema/swagger-ui/)

