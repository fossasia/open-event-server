# pushes API docs to gh-pages on successful build
#
#!/bin/sh
set -e

git config --global user.name "Circle CI"
git config --global user.email "noreply+circleci@fossasia.org"

# export DEPLOY_BRANCH=${DEPLOY_BRANCH:-master}
export DEPLOY_BRANCH='development' # TODO change before merging to dev

if [ "$CIRCLE_PULL_REQUEST" -o  "$CIRCLE_BRANCH" != "$DEPLOY_BRANCH" ]; then
    echo "We update docs only from master. So, let's skip this shall we ? :)"
    exit 0
fi

# clone and do
git clone -b gh-pages "git@github.com:fossasia/open-event-server.git" gh-pages
rm -rf gh-pages/api/v1/*
npx aglio --theme-full-width --theme-variables slate -i docs/api/api_blueprint.apib -o gh-pages/api/v1/index.html
cp -R docs/general/* gh-pages/_docs/
cp -R docs/installation/* gh-pages/_installation/
cd gh-pages
git add .
git diff-index --quiet HEAD || git commit -m '[skip ci] Updated API Docs'
git push origin gh-pages

exit 0
