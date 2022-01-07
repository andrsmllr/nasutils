#!/bin/bash
#
# Do a snapraid scrub with logging.

# First argument is the scrub percentage, default to 15 if no argument given.
scrub_percentage=${1:-15}

# Second argument is the log file, default /var/log/snapraid.scrub.log if no argument given.
logfile=${2:-/var/log/snapraid.scrub.log}

start_time=$(date +%Y-%m-%d_%H:%M:%S)
echo "### Snapraid scrub of ${scrub_percentage}% starting at ${start_time} ###" >> ${logfile}

snapraid -p ${scrub_percentage} scrub -l ${logfile}

done_time=$(date +%Y-%m-%d_%H:%M:%S)
echo "### Snapraid scrub of ${scrub_percentage}% completed at ${done_time} ###" >> ${logfile}
