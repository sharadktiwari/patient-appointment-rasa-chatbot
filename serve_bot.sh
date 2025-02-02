#!/bin/bash

docker compose -f docker-compose-ngnix.yaml up -d &
docker compose up -d &
./botui.sh &
./actionserver.sh &
./apiserver.sh &

