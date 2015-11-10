#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from bitstring import BitArray


class HuffNode():

    """Simple Node class for data structure"""

    def __init__(self, name="", count=0):
        self.children = []
        self.name = name
        self.count = count
        self.code = BitArray()

    def add(self, child):
        """ Add a child to self node.
            A huffman node have a maximum of 2 children """
        if not self.is_complete():
            self.children.append(child)
            return True
        else:
            print("Incompatible node. A huffman node have a maximum of 2 children")
            return False

    def disp(self, depth=0):
        print("{0}{1.name}, {1.count}, {2}".format("   " * depth, self, self.code.bin))
        for child in self.children:
            child.disp(depth + 1)

    def set_codewords(self, parent_code=BitArray()):
        self.code = parent_code
        if len(self.children) > 1:
            self.children[0].set_codewords(self.code + [0])
            self.children[1].set_codewords(self.code + [1])

    def is_leaf(self):
        if self.children:
            return False
        else:
            return True

    def is_complete(self):
        if len(self.children) == 2:
            return True
        else:
            return False
