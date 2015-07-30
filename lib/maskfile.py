# read write mask ir file

# ------------------------------------ escaping functions

#$ followed by a newline - escape the newline (continue the current line across a line break).
#$ followed by text a variable reference.
#${varname} alternate syntax for $varname.
#$ followed by space - a space. (This is only necessary in lists of paths, where a space would otherwise separate filenames. See below.)
#$: a colon. (This is only necessary in build lines, where a colon would otherwise terminate the list of outputs.)
#$$ a literal $.

def to_esc(str):
	# TODO how to escape variable reference lol ?
	return str.replace("$", "$$").replace(":", "$:").replace(" ", "$ ").replace("\n", "$\n")

def from_esc(str):
	return str.replace("$\n", "\n").replace("$ ", " ").replace("$:", ":").replace("$$", "$")

def to_esc_iter(iter):
	return [to_esc(s) for s in iter]

def from_esc_iter(iter):
	return [from_esc(s) for s in iter]

# ------------------------------------ basic structures

class Var:
	def __init__(self, name = "", value = ""):
		self.name = name
		self.value = value

	def __repr__(self):
		return "%s = %s" % (self.name, to_esc(self.value))

class Rule:
	def __init__(self, name = "", variables = []):
		self.name = name
		self.variables = variables # array of Var

	def __repr__(self):
		return "rule %s%s" % (
			self.name,
			"\n  " + "\n  ".join([v.__repr__() for v in self.variables]) if len(self.variables) else ""
		)

class Build:
	def __init__(self):
		self.targets_explicit = [] # array of strings, sets are slightly slower to iterate over
		self.targets_implicit = []
		self.inputs_explicit = []
		self.inputs_implicit = []
		self.inputs_order = []
		self.rule = "" # string

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
	def __init__(self):
		self.name = ""
		self.variables = [] # array of Var

	def __repr__(self):
		return "project %s%s" % (
			self.name,
			"\n  " + "\n  ".join([v.__repr__() for v in self.variables]) if len(self.variables) else ""
		)

# ------------------------------------ read only IR

class ReadonlyIR:
	def __init__(self):
		self.rules = {}		# dict of key = rule name string, val = Rule
		self.builds = []	# array of Build
		self.projects = {}	# dict of key = project name string, val = Project

# ------------------------------------ parsing helper

class Parse:
	def __init__(self):
		self.ir = ReadonlyIR()
		self.mode = 0 # 0 - variables, 1 - rules, 2 - builds, 3 - projects
		self.variables = [] # array of Var
		self.last_rule = ""

	def parse_comment(self, line): # don't care
		pass

	def parse_var(self, line, add = True, scope_rule = False, scope_project = False):
		name, value = line.split(" = ", 1)
		var = Var(name, from_esc(value))

		if scope_rule:
			pass
		elif scope_project:
			pass
		else:
			pass

		if add:
			self.variables.append(var)
			print("added " + str(var))
		return var

	def parse_rule(self, line):
		if line.startswith("  "):
			var = self.parse_var(line[2:], add = False)
			self.ir.rules[self.last_rule].variables.append(var)
			print("added " + str(var))
		else:
			rule = Rule(line[len("rule "):])
			self.ir.rules[rule.name] = rule
			self.last_rule = rule.name
			print("added " + str(rule))

	def parse_build(self, line):
		pass

	def parse_project(self, project):
		pass

	def parse(self, line):
		if line.startswith("#"): # read comment
			self.parse_comment(line)
		elif self.mode == 0:
			if line.startswith("rule "):
				self.mode = 1
				self.parse_rule(line)
			else:
				self.parse_var(line)
		elif self.mode == 1:
			if line.startswith("build "):
				self.mode = 2
				self.parse_build(line)
			else:
				self.parse_rule(line)
		elif self.mode == 2:
			if line.startswith("project "):
				self.mode = 3
				self.parse_project(line)
			else:
				self.parse_build(line)
		elif self.mode == 3:
			self.parse_project(line)

# ------------------------------------ IO functions

def from_string(text):
	p = Parse()
	line = ""
	for fileline in text.split("\n"):
		line += fileline
		if fileline.endswith("$"): # join with previous line to parse $\n case
			line += "\n"
			continue
		if len(line):
			p.parse(line)
			line = ""
	return p.ir

def from_file(filename):
	with open(filename, "r") as f:
		return from_string(f.read())

def to_string(ir):
	pass

def to_file(ir, filename):
	with open(filename, "w") as f:
		f.write(to_string(ir))
