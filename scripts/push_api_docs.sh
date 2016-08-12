# pushes API docs to gh-pages on successful build
#
# thanks to https://gist.github.com/domenic/ec8b0fc8ab45f39403dd
#!/bin/sh
set -e

git config --global user.name "Travis CI"
git config --global user.email "noreply+travis@fossasia.org"

# set ssh
openssl aes-256-cbc -K $encrypted_512f7587e087_key -iv $encrypted_512f7587e087_iv -in opev_orga_mine.enc -out deploy_key -d
chmod 600 deploy_key
eval `ssh-agent -s`
ssh-add deploy_key

# clone and do
git clone -b gh-pages "git@github.com:aviaryan/open-event-orga-server.git" gh-pages
cp static/temp/swagger.json gh-pages/api/v2/swagger.json
cd gh-pages
git commit -m '[Auto] Updated API docs' api/v2/swagger.json || echo "no changes"
git push origin gh-pages

exit 0
