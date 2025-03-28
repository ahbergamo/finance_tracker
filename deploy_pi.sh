#!/bin/bash
set -e

PI_USER="<PI User>"
PI_HOST="<PI IP>"

TMP_DIR="/tmp/deploy_tmp"
DEPLOY_FILE="deployment_package.tar.gz"
EXCLUDES=(".git" ".vscode" ".devcontainer" ".gitignore" "deploy.py" "clean.sh" "deploy.sh")

# Clean temporary directory
rm -rf "$TMP_DIR"
mkdir -p "$TMP_DIR"

# Copy all files/directories except explicitly excluded ones
shopt -s dotglob
for item in * .*; do
    [[ "$item" == "." || "$item" == ".." ]] && continue
    if [[ ! " ${EXCLUDES[@]} " =~ " ${item} " ]]; then
        cp -a "$item" "$TMP_DIR/"
    fi
done
shopt -u dotglob

# Production: Move files from docker/ to root of tmp dir
if [[ -d "$TMP_DIR/docker" ]]; then
    mv "$TMP_DIR"/docker/* "$TMP_DIR/"
    mv "$TMP_DIR/docker/.env" "$TMP_DIR/"
    rm -rf "$TMP_DIR/docker"
fi

# Create deployment archive
tar -czf "$DEPLOY_FILE" -C "$TMP_DIR" .
rm -rf "$TMP_DIR"

# Deploy to Raspberry Pi server
PI_DIR="/home/$PI_USER/finance_tracker"
echo "Transferring deployment package to production server..."
scp -o "RequestTTY=no" "$DEPLOY_FILE" "$PI_USER@$PI_HOST:/home/$PI_USER"
ssh "$PI_USER@$PI_HOST" bash -l -c "'
    docker stop finance_tracker 2>/dev/null || true &&
    docker container rm finance_tracker 2>/dev/null || true &&
    sudo rm -rf \"$PI_DIR\" &&
    mkdir -p \"$PI_DIR\" &&
    tar -xzf \"/home/$PI_USER/$DEPLOY_FILE\" -C \"$PI_DIR\" &&
    rm \"/home/$PI_USER/$DEPLOY_FILE\" &&
    cd \"$PI_DIR\" &&
    set -a && source .env && set +a &&
    docker-compose up -d --build
'"

rm "$DEPLOY_FILE"
echo "✅ Production deployment completed successfully."