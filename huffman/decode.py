#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse

import HuffTree as hufftree


def str2binstr():
    pass


def main():
    """ Main code to uncompress a .huf file """
    my_argparse = argparse.ArgumentParser(description="Main arg parser")
    my_argparse.add_argument("-i", "--in_file",
                             help="compressed file",
                             type=str)

    args = my_argparse.parse_args()
    source_file = args.in_file

    try:
        txt = open(source_file, "rb").read()
    except IOError as e:
        print("I/O error({}): {}".format(e.errno, e.strerror))

    treeStructSize = txt[0]

    buf = ""
    i = 1
    while len(buf) < treeStructSize:
        buf += str(bin(txt[i]))[2:].rjust(8, '0')
        i += 1

    buf = buf.rstrip('0')
    myTree = hufftree.HuffTree(struct=buf)
    data = txt[i:]

    char_list_size = myTree.SetLeafName(data)
    myTree.setCode()
    print("Hello -----: {}".format(char_list_size))
    data = txt[i+char_list_size:]
    myTree.disp()

    # treeStruct = txt[1:1+treeStructSize/8]
    # treeStruct = ""


if __name__ == '__main__':
    main()