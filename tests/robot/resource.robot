*** Settings ***
Documentation     A resource file with reusable keywords and variables.
...
...               The system specific keywords created here form our own
...               domain specific language. They utilize keywords provided
...               by the imported Selenium2Library.
Library           Selenium2Library

*** Variables ***
${SERVER}         localhost:5000
${BROWSER}        Firefox
${DELAY}          0
${SUPERUSER_USERNAME}   open_event_test_user@fossasia.org
${SUPERUSER_PASSWORD}   fossasia
