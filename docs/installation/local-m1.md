# Local development on Mac M1

## Quickstart

### 0. Install homebrew and docker

```bash
# install homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# check version
❯ brew -v
Homebrew 4.0.17

# install docker
brew install --cask docker

# check version
❯ docker -v
Docker version 20.10.21, build baeda1f

❯ docker-compose version
Docker Compose version v2.13.0

# run postgres and redis
docker-compose -f docker-compose.dev.yml up -d
# redis host: redis://localhost:6379
# postgres host: postgres://localhost:5432
```

### 1. Install pyenv

```bash
# install
brew install pyenv

# check version
❯ pyenv -v
pyenv 2.3.17
```

### 2. Install python 3.8.16

```bash
# install
pyenv install 3.8.16

# activate
pyenv global 3.8.16 # or pyenv shell 3.8.16 (for current shell only)
```

### 3. Install poetry

```bash
# install
brew install poetry

# check version
❯ poetry -V
Poetry (version 1.4.2)
```

### 4. Install dependencies

```bash
# init virtualenv 3.8.16
poetry env use 3.8.16

# active virtualenv
poetry shell

# install
poetry install
```

### 5. Setup environment variables

```bash
# create .env file
cp .env.example .env

# edit .env file

# postgres
DATABASE_URL=postgresql://open_event_user:opev_pass@127.0.0.1:5432/oevent

# secret key
SECRET_KEY=741a6f7389de40a91b930869b5e32baaae6953170b6fc1b9856001598a5ef0b8 # random generate using secrets

# redis
REDIS_URL=redis://localhost:6379/0

# default super admin
SUPER_ADMIN_EMAIL=open_event_test_user@fossasia.org
SUPER_ADMIN_PASSWORD=fossasia
```

### 6. Run migrations

```bash
# run migrations
poetry run python manage.py prepare_db
```

### 7. Run the app

```bash
# run server
poetry run python manage.py runserver

# go to http://127.0.0.1:5000/

# run celery on another terminal
poetry run celery -A app.instance.celery worker -B -l INFO -c 2
```

### 8. Run tests

```bash
# connect to postgres via client
create database oevent_test;

# run tests
poetry run pytest

==================================== 393 passed, 1 skipped, 586 warnings in 182.93s (0:03:02) ====================================
```

## Additional steps

```
# install redis client
# https://redis.com/redis-enterprise/redis-insight/
brew install --cask redisinsight

# install postgres client
# https://www.beekeeperstudio.io/
brew install --cask beekeeper-studio
```

## Troubleshooting

1. If you get error related to `openssl`, `cmake`, `fontconfig` while installing dependencies, try this:

```bash
brew install openssl re2 cmake

LDFLAGS="-L$(/opt/homebrew/bin/brew --prefix openssl)/lib -L$(/opt/homebrew/bin/brew --prefix re2)/lib" CPPFLAGS="-I$(/opt/homebrew/bin/brew --prefix openssl)/include -I$(/opt/homebrew/bin/brew --prefix re2)/include" GRPC_BUILD_WITH_BORING_SSL_ASM="" GRPC_PYTHON_BUILD_SYSTEM_RE2=true GRPC_PYTHON_BUILD_SYSTEM_OPENSSL=true GRPC_PYTHON_BUILD_SYSTEM_ZLIB=true poetry install 

brew install fontconfig

sudo cp $(brew --prefix fontconfig)/lib/libfontconfig.* /usr/local/lib

```
