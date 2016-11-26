#!/bin/bash
git clone ${REPOSITORY} open_event
cd open_event
git checkout ${BRANCH}

if [ -v COMMIT_HASH ]; then
    git reset --hard ${COMMIT_HASH}
fi

pip install --no-cache-dir -r requirements.txt
bower install --allow-root && bower cache clean --allow-root
chmod +x ./kubernetes/run.sh
chmod -R 0777 ./static
# /bin/bash ./kubernetes/run.sh
