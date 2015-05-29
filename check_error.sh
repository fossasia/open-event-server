#!/bin/bash
pylint open_event
pep8 open_event

nosetests --with-coverage --cover-erase --cover-package=open_event --cover-html