# rmask ir file

import re
import pipes

# ------------------------------------ escaping functions

#$ followed by a newline - escape the newline (continue the current line across a line break)
#${varname} variable expansion
#$ followed by space - a space
#$: a colon. (This is only necessary in build lines, where a colon would otherwise terminate the list of outputs.)
#$$ a literal $.

# TODO escape for | ?

import re
def to_esc(str, escape_space = True):
	str = str.replace("$", "$$").replace(":", "$:").replace("\n", "$\n")
	
	if escape_space:
		str = str.replace(" ", "$ ")

	# TODO this is (facepalm) solution for variable escaping, fix it !
	def repl(matchobj):
		return "${" + matchobj.group(1) + "}"
	str = re.sub("\$\${([a-zA-Z0-9_.-]+)}", repl, str)
	return str

def from_esc(str):
	return str.replace("$\n", "").replace("$ ", " ").replace("$:", ":").replace("$$", "$")

def to_esc_iter(iter):
	return [to_esc(s) for s in iter]

def from_esc_iter(iter):
	return [from_esc(s) for s in iter]

def to_esc_shell(str):
	# TODO replace with shlex.quote on python 3.3+
	unsafe = ["\"", " "]
	if any(s in str for s in unsafe):
		return "\"" + str.replace(" ", "\\ ").replace("\"", "\\\"") + "\""
	else:
		return str

# ------------------------------------ basic structures

class Rule:
	def __init__(self, name = "", variables = {}, comment = ""):
		self.name = name
		self.variables = variables # dict of key = name string, val = value string
		self.comment = comment

		# TODO
		# possible variables : command depfile deps msvc_deps_prefix description generator restat rspfile rspfile_content

	def __repr__(self):
		return "%srule %s%s" % (
			"#" + self.comment + "\n" if len(self.comment) else "",
			self.name,
			"\n  " + "\n  ".join(["%s = %s" % (k, to_esc(v, escape_space = False)) for k, v in self.variables.items()]) if len(self.variables) else ""
		)

	def evaluate(self, var_name, build):
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
		return re.sub("\${([a-zA-Z0-9_.-]+)}", repl, self.variables[var_name])

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
	def __init__(self, name = "", variations = {}, comment = ""):
		self.name = name
		self.variations = variations # dict of key = variation name string, val = list of targets strings
		self.comment = comment

	def __repr__(self):
		variables = [k + " = " + " ".join(to_esc_iter(v)) for k, v in self.variations.items()]
		return "%sproject %s%s" % (
			"#" + self.comment + "\n" if len(self.comment) else "",
			self.name,
			"\n  " + "\n  ".join(variables) if len(self.variations) else ""
		)

# ------------------------------------ IR

class IR:
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
