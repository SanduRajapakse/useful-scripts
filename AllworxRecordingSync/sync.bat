@echo off
setlocal

:: Load DEST_FOLDER_ID from config.txt
for /f "tokens=2 delims==" %%A in ('findstr "DEST_FOLDER_ID" config.txt') do set "DEST_FOLDER_ID=%%A"
set "DEST_FOLDER_ID=%DEST_FOLDER_ID:"=%"  :: Remove quotes if present

:: Set paths
set "SOURCE_FOLDER=%USERPROFILE%\Documents\AllworxRecordings"
set "LOG_FILE=sync_log.txt"

:: Create folder and seed file if not exist
if not exist "%SOURCE_FOLDER%" (
    mkdir "%SOURCE_FOLDER%"
    echo Do not delete this folder of files - Sandu :^) > "%SOURCE_FOLDER%\DoNotDeleteThisFolderOrFiles.txt"
)

:: Upload all files except the excluded one, and clean up local
rclone.exe move "%SOURCE_FOLDER%" "GDrive Allworx Recordings:" ^
  --config="rclone.conf" ^
  --drive-root-folder-id=%DEST_FOLDER_ID% ^
  --drive-shared-with-me ^
  --ignore-existing ^
  --no-traverse ^
  --exclude "DoNotDeleteThisFolderOrFiles.txt" ^
  --delete-empty-src-dirs ^
  --log-level INFO ^
  --log-file="%LOG_FILE%"

endlocal
pause
