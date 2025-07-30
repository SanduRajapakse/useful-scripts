@echo off
setlocal enabledelayedexpansion

:: === Scheduler Test Section ===

:: Define log folder
set LOGDIR=%~dp0logs
if not exist "%LOGDIR%" mkdir "%LOGDIR%"

:: Delete logs older than 5 minutes (testing)
powershell -Command "Get-ChildItem -Path '%LOGDIR%' -Filter *.txt | Where-Object { $_.LastWriteTime -lt (Get-Date).AddMinutes(-5) } | Remove-Item -Force"

:: Create timestamp
for /f "tokens=1-4 delims=/ " %%a in ("%DATE%") do (
    set MM=%%a
    set DD=%%b
    set YYYY=%%c
)
set HH=%TIME:~0,2%
set MN=%TIME:~3,2%
set SS=%TIME:~6,2%
if "%HH:~0,1%"==" " set HH=0%HH:~1,1%

set TIMESTAMP=%YYYY%-%MM%-%DD%_%HH%-%MN%-%SS%
set LOGFILE=%LOGDIR%\runlog_%TIMESTAMP%.txt
set SUMMARYLOG=%LOGDIR%\scheduler_summary_log.txt

:: Start log
echo ==== Scheduler Test Log (%TIMESTAMP%) ==== > "%LOGFILE%"
echo Timestamp: %DATE% %TIME% >> "%LOGFILE%"
set STATUS=SUCCESS

:: User info
echo User: %USERNAME% >> "%LOGFILE%"
whoami /all >> "%LOGFILE%" 2>>"%LOGFILE%"

:: Directory check
echo Script is running from: %~dp0 >> "%LOGFILE%"

:: Test file creation
set TESTFILE=%~dp0test_output.txt
echo Testing file creation at %TIME% > "%TESTFILE%"
if exist "%TESTFILE%" (
    echo File creation: SUCCESS >> "%LOGFILE%"
) else (
    echo File creation: FAILED >> "%LOGFILE%"
    set STATUS=FAILURE
)

:: Directory listing
dir %~dp0 >> "%LOGFILE%" 2>>"%LOGFILE%"

:: Environment info
echo Computer Name: %COMPUTERNAME% >> "%LOGFILE%"
echo User Profile: %USERPROFILE% >> "%LOGFILE%"
echo TEMP Dir: %TEMP% >> "%LOGFILE%"

:: TEMP write test
set TEMPFILE=%TEMP%\scheduler_temp_test.txt
echo TEMP file test at %TIME% > "%TEMPFILE%"
if exist "%TEMPFILE%" (
    echo TEMP directory write: SUCCESS >> "%LOGFILE%"
    del "%TEMPFILE%"
) else (
    echo TEMP directory write: FAILED >> "%LOGFILE%"
    set STATUS=FAILURE
)

:: Wrap-up
echo Script completed at: %TIME% >> "%LOGFILE%"
echo ============================== >> "%LOGFILE%"
echo.
echo %DATE% %TIME% - Status: %STATUS% - Log: runlog_%TIMESTAMP%.txt >> "%SUMMARYLOG%"


:: === Rclone Sync Section ===

:: Load DEST_FOLDER_ID from config.txt
for /f "tokens=2 delims==" %%A in ('findstr "DEST_FOLDER_ID" config.txt') do set "DEST_FOLDER_ID=%%A"
set "DEST_FOLDER_ID=%DEST_FOLDER_ID:"=%"  :: Remove quotes

:: Set paths
set "SOURCE_FOLDER=%USERPROFILE%\Documents\AllworxRecordings"
set "LOG_FILE=%LOGDIR%\sync_log_%TIMESTAMP%.txt"

:: Ensure folder exists
if not exist "%SOURCE_FOLDER%" (
    mkdir "%SOURCE_FOLDER%"
    echo Do not delete this folder of files - Sandu :^) > "%SOURCE_FOLDER%\DoNotDeleteThisFolderOrFiles.txt"
)

:: Perform rclone move
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
exit /b 0
