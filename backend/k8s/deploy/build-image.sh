#!/bin/bash

DOCKERFILE_PATH=$1
DOCKER_IMAGE_NAME=$2
DOCKER_IMAGE_TAG=$3

# Build the Docker image
echo "Building Docker image $DOCKER_IMAGE_NAME:$DOCKER_IMAGE_TAG from $DOCKERFILE_PATH"

docker build -f $DOCKERFILE_PATH -t $DOCKER_IMAGE_NAME:$DOCKER_IMAGE_TAG . --platform linux/amd64

# Push the Docker image
docker push $DOCKER_IMAGE_NAME:$DOCKER_IMAGE_TAG