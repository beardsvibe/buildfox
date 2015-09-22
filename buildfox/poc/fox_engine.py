# fox engine

import os, re, copy
from fox_parser2 import Parser
from pprint import pprint

core_file = "fox_core.fox"
re_var = re.compile("\${([a-zA-Z0-9_.-]+)}|\$([a-zA-Z0-9_-]+)")
re_folder_part = re.compile(r"(?:[^\r\n(\[\"/\\]|\\.)+") # match folder part in filename regex

workdir = os.getcwd()
output = ["# generated with love by buildfox"]

def rel_dir(filename):
	return os.path.relpath(os.path.dirname(os.path.abspath(filename)), workdir) + "/"

def wildcard_regex(filename):
	if filename.startswith("r\""):
		return filename[2:-1] # strip r" and "
	elif "*" in filename or "?" in filename or "[" in filename:
		# based on fnmatch.translate with each wildcard is a capture group
		i, n = 0, len(filename)
		res = ""
		while i < n:
			c = filename[i]
			i = i + 1
			if c == "*":
				res = res + "(.*)"
			elif c == "?":
				res = res + "(.)"
			elif c == "[":
				j = i
				if j < n and filename[j] == "!":
					j = j + 1
				if j < n and filename[j] == "]":
					j = j + 1
				while j < n and filename[j] != "]":
					j = j + 1
				if j >= n:
					res = res + "\\["
				else:
					stuff = filename[i:j].replace("\\", "\\\\")
					i = j + 1
					if stuff[0] == "!":
						stuff = "^" + stuff[1:]
					elif stuff[0] == "^":
						stuff = "\\" + stuff
					res = "%s([%s])" % (res, stuff)
			else:
				res = res + re.escape(c)
		return res #+ "\Z(?ms)" # TODO do we need that ?
	else:
		return None

class Engine:
	def __init__(self, parent = None):
		if not parent:
			self.variables = {} # name: value
			self.auto_presets = {} # name: (inputs, outputs, assigns)
			self.rel_path = "" # this should be prepended to all parsed paths
		else:
			self.variables = copy.copy(parent.variables)
			self.auto_presets = copy.copy(parent.auto_presets)
			self.rel_path = parent.rel_path
		self.need_eval = False

	# load manifest
	def load(self, filename):
		self.rel_path = rel_dir(filename)
		parser = Parser(self, filename)
		parser.parse()

	# load core definitions
	def load_core(self):
		self.load(core_file)

	# TODO what we do with from_esc / to_esc ? now text are just passing without escaping
	def eval(self, text):
		def repl(matchobj):
			name = matchobj.group(1) or matchobj.group(2)
			if name in self.variables:
				self.need_eval = True
				return self.variables.get(name)
			else:
				return "${" + name + "}"
		self.need_eval = len(text) > 0
		while self.need_eval:
			self.need_eval = False
			text = re_var.sub(repl, text)
		return text

	# input can be string or list of strings
	# outputs are always lists
	def eval_path(self, inputs, outputs = None):
		# TODO
		# TODO we also need to prepend relative manifest location
		
		if inputs:
			result = []
			for input in inputs:
				regex = wildcard_regex(input)
				if regex:
					base_folder = re_folder_part.match(regex)
					if base_folder:
						base_folder = base_folder.group().replace("\\\\", "/").replace("\\/", "/")
						base_folder = os.path.dirname(base_folder)
					else:
						base_folder = ""

					print(base_folder)
				
				else:
					result.append(input)
			inputs = result

		if outputs:
			return inputs, outputs
		else:
			return inputs

	def eval_auto(self, inputs, outputs):
		# TODO
		return "auto", []

	def eval_filter(self, name, value):
		# TODO
		return True

	def write_assigns(self, assigns):
		for assign in assigns:
			name = self.eval(assign[0])
			value = self.eval(assign[1])
			output.append("  %s = %s" % (name, value))

	def rule(self, obj, assigns):
		name = self.eval(obj)
		output.append("rule " + name)
		self.write_assigns(assigns)

	def build(self, obj, assigns):
		inputs_explicit, targets_explicit = self.eval_path(obj[3], obj[0])
		targets_implicit = self.eval_path(obj[1])
		rule_name = self.eval(obj[2])
		inputs_implicit = self.eval_path(obj[4])
		inputs_order = self.eval_path(obj[5])

		if rule_name == "auto":
			name, vars = self.eval_auto(inputs_explicit, targets_explicit)
			rule_name = name
			assigns = vars + assigns

		output.append("build %s: %s%s%s%s" % (
			" ".join(targets_explicit),
			rule_name,
			" " + " ".join(inputs_explicit) if inputs_explicit else "",
			" | " + " ".join(inputs_implicit) if inputs_implicit else "",
			" || " + " ".join(inputs_order) if inputs_order else "",
		))

		self.write_assigns(assigns)

		if targets_implicit: # TODO remove this when https://github.com/martine/ninja/pull/989 is merged
			output.append("build %s: phony %s" % (
				" ".join(targets_implicit),
				" " + " ".join(targets_explicit),
			))

	def default(self, obj, assigns):
		paths = self.eval_path(obj)
		output.append("default " + " ".join(paths))
		self.write_assigns(assigns)

	def pool(self, obj, assigns):
		name = self.eval(obj)
		output.append("pool " + name)
		self.write_assigns(assigns)

	def filter(self, obj):
		for filt in obj:
			name = self.eval(filt[0])
			value = self.eval(filt[1])
			if not self.eval_filter(name, value):
				return False
		return True

	def auto(self, obj, assigns):
		outputs = [self.eval(output) for output in obj[0]] # this shouldn't be eval_path !
		name = self.eval(obj[1])
		inputs = [self.eval(input) for input in obj[2]] # this shouldn't be eval_path !
		self.auto_presets[name] = (inputs, outputs, assigns) # TODO do we need to eval vars here ?

	def assign(self, obj):
		name = self.eval(obj[0])
		value = obj[1]
		self.variables[name] = value

	def include(self, obj):
		path = self.eval_path(obj)
		old_rel_path = self.rel_path
		self.rel_path = rel_dir(filename)
		parser = Parser(self, path)
		parser.parse()
		self.rel_path = old_rel_path

	def subninja(self, obj):
		path = self.eval_path(obj)
		engine = Engine(self)
		engine.load(path)
		# TODO we need namescope for rules, pools, auto

engine = Engine()
#engine.load_core()
#engine.load("examples/fox_test.fox")
engine.load("fox_parser_test2.ninja")

print("\n".join(output))