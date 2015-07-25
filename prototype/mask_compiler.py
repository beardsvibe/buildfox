# mask compiler
# accepts mask IR, generates list of shell commands with dependency information

from pprint import pprint
import re

import mask_ir

text = """
d = k
k = $d
rule test
  command = abc $in $out $k
  e = f

# test

build a.txt:test b.txt
#  lol = wow
#  lol2 = wow2
e = d
build c.txt:test d.txt

"""

class Namescope:
	def __init__(self):
		self.vars = []
		self.rules = []
		self.builds = []

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
		for var in vars:
			if name == var["to"]:
				return var
		raise ValueError("cant find var in scope " + name)

	def get_var_value(self, vars, name, lookup = []):
		var = self.get_var_in_scope(vars, name)
		val = var["val"]

		sub_vars = re.finditer("\$([a-zA-Z0-9_.-]+)", val)

		for sub_var in reversed(list(sub_vars)):
			name = sub_var.group(1)
			if name in lookup:
				raise ValueError("recursive lookup for " + name + " with lookup stack " + str(lookup))
			sub_val = self.get_var_value(vars, name, lookup + [name])
			val = val[0:sub_var.start()] + sub_val + val[sub_var.end():]

		return val


	def compile(self):
		for build in self.builds:
			print(build)

			rule = self.get_rule(build["build"]["rule_name"])

			vars = []
			vars.extend(self.vars[:rule["var_index"]])

			if build["build"]["vars"]: # you need to evaluate them with build var_index scope
				print("probably this doesn't work fully yet")
				vars.extend(build["build"]["vars"])

			vars.append({"to": "in", "val": " ".join(build["build"]["inputs"])})
			vars.append({"to": "out", "val": " ".join(build["build"]["outputs"])})
			vars.extend(rule["rule"]["vars"])

			cmd = self.get_var_value(vars, "command")
			print(cmd)

namescope = Namescope()
parser = mask_ir.mask_ir_Parser()
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