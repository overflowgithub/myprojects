#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class HuffNode():

    """Simple Node class for data structure"""

    def __init__(self, name="", count=0, code=""):
        self.children = []
        self.name = name
        self.count = count
        self.code = code

    def add(self, child):
        self.children.append(child)

    def disp(self, depth=0):
        print("{0}{1.name}, {1.count}, {1.code}".format("  " * depth, self))
        for child in self.children:
            child.disp(depth + 1)

    def setCode(self, parent_code=""):
        self.code = parent_code
        if len(self.children) > 1:
            self.children[0].setCode(self.code + '0')
            self.children[1].setCode(self.code + '1')

    def isLeaf(self):
        if self.children:
            return False
        else:
            return True
