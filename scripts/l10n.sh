#!/bin/sh

if [ $1 = "extract" ]
then
    pybabel extract -F babel.cfg -k _l -o app/translations/messages.pot .
fi

if [ $1 = "update" ]
then
    pybabel update -i app/translations/messages.pot -d app/translations
fi

if [ $1 = "generate" ]
then
    pybabel compile -d app/translations
fi
