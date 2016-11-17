#!/usr/bin/env bash

if [ "$TRAVIS_PULL_REQUEST" != "false" -o "$TRAVIS_REPO_SLUG" != "fossasia/open-event-orga-server" ]; then
    echo "Just a PR. Skip google cloud deployment."
    exit 0
fi

cd kubernetes/image
docker build -t gcr.io/eventyay/web:$TRAVIS_COMMIT .
docker tag gcr.io/eventyay/web:$TRAVIS_COMMIT gcr.io/eventyay/web:latest
gcloud docker -- push gcr.io/eventyay/web
kubectl patch deployment web -p \ '{"spec":{"template":{"spec":{"containers":[{"name":"web","image":"gcr.io/eventyay/web:'"$TRAVIS_COMMIT"'"}]}}}}'
kubectl patch deployment celery -p \ '{"spec":{"template":{"spec":{"containers":[{"name":"celery","image":"gcr.io/eventyay/web:'"$TRAVIS_COMMIT"'"}]}}}}'
