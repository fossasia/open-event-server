## Changelog

##### v1.8.0 (Unreleased):

- No Changes

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
