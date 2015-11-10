#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import huffnode
from bitstring import BitArray, Bits


class HuffTree():
    """ Tree class huffman oriented """

    def __init__(self, stats=None, filepath=""):
        """ Huffman tree can be created with a (symbols, weight) tuples list
            or with a binstring description """

        self.root = None

        if stats:
            self.tmp = [huffnode.HuffNode(name=char, count=count)
                        for char, count in stats]
            self._prob2tree()
        elif filepath:
            struct = Bits(filename=filepath)
            n_node = 0
            n_leaf = 0
            while n_leaf < n_node + 1:
                if struct[n_leaf + n_node] == True:
                    n_leaf += 1
                else:
                    n_node += 1

            tree_struct = struct[:n_leaf + n_node]
            self._struct2tree(struct[:n_leaf + n_node])
            self.tree_struct_size = len(tree_struct.tobytes())
        else:
            print("Error - No valid parameters to build HuffTree")

        # Tree is built. prefix code is added to each leaf
        self.set_codewords()

    def _prob2tree(self):
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

    def _struct2tree(self, binstruct):
        """ Create the huffman tree with a Bit describing tree
            A 0 is a node, a 1 is a leaf. As soon as a leaf is reached,
            the binstring continue from the last uncompleted node (parsing
            the tree depth first)
            Note: _struct2tree can be called as long as the tree is not
            complete """

        if not self.root:
            self.root = huffnode.HuffNode(name="root")
            binstruct = binstruct[1:]

        self.struct2tree_rec(self.root, binstruct)

    def struct2tree_rec(self, node, binstruct):
        subtrees = self._get_subtree(binstruct)

        for subtree in subtrees:
            if subtree[0] == True:
                node.add(huffnode.HuffNode("Leaf"))
            else:
                node.add(huffnode.HuffNode("Node"))
                self.struct2tree_rec(node.children[-1], subtree[1:])

    def _get_subtree(self, binstruct):
        n_node = 0
        n_leaf = 0
        while n_leaf < n_node + 1:
            if binstruct[n_leaf + n_node] == True:
                n_leaf += 1
            else:
                n_node += 1

        left_subtree = binstruct[:n_leaf + n_node]
        right_subtree = binstruct[n_leaf + n_node:]

        return [left_subtree, right_subtree]

    def set_codewords(self):
        self.root.set_codewords()

    def disp(self, depth=0):
        self.root.disp(1)

    def _parse(self):
        """ generator returning all nodes, depth first """
        queue = [self.root]
        while queue:
            yield queue[0]
            expansion = queue[0].children
            queue = expansion + queue[1:]

    def get_codewords(self):
        """ return {symbol: codeword} from the tree """
        codewords = {}
        for leaf in self.get_leaves():
            codewords[leaf.name] = leaf.code
        return codewords

    def get_leaves(self):
        queue = [self.root]
        while queue:
            if not queue[0].children:
                yield queue[0]
            expansion = queue[0].children
            queue = expansion + queue[1:]

    def get_bitstring_struct(self):
        """ return a unique BitArray describing the tree
            The tree is _parse (depth first). A node is coded as '0',
            a leaf as '1' """
        struct = BitArray()
        for node in self._parse():
            if node.is_leaf():
                struct += [1]
            else:
                struct += [0]

        return struct

    def get_symbols(self):
        """ get all symbols from tree leaves """
        symbols = []
        for node in self.get_leaves():
            symbols.append(node.name)
        return symbols

    def get_header_size(self):
        return self.tree_struct_size

    def set_leaves_symbol(self, data):
        """ from utf-8 data, set each leaf name with corresponding char """
        data_decode = data.decode('utf-8', 'ignore')
        idx = 0
        buf = ""
        for leaf in self.get_leaves():
            leaf.name = data_decode[idx]
            buf += data_decode[idx]
            idx += 1

        return len(bytearray(buf.encode('utf-8')))
