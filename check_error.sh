#!/bin/bash
pylint open_event
pep8 open_event
#path = pwd
export PYTHONPATH=${PYTHONPATH}:/home/user/.../open-event-orga-server
find . -name "*.pyc" -exec rm -rf {} \;
nosetests --with-coverage --cover-erase --cover-package=open_event --cover-html