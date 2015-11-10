#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os.path

from bitstring import BitArray

import hufftree


def main():
    """ Main code to uncompress a .huf file """
    my_argparse = argparse.ArgumentParser(description="Main arg parser")
    my_argparse.add_argument("-i", "--in_file",
                             help="compressed file",
                             type=str)

    args = my_argparse.parse_args()
    source_filepath = args.in_file

    try:
        source_file = open(source_filepath, "rb").read()
    except IOError as e:
        print("I/O error({}): {}".format(e.errno, e.strerror))

    # ----------------------------------------------------------------------- #
    # Build the Huffman tree and the prefix-free binary code for each symbol
    # ----------------------------------------------------------------------- #

    huff_tree = hufftree.HuffTree(filepath=source_filepath)
    header_size = huff_tree.get_header_size()

    char_list_size = huff_tree.set_leaves_symbol(source_file[header_size:])

    data = source_file[header_size+char_list_size:]

    data_bin = BitArray(data)
    decoded_str = binstr2symbols(huff_tree, data_bin)

    dest_filepath = "{}_decoded.txt".format(os.path.splitext(source_filepath)[0])
    dest_file = open(dest_filepath, "w")
    dest_file.write(decoded_str)
    dest_file.close()
    print("Decoding succeed: {} !!!".format(dest_filepath))


def binstr2symbols(tree, binstr):
        tmp = tree.root
        buf = ""
        for bit in binstr:
            if not bit:
                tmp = tmp.children[0]
            else:
                tmp = tmp.children[1]

            if tmp.is_leaf():
                buf += tmp.name
                tmp = tree.root

        return buf

if __name__ == '__main__':
    main()
