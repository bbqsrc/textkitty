#!/usr/bin/env python3

import textkitty
import sys

if len(sys.argv) > 2:
	textkitty.make_profile(open(sys.argv[1]), open(sys.argv[2], 'w'))
else:
	print("Usage:", sys.argv[0], "infile", "outfile")
