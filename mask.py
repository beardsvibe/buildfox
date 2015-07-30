# mask infrastructure console tool

import os
import argparse
from lib import maskfile_parser, maskfile_writer

argsparser = argparse.ArgumentParser(description = "mask build infrastructure")
argsparser.add_argument("input", help = "input file")
argsparser.add_argument("output", help = "output file")
argsparser.add_argument("--verbose", action = "store_true", help = "verbose output")
args = vars(argsparser.parse_args())

verbose = args["verbose"]
in_file = args["input"]
out_file = args["output"]
in_ext = os.path.splitext(in_file)[1]
out_ext = os.path.splitext(out_file)[1]

ir = None

# import
if in_ext == ".mask":
	if verbose:
		print("trying to parse mask file " + in_file)
	ir = maskfile_parser.from_file(in_file)

if verbose:
	print("parsed ir : ")
	print(ir)

# export
if out_ext == ".mask":
	if verbose:
		print("trying to save mask file " + out_file)
	ir = maskfile_writer.to_file(out_file, ir)
