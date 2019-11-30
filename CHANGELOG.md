## Changelog

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
