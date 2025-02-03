#!/bin/sh

# 顯示使用說明的函數
show_usage() {
    echo "Usage: $0 [DOCKER_REPO] DOCKER_IMAGE_NAME [DOCKER_IMAGE_TAG] [DOCKERFILE_PATH]"
    echo "DOCKER_REPO defaults to 'docker.io' if not provided"
    echo "If DOCKER_IMAGE_TAG is not provided, you will be prompted to enter it"
    echo "DOCKERFILE_PATH defaults to './Dockerfile' if not provided"
    exit 1
}

# 檢查必要參數
if [ $# -lt 2 ] || [ $# -gt 4 ]; then
    show_usage
fi

# 根據參數數量設定變數
if [ $# -eq 2 ]; then
    DOCKER_REPO="docker.io"
    DOCKER_IMAGE_NAME=$1
    DOCKER_IMAGE_TAG=$2
    DOCKERFILE_PATH="./Dockerfile"
elif [ $# -eq 3 ]; then
    DOCKER_REPO=$1
    DOCKER_IMAGE_NAME=$2
    DOCKER_IMAGE_TAG=$3
    DOCKERFILE_PATH="./Dockerfile"
elif [ $# -eq 4 ]; then
    DOCKER_REPO=$1
    DOCKER_IMAGE_NAME=$2
    DOCKER_IMAGE_TAG=$3
    DOCKERFILE_PATH=$4
fi

# 確認所有必要變數都有值
if [ -z "$DOCKER_IMAGE_NAME" ] || [ -z "$DOCKER_IMAGE_TAG" ]; then
    show_usage
fi

# 檢查 Dockerfile 是否存在
if [ ! -f "$DOCKERFILE_PATH" ]; then
    echo "Error: Dockerfile not found at $DOCKERFILE_PATH"
    exit 1
fi

echo "Building image with tag: $DOCKER_REPO/$DOCKER_IMAGE_NAME:$DOCKER_IMAGE_TAG"
echo "Using Dockerfile at: $DOCKERFILE_PATH"

# 執行 docker build 指令
docker build --no-cache -t $DOCKER_REPO/$DOCKER_IMAGE_NAME:$DOCKER_IMAGE_TAG -f $DOCKERFILE_PATH . --platform linux/amd64

# 如果執行成功，顯示成功訊息
if [ $? -eq 0 ]; then
    echo "Image built successfully"
else
    echo "Image build failed"
fi

# 執行 docker push 指令
docker push $DOCKER_REPO/$DOCKER_IMAGE_NAME:$DOCKER_IMAGE_TAG

# 如果執行成功，顯示成功訊息
if [ $? -eq 0 ]; then
    echo "Image pushed successfully"
else
    echo "Image push failed"
fi