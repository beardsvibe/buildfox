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
		if outcome:
			return income, outcome
		else:
			return income

	processed_income = []
	parsed_map = {}
	for filename in income:
		if filename.startswith("r\""):
			print("TODO regex")
		elif "*" in filename or "?" in filename or "[" in filename:
			regex_text = translate(filename)
			regex = re.compile(regex_text)
			files = set(glob(filename)).union(set(fnmatch.filter(generated_files, filename)))
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

auto_rules = {} # name: (inputs, outputs)

# ninja escaping functions
# "$\n" = "\n"
# "$ " = " "
# "$:" = ":"
# "$$" = "$"
def to_esc(str, escape_space = True):
	str = str.replace("\n", "$\n")
	#str = str.replace("$", "$$").replace(":", "$:").replace("\n", "$\n")
	#if escape_space:
	#	str = str.replace(" ", "$ ")
	## TODO this is (facepalm) solution for variable escaping, fix it !
	#def repl(matchobj):
	#	return "${" + (matchobj.group(1) or matchobj.group(2)) + "}"
	#str = re.sub("\$\${([a-zA-Z0-9_.-]+)}|\$\$([a-zA-Z0-9_-]+)", repl, str)
	return str
def from_esc(str):
	#return str.replace("$\n", "").replace("$ ", " ").replace("$:", ":").replace("$$", "$")
	return str.replace("$\n", "")
def to_esc2(s):
	if not s:
		return None
	if type(s) is str:
		s = s.replace("$", "$$").replace(":", "$:").replace("\n", "$\n").replace(" ", "$ ")
		def repl(matchobj):
			return "${" + (matchobj.group(1) or matchobj.group(2)) + "}"
		s = re.sub("\$\${([a-zA-Z0-9_.-]+)}|\$\$([a-zA-Z0-9_-]+)", repl, s)
		return s
	else:
		return [to_esc2(str) for str in s]
def from_esc2(s):
	if not s:
		return None
	if type(s) is str:
		return s.replace("$\n", "").replace("$ ", " ").replace("$:", ":").replace("$$", "$")
	else:
		return [from_esc2(str) for str in s]

re_eval2 = True
def evaluate_text(text):
	global re_eval2
	re_eval2 = True
	def repl(matchobj):
		global re_eval2
		name = matchobj.group(1) or matchobj.group(2)
		if name in variable_scope:
			re_eval2 = True
			return variable_scope.get(name)
		else:
			return "${" + name + "}"
	while re_eval2:
		re_eval2 = False
		text = re.sub("\${([a-zA-Z0-9_.-]+)}|\$([a-zA-Z0-9_-]+)", repl, text)
	return text

def get_vars(expr):
	arr = []
	for var in expr.get("vars"):
		val = from_esc(var.get("value"))
		val = evaluate_text(val)
		arr.append("  %s = %s\n" % (var.get("assign"), to_esc(val, escape_space = False)))
	return "".join(arr)
def do_expr(expr):
	if "assign" in expr:
		variable_scope[expr.get("assign")] = expr.get("value")
		# TODO probably not needed
		#return "%s = %s\n" % (expr.get("assign"), expr.get("value"))
		return ""
	elif "rule" in expr:
		return "rule %s\n%s" % (expr.get("rule"), get_vars(expr))
	elif "build" in expr:
		targets = from_esc2(expr.get("targets_explicit"))
		fox_inputs = from_esc2(expr.get("inputs_explicit"))
		
		fox_inputs = [evaluate_text(text) for text in fox_inputs] if fox_inputs else None
		targets = [evaluate_text(text) for text in targets] if targets else None

		wildcard_target = False
		for target in targets:
			if target.startswith("r\"") or "*" in target or "?" in target or "[" in target:
				wildcard_target = True

		inputs, outputs = get_paths(fox_inputs, targets)
		#pprint(inputs)
		#pprint(outputs)
		
		inputs_implicit = get_paths(from_esc2(expr.get("inputs_implicit")))
		inputs_order = get_paths(from_esc2(expr.get("inputs_order")))
		inputs_implicit = [evaluate_text(text) for text in inputs_implicit] if inputs_implicit else None
		inputs_order = [evaluate_text(text) for text in inputs_order] if inputs_order else None
		add_inputs = ""
		if inputs_implicit:
			add_inputs += " | " + " ".join(to_esc2(inputs_implicit))
		if inputs_order:
			add_inputs += " | " + " ".join(to_esc2(inputs_order))

		build = expr.get("build")

		# magic
		if build == "auto":
			inputs_set = set(inputs) if inputs else set()
			outputs_set = set(outputs)
			name_set = False
			for name, val in auto_rules.items():
				fail = False
				for v in val[0]:
					if v.startswith("r\""):
						print("TODO regex")
					elif "*" in v or "?" in v or "[" in v:
						if not fnmatch.filter(inputs_set, v):
							fail = True
							break
					else:
						if v not in inputs_set:
							fail = True
							break
				for v in val[1]:
					if v.startswith("r\""):
						print("TODO regex")
					elif "*" in v or "?" in v or "[" in v:
						if not fnmatch.filter(outputs_set, v):
							fail = True
							break
					else:
						if v not in outputs_set:
							fail = True
							break
				if not fail:
					build = name
					name_set = True
					break
			
			if not name_set:
				print("Cant figure out build rule for : ")
				pprint(expr)

		if wildcard_target and len(inputs) == len(outputs):
			output = ""
			for i, input in enumerate(inputs):
				output += "build %s: %s %s%s\n" % (to_esc2(outputs[i]), build, to_esc2(inputs[i]), add_inputs)
				output += get_vars(expr)
			return output
		else:
			output = "build %s: %s" % (" ".join(to_esc2(outputs)), build)
			if inputs:
				output += " " + " ".join(to_esc2(inputs))
			return "%s%s\n%s" % (output, add_inputs, get_vars(expr))
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
			# TODO probably not needed
			#output += "%s = %s\n" % (var.get("assign"), var.get("value"))
		return output
	elif "auto" in expr:
		auto_rules[expr.get("auto")] = (expr.get("inputs"), expr.get("targets"))
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

output_text = do_file(os.path.dirname(os.path.abspath(__file__)) + "/fox_core.fox") + "\n"
output_text += do_file(args.get("in"))

if args.get("out"):
	with open(args.get("out"), "w") as f:
		f.write(output_text)
else:
	print(output_text)
