#!/bin/bash
set -e
   
# Extract the version from your config. Adjust the import if needed.
APP_VERSION=$(python3 -c "from config.config import DevelopmentConfig; print(DevelopmentConfig.VERSION)")
echo "Building version: ${APP_VERSION}"

echo "Copying files from docker_portable directory..."
echo "Copying files from docker_portable directory (files only)..."
find docker_portable -maxdepth 1 -type f -exec cp {} ./ \;

# Create and use a Buildx builder (only needed once)
docker buildx create --name mybuilder --use || docker buildx use mybuilder
docker buildx inspect --bootstrap

# Build and push the finance_tracker image with the version tag and latest tag
docker buildx build --no-cache \
  --platform linux/amd64,linux/arm64 \
  -t abergamo/finance-tracker:"${APP_VERSION}" \
  -t abergamo/finance-tracker:latest \
  --push \
  .

# Build and push the nginx image using nginx.Dockerfile with version tag and default tag
docker buildx build --no-cache \
  --platform linux/amd64,linux/arm64 \
  -f nginx.Dockerfile \
  -t abergamo/finance-tracker:nginx-"${APP_VERSION}" \
  -t abergamo/finance-tracker:nginx \
  --push \
  .

echo "Cleaning up Docker configuration files..."
rm docker-compose.yml Dockerfile nginx.conf nginx.Dockerfile entrypoint.sh

echo "Removing .env file..."
rm .env_default

echo "Build and push complete. Use 'docker-compose up' to start all services."