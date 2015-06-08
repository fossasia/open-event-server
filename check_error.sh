#!/bin/bash
pylint open_event
pep8 open_event
#export PYTHONPATH=${PYTHONPATH}:/home/user/.../open-event-orga-server
nosetests --with-coverage --cover-erase --cover-package=open_event --cover-html