#!/bin/bash
git clone ${REPOSITORY} open_event
cd open_event
git checkout ${BRANCH}
pip install --no-cache-dir -r requirements.txt
bower install --allow-root && bower cache clean --allow-root
chmod +x ./kubernetes/run.sh
# /bin/bash ./kubernetes/run.sh
