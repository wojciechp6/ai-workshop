#!/usr/bin/env bash

sh configure_cuda_env.sh
docker compose up --build --abort-on-container-exit --exit-code-from client

