# Install essential packages from Apt
apt-get update -y
# Python dev packages
apt-get install -y build-essential python python-dev python-setuptools python-pip
apt-get install -y libxml2-dev libxslt1-dev
apt-get install -y nginx uwsgi uwsgi-plugin-python
apt-get install -y postgresql postgresql-contrib libpq-dev

#Flask
pip install flask
pip install flask-admin
pip install flask-sqlalchemy
pip install Flask-WTF
pip install flask-migrate
