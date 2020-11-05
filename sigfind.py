#!/usr/bin/env python3

import sys

from argparse import ArgumentParser
from os import stat

parser = ArgumentParser()
# Standard options taken from sigfind
parser.add_argument('-b', '--bsize', dest='block_size', type=int, default=512,
                    help='Give block size (default 512)')
parser.add_argument('-o', '--offset', type=int, default=0,
                    help='Give offset into block where signature should exist (default 0)')
# Options taken from dd
parser.add_argument('-s', '--seek', type=int, default=0,
                    help='Seek to this block before searching (default 0)')
# Options taken from grep
parser.add_argument('-l', '--files-with-matches', action='store_true',
                    help='print only names of FILEs with selected lines')
parser.add_argument('-m', '--max-count',type=int, default=0,
                    help='stop after specified number of matches')
parser.add_argument('-H', '--with-filename', action='store_true',
                    help='print file name with output lines')
parser.add_argument('hex_signature')
parser.add_argument('file')
args = parser.parse_args()

offset = int(args.offset)
hex_signature = bytes.fromhex(args.hex_signature)

# Check if we want to read from stdin
if args.file == '-':
    size = 0
    # Read from standard input
    img = sys.stdin.buffer
    # Seek to the specified sector
    img.read(args.seek * args.block_size)
else:
    size = stat(args.file).st_size
    # Open the disk image
    img = open(args.file, 'rb')
    # Seek to the specified sector
    img.seek(args.seek * args.block_size)

# Calculate zero padding
if size > 0:
    blocks = int(size/args.block_size)
    block_len = len(str(blocks))
else:
    block_len = 8
offset_len = len(str(args.block_size))

last = None
found = -1
matches = 0
# Our starting position in bytes before reading
position = (args.seek - 1) * args.block_size
while not size or position < size:
    try:
        # Read one sector
        chunk = img.read(args.block_size)
    except Exception as e:
        print(e)
        break
    # We got no data back (from stdin)
    if not chunk:
        break
    position += args.block_size
    match = False
    # If we specified an offset of 0 or greater
    if offset >= 0:
        # Look in the specified offset
        if chunk[offset:offset+len(hex_signature)] == hex_signature:
            match = True
    # If we specified an offset of -1
    else:
        # Look in the entire sector
        found = chunk.find(hex_signature)
        if found >= 0:
            match = True
    # If we found a match
    if match:
        sector = int(position / args.block_size)
        # Calculate the distance from the last match
        if last is None:
            distance = '-'
        else:
            distance = '+{0}'.format(sector - last)
        last = sector
        # Print only the file names if requested
        if args.files_with_matches:
            print('{0}'.format(args.file))
            break
        # Print the file names if requested
        if args.with_filename:
            print('{0}:'.format(args.file), end='')
        else:
            print('Block: ', end='')
        # Otherwise print out the sector
        if offset >= 0:
            print('{0: >{1}} ({2})'.format(sector, block_len, distance))
        else:
            print('{0: >{1}}:{2: <{3}} ({4})'.format(sector, block_len, found, offset_len, distance))
        matches += 1
        if args.max_count > 0 and matches >= args.max_count:
            break

