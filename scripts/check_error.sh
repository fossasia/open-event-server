#!/bin/bash
pylint app
pep8 app
#path = pwd
export PYTHONPATH=${PYTHONPATH}:/home/user/.../open-event-server
find . -name "*.pyc" -exec rm -rf {} \;
nosetests --with-coverage --cover-erase --cover-package=app --cover-html
