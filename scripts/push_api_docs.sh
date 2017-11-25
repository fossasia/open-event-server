# pushes API docs to gh-pages on successful build
#
#!/bin/sh
set -e

git config --global user.name "Travis CI"
git config --global user.email "noreply+travis@fossasia.org"

# export DEPLOY_BRANCH=${DEPLOY_BRANCH:-master}
export DEPLOY_BRANCH='development' # TODO change before merging to dev

if [ "$TRAVIS_PULL_REQUEST" != "false" -o "$TRAVIS_REPO_SLUG" != "fossasia/open-event-server" -o  "$TRAVIS_BRANCH" != "$DEPLOY_BRANCH" ]; then
    echo "We update docs only from master. So, let's skip this shall we ? :)"
    exit 0
fi

npm install -g aglio

# set ssh
openssl aes-256-cbc -K $encrypted_512f7587e087_key -iv $encrypted_512f7587e087_iv -in ./scripts/opev_orga.enc -out deploy_key -d
chmod 600 deploy_key
eval `ssh-agent -s`
ssh-add deploy_key

# clone and do
git clone -b gh-pages "git@github.com:fossasia/open-event-server.git" gh-pages
rm -rf gh-pages/api/v1/*
aglio --theme-full-width --theme-variables slate -i docs/api/api_blueprint.apib -o gh-pages/api/v1/index.html
cp -R docs/general/* gh-pages/_docs/
cp -R docs/installation/* gh-pages/_installation/
cd gh-pages
git add .
git commit -m '[Auto] Updated API Docs'
git push origin gh-pages

exit 0
