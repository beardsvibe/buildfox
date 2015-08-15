# mask ir file

import re
from lib.mask_esc import to_esc, to_esc_iter, to_esc_shell

# ------------------------------------ basic structures

# variables are based on ninja variables :
# command
# depfile
# deps
# msvc_deps_prefix
# description
# generator
# restat
# rspfile
# rspfile_content

class Build:
	def __init__(self):
		self.targets_explicit = [] # list of unique strings, sets are slightly slower to iterate over
		self.targets_implicit = []
		self.inputs_explicit = []
		self.inputs_implicit = []
		self.inputs_order = []
		self.rule = ""

	def __repr__(self):
		# TODO fix this mess
		return "build %s%s:%s %s%s%s" % (
			" ".join(to_esc_iter(self.targets_explicit)),
			" | " + " ".join(to_esc_iter(self.targets_implicit)) if len(self.targets_implicit) else "",
			self.rule,
			" ".join(to_esc_iter(self.inputs_explicit)),
			" | " + " ".join(to_esc_iter(self.inputs_implicit)) if len(self.inputs_implicit) else "",
			" || " + " ".join(to_esc_iter(self.inputs_order)) if len(self.inputs_order) else ""
		)

class Project:
	def __init__(self, name = "", variations = {}):
		self.name = name
		self.variations = variations # dict of key = variation name string, val = list of targets strings

	def __repr__(self):
		variables = [k + " = " + " ".join(to_esc_iter(v)) for k, v in self.variations.items()]
		return "project %s%s" % (
			self.name,
			"\n  " + "\n  ".join(variables) if len(self.variations) else ""
		)

# ------------------------------------ IR

class IR:
	def __init__(self):
		self.rules = {}		# dict of key = rule name string, val = Rule
		self.builds = []	# list of Build
		self.projects = {}	# dict of key = project name string, val = Project

	def add_rule(self, name, variables):
		self.rules[name] = variables

	def evaluate(self, rule_name, var_name, build):
		def repl(matchobj):
			name = matchobj.group(1)
			if name == "in":
				return " ".join([to_esc_shell(v) for v in build.inputs_explicit] if var_name == "command" else build.inputs_explicit)
			if name == "out":
				return " ".join([to_esc_shell(v) for v in build.targets_explicit] if var_name == "command" else build.targets_explicit)
			if name == "in_newline":
				return "\n".join([to_esc_shell(v) for v in build.inputs_explicit] if var_name == "command" else build.inputs_explicit)
			else:
				return ""
		return re.sub("\${([a-zA-Z0-9_.-]+)}", repl, self.rules[rule_name][var_name])

	def __repr__(self):
		rules = ""
		for k, variables in self.rules.items():
			rules += "rule %s%s\n" % (
				k,
				"\n  " + "\n  ".join(["%s = %s" % (k, to_esc(v, escape_space = False)) for k, v in variables.items()]) if len(variables) else ""
			)

		return "\n".join(filter(len, [
			rules,
			"\n".join([str(v) for v in self.builds]) if len(self.builds) else "",
			"\n".join([str(v) for k, v in self.projects.items()] if len(self.projects) else "")
		]))
