#!/bin/python3

from argparse import ArgumentParser
from glob import glob
import hashlib
from multihash import multihash
from multibase import multibase
from pathlib import Path
import re
import sys


def parse_arguments(argv):
    parser = ArgumentParser()
    parser.add_argument('-d', '--digestfile', type=Path, default='hashfile.txt',
                        help="Digest file to write or verify")
    parser.add_argument('-e', '--encoding', type=str, default='base64',
                        help="Multibase encoding used to write digest")
    parser.add_argument('-f', '--force', action='store_true',
                        help="Overwrite digest file if it exists")
    parser.add_argument('-H', '--hash', type=str, default='sha256',
                        help="Multihash algorithm used to calculate digest")
    parser.add_argument('-p', '--path', type=Path, required=True,
                        help="Files on this path will be hashed")
    parser.add_argument('-v', '--verify', action='store_true',
                        help="Verify digest file, will not write anything new or do anything else")
    return parser.parse_args()


def iterate_files(path):
    for f in path.rglob("*"):
        if f.is_file():
            yield f


def calculate_file_hash(path, hashName):
    if hashName == 'sha256': hash = hashlib.sha256()
    if hashName == 'sha512': hash = hashlib.sha512()
    if hashName == 'sha3-256': hash = hashlib.sha3_256()
    if hashName == 'sha3-384': hash = hashlib.sha3_384()
    if hashName == 'sha3-512': hash = hashlib.sha3_512()
    # Buffer 128 Kbyte
    b  = bytearray(128 * 1024)
    memv = memoryview(b)
    with open(path.resolve(), 'rb', buffering=0) as file:
        for n in iter(lambda : file.readinto(memv), 0):
            hash.update(memv[:n])
    return hash


def hashlib2multihash(hash_name):
    """Convert from hashlib hash name to multihash hash name, incomplete"""
    if re.match('sha\d{3}', hash_name) : return 'sha2-' + hash_name[-3:]
    if re.match('sha3_\d{3}', hash_name) : return 'sha3-' + hash_name[-3:]
    return hash_name


def multihash2hashlib(mhash_name):
    """Convert from multihash hash name to hashlib hash name, incomplete"""
    if re.match('sha2-\d{3}', mhash_name): return 'sha' + mhash_name[-3:]
    if re.match('sha3-\d{3}', mhash_name): return 'sha3_' + mhash_name[-3:]
    return mhash_name


def encode_multihash(hash):
    """Take a hashlib.hash object and return a equivalent multihash"""
    mhash_name = hashlib2multihash(hash.name)
    mhash = multihash.encode(hash.digest(), mhash_name)
    return mhash


def decode_multihash(mhash):
    """Return decoded multihash object"""
    if multihash.is_valid(mhash):
        return multihash.decode(mhash)
    else:
        raise Exception("Not a valid multihash")


def read_hashlines(hashfileHandle):
    """
    Iterate over lines in a hashfile.
    Each line contains a multihashDigest followed by a file path.
    Return a tuple of (multihashDigest Path).
    """
    for line in hashfileHandle:
        # split line into multihashDigest and filePath/rest.
        # maxsplit=1 ensures that paths which contain spaces are handled correctly.
        (digest, filePath) = line.strip().split(" ", maxsplit=1)
        yield (digest, Path(filePath).resolve())


def read_hashfile(hashfile):
    """
    Read complete hashfile and return list of (multihashDigest Path) tuples.
    Be warned that this list can become large when hashfile contains many lines.
    """
    content = []
    with open(hashfile, 'r') as hashfileHandle:
        for hashline in read_hashlines(hashfileHandle):
            content.append(hashline)
    return content


def verify_hashline(hashline):
    (mhash, path) = hashline
    """Return True if digest of file is unchanged"""
    hashName = multihash2hashlib(mhash.name)
    if path.is_file():
        calculated_hash = calculate_file_hash(path, hashName)
    else:
        print(f"NOK file not found {path}")
        return False
    return calculated_hash.digest() == mhash.digest


def verify_hashfile(hashfile):
    """Return True if hash is same, False otherwise"""
    with open(hashfile, 'r') as hashfileHandle:
        for hashline in read_hashlines(hashfileHandle):
            (digest, filePath) = hashline
            if multibase.is_encoded(digest):
                digest = multibase.decode(digest)
            mhash = multihash.decode(digest)
            if not verify_hashline((mhash, filePath)):
                print(f"NOK digest mismatch {filePath}")


def write_hashlines(hashfileHandle, hashlines):
    for hashline in hashlines:
        hashfileHandle.write(f"{hashline[0]} {hashline[1]}\n")


def write_hashfile(path, outfile, hashName, encodingName):
    with open(outfile, mode='w', encoding='utf-8') as fh:
        for file in iterate_files(path):
            hash = calculate_file_hash(file, hashName)
            mhash = encode_multihash(hash)
            mhash_base64 = multibase.encode(encodingName, mhash)
            fh.write(f"{mhash_base64.decode()} {file.resolve()}\n")


if __name__ == '__main__':
    args = parse_arguments(sys.argv)
    if args.verify:
        verify_hashfile(args.digestfile)
    else:
        if args.path.is_file():
            if not args.force:
                raise FileExistsError()
        write_hashfile(args.path, args.digestfile, args.hash, args.encoding)
