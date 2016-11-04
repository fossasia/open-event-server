#!/bin/bash
git clone ${REPOSITORY} open_event
cd open_event
git checkout ${BRANCH}
chmod +x ./kubernetes/run.sh
/bin/bash ./kubernetes/run.sh
