# Install essential packages from Apt
apt-get update -y
# Python dev packages
apt-get install -y build-essential python python-dev python-setuptools python-pip

#Flask
pip install flask
pip install flask-admin
pip install flask-sqlalchemy
pip install Flask-WTF