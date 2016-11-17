#!/usr/bin/env bash

if [ "$TRAVIS_PULL_REQUEST" != "false" -o "$TRAVIS_REPO_SLUG" != "fossasia/open-event-orga-server" ]; then
    echo "Just a PR. Skip google cloud deployment."
    exit 0
fi

cd kubernetes/image
docker build --build-arg COMMIT_HASH=$TRAVIS_COMMIT --no-cache -t gcr.io/eventyay/web:$TRAVIS_COMMIT .
docker tag gcr.io/eventyay/web:$TRAVIS_COMMIT gcr.io/eventyay/web:latest
gcloud docker -- push gcr.io/eventyay/web
kubectl set image deployment/web web=gcr.io/eventyay/web:$TRAVIS_COMMIT
kubectl set image deployment/celery celery=gcr.io/eventyay/web:$TRAVIS_COMMIT
