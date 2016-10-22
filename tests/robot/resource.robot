*** Settings ***
Documentation     A resource file with reusable keywords and variables.
...
...               The system specific keywords created here form our own
...               domain specific language. They utilize keywords provided
...               by the imported Selenium2Library.
Library           Selenium2Library      run_on_failure=Nothing

*** Variables ***
${SERVER}         localhost:5000
${BROWSER}        phantomjs
${DELAY}          0
${SUPERUSER_USERNAME}   open_event_test_user@fossasia.org
${SUPERUSER_PASSWORD}   fossasia
${LOGIN URL}      http://${SERVER}/login/
${WELCOME URL}     http://${SERVER}/

*** Keywords ***
Login Page Should Be Open
    Title Should Be    Login - Open Event

Open Browser To Login Page
    Open Browser    ${LOGIN URL}    ${BROWSER}
    Maximize Browser Window
    Set Selenium Speed    ${DELAY}
    Login Page Should Be Open

Go To Login Page
    Go To    ${LOGIN URL}
    Login Page Should Be Open

Input Username
    [Arguments]    ${username}
    Input Text    email    ${username}

Input Password
    [Arguments]    ${password}
    Input Text    password    ${password}

Submit Credentials
    Click Button    Log in

Welcome Page Should Be Open
    Location Should Be    ${WELCOME URL}
    Title Should Be    Home - Open Event

Login to Open Event
    Open Browser To Login Page
    Input Username    ${SUPERUSER_USERNAME}
    Input Password    ${SUPERUSER_PASSWORD}
    Submit Credentials
    Welcome Page Should Be Open

