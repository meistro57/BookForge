#!/usr/bin/env bash
set -e

# BookForge Automated Production Build & Deployment Script
# Usage: ./scripts/deploy.sh [TARGET_DIR] [BACKUP_DIR]

TARGET_DIR="${1:-/var/www/html/BookForge}"
BACKUP_DIR="${2:-/var/www/html/BookForge_backup_$(date +%Y%m%d_%H%M%S)}"

echo "==> Step 1: Running production build..."
npm run build

if [ ! -d "dist" ]; then
  echo "Error: Build failed or dist directory was not created!"
  exit 1
fi

echo "==> Step 2: Checking target directory ${TARGET_DIR}..."
if [ -d "${TARGET_DIR}" ]; then
  echo "--> Creating backup of existing deployment at ${BACKUP_DIR}..."
  mkdir -p "$(dirname "${BACKUP_DIR}")"
  cp -r "${TARGET_DIR}" "${BACKUP_DIR}"
fi

echo "==> Step 3: Deploying dist contents to ${TARGET_DIR}..."
mkdir -p "${TARGET_DIR}"
cp -r dist/* "${TARGET_DIR}/"
if [ -f "dist/.htaccess" ]; then
  cp dist/.htaccess "${TARGET_DIR}/.htaccess"
fi

echo "==> Step 4: Applying file and directory permissions..."
find "${TARGET_DIR}" -type d -exec chmod 755 {} +
find "${TARGET_DIR}" -type f -exec chmod 644 {} +

echo "==> Deployment completed successfully to ${TARGET_DIR}!"
