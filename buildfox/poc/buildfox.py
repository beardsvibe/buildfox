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
def get_paths(income, outcome = None):
	if outcome:
		pprint(income)
		pprint(outcome)
		return income, outcome
	return income

def get_vars(expr):
	for var in expr.get("vars"):
		yield "  %s = %s\n" % (var.get("assign"), var.get("value"))
def do_expr(expr):
	if "assign" in expr:
		return "%s = %s\n" % (expr.get("assign"), expr.get("value"))
	elif "rule" in expr:
		return "rule %s\n%s" % (expr.get("rule"), get_vars(expr))
	elif "build" in expr:
		inputs, outputs = get_paths(expr.get("inputs_explicit"), expr.get("targets_explicit"))
		inputs_implicit = get_paths(expr.get("inputs_implicit"))
		inputs_order = get_paths(expr.get("inputs_order"))
		output = "build %s: %s" % (" ".join(outputs), expr.get("build"))
		if inputs:
			output += " " + " ".join(inputs)
		if inputs_implicit:
			output += " | " + " ".join(inputs_implicit)
		if inputs_order:
			output += " | " + " ".join(inputs_order)
		return "%s\n%s" % (output, get_vars(expr))
	elif "filter" in expr:
		print("TODO support filter")
		pprint(expr)
		return ""
	elif "defaults" in expr:
		return "defaults %s\n" % (" ".join(get_paths(expr.get("defaults"))))
	elif "pool" in expr:
		return "pool %s\n%s" % (expr.get("pool"), get_vars(expr))
	elif "include" in expr:
		print("TODO support include")
		pprint(expr)
		return ""
	elif "subninja" in expr:
		print("TODO support subninja")
		pprint(expr)
		return ""
	else:
		raise ValueError("unknown ast expr " + str(expr))

def do_file(filename):
	with open(filename, "r") as f:
		input_text = f.read()
		parser = fox_Parser(parseinfo = False)
		ast = parser.parse(input_text, "manifest", trace = False, whitespace = string.whitespace, nameguard = True)
		output = ""
		for expr in ast:
			output += do_expr(expr)
		return output

output_text = do_file(args.get("in"))

if args.get("out"):
	with open(args.get("out"), "w") as f:
		f.write(output_text)
