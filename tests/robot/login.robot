*** Settings ***
Documentation     A test suite with a single test for valid login.
...
...               This test has a workflow that is created using keywords in
...               the imported resource file.
Resource          resource.robot

*** Test Cases ***
Valid Login
    Login to Open Event
    [Teardown]    Close Browser

Invalid Login nonexistent user
    Open Browser To Login Page
    Input Username    some_random_email_id@fossasia.org
    Input Password    some_random_password
    Submit Credentials
    Page Should Contain     User doesn't exist
    [Teardown]    Close Browser

Invalid Login wrong password
    Open Browser To Login Page
    Input Username    ${SUPERUSER_USERNAME}
    Input Password    some_random_password
    Submit Credentials
    Page Should Contain     Incorrect Password
    [Teardown]    Close Browser
