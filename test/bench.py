import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

import cProfile
from canoser import *
import pdb

def bench_int_decode():
    for _i in range(553000):
        x1 = Uint32.decode_bytes(b"\x12\x34\x56\x78")
        x2 = Uint32.decode_bytes2(b"\x12\x34\x56\x78")
        assert x1 == x2

cProfile.run('bench_int_decode()', sort='cumtime')