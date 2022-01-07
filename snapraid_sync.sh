#!/bin/bash
#
# Do a snapraid sync.

# The first argument is the log file, default /var/log/snapraid.sync.log if no argument given.
logfile=${1:-/var/log/snapraid.sync.log}

start_time=$(date +%Y-%m-%d_%H:%M:%S)
echo "### Snapraid sync starting at ${start_time} ###" >> ${logfile}

snapraid sync -l ${logfile}

done_time=$(date +%Y-%m-%d_%H:%M:%S)
echo "### Snapraid sync completed at ${done_time} ###" >> ${logfile}
