#!/bin/bash

# DB Backup Script 
# Requirements: docker container name of postgres and rclone configured with pcloud

set -e

cd /home/fossasia/backup/db
docker exec opev-postgres pg_dump -U open_event_user open_event > open-event-$(date +%y-%m-%d_%H:%M).bak
fdupes . -d -N
rclone copy -vv --fast-list . pcloud:production/backup/db
find . -mtime +7 -delete
