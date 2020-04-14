## Changelog

#### v1.15.0 (2020-04-15):

**BREAKING CHANGE**
We are making two-fold change in the underlying DB, we are upgrading from postgres 10 to 12, which was a long time due. And also, we are going to use postgis in future for nearby event fetching, hence we are doing this now in order to avoid changing DB layer later again in future.

These are the steps you need to take before upgrading to this release:
1. Backup the current database  
`docker exec -it opev-postgres pg_dump -U open_event_user -d open_event > bak.sql`  
Note that if you changed the user and DB name using enironment variables, you have to use those values here  
2. Shutdown the server  
`docker-compose down`
3. Remove the DB volume  
`docker volume rm server_pg`
4. Now pull the latest changes to your local docker-compose file changing the postgres image to `postgis/postis:12-2.5-alpine`. You don't have to do this change manually if you are using the tracked version of docker-compose.yml from our git repository
5. Start just the postgres server  
`docker-compose up -d postgres`
6. Restore the backup on DB  
`docker-compose exec -T postgres psql -U open_event_user -d open_event < bak.sql`
7. Start the servers up  
`docker-compose up -d`

- GraphQL alpha trial
- Allow old dates in session PATCH requests
- Add postgis DB for future use
- Integrate Sentry APM tracing support
- Bug fixes and dependency updates

#### v1.14.0 (2020-03-08):

- Fix discount code quantity calculation
- Dependency updates

#### v1.13.1 (2020-03-05):

- Fix ticket sold count query

#### v1.13.1 (2020-02-20):

- Fix keyerror due to my_tickets_url resulting in failure of order patch.

#### v1.13.0 (2020-02-20):

- Fix cron job timings preventing multiple emails to attendees
- Change email links to be more accessible
- Fix invoice email generation errors
- Add proper etag support by changing to weak etags

#### v1.12.0 (2020-02-02):

- Add check if donation ticket has payment method enabled
- Fix general event statistics type
- Internal refactoring and code cleanup

#### v1.11.2 (2020-01-25):

- Fix celery task status endpoint

#### v1.11.1 (2020-01-23):

- Fix event fee notification task being triggered every minute

#### v1.11.0 (2020-01-23):

- **BREAKING:** Fix security issues related to secret key. You **MUST** add the current secret key set in DB as `SECRET_KEY` environment variable before upgrading. After upgrading, the column will be removed from DB 
- Fix count query of tickets used to reserve tickets
- Support event statistics in include query
- Restrict deletion of orders except by admin
- Fix missing fields and incorrect column value in session csv export
- Addition of field for Promoted Events, Instagram Speaker URL, Age Groups for Attendee
- Replaced jobs running with APS to celery-beat
- Fix sessions can be edited after CFS has ended
- Removed elasticsearch initialisation and redundant APIs
- Change country field type to select in forms
- Other minor fixes

##### v1.10.0 (2019-12-22):

- Fix event and speaker image resizing, and add management command to resize event and speaker images which remained to be resized.  
Run `python manage.py fix_event_and_speaker_images` to resize images which weren't resized due to the bug
- Optimize link generation of relationships with up to 10X speedup
- Add scheduled job to automatically remove orphan ticket holders with no order ID
- Add created and modified times in ticket holder
- Allow new tickets to have same name as deleted tickets
- Fix PayTM payment gateway

##### v1.9.0 (2019-11-28):

- Fix billing info requirements from attendees
- Fix stripe connection issue in event wizard
- Check proper access permissions for event exporting API


##### v1.8.0 (2019-11-24):

- Run `python manage.py fix_digit_identifier` to correct all digit identifiers
- Handelled invalid price value in paid tickets
- Check if event identifier does not contain of all digits
- Fix check for `is_email_overridden` for speaker form
- Improve test timings

##### v1.7.0 (2019-10-19):

- ** BREAKING ** Requires Python 3.7
- Add info endpoint to get server version
- Add management script to switch modules on or off
- Increase gunicorn workers in docker and add options for configuration
- Fix CSV export *(included as hotfix in previous version)*
- Fix order PDF not found errors by mounting `generated` folder in docker
- Fix ICal attribute errors and add tests
- Fix Pentabarf export and add tests
- Add workaround for multiprocess engine forking
- Use pool pre ping option to avoid dropped connections
- Add .env in docker compose to override environment variables
- Configure redis and celery in sentry integration
- Convert some classes to dataclasses
- Update dependencies
