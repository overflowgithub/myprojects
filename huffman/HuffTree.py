#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import HuffNode as huffnode


class HuffTree():

    """Tree class huffman oriented"""

    def __init__(self, stats=None, struct=""):
        self.root = None
        if stats:
            self.tmp = [huffnode.HuffNode(name=char, count=count)
                        for char, count in stats]
            self.buildTree()
        else:
            if struct:
                self.builTreeStr(struct)

    def SetLeafName(self, data):
        """ from utf-8 data, set each leaf name with corresponding char """
        data_decode = data.decode('utf-8', 'ignore')
        idx = 0
        buf = ""
        for leaf in self.getLeafs():
            leaf.name = data_decode[idx]
            buf += data_decode[idx]
            idx += 1

        return len(bytearray(buf.encode('utf-8')))

    def getLastUncompletedNode(self):
        parent = self.root
        for node in self.parse():
            if len(node.children) == 2:
                return parent
            else:
                parent = node

    def builTreeStr(self, struct):
        self.root = huffnode.HuffNode(name="root")

        current = self.root
        for x in struct[1:]:
            if x == '0':
                # Create a node
                current.add(huffnode.HuffNode("Node"))
                current = current.children[-1]
            if x == '1':
                # Create a leaf
                current.add(huffnode.HuffNode("Leaf"))
                if len(current.children) == 2:
                    current = self.getLastUncompletedNode()

    def buildTree(self):
        """ Create the huffman tree """
        while len(self.tmp) > 1:
            parent = huffnode.HuffNode(
                "{}{}".format(self.tmp[0].name, self.tmp[1].name),
                self.tmp[0].count + self.tmp[1].count)

            parent.add(self.tmp.pop(0))
            parent.add(self.tmp.pop(0))

            self.tmp.insert(0, parent)
            # TODO: sort by count then
            # alphabetical order to always have the same tree
            self.tmp.sort(key=lambda x: x.count)

        self.root = self.tmp[0]
        self.root.code = ""

    def setCode(self, parent_code=""):
        self.root.setCode()

    def getLeafs(self):
        queue = [self.root]
        while queue:
            if not queue[0].children:
                yield queue[0]
            expansion = queue[0].children
            queue = expansion + queue[1:]

    def disp(self, depth=0):
        self.root.disp(1)

    def parse(self):
        """ Parse the whole tree, depth first """
        queue = [self.root]
        while queue:
            yield queue[0]
            expansion = queue[0].children
            queue = expansion + queue[1:]

    def getTreeStruct(self):
        """ return a unique string describing the tree
            The tree is parse (depth first). A node is coded as '0',
            a leaf as '1' """
        struct = ""
        char_table = ""
        for node in self.parse():
            if node.isLeaf():
                struct += '1'
                char_table += node.name
            else:
                struct += '0'

        return (struct, char_table)
