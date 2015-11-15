#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os.path
import logging
import time


from bitstring import BitArray

import huffprob
import hufftree

start_time = 0


def main():
    """ Main code to compress/extract text file """

    huff_args_parser = argparse.ArgumentParser(
        description="Huffman encoding/decoding for text files"
    )

    huff_args_parser.add_argument("-v", "--verbose",
                                  action="count",
                                  default=0,
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

    if args.verbose >= 2:
        logging.basicConfig(level=logging.DEBUG)
    elif args.verbose == 1:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.ERROR)

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
        logging.critical("I/O error({}): {}".format(e.errno, e.strerror))
    except:
        logging.critical("{} is not a valid encoded utf-8 file".
                         format(source_file))

    # ----------------------------------------------------------------------- #
    # Get information on the source file:
    #   - Alphabet and weight of each symbol from the alphabet
    # ----------------------------------------------------------------------- #
    huff_prob = huffprob.HuffProb(source_file)
    stats = huff_prob.get_stats()

    get_process_time("Get stats")
    # ----------------------------------------------------------------------- #
    # Build the Huffman tree and the prefix-free binary code for each symbol
    # ----------------------------------------------------------------------- #
    huff_tree = hufftree.HuffTree(stats)

    get_process_time("Build HuffTree")
    # ----------------------------------------------------------------------- #
    # Encode the source file using the prefix-free binary code
    # ----------------------------------------------------------------------- #
    codewords = huff_tree.get_codewords()
    buf = BitArray()
    for char in source_file:
        buf += codewords[char]

    # Convert "01101..." BitArray to a bytearray
    encoded_data = buf.tobytes()

    get_process_time("Encode file")
    # ----------------------------------------------------------------------- #
    # Create the output file:
    #   - Add a header with the tree and symbol list
    #   - Add the encoded data
    # ----------------------------------------------------------------------- #
    tree_struct = huff_tree.get_bitstring_struct()
    tree_symbols = huff_tree.get_symbols()

    header = tree_struct.tobytes()
    header += bytearray(''.join(tree_symbols).encode('utf-8'))

    get_process_time("Build header")

    dest_filepath = "{}.huf".format(os.path.splitext(source_filepath)[0])
    dest_file = open(dest_filepath, "wb")
    dest_file.write(header + encoded_data)
    dest_file.close()

    get_process_time("Write .huf file")
    # ----------------------------------------------------------------------- #
    # Performance report
    # ----------------------------------------------------------------------- #
    source_size = os.path.getsize(source_filepath)
    dest_size = os.path.getsize(dest_filepath)
    rate = 1 - (dest_size / source_size)

    logging.info("{} ({}b) -> {} ({}b)".format(source_filepath,
                                               source_size,
                                               dest_filepath,
                                               dest_size
                                               ))
    logging.info("Compression rate: {:.2%}".format(rate))


def extract(source_filepath, dest):

    try:
        source_file = open(source_filepath, "rb").read()
    except IOError as e:
        logging.critical("I/O error({}): {}".format(e.errno, e.strerror))

    # ----------------------------------------------------------------------- #
    # Build the Huffman tree and the prefix-free binary code for each symbol
    # ----------------------------------------------------------------------- #

    huff_tree = hufftree.HuffTree(filepath=source_filepath)
    header_size = huff_tree.get_header_size()

    char_list_size = huff_tree.set_leaves_symbol(source_file[header_size:])
    get_process_time("ReBuild HuffTree")

    data = source_file[header_size + char_list_size:]

    data_bin = BitArray(data)
    decoded_str = binstr2symbols(huff_tree, data_bin)
    get_process_time("Decode data")

    dest_filepath = "{}_decoded.txt".\
                    format(os.path.splitext(source_filepath)[0])
    dest_file = open(dest_filepath, "w")
    dest_file.write(decoded_str)
    dest_file.close()
    logging.info("Decoding succeed: {} !!!".format(dest_filepath))


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


def get_process_time(prefix):
    global start_time
    logging.debug("{}: {:.2} seconds".format(prefix, time.time() - start_time))
    start_time = time.time()

if __name__ == '__main__':
    main()
