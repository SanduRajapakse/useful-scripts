@echo off
setlocal enabledelayedexpansion

:: Step 0: Set base paths
set "SCRIPT_DIR=%~dp0"
set "TARGET_DIR=%SCRIPT_DIR%..\AllworxCallRecordings"
set "CONF_FILE=%SCRIPT_DIR%conf.txt"
set "TOKEN_FILE=%SCRIPT_DIR%token.json"
set "LOG_DIR=%SCRIPT_DIR%logs"
set "TEMP_RCLONE_CONF=%TEMP%\rclone_allworx.conf"
set "RCLONE_EXE=%SCRIPT_DIR%rclone.exe"

:: Ensure logs directory exists
if not exist "!LOG_DIR!" mkdir "!LOG_DIR!"

:: Create timestamp for log file
for /f "tokens=1-4 delims=/ " %%a in ("%DATE%") do (
    set MM=%%a
    set DD=%%b
    set YYYY=%%c
)
set HH=%TIME:~0,2%
set MN=%TIME:~3,2%
set SS=%TIME:~6,2%
if "%HH:~0,1%"==" " set HH=0%HH:~1,1%
set "TIMESTAMP=%YYYY%-%MM%-%DD%_%HH%-%MN%-%SS%"
set "LOG_FILE=!LOG_DIR!\upload_log_!TIMESTAMP!.txt"

:: Delete logs older than 30 days
powershell -Command "Get-ChildItem -Path '%LOG_DIR%' -Filter *.txt | Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-30) } | Remove-Item -Force"

:: Step 1: Create AllworxCallRecordings folder if it doesn't exist
if not exist "!TARGET_DIR!" (
    mkdir "!TARGET_DIR!"
)

:: Step 2: Create the marker file if not present
set "MARKER_FILE=!TARGET_DIR!\DoNotDeleteThisFolderOrFiles.txt"
if not exist "!MARKER_FILE!" (
    echo Do not delete this folder of files - Sandu :^) > "!MARKER_FILE!"
)

:: Step 3: Read DEST_FOLDER_ID from conf.txt
set "DEST_FOLDER_ID="
for /f "tokens=1,2 delims==" %%A in ('findstr /R "^DEST_FOLDER_ID=" "!CONF_FILE!"') do (
    set "DEST_FOLDER_ID=%%~B"
)
set "DEST_FOLDER_ID=%DEST_FOLDER_ID:"=%"

:: Step 4: Generate rclone config file
> "!TEMP_RCLONE_CONF!" echo [GDrive Allworx Recordings]
>> "!TEMP_RCLONE_CONF!" echo type = drive
>> "!TEMP_RCLONE_CONF!" echo scope = drive
>> "!TEMP_RCLONE_CONF!" echo team_drive = 0AEl_R6zwAUbiUk9PVA
>> "!TEMP_RCLONE_CONF!" echo root_folder_id =

:: Step 5: Read token.json into a single line
set "TOKEN_LINE="
for /f "usebackq delims=" %%A in ("!TOKEN_FILE!") do (
    set "LINE=%%A"
    set "TOKEN_LINE=!TOKEN_LINE!!LINE!"
)
>> "!TEMP_RCLONE_CONF!" echo token = !TOKEN_LINE!

:: Step 6: Run rclone move command
echo ==== Starting Rclone Move: %DATE% %TIME% ==== >> "!LOG_FILE!"
echo RCLONE_EXE resolved to: "!RCLONE_EXE!" >> "!LOG_FILE!"
echo From: "!TARGET_DIR!" >> "!LOG_FILE!"
echo To:   "GDrive Allworx Recordings:" >> "!LOG_FILE!"
echo Config: "!TEMP_RCLONE_CONF!" >> "!LOG_FILE!"

if exist "!RCLONE_EXE!" (
    "!RCLONE_EXE!" move "!TARGET_DIR!" "GDrive Allworx Recordings:" ^
        --config="!TEMP_RCLONE_CONF!" ^
        --drive-root-folder-id=!DEST_FOLDER_ID! ^
        --drive-shared-with-me ^
        --ignore-existing ^
        --no-traverse ^
        --exclude "DoNotDeleteThisFolderOrFiles.txt" ^
        --delete-empty-src-dirs ^
        --log-level INFO >> "!LOG_FILE!" 2>>&1

    echo Rclone exit code: !ERRORLEVEL! >> "!LOG_FILE!"
) else (
    echo ERROR: rclone.exe not found at "!RCLONE_EXE!" >> "!LOG_FILE!"
)

echo ==== Rclone Completed: %DATE% %TIME% ==== >> "!LOG_FILE!"
echo. >> "!LOG_FILE!"

:: Step 7: Optional test file if CONFIG_TESTING=true
set "CONFIG_TESTING=false"
for /f "tokens=1,2 delims==" %%A in ('findstr /R "^CONFIG_TESTING=" "!CONF_FILE!"') do (
    set "CONFIG_TESTING=%%~B"
)
set "CONFIG_TESTING=%CONFIG_TESTING:"=%"

if /i "!CONFIG_TESTING!"=="true" (
    call :CreateTestFile
)

echo Upload complete. Log: "!LOG_FILE!"
endlocal
exit /b 0

:CreateTestFile
for /f "tokens=1-4 delims=/ " %%a in ("%DATE%") do (
    set MM=%%a
    set DD=%%b
    set YYYY=%%c
)
set HH=%TIME:~0,2%
set MN=%TIME:~3,2%
set SS=%TIME:~6,2%
if "%HH:~0,1%"==" " set HH=0%HH:~1,1%
set "TIMESTAMP=%YYYY%-%MM%-%DD%_%HH%-%MN%-%SS%"
set "TEST_FILENAME=TestFile_!TIMESTAMP!.txt"
echo !TEST_FILENAME! > "!TARGET_DIR!\!TEST_FILENAME!"
echo Created test file: !TEST_FILENAME!
exit /b
