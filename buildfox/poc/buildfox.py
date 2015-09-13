# BuildFox proof of concept (POC)

import re
import os
import string
import fnmatch
import argparse
from glob import glob
from pprint import pprint
from fox_parser import fox_Parser

# ----------------------------------------------------------- args
argsparser = argparse.ArgumentParser(description = "buildfox ninja generator")
argsparser.add_argument("-i", "--in", help = "input file", required = True)
argsparser.add_argument("-o", "--out", help = "output file")
argsparser.add_argument("-w", "--workdir", help = "working directory")
argsparser.add_argument("-d", "--define", nargs = 2, help = "define var value", action="append")
argsparser.add_argument("-v", "--verbose", action = "store_true", help = "verbose output")
args = vars(argsparser.parse_args())
#pprint(args)

verbose = args.get("verbose", False)

if args.get("workdir"):
	os.chdir(args.get("workdir"))

# ----------------------------------------------------------- regex/wildcard lookup
generated_files = set()

def translate(pat):
	# based on fnmatch.translate
	# and each wildcard is a capture group now
	i, n = 0, len(pat)
	res = ''
	while i < n:
		c = pat[i]
		i = i+1
		if c == '*':
			res = res + '(.*)'
		elif c == '?':
			res = res + '(.)'
		elif c == '[':
			j = i
			if j < n and pat[j] == '!':
				j = j+1
			if j < n and pat[j] == ']':
				j = j+1
			while j < n and pat[j] != ']':
				j = j+1
			if j >= n:
				res = res + '\\['
			else:
				stuff = pat[i:j].replace('\\','\\\\')
				i = j+1
				if stuff[0] == '!':
					stuff = '^' + stuff[1:]
				elif stuff[0] == '^':
					stuff = '\\' + stuff
				res = '%s([%s])' % (res, stuff)
		else:
			res = res + re.escape(c)
	return res + '\Z(?ms)'

def get_paths(income, outcome = None):
	if not income:
		return income

	processed_income = []
	parsed_map = {}
	for filename in income:
		if filename.startswith("r\""):
			print("TODO regex")
		elif "*" in filename or "?" in filename or "[" in filename:
			regex_text = translate(filename)
			regex = re.compile(regex_text)
			files = glob(filename) + fnmatch.filter(generated_files, filename)
			processed_income.extend(files)
			for file in files:
				obj = regex.match(file)
				parsed_map[file] = obj.groups()
		else:
			processed_income.append(filename)

	if outcome:
		wildcard_files = [val for k, val in parsed_map.items()]

		processed_outcome = []
		for filename in outcome:
			if filename.startswith("r\""):
				print("TODO regex")
			elif "*" in filename or "?" in filename: # TODO [ ?
				for f in wildcard_files:
					out = ""
					group = 0
					for c in filename:
						if c in ["*", "?"]:
							if group < len(f):
								out += f[group]
						else:
							out += c
					processed_outcome.append(out)
			else:
				processed_outcome.append(filename)

		for out in processed_outcome:
			generated_files.add(out)

		return processed_income, processed_outcome
	else:
		return processed_income

# ----------------------------------------------------------- parsing
variable_scope = {}

for d in args.get("define"):
	variable_scope[d[0]] = d[1]

def get_vars(expr):
	arr = []
	for var in expr.get("vars"):
		arr.append("  %s = %s\n" % (var.get("assign"), var.get("value")))
	return " ".join(arr)
def do_expr(expr):
	if "assign" in expr:
		variable_scope[expr.get("assign")] = expr.get("value")
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
	elif "filters" in expr:
		match = True
		for var in expr.get("filters"):
			name = var.get("var")
			val = var.get("value")
			if name in variable_scope:
				val_ref = variable_scope.get(name)
				if val.startswith("r\""):
					print("TODO regex")
				elif "*" in val or "?" in val or "[" in val:
					if not fnmatch.fnmatch(val_ref, val):
						return ""
				elif val != val_ref:
					return ""
			else:
				return ""
		output = ""
		for var in expr.get("vars"):
			variable_scope[var.get("assign")] = var.get("value")
			output += "%s = %s\n" % (var.get("assign"), var.get("value"))
		return output
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

# ----------------------------------------------------------- output generation
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
else:
	print(output_text)
