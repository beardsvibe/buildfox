# mask infrastructure console tool

import os
import argparse
from lib import from_mask, from_ninja, from_shell
from lib import to_mask, to_shell, to_ninja, to_msvc, to_qmake

parsers = {
	".mask":	from_mask.from_file,
	".ninja":	from_ninja.from_file,
	".sh":	from_shell.from_file,
	".bat":	from_shell.from_file
}

generators = {
	".mask":	to_mask.to_file,
	".sh":		to_shell.to_file,
	".bat":		to_shell.to_file,
	".ninja":	to_ninja.to_file,
	".sln":		to_msvc.to_file,
	".pro":		to_qmake.to_file
}

argsparser = argparse.ArgumentParser(description = "mask build infrastructure")
argsparser.add_argument("input", help = "input file")
argsparser.add_argument("output", help = "output file")
argsparser.add_argument("--verbose", action = "store_true", help = "verbose output")
argsparser.add_argument("--variation", help = "sets project variation for some exporters, for example debug")
args = vars(argsparser.parse_args())

in_file = args["input"]
out_file = args["output"]
in_ext = os.path.splitext(in_file)[1]
out_ext = os.path.splitext(out_file)[1]

out_path = os.path.dirname(out_file)

if in_ext not in parsers:
	raise ValueError("unknown input extension " + in_ext)
if out_ext not in generators:
	raise ValueError("unknown output extension " + out_ext)

ir = parsers[in_ext](in_file)

if not os.path.isdir(out_path):
	os.mkdir(out_path)

generators[out_ext](out_file, ir, args)
