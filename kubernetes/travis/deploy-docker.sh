#!/usr/bin/env bash

export DEPLOY_BRANCH=${DEPLOY_BRANCH:-master}

if [ "$TRAVIS_PULL_REQUEST" != "false" -o "$TRAVIS_REPO_SLUG" != "fossasia/open-event-server" -o  "$TRAVIS_BRANCH" != "$DEPLOY_BRANCH" ]; then
    echo "Skip production deployment for a very good reason."
    exit 0
fi

export REPOSITORY="https://github.com/${TRAVIS_REPO_SLUG}.git"

cd kubernetes/images/web
docker build --build-arg COMMIT_HASH=$TRAVIS_COMMIT --build-arg BRANCH=$DEPLOY_BRANCH --build-arg REPOSITORY=$REPOSITORY --no-cache -t eventyay/api-server:$TRAVIS_COMMIT .
docker login -u="$DOCKER_USERNAME" -p="$DOCKER_PASSWORD"
docker tag eventyay/api-server:$TRAVIS_COMMIT eventyay/api-server:latest
docker push eventyay/api-server
