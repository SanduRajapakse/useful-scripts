# Allworx Call Sync Script
By: Sandu Rajapakse

## Setup
Copy files do Documents folder of the system.

On MAC, make the sync.sh file executable:
```sh
chmod +x ~/Documents/AllworxSync/sync.sh
```


# Scheduling:
On Windows (Task Scheduler)
Schedule sync.bat to run every 30 minutes.

On macOS/Linux
crontab -e

Add
*/30 * * * * /Documents/AllworxSync/sync.sh