#!/bin/bash

set -e

rclone copy -vv --fast-list /home/fossasia/apps/server/static pcloud:production/backup/media
