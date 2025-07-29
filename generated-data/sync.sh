#!/bin/bash

set -e

trap "echo 'Interrupted. Exiting...'; exit 1" SIGINT

while true; do
  databricks sync \
    --watch . \
    --exclude 'sync.sh' \
    --exclude '.*' \
    --exclude '**/.*' \
    /Workspace/Users/reggie.pierce@databricks.com/databricks_apps/reggie-pierce-data-app_2025_07_25-13_49/dash-data-app-obo-user
  echo "Sync exited with error. Retrying in 1 second..."
  sleep 1
done