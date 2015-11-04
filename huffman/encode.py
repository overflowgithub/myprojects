#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
import struct

import HuffParser as huffparser
import HuffTree as hufftree


def binstr2bytearray(binstr):
    """ Convert "01101..." string to a byte array """
    buf = ""
    out = bytearray()
    for char in binstr:
        buf += char
        while len(buf) >= 8:
            out.append(int(buf[0:8], 2))
            buf = buf[8:]
    # buf left over is padded with 0!
    out.append(int(buf[:].ljust(8, '0'), 2))
    return out


def main():
    """ Main code to compress a text file """
    my_argparse = argparse.ArgumentParser(description="Main arg parser")
    my_argparse.add_argument("-i", "--in_file",
                             help="source filepath to compress",
                             type=str)
    my_argparse.add_argument("-s", "--static",
                             help="static huffman compression",
                             action="store_true")
    my_argparse.add_argument("-a", "--adaptative",
                             help="semi adaptative huffman compression",
                             action="store_true")

    args = my_argparse.parse_args()
    source_file = args.in_file
    try:
        txt = open(source_file, "rb").read().decode('utf-8')
    except IOError as e:
        print("I/O error({}): {}".format(e.errno, e.strerror))

    myhuffparser = huffparser.HuffParser(txt)
    stats = myhuffparser.get_stats()

    mytree = hufftree.HuffTree(stats)
    mytree.setCode()

    char_code = {}
    for leaf in mytree.getLeafs():
        char_code[leaf.name] = leaf.code

    # Encode each char from source file to corresponding "0101.." code
    buf = ""
    for char in txt:
        buf += char_code[char]
    # Convert "01101..." string to a byte array
    out_data = binstr2bytearray(buf)

    # Create out_header with the huffman tree
    # out_header struct:
    # size of the tree scheme
    # tree scheme (depth scan first, 0=leaf, 1=node)
    # characters corresponding to leafs
    # (first leaf found in the tree scheme correspond to the first character,
    # second leaf to the second char etc.)

    (treeStruct, charTable) = mytree.getTreeStruct()
    treeStructSize = len(treeStruct)
    print(treeStruct)
    out_header = bytearray(struct.pack("B", treeStructSize))
    out_header += binstr2bytearray(treeStruct)
    out_header += bytearray(charTable.encode('utf-8'))
    
    out_file = open("{}.huf".format(source_file), "wb")
    out_file.write(out_header)
    out_file.write(out_data)
    out_file.close()

    # Results
    source_size = os.path.getsize(source_file)
    dest_size = os.path.getsize("{}.huf".format(source_file))

    rate = 1 - (dest_size / source_size)
    print("{}: {}b -> {}b. Compression rate: {:.2%} ".format(source_file,
                                                             source_size,
                                                             dest_size,
                                                             rate))

if __name__ == '__main__':
    main()
