#!/usr/bin/env bash

export DEPLOY_BRANCH=${DEPLOY_BRANCH:-master}

if [ "$TRAVIS_PULL_REQUEST" != "false" -o "$TRAVIS_REPO_SLUG" != "fossasia/open-event-orga-server" -o  "$TRAVIS_BRANCH" != "$DEPLOY_BRANCH" ]; then
    echo "Skip production deployment for a very good reason."
    exit 0
fi

export REPOSITORY="https://github.com/${TRAVIS_REPO_SLUG}.git"

sudo rm -f /usr/bin/git-credential-gcloud.sh
sudo rm -f /usr/bin/bq
sudo rm -f /usr/bin/gsutil
sudo rm -f /usr/bin/gcloud

curl https://sdk.cloud.google.com | bash;
source ~/.bashrc
gcloud components install kubectl

gcloud config set compute/zone us-west1-a
# Decrypt the credentials we added to the repo using the key we added with the Travis command line tool
openssl aes-256-cbc -K $encrypted_27e15b7757b4_key -iv $encrypted_27e15b7757b4_iv -in ./kubernetes/travis/eventyay-8245fde7ab8a.json.enc -out eventyay-8245fde7ab8a.json -d
mkdir -p lib
gcloud auth activate-service-account --key-file eventyay-8245fde7ab8a.json
export GOOGLE_APPLICATION_CREDENTIALS=$(pwd)/eventyay-8245fde7ab8a.json
gcloud config set project eventyay
gcloud container clusters get-credentials eventyay-cluster
cd kubernetes/images/web
docker build --build-arg COMMIT_HASH=$TRAVIS_COMMIT --build-arg BRANCH=$DEPLOY_BRANCH --build-arg REPOSITORY=$REPOSITORY --no-cache -t gcr.io/eventyay/web:$TRAVIS_COMMIT .
docker tag gcr.io/eventyay/web:$TRAVIS_COMMIT gcr.io/eventyay/web:latest
gcloud docker -- push gcr.io/eventyay/web
kubectl set image deployment/web web=gcr.io/eventyay/web:$TRAVIS_COMMIT
kubectl set image deployment/celery celery=gcr.io/eventyay/web:$TRAVIS_COMMIT
