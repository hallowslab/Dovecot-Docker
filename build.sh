#!/bin/bash
set -e

# Usage: ./build.sh <username> <os> <variant> [--push]

USERNAME=$1
OS=$2
VARIANT=$3
PUSH=false

if [ -z "$USERNAME" ] || [ -z "$OS" ] || [ -z "$VARIANT" ]; then
    echo "Usage: ./build.sh <dockerhub_username> <os> <variant> [--push]"
    exit 1
fi

if [[ "$4" == "--push" ]]; then
    PUSH=true
fi

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOCKERFILE="$REPO_ROOT/variants/$OS/$VARIANT/Dockerfile"
IMAGE_NAME="$USERNAME/dovecot-$OS:$VARIANT"

if [ ! -f "$DOCKERFILE" ]; then
    echo "Error: Dockerfile not found for variant '$OS/$VARIANT' at $DOCKERFILE"
    exit 1
fi

echo "Building image: $IMAGE_NAME"
docker build -t "$IMAGE_NAME" -f "$DOCKERFILE" "$REPO_ROOT"

if [ "$PUSH" = true ]; then
    echo "Pushing image: $IMAGE_NAME"
    docker push "$IMAGE_NAME"
fi
