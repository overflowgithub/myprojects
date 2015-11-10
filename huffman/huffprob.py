#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class HuffProb():

    def __init__(self, source):
        self.source = source

    def get_stats(self):
        """ Compute (symbol, weight) tuples list (not sorted)
            For text file: symbol=char, weight=occurence """

        assert self.source, "Assertion - source file is empty"

        return [(x, self.source.count(x))
                for x in set(self.source)
                ]
