# -*- coding: utf-8 -*-

# Copyright 2011 Mats Ekberg
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import with_statement

from common import *

class BlockChecksum:
    def __init__(self, window_size):
        self.buffer = ""
        self.window_size = window_size
        self.position = 0
        self.blocks = []

    def feed_string(self, s):
        self.buffer += s
        while len(self.buffer) >= self.window_size:
            block = self.buffer[0:self.window_size]
            block_sha256 = sha256(block)
            self.blocks.append((self.position, sum(map(ord, block)), block_sha256))
            self.position += self.window_size
            self.buffer = self.buffer[self.window_size:]
            

class RollingChecksum:
    def __init__(self, window_size):
        self.sum = 0
        self.buffer = []
        self.window_size = window_size
        self.position = 0

    def feed_string(self, s):
        for c in s:
            yield self.feed_byte(ord(c))

    def feed_byte(self, b):
        assert type(b) == int and b <= 255 and b >= 0
        self.buffer.append(b)
        self.sum += b
        if len(self.buffer) == self.window_size + 1:
            self.sum -= self.buffer[0]
            self.position += 1
            self.buffer.pop(0)
            result = self.position, self.sum
        elif len(self.buffer) < self.window_size: 
            result = None
        elif len(self.buffer) == self.window_size: 
            result = self.position, self.sum
        else:
            assert False, "Unexpected buffer size"
        return result

def self_test():
    rs = RollingChecksum(3)
    result = list(rs.feed_string([chr(x) for x in range(1,10)]))
    assert result == [None, None, (0, 6), (1, 9), (2, 12), (3, 15), (4, 18), (5, 21), (6, 24)]

    bs = BlockChecksum(3)
    bs.feed_string("".join([chr(x) for x in range(1,10)]))
    assert bs.blocks == [(0, 6, '039058c6f2c0cb492c533b0a4d14ef77cc0f78abccced5287d84a1a2011cfb81'), 
                         (3, 15, '787c798e39a5bc1910355bae6d0cd87a36b2e10fd0202a83e3bb6b005da83472'), 
                         (6, 24, '66a6757151f8ee55db127716c7e3dce0be8074b64e20eda542e5c1e46ca9c41e')]

self_test()

"""
import sys
rs = RollingChecksum(100)
for block in file_reader(sys.stdin):
    print len(block)
    rs.feed_string(block)
"""
