# Auto deployment

This directory contains a Python auto deployment script that polls the github
projects of Open Event and updates docker-compose containers

# WARNING

Edit `.env` before deployment - the admin credentials are stored there

## Config format

Edit `config.yml` for adding new projects

Example config:
```yml
server:
    url: https://github.com/fossasia/open-event-server
    branch: development
    container: web
    upgrade: bash scripts/upgrade.sh
    init: bash scripts/init.sh
frontend:
    url: https://github.com/fossasia/open-event-frontend
    branch: development
```

As you can see, the `yaml` file contains the project name, github url, branch
and upgrade commands for migrations or database creation. Every projects needs a
`docker-compose.yml` file in the root directory for this to work.

## Running the process

After `docker` and `docker-compose` are installed on your system, execute

```bash
python3 autodeploy/main.py --workdir WORKDIR --config CONFIG
```
where `WORKDIR` and `CONFIG` are the location of your project and the config.yml file respectively.

and see the log output for results.
