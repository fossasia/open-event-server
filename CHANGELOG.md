## Changelog

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
