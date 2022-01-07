#!/bin/bash
#
# Calculate md5 hash digest for all files in given directory.
# TODO: use multihash

if [ $# -lt 2 ]; then
    echo "Usage:"
    echo "${0} DIRECTORY OUTPUT_FILE"
    exit 1
fi

# First arg is the search directory,
# defaults to current work directory.
directory=${1:-$(pwd)}
directory=$(realpath ${directory})
if [ ! -d ${directory} ]; then
    echo "Directory does not exist: ${directory}"
    exit 1
fi

# Second arg is the output file to which to write the hash digests,
# defaults to hash_digests.txt
output_file=${2:-hash_digests.txt}

# Backup output_file if it exists already.
# Existing backups will be overwritten.
if [ -e ${output_file} ]; then
  mv -f ${output_file} ${output_file}~
fi

echo "# md5sums of each file in ${directory}" > ${output_file}
find ${search_directory} -type f -exec md5sum -b {} \; >> ${output_file}
