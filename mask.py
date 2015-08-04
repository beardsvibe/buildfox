# mask infrastructure console tool

import os
import argparse
from lib import from_mask, from_ninja
from lib import to_mask, to_shell, to_ninja

argsparser = argparse.ArgumentParser(description = "mask build infrastructure")
argsparser.add_argument("input", help = "input file")
argsparser.add_argument("output", help = "output file")
argsparser.add_argument("--verbose", action = "store_true", help = "verbose output")
argsparser.add_argument("--variation", help = "sets project variation for some exporters, for example debug")
args = vars(argsparser.parse_args())

verbose = args.get("verbose")
variation = args.get("variation")
in_file = args["input"]
out_file = args["output"]
in_ext = os.path.splitext(in_file)[1]
out_ext = os.path.splitext(out_file)[1]

ir = None

# import
if in_ext == ".mask":
	if verbose:
		print("trying to parse mask file " + in_file)
	ir = from_mask.from_file(in_file)
elif in_ext == ".ninja":
	if verbose:
		print("trying to parse ninja file " + in_file)
	ir = from_ninja.from_file(in_file)

# do some processing
#if verbose:
	#print("parsed ir : ")
	#print(ir)

# export
if out_ext == ".mask":
	if verbose:
		print("trying to save mask file " + out_file)
	to_mask.to_file(out_file, ir)
elif out_ext == ".sh" or out_ext == ".bat":
	if verbose:
		print("trying to save shell script file " + out_file)
	to_shell.to_file(out_file, ir, variation)
elif out_ext == ".ninja":
	if verbose:
		print("trying to save ninja manifest file " + out_file)
	to_ninja.to_file(out_file, ir, variation)
