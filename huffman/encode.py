#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os.path

from bitstring import BitArray

import huffprob
import hufftree


def main():
    """ Main code to compress a text file """
    huff_arg_parser = argparse.ArgumentParser(description="Main arg parser")
    huff_arg_parser.add_argument("-i", "--in_file",
                                 help="source filepath to compress",
                                 type=str)

    args = huff_arg_parser.parse_args()
    source_filepath = args.in_file
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

if __name__ == '__main__':
    main()
