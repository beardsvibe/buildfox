# read write mask ir file

import re
from lib.maskfile_esc import to_esc, to_esc_iter

# ------------------------------------ basic structures

class Var:
	def __init__(self, name = "", value = "", comment = ""):
		self.name = name
		self.value = value
		self.comment = comment

	def __repr__(self):
		return "%s%s = %s" % (
			"#" + self.comment + "\n" if len(self.comment) else "",
			self.name,
			to_esc(self.value, escape_space = False)
		)

class Rule:
	def __init__(self, name = "", variables = {}, comment = ""):
		self.name = name
		self.variables = variables # dict of key = var name string, val = Var
		self.comment = comment

		# TODO
		# possible variables : command depfile deps msvc_deps_prefix description generator restat rspfile rspfile_content

	def __repr__(self):
		return "%srule %s%s" % (
			"#" + self.comment + "\n" if len(self.comment) else "",
			self.name,
			"\n  " + "\n  ".join([v.__repr__() for k, v in self.variables.items()]) if len(self.variables) else ""
		)

	def evaluate(self, name, build):
		def repl(matchobj):
			name = matchobj.group(1)
			if name == "in":
				return " ".join(build.inputs_explicit)
			if name == "out":
				return " ".join(build.targets_explicit)
			if name == "in_newline":
				return "\n".join(build.inputs_explicit)
			else:
				return ""
		return re.sub("\${([a-zA-Z0-9_.-]+)}", repl, self.variables[name].value)

class Build:
	def __init__(self, comment = ""):
		self.targets_explicit = [] # list of strings, sets are slightly slower to iterate over
		self.targets_implicit = []
		self.inputs_explicit = []
		self.inputs_implicit = []
		self.inputs_order = []
		self.rule = ""
		self.comment = comment

	def __repr__(self):
		# TODO fix this mess
		return "%sbuild %s%s:%s %s%s%s" % (
			"#" + self.comment + "\n" if len(self.comment) else "",
			" ".join(to_esc_iter(self.targets_explicit)),
			" | " + " ".join(to_esc_iter(self.targets_implicit)) if len(self.targets_implicit) else "",
			self.rule,
			" ".join(to_esc_iter(self.inputs_explicit)),
			" | " + " ".join(to_esc_iter(self.inputs_implicit)) if len(self.inputs_implicit) else "",
			" || " + " ".join(to_esc_iter(self.inputs_order)) if len(self.inputs_order) else ""
		)

class Project:
	def __init__(self, name = "", comment = ""):
		self.name = name
		self.variations = {} # dict of key = variation name string, val = list of targets
		self.comment = comment

	def __repr__(self):
		variables = [k + " = " + " ".join(to_esc_iter(v)) for k, v in self.variations.items()]
		return "%sproject %s%s" % (
			"#" + self.comment + "\n" if len(self.comment) else "",
			self.name,
			"\n  " + "\n  ".join(variables) if len(self.variations) else ""
		)

# ------------------------------------ read only IR

class ReadOnlyIR:
	def __init__(self):
		self.rules = {}		# dict of key = rule name string, val = Rule
		self.builds = []	# list of Build
		self.projects = {}	# dict of key = project name string, val = Project

	def __repr__(self):
		return "\n".join(filter(len, [
			"\n".join([str(v) for k, v in self.rules.items()]),
			"\n".join([str(v) for v in self.builds]) if len(self.builds) else "",
			"\n".join([str(v) for k, v in self.projects.items()] if len(self.projects) else "")
		]))

# ------------------------------------ write only IR

class WriteOnlyIR:
	def __init__(self):
		self.variables = []	# list of Var
		self.rules = []		# list of Rule
		self.builds = []	# list of Build
		self.projects = []	# list of Project

	def __repr__(self):
		return "\n".join(filter(len, [
			"\n".join([str(v) for v in self.variables]),
			"\n" + "\n".join([str(v) for v in self.rules]) if len(self.rules) else "",
			"\n" + "\n".join([str(v) for v in self.builds]) if len(self.builds) else "",
			"\n" + "\n".join([str(v) for v in self.projects] if len(self.projects) else "")
		]))
