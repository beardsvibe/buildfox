# ------------------------------------ parsing helper

# this parser is just shitty prototype
# it doesn't report errors, slow, etc
# TODO create proper parser !

import re
from lib.maskfile import from_esc, from_esc_iter, Var, Rule, Build, Project, ReadOnlyIR

class Parse:
	def __init__(self):
		self.ir = ReadOnlyIR()
		self.mode = 0 # 0 - variables, 1 - rules, 2 - builds, 3 - projects
		self.variables = {} # dict of key = var name string, value Var
		self.last_rule = ""
		self.last_project = ""
		self.last_comment = ""

	def parse_comment(self, line):
		self.last_comment = line[1:]

	def expand_vars(self, string, scope_rule = False, scope_project = False):
		scope = {}
		# figure out scope, dict(a, **b) will create union where b elements are preferred
		if scope_rule:
			scope = dict(self.variables, **self.ir.rules[self.last_rule].variables)
		elif scope_project:
			scope = dict(self.variables, **self.ir.projects[self.last_project].variables)
		else:
			scope = self.variables

		def repl(matchobj):
			name = matchobj.group(1)
			if name in ["in", "out", "in_newline"]:
				return "${" + name + "}"
			elif name in scope:
				return scope[name].value
			else:
				return ""
		string = re.sub("\${([a-zA-Z0-9_.-]+)}", repl, string)

		return string

	def parse_var(self, line, add = True):
		name, value = line.split(" = ", 1)
		var = Var(name, value = from_esc(value), comment = self.last_comment)

		if add: # add if needed
			var.value = self.expand_vars(var.value)
			self.variables[var.name] = var
			#print("added " + str(var))
		return var

	def parse_rule(self, line):
		if line.startswith("  "):
			var = self.parse_var(line[2:], add = False)
			var.value = self.expand_vars(var.value, scope_rule = True)
			self.ir.rules[self.last_rule].variables[var.name] = var
			#print("added " + str(var))
		else:
			rule = Rule(line[len("rule "):], comment = self.last_comment)
			self.ir.rules[rule.name] = rule
			self.last_rule = rule.name
			#print("added " + str(rule))

	def parse_path_string(self, string):
		paths = re.split("(?<!\$) +", string) # split by non escaped space
		paths = filter(len, paths) # remove empty elements from list
		paths = from_esc_iter(paths)
		paths = [self.expand_vars(s) for s in paths]
		return paths

	def parse_build(self, line):
		line = line[len("build "):]
		build = Build(comment = self.last_comment)

		regex = "\|\|?|(?<!\$):|$"
		arr = re.split(regex, line)
		colon = False
		mode = 0

		for i, f in enumerate(re.finditer(regex, line)):
			sep = f.group(0)
			paths = self.parse_path_string(arr[i])

			if colon:
				if mode == 0:
					build.rule = paths[0]
					build.inputs_explicit = paths[1:]
				elif mode == 1:
					build.inputs_implicit = paths
				elif mode == 2:
					build.inputs_order = paths

				if sep == ":":
					raise ValueError("only one : is valid")
				elif sep == "|":
					mode = 1
				elif sep == "||":
					mode = 2
			else:
				if mode == 0:
					build.targets_explicit = paths
				elif mode == 1:
					build.targets_implicit = paths

				if sep == ":":
					colon = True
					mode = 0
				elif sep == "|":
					mode = 1
				elif sep == "||":
					raise ValueError("|| in targets is invalid")

		self.ir.builds.append(build)
		#print("added " + str(build))

	def parse_project(self, line):
		if line.startswith("  "):
			name, value = line[2:].split(" = ", 1)
			paths = self.parse_path_string(value)
			self.ir.projects[self.last_project].variations[name] = paths
			#print("added " + name + " = " + paths)
		else:
			project = Project(line[len("project "):], comment = self.last_comment)
			self.ir.projects[project.name] = project
			self.last_project = project.name
			#print("added " + str(project))

	def parse(self, line):
		if line.startswith("#"): # read comment
			self.parse_comment(line)
		else:
			if self.mode == 0:
				if line.startswith("rule "):
					self.mode = 1
					self.parse_rule(line)
				elif line.startswith("build "):
					self.mode = 2
					self.parse_build(line)
				elif line.startswith("project "):
					self.mode = 3
					self.parse_project(line)
				else:
					self.parse_var(line)
			elif self.mode == 1:
				if line.startswith("build "):
					self.mode = 2
					self.parse_build(line)
				elif line.startswith("project "):
					self.mode = 3
					self.parse_project(line)
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
			self.last_comment = ""

# ------------------------------------ IO functions

def from_string(text):
	p = Parse()
	line = ""
	for fileline in text.split("\n"):
		line += fileline
		# join with previous line to parse $\n case, mind $$\n case
		if fileline.endswith("$") and not fileline.endswith("$$"):
			line += "\n"
			continue
		if len(line):
			p.parse(line)
			line = ""
	return p.ir

def from_file(filename):
	with open(filename, "r") as f:
		return from_string(f.read())
