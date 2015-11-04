#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class HuffParser():

    """ Compute (symbol, occurence) list needed to build Huffman tree"""

    def __init__(self, source="", sample_len=None):
        self.source = source
        self.sample_len = sample_len

    def get_stats(self):
        if self.sample_len:
            return [(x, self.source.count(x))
                    for x in set(self.source[:self.sample_len])
                    ]
        else:
            return [(x, self.source.count(x))
                    for x in set(self.source)
                    ]
