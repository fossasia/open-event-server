#!/bin/bash
git clone ${REPOSITORY} open_event_android
cd open_event_android
git checkout ${BRANCH}

pip install --no-cache-dir -r requirements.txt
npm install
