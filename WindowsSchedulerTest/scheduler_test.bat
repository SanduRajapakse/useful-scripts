@echo off
setlocal enabledelayedexpansion

:: Delete logs older than 5 minutes (for testing)
set LOGDIR=%~dp0logs
if not exist "%LOGDIR%" mkdir "%LOGDIR%"

powershell -Command "Get-ChildItem -Path '%LOGDIR%' -Filter *.txt | Where-Object { $_.LastWriteTime -lt (Get-Date).AddMinutes(-5) } | Remove-Item -Force"


:: Create unique timestamp for this run
for /f "tokens=1-4 delims=/ " %%a in ("%DATE%") do (
    set MM=%%a
    set DD=%%b
    set YYYY=%%c
)
set HH=%TIME:~0,2%
set MN=%TIME:~3,2%
set SS=%TIME:~6,2%

:: Clean up leading space in hour
if "%HH:~0,1%"==" " set HH=0%HH:~1,1%

set TIMESTAMP=%YYYY%-%MM%-%DD%_%HH%-%MN%-%SS%

:: Paths
set LOGDIR=%~dp0logs
if not exist "%LOGDIR%" mkdir "%LOGDIR%"

set LOGFILE=%LOGDIR%\runlog_%TIMESTAMP%.txt
set SUMMARYLOG=%LOGDIR%\scheduler_summary_log.txt

:: Start logging
echo ==== Scheduler Test Log (%TIMESTAMP%) ==== > "%LOGFILE%"
echo Timestamp: %DATE% %TIME% >> "%LOGFILE%"
set STATUS=SUCCESS

:: Current user and privileges
echo User: %USERNAME% >> "%LOGFILE%"
whoami /all >> "%LOGFILE%" 2>>"%LOGFILE%"

:: Current directory
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

:: Test directory listing
dir %~dp0 >> "%LOGFILE%" 2>>"%LOGFILE%"

:: Test environment variables
echo Computer Name: %COMPUTERNAME% >> "%LOGFILE%"
echo User Profile: %USERPROFILE% >> "%LOGFILE%"
echo TEMP Dir: %TEMP% >> "%LOGFILE%"

:: Test write to TEMP
set TEMPFILE=%TEMP%\scheduler_temp_test.txt
echo TEMP file test at %TIME% > "%TEMPFILE%"
if exist "%TEMPFILE%" (
    echo TEMP directory write: SUCCESS >> "%LOGFILE%"
    del "%TEMPFILE%"
) else (
    echo TEMP directory write: FAILED >> "%LOGFILE%"
    set STATUS=FAILURE
)

:: Wrap up
echo Script completed at: %TIME% >> "%LOGFILE%"
echo ============================== >> "%LOGFILE%"
echo.

:: Update summary log
echo %DATE% %TIME% - Status: %STATUS% - Log: runlog_%TIMESTAMP%.txt >> "%SUMMARYLOG%"

endlocal
exit /b 0
