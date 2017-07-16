#!/bin/bash
git clone ${REPOSITORY} open_event
cd open_event
git checkout ${BRANCH}

if [ -v COMMIT_HASH ]; then
    git reset --hard ${COMMIT_HASH}
fi

pip install --no-cache-dir -r requirements.txt
rm -rf app/vintage
touch .env
chmod +x ./kubernetes/run.sh
chmod -R 0777 ./static
# /bin/bash ./kubernetes/run.sh
