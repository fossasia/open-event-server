-- Open Event database
CREATE USER john WITH PASSWORD 'start';
CREATE DATABASE oevent_2 WITH OWNER john;

-- Test database
CREATE USER open_event_user WITH PASSWORD 'test';
CREATE DATABASE opev_test WITH OWNER open_event_user;
