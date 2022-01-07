#!/bin/bash
#
# Check the md5 hash digests from given file.
#

if [ $# -lt 1 ]; then
    echo "Usage:"
    echo "${0} HASH_FILE"
    exit 1
fi

hash_digest_file=${1}

md5sum --check --quiet ${hash_digest_file}
