#!/bin/bash

# Load folder ID from config
DEST_FOLDER_ID=$(grep DEST_FOLDER_ID config.txt | cut -d '=' -f2 | xargs | tr -d '"')

SOURCE_FOLDER="$HOME/Documents/AllworxRecordings"
LOG_FILE="./sync_log.txt"

# Create local folder and seed file if not exist
if [ ! -d "$SOURCE_FOLDER" ]; then
  mkdir -p "$SOURCE_FOLDER"
  echo "Do not delete this folder of files - Sandu : )" > "$SOURCE_FOLDER/DoNotDeleteThisFolderOrFiles.txt"
fi

# Upload all except the excluded file and clean up local
rclone move "$SOURCE_FOLDER" "GDrive Allworx Recordings:" \
  --config="./rclone.conf" \
  --drive-root-folder-id="$DEST_FOLDER_ID" \
  --drive-shared-with-me \
  --ignore-existing \
  --no-traverse \
  --exclude "DoNotDeleteThisFolderOrFiles.txt" \
  --delete-empty-src-dirs \
  --log-level INFO \
  --log-file="$LOG_FILE"
