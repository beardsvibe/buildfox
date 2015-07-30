# mask infrastructure console tool

import lib

z = lib.maskfile_parser.from_string(
"""
a = b
c = ${a}
d = k${c}${c}
k2 = z
# test
rule e
  k1 = v1${d}
  k2 = v2
build t1 t2 | t3 t4$ $: : r i1 i2 | i3 i4$ $: || i5 i6$ $$
build t1${d} ${a} :r t3
project test
  k2 = k
  k1 = z${k2}
""")

print(z)

#a = lib.maskfile.Var("name", "value ${test} $ : \n test")
#print(a)