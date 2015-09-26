# fox engine

import os, re, copy
from fox_parser2 import Parser
from pprint import pprint

core_file = "fox_core.fox"
re_var = re.compile("\${([a-zA-Z0-9_.-]+)}|\$([a-zA-Z0-9_-]+)")
re_folder_part = re.compile(r"(?:[^\r\n(\[\"\\]|\\.)+") # match folder part in filename regex
re_capture_group_ref = re.compile(r"(?<!\\)\\(\d)") # match regex capture group reference

workdir = os.getcwd()
output = ["# generated with love by buildfox"]

def rel_dir(filename):
	path = os.path.relpath(os.path.dirname(os.path.abspath(filename)), workdir) + "/"
	if path == "./":
		path = ""
	return path

def wildcard_regex(filename, output = False):
	if filename.startswith("r\""):
		return filename[2:-1] # strip r" and "
	elif "*" in filename or "?" in filename or "[" in filename:
		# based on fnmatch.translate with each wildcard is a capture group
		i, n = 0, len(filename)
		groups = 1
		res = ""
		while i < n:
			c = filename[i]
			i = i + 1
			if c == "*":
				if output:
					res = res + "\\" + str(groups)
					groups += 1
				else:
					res = res + "(.*)"
			elif c == "?":
				if output:
					res = res + "\\" + str(groups)
					groups += 1
				else:
					res = res + "(.)"
			elif output:
				res = res + c
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
		if output:
			return res
		else:
			return res + "\Z(?ms)"
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
		# TODO add output files to generated files list so next inputs can also catch them

		if inputs:
			result = []
			matched = []
			for input in inputs:
				input = self.eval(input)
				regex = wildcard_regex(input)
				if regex:
					# find the folder where to look for files
					base_folder = re_folder_part.match(regex)
					if base_folder:
						base_folder = base_folder.group().replace("\\\\", "\\").replace("\\/", "/")
						separator = "\\" if base_folder.rfind("\\") > base_folder.rfind("/") else "/"
						base_folder = os.path.dirname(base_folder)
						list_folder = self.rel_path + base_folder
					else:
						separator = ""
						base_folder = ""
						if len(self.rel_path):
							list_folder = self.rel_path[:-1] # strip last /
						else:
							list_folder = "."

					# look for files
					re_regex = re.compile(regex)
					for file in os.listdir(list_folder):
						name = base_folder + separator + file
						match = re_regex.match(name)
						if match:
							result.append(self.rel_path + name)
							#result.append(name)
							matched.append(match.groups())
				else:
					result.append(self.rel_path + input)
			inputs = result

		if outputs:
			result = []
			for output in outputs:
				output = self.eval(output)
				# we want \number instead of capture groups
				regex = wildcard_regex(output, True)
				if regex:
					for match in matched:
						# replace \number with data
						def replace_group(matchobj):
							index = int(matchobj.group(1)) - 1
							if index >= 0 and index < len(match):
								return match[index]
							else:
								return ""
						file = re_capture_group_ref.sub(replace_group, regex)
						result.append(self.rel_path + file)
				else:
					result.append(self.rel_path + output)
			return inputs, result
		else:
			return inputs

	def eval_auto(self, inputs, outputs):
		for rule_name, auto in self.auto_presets.items(): # name: (inputs, outputs, assigns)
			# check if all inputs match required auto inputs
			for auto_input in auto[0]:
				regex = wildcard_regex(auto_input)
				if regex:
					re_regex = re.compile(regex)
					match = all(re_regex.match(input) for input in inputs)
				else:
					match = all(input == auto_input for input in inputs)
				if not match:
					break
			if not match:
				continue
			# check if all outputs match required auto outputs
			for auto_output in auto[1]:
				regex = wildcard_regex(auto_output)
				if regex:
					re_regex = re.compile(regex)
					match = all(re_regex.match(output) for output in outputs)
				else:
					match = all(output == auto_output for output in outputs)
				if not match:
					break
			if not match:
				continue
			# if everything match - return rule name and variables
			return rule_name, auto[2]
		# if no rule found then just return None
		return None, None

	def eval_filter(self, name, regex_or_value):
		value = self.variables.get(name, "")
		regex = wildcard_regex(regex_or_value)
		if regex:
			return re.match(regex, value)
		else:
			return regex_or_value == value

	def write_assigns(self, assigns):
		for assign in assigns:
			name = self.eval(assign[0])
			value = self.eval(assign[1])
			output.append("  %s = %s" % (name, value))

	def comment(self, comment):
		output.append("#" + comment)

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
			if not name:
				return False
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
		return True

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
		self.auto_presets[name] = (inputs, outputs, assigns)

	def assign(self, obj):
		name = self.eval(obj[0])
		value = obj[1]
		self.variables[name] = value

	def include(self, obj):
		paths = self.eval_path([obj])
		for path in paths:
			old_rel_path = self.rel_path
			self.rel_path = rel_dir(path)
			parser = Parser(self, path)
			parser.parse()
			self.rel_path = old_rel_path

	def subninja(self, obj):
		paths = self.eval_path([obj])
		for path in paths:
			engine = Engine(self)
			print("LOAD " + path)
			engine.load(path)
			# TODO we need namescope for rules, pools, auto

engine = Engine()
#engine.load_core()
#engine.load("examples/fox_test.fox")
engine.load("fox_parser_test2.ninja")

print("#------------------ result")
print("\n".join(output))