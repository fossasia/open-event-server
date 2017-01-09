# pushes API docs to gh-pages on successful build
#
# thanks to https://gist.github.com/domenic/ec8b0fc8ab45f39403dd
#!/bin/sh
set -e

git config --global user.name "Travis CI"
git config --global user.email "noreply+travis@fossasia.org"

if [ "$TRAVIS_PULL_REQUEST" != "false" -o "$TRAVIS_REPO_SLUG" != "fossasia/open-event-orga-server" ]; then
    echo "Just a PR. No push"
    exit 0
fi

# set ssh
openssl aes-256-cbc -K $encrypted_512f7587e087_key -iv $encrypted_512f7587e087_iv -in ./scripts/opev_orga.enc -out deploy_key -d
chmod 600 deploy_key
eval `ssh-agent -s`
ssh-add deploy_key

# clone and do
git clone -b gh-pages "git@github.com:fossasia/open-event-orga-server.git" gh-pages
cp static/temp/swagger.json gh-pages/api/v1/swagger.json
cp report.html gh-pages/robot/report.html
cp log.html gh-pages/robot/log.html
cp output.xml gh-pages/robot/output.xml
cd gh-pages
git add robot/log.html
git add robot/output.xml
git add robot/report.html
git add api/v1/swagger.json
git commit -m '[Auto] Updated API docs and robot test results'
git push origin gh-pages

exit 0
