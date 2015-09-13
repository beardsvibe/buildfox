# BuildFox proof of concept (POC)

from pprint import pprint
import os
import argparse
from fox_parser import fox_Parser
import string

# ----------------------------------------------------------- args
argsparser = argparse.ArgumentParser(description = "buildfox ninja generator")
argsparser.add_argument("-i", "--in", help = "input file", required = True)
argsparser.add_argument("-o", "--out", help = "output file")
argsparser.add_argument("-w", "--workdir", help = "working directory, root folder for file lookup")
argsparser.add_argument("-d", "--define", nargs = 2, help = "define var value")
argsparser.add_argument("-v", "--verbose", action = "store_true", help = "verbose output")
args = vars(argsparser.parse_args())

#pprint(args)

verbose = args.get("verbose", False)

if args.get("workdir"):
	os.chdir(args.get("workdir"))

# ----------------------------------------------------------- parsing
def do_file(filename):
	with open(filename, "r") as f:
		input_text = f.read()
		parser = fox_Parser(parseinfo = False)
		ast = parser.parse(input_text, "manifest", trace = False, whitespace = string.whitespace, nameguard = True)

		pprint(ast)

	return "hello there"

output_text = do_file(args.get("in"))

if args.get("out"):
	with open(args.get("out"), "w") as f:
		f.write(output_text)
