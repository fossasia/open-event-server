#!/bin/sh
pycln --config pyproject.toml .
isort .
black .
