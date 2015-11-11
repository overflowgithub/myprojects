#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os.path

from bitstring import BitArray

import huffprob
import hufftree


def main():
    """ Main code to compress a text file """

    huff_args_parser = argparse.ArgumentParser(
                        description="Huffman encoding/decoding for text files"
                        )

    huff_args_parser.add_argument("-v", "--verbose",
                                  action="store_true",
                                  help="increase output verbosity")
    group = huff_args_parser.add_mutually_exclusive_group()
    group.add_argument("-c", "--compress", action="store_true",
                       help="compress with semi adaptative huffman coding")
    group.add_argument("-x", "--extract", action="store_true",
                       help="extract huffman compressed files")

    huff_args_parser.add_argument("source",
                                  help="source filepath to compress/extract",
                                  type=str)

    huff_args_parser.add_argument("dest",
                                  help="dest filepath to extract/compress",
                                  type=str,
                                  nargs='?')

    args = huff_args_parser.parse_args()

    assert os.path.isfile(args.source)

    source_path = args.source

    if args.compress:
        if args.dest:
            dest_path = args.dest
        else:
            dest_path = "{}.huf".format(os.path.splitext(source_path)[0])

        compress(source_path, dest_path)
    else:
        if args.dest:
            dest_path = args.dest
        else:
            dest_path = "{}_decoded.txt".\
                        format(os.path.splitext(source_path)[0])
        extract(source_path, dest_path)


def compress(source_filepath, dest):
    try:
        source_file = open(source_filepath, "rb").read().decode('utf-8')
    except IOError as e:
        print("I/O error({}): {}".format(e.errno, e.strerror))
    except:
        print("{} is not a valid encoded utf-8 file".format(source_file))

    # ----------------------------------------------------------------------- #
    # Get information on the source file:
    #   - Alphabet and weight of each symbol from the alphabet
    # ----------------------------------------------------------------------- #
    huff_prob = huffprob.HuffProb(source_file)
    stats = huff_prob.get_stats()

    # ----------------------------------------------------------------------- #
    # Build the Huffman tree and the prefix-free binary code for each symbol
    # ----------------------------------------------------------------------- #
    huff_tree = hufftree.HuffTree(stats)

    # ----------------------------------------------------------------------- #
    # Encode the source file using the prefix-free binary code
    # ----------------------------------------------------------------------- #
    codewords = huff_tree.get_codewords()
    buf = BitArray()
    for char in source_file:
        buf += codewords[char]

    # Convert "01101..." BitArray to a bytearray
    encoded_data = buf.tobytes()

    # ----------------------------------------------------------------------- #
    # Create the output file:
    #   - Add a header with the tree and symbol list
    #   - Add the encoded data
    # ----------------------------------------------------------------------- #
    tree_struct = huff_tree.get_bitstring_struct()
    tree_symbols = huff_tree.get_symbols()

    header = tree_struct.tobytes()
    header += bytearray(''.join(tree_symbols).encode('utf-8'))

    dest_filepath = "{}.huf".format(os.path.splitext(source_filepath)[0])
    dest_file = open(dest_filepath, "wb")
    dest_file.write(header + encoded_data)
    dest_file.close()

    # ----------------------------------------------------------------------- #
    # Performance report
    # ----------------------------------------------------------------------- #
    source_size = os.path.getsize(source_filepath)
    dest_size = os.path.getsize(dest_filepath)
    rate = 1 - (dest_size / source_size)

    print("{} ({}b) -> {} ({}b)".format(source_filepath,
                                        source_size,
                                        dest_filepath,
                                        dest_size
                                        ))
    print("Compression rate: {:.2%}".format(rate))


def extract(source_filepath, dest):

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

    dest_filepath = "{}_decoded.txt".\
                    format(os.path.splitext(source_filepath)[0])
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
