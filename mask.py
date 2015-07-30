# mask infrastructure console tool

import lib

print("hello there")

lib.maskfile.from_string(
"""
a = b
c = d
rule e
  k1 = v1
  k2 = v2
""")
