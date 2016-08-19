*** Settings ***
Documentation     A test suite with a single test for valid login.
...
...               This test has a workflow that is created using keywords in
...               the imported resource file.
Resource          resource.robot

*** Variables ***
${LOGIN URL}      http://${SERVER}/login
${WELCOME URL}     http://${SERVER}/
*** Keywords ***
Open Browser To Login Page
    Open Browser    ${LOGIN URL}    ${BROWSER}
    Maximize Browser Window
    Set Selenium Speed    ${DELAY}
    Login Page Should Be Open

Login Page Should Be Open
    Title Should Be    Login - Open Event

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

*** Test Cases ***
Valid Login
    Open Browser To Login Page
    Input Username    ${SUPERUSER_USERNAME}
    Input Password    ${SUPERUSER_PASSWORD}
    Submit Credentials
    Welcome Page Should Be Open
    [Teardown]    Close Browser
