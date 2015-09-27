# fox engine

import os, re, copy, collections
from fox_parser2 import Parser
from pprint import pprint

core_file = "fox_core.fox"
re_var = re.compile("\${([a-zA-Z0-9_.-]+)}|\$([a-zA-Z0-9_-]+)")
re_folder_part = re.compile(r"(?:[^\r\n(\[\"\\]|\\.)+") # match folder part in filename regex
re_capture_group_ref = re.compile(r"(?<!\\)\\(\d)") # match regex capture group reference
re_variable = re.compile("\$\${([a-zA-Z0-9_.-]+)}|\$\$([a-zA-Z0-9_-]+)")
re_non_escaped_char = re.compile(r"(?<!\\)\\(.)") # looking for not escaped \ with char
re_alphanumeric = re.compile(r"\W+")

class Engine:
	class Context:
		def __init__(self):
			# key is folder name, value is set of file names
			self.generated = collections.defaultdict(set)
			# number of generated subninja files
			self.subninja_num = 0

	def __init__(self, parent = None):
		if not parent:
			self.variables = {} # name: value
			self.auto_presets = {} # name: (inputs, outputs, assigns)
			self.rel_path = "" # this should be prepended to all parsed paths
			self.context = Engine.Context()
		else:
			self.variables = copy.copy(parent.variables)
			self.auto_presets = copy.copy(parent.auto_presets)
			self.rel_path = parent.rel_path
			self.context = parent.context
		self.output = []
		self.need_eval = False
		self.filename = ""
		self.current_line = ""
		self.current_line_i = 0

	# load manifest
	def load(self, filename):
		self.filename = filename
		self.rel_path = self.rel_dir(filename)
		self.output.append("# generated with love by buildfox from %s" % filename)
		parser = Parser(self, filename)
		parser.parse()

	# load core definitions
	def load_core(self):
		self.load(core_file)

	# return output text
	def text(self):
		return "\n".join(self.output)

	def save(self, filename):
		with open(filename, "w") as f:
			f.write(self.text())

	# return relative path to current work dir
	def rel_dir(self, filename):
		path = os.path.relpath(os.path.dirname(os.path.abspath(filename)), os.getcwd()).replace("\\", "/") + "/"
		if path == "./":
			path = ""
		return path

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

	# return regex value in filename is regex or wildcard
	def wildcard_regex(self, filename, output = False):
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

	# input can be string or list of strings
	# outputs are always lists
	def eval_path(self, inputs, outputs = None):
		if inputs:
			result = []
			matched = []
			for input in inputs:
				input = self.eval(input)
				regex = self.wildcard_regex(input)
				if regex:
					# find the folder where to look for files
					base_folder = re_folder_part.match(regex)
					if base_folder:
						base_folder = base_folder.group()
						# rename regex back to readable form
						def replace_non_esc(match_group):
							return match_group.group(1)
						base_folder = re_non_escaped_char.sub(replace_non_esc, base_folder)
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
					list_folder = os.path.normpath(list_folder).replace("\\", "/")
					re_regex = re.compile(regex)
					fs_files = set(os.listdir(list_folder))
					generated_files = self.context.generated.get(list_folder, set())
					for file in fs_files.union(generated_files):
						name = base_folder + separator + file
						match = re_regex.match(name)
						if match:
							result.append(self.rel_path + name)
							matched.append(match.groups())
				else:
					result.append(self.rel_path + input)
			inputs = result

		if outputs:
			result = []
			for output in outputs:
				output = self.eval(output)
				# we want \number instead of capture groups
				regex = self.wildcard_regex(output, True)
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

			# normalize results
			result = [os.path.normpath(file).replace("\\", "/") for file in result]

			# add them to generated files dict
			for file in result:
				dir = os.path.dirname(file)
				name = os.path.basename(file)
				if name in self.context.generated[dir]:
					raise ValueError("two or more commands generate '%s' in '%s' (%s:%i)" % (
						file,
						self.current_line,
						self.filename,
						self.current_line_i,
					))
				else:
					self.context.generated[dir].add(name)

		# normalize inputs
		inputs = [os.path.normpath(file).replace("\\", "/") for file in inputs]

		if outputs:
			return inputs, result
		else:
			return inputs

	def eval_auto(self, inputs, outputs):
		for rule_name, auto in self.auto_presets.items(): # name: (inputs, outputs, assigns)
			# check if all inputs match required auto inputs
			for auto_input in auto[0]:
				regex = self.wildcard_regex(auto_input)
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
				regex = self.wildcard_regex(auto_output)
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
		# if no rule found then just fail and optionally return None 
		raise ValueError("unable to deduce auto rule in '%s' (%s:%i)" % (
			self.current_line,
			self.filename,
			self.current_line_i,
		))
		return None, None

	def eval_filter(self, name, regex_or_value):
		value = self.variables.get(name, "")
		regex = self.wildcard_regex(regex_or_value)
		if regex:
			return re.match(regex, value)
		else:
			return regex_or_value == value

	def write_assigns(self, assigns, do_not_eval = False):
		for assign in assigns:
			name = assign[0] if do_not_eval else self.eval(assign[0])
			value = assign[1] if do_not_eval else self.eval(assign[1])
			self.output.append("  %s = %s" % (name, value))

	def comment(self, comment):
		self.output.append("#" + comment)

	def rule(self, obj, assigns):
		name = self.eval(obj)
		self.output.append("rule " + name)
		self.write_assigns(assigns, do_not_eval = True)

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

		# make generated output stable
		targets_explicit = sorted(targets_explicit)
		targets_implicit = sorted(targets_implicit)
		inputs_explicit = sorted(inputs_explicit)
		inputs_implicit = sorted(inputs_implicit)
		inputs_order = sorted(inputs_order)

		self.output.append("build %s: %s%s%s%s" % (
			" ".join(self.to_esc(targets_explicit)),
			rule_name,
			" " + " ".join(self.to_esc(inputs_explicit)) if inputs_explicit else "",
			" | " + " ".join(self.to_esc(inputs_implicit)) if inputs_implicit else "",
			" || " + " ".join(self.to_esc(inputs_order)) if inputs_order else "",
		))

		self.write_assigns(assigns)

		if targets_implicit: # TODO remove this when https://github.com/martine/ninja/pull/989 is merged
			self.output.append("build %s: phony %s" % (
				" ".join(self.to_esc(targets_implicit)),
				" " + " ".join(self.to_esc(targets_explicit)),
			))

	def default(self, obj, assigns):
		paths = self.eval_path(obj)
		self.output.append("default " + " ".join(self.to_esc(paths)))
		self.write_assigns(assigns)

	def pool(self, obj, assigns):
		name = self.eval(obj)
		self.output.append("pool " + name)
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

	def print(self, obj):
		print(self.eval(obj))

	def assign(self, obj):
		name = self.eval(obj[0])
		value = obj[1]
		self.variables[name] = value
		self.output.append("%s = %s" % (name, value))

	def include(self, obj):
		paths = self.eval_path([obj])
		for path in paths:
			old_rel_path = self.rel_path
			self.rel_path = self.rel_dir(path)
			parser = Parser(self, path)
			parser.parse()
			self.rel_path = old_rel_path

	def subninja(self, obj):
		paths = self.eval_path([obj])
		for path in paths:
			gen_filename = "__gen_%i_%s.ninja" % (
				self.context.subninja_num,
				re_alphanumeric.sub("", os.path.splitext(os.path.basename(path))[0])
			)
			self.context.subninja_num += 1
			engine = Engine(self)
			engine.load(path)
			engine.save(gen_filename)
			self.output.append("subninja " + self.to_esc(gen_filename))

	def to_esc(self, value):
		if value == None:
			return None
		elif type(value) is str:
			value = value.replace("$", "$$").replace(":", "$:").replace("\n", "$\n").replace(" ", "$ ")
			# escaping variables
			def repl(matchobj):
				return "${" + (matchobj.group(1) or matchobj.group(2)) + "}"
			return re_variable.sub(repl, value)
		else:
			return [self.to_esc(str) for str in value]

#os.chdir("..")
engine = Engine()
engine.load_core()
#engine.load("examples/fox_test.fox")
engine.load("fox_parser_test.ninja")

print("#------------------ result")
print(engine.text())

engine.save("__gen_output.ninja")