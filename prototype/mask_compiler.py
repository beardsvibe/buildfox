# mask compiler
# accepts mask IR, generates mask asm - list of shell commands with dependency information

import argparse
from pprint import pprint
import re

import mask_ir_parser

class Namescope:
	def __init__(self):
		self.vars = []
		self.rules = []
		self.builds = []
		self.cmds = []

	def var(self, var):
		self.vars.append(var)

	def rule(self, rule):
		self.rules.append({"var_index": len(self.vars), "rule": rule})

	def build(self, build):
		self.builds.append({"var_index": len(self.vars), "build": build})

	def get_rule(self, name):
		for rule in self.rules:
			if name == rule["rule"]["name"]:
				return rule
		raise ValueError("cant find rule " + name)

	def get_var_in_scope(self, vars, name):
		for var in reversed(vars):
			if name == var["to"]:
				return var
		raise ValueError("cant find var in scope " + name)

	def get_varstr_value(self, vars, val, lookup = []):
		sub_vars = re.finditer("\$([a-zA-Z0-9_.-]+)", val)
		for sub_var in reversed(list(sub_vars)):
			name = sub_var.group(1)
			if name in lookup:
				raise ValueError("recursive lookup for " + name + " with lookup stack " + str(lookup))
			sub_val = self.get_var_value(vars, name, lookup + [name])
			val = val[0:sub_var.start()] + sub_val + val[sub_var.end():]
		return val

	def get_var_value(self, vars, name, lookup = []):
		var = self.get_var_in_scope(vars, name)
		return self.get_varstr_value(vars, var["val"], lookup)

	def compile(self):
		for build in self.builds:
			rule = self.get_rule(build["build"]["rule_name"])
			rule_vars = self.vars[:rule["var_index"]]

			build_vars = self.vars[:build["var_index"]]

			if build["build"]["vars"]:
				build_nested_vars = build["build"]["vars"]
				if build_nested_vars is not list:
					build_nested_vars = [build_nested_vars]
				for var in build_nested_vars:
					rule_vars.append({"to": var["to"], "val": self.get_varstr_value(build_vars, var["val"])})

			inputs = [self.get_varstr_value(build_vars, input) for input in build["build"]["inputs"]]
			outputs = [self.get_varstr_value(build_vars, output) for output in build["build"]["outputs"]]

			rule_vars.append({"to": "in", "val": " ".join(inputs)})
			rule_vars.append({"to": "out", "val": " ".join(outputs)})
			rule_vars.extend(rule["rule"]["vars"])

			cmd = self.get_var_value(rule_vars, "command")
			self.cmds.append({"cmd": cmd, "depend_on": inputs, "touch": outputs})

argsparser = argparse.ArgumentParser(description = "Mask IR compiler, produces mask asm")
argsparser.add_argument("--input", required = True, help = "input mask IR file")
argsparser.add_argument("--output", required = True, help = "output mask asm file")
args = vars(argsparser.parse_args())

with open(args["input"], "r") as f:
	text = f.read()
text += "\n"

namescope = Namescope()
parser = mask_ir_parser.mask_ir_Parser()
ast = parser.parse(text, rule_name = "manifest", whitespace = "")

for expr in ast:
	if "to" in expr:
		namescope.var(expr)
	elif "name" in expr:
		namescope.rule(expr)
	elif "rule_name" in expr:
		namescope.build(expr)
	else:
		print("unknown " + str(expr))

namescope.compile()

pprint(namescope.cmds)

import json
with open(args["output"], "w") as result:
	json.dump(namescope.cmds, result, sort_keys = True, indent = 4)
