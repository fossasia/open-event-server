-- Open Event database
CREATE USER open_event_user WITH PASSWORD 'opev_pass';
CREATE DATABASE open_event WITH OWNER open_event_user;

-- Test database
CREATE DATABASE opev_test WITH OWNER open_event_user;
