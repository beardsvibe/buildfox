# BuildFox ninja generator

import os
import re
import copy
import collections
from lib_parser import parse
from lib_util import rel_dir, wildcard_regex

# engine regexes
re_var = re.compile("\${([a-zA-Z0-9_.-]+)}|\$([a-zA-Z0-9_-]+)")
re_folder_part = re.compile(r"(?:[^\r\n(\[\"\\]|\\.)+") # match folder part in filename regex
re_capture_group_ref = re.compile(r"(?<!\\)\\(\d)") # match regex capture group reference
re_variable = re.compile("\$\${([a-zA-Z0-9_.-]+)}|\$\$([a-zA-Z0-9_-]+)")
re_non_escaped_char = re.compile(r"(?<!\\)\\(.)") # looking for not escaped \ with char
re_alphanumeric = re.compile(r"\W+")
re_subst = re.compile(r"(?<!\$)\$\{param\}")

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
			self.rules = {} # rule_name: {var_name: var_value}
			self.transformers = {} # target: pattern
			self.context = Engine.Context()
		else:
			self.variables = copy.copy(parent.variables)
			self.auto_presets = copy.copy(parent.auto_presets)
			self.rel_path = parent.rel_path
			self.rules = copy.copy(parent.rules)
			self.transformers = copy.copy(parent.transformers)
			self.context = parent.context
		self.output = []
		self.need_eval = False
		self.filename = ""
		self.current_line = ""
		self.current_line_i = 0

	# load manifest
	def load(self, filename):
		self.filename = filename
		self.rel_path = rel_dir(filename)
		self.output.append("# generated with love by buildfox from %s" % filename)
		parse(self, filename)

	# load core definitions
	def load_core(self, fox_core):
		self.filename = "fox_core.fox"
		self.rel_path = ""
		parse(self, self.filename, text = fox_core)

	# return output text
	def text(self):
		return "\n".join(self.output) + "\n"

	def save(self, filename):
		with open(filename, "w") as f:
			f.write(self.text())

	def eval(self, text):
		if text == None:
			return None
		elif type(text) is str:
			def repl(matchobj):
				name = matchobj.group(1) or matchobj.group(2)
				if (name in self.variables) and (name not in self.visited_vars):
					self.need_eval = True
					self.visited_vars.add(name)
					return self.variables.get(name)
				else:
					return "${" + name + "}"
			self.need_eval = len(text) > 0
			self.visited_vars = set()
			while self.need_eval:
				self.need_eval = False
				text = re_var.sub(repl, text)
			return text
		else:
			return [self.eval(str) for str in text]

	# input can be string or list of strings
	# outputs are always lists
	def eval_path(self, inputs, outputs = None):
		if inputs:
			result = []
			matched = []
			for input in inputs:
				regex = wildcard_regex(input)
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
					if os.path.isdir(list_folder):
						fs_files = set(os.listdir(list_folder))
					else:
						fs_files = set()
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

			# normalize results
			result = [os.path.normpath(file).replace("\\", "/") for file in result]

		# normalize inputs
		inputs = [os.path.normpath(file).replace("\\", "/") for file in inputs]

		if outputs:
			return inputs, result
		else:
			return inputs

	def add_generated_files(self, files):
		for file in files:
			dir = os.path.dirname(file)
			if dir == "":
				dir = "."
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
		# if no rule found then just fail and optionally return None 
		raise ValueError("unable to deduce auto rule in '%s' (%s:%i)" % (
			self.current_line,
			self.filename,
			self.current_line_i,
		))
		return None, None

	def eval_filter(self, name, regex_or_value):
		value = self.variables.get(name, "")
		regex = wildcard_regex(regex_or_value)
		if regex:
			return re.match(regex, value)
		else:
			return regex_or_value == value

	def eval_assign_op(self, value, prev_value, op):
		if op == "+=":
			return prev_value + value
		elif op == "-=":
			if value in prev_value:
				return prev_value.replace(value, "")
			else:
				return prev_value.replace(value.strip(), "")
		else:
			return value

	def write_assigns(self, assigns):
		local_scope = {}
		for assign in assigns:
			name = self.eval(assign[0])
			value = self.eval(assign[1])
			op = assign[2]

			if name in local_scope:
				value = self.eval_assign_op(value, local_scope.get(name), op)
			else:
				value = self.eval_assign_op(value, self.variables.get(name, ""), op)

			self.output.append("  %s = %s" % (name, value))
			local_scope[name] = value

	def comment(self, comment):
		self.output.append("#" + comment)

	def rule(self, obj, assigns):
		rule_name = self.eval(obj)
		self.output.append("rule " + rule_name)
		vars = {}
		for assign in assigns:
			name = assign[0]
			value = assign[1]
			op = assign[2]
			# only = is supported because += and -= are not native ninja features
			# and rule nested variables are evaluated in ninja
			# so there is no way to implement this in current setup
			if op != "=":
				raise ValueError("only \"=\" is supported in rule nested variables, "\
								 "got invalid assign operation '%s' at rule '%s' (%s:%i)" % (
					op,
					self.current_line,
					self.filename,
					self.current_line_i,
				))
			vars[name] = value
			if name != "expand":
				self.output.append("  %s = %s" % (name, value))
		self.rules[rule_name] = vars

	def build(self, obj, assigns):
		inputs_explicit, targets_explicit = self.eval_path(self.eval(self.from_esc(obj[3])), self.eval(self.from_esc(obj[0])))
		targets_implicit = self.eval_path(self.eval(self.from_esc(obj[1])))
		rule_name = self.eval(obj[2])
		inputs_implicit = self.eval_path(self.eval(self.from_esc(obj[4])))
		inputs_order = self.eval_path(self.eval(self.from_esc(obj[5])))

		self.add_generated_files(targets_explicit)

		if targets_implicit:
			self.add_generated_files(targets_implicit)

		# deduce auto rule
		if rule_name == "auto":
			name, vars = self.eval_auto(inputs_explicit, targets_explicit)
			rule_name = name
			assigns = vars + assigns

		# rule should exist
		if rule_name not in self.rules:
			raise ValueError("unknown rule %s at '%s' (%s:%i)" % (
				rule_name,
				self.current_line,
				self.filename,
				self.current_line_i,
			))

		# expand this rule
		expand = self.rules.get(rule_name).get("expand", None)

		if expand:
			# TODO probably this expand implementation is not enough

			if len(targets_explicit) != len(inputs_explicit):
				raise ValueError("cannot expand rule %s because of different amount of targets and inputs at '%s' (%s:%i)" % (
					rule_name,
					self.current_line,
					self.filename,
					self.current_line_i,
				))

			targets_explicit_indx = sorted(range(len(targets_explicit)), key = lambda k: targets_explicit[k])
			inputs_explicit_indx = sorted(range(len(inputs_explicit)), key = lambda k: inputs_explicit[k])
			targets_implicit = sorted(targets_implicit)
			inputs_implicit = sorted(inputs_implicit)
			inputs_order = sorted(inputs_order)

			for target_index in targets_explicit_indx:
				target = targets_explicit[target_index]
				input = inputs_explicit[target_index]

				self.output.append("build %s: %s %s%s%s" % (
					self.to_esc(target),
					rule_name,
					self.to_esc(input),
					" | " + " ".join(self.to_esc(inputs_implicit)) if inputs_implicit else "",
					" || " + " ".join(self.to_esc(inputs_order)) if inputs_order else "",
				))

				self.write_assigns(assigns)

			if targets_implicit: # TODO remove this when https://github.com/martine/ninja/pull/989 is merged
				self.output.append("build %s: phony %s" % (
					" ".join(self.to_esc(targets_implicit)),
					" ".join(self.to_esc(sorted(targets_explicit))),
				))
		else:
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
					" ".join(self.to_esc(targets_explicit)),
				))

	def default(self, obj, assigns):
		paths = self.eval_path(self.eval(self.from_esc(obj)))
		self.output.append("default " + " ".join(self.to_esc(paths)))
		self.write_assigns(assigns)

	def pool(self, obj, assigns):
		name = self.eval(obj)
		self.output.append("pool " + name)
		self.write_assigns(assigns)

	def filter(self, obj):
		for filt in obj:
			name = self.eval(filt[0])
			value = self.eval(self.from_esc(filt[1]))
			if not self.eval_filter(name, value):
				return False
		return True

	def auto(self, obj, assigns):
		outputs = [self.eval(output) for output in self.from_esc(obj[0])] # this shouldn't be eval_path !
		name = self.eval(obj[1])
		inputs = [self.eval(input) for input in self.from_esc(obj[2])] # this shouldn't be eval_path !
		self.auto_presets[name] = (inputs, outputs, assigns)

	def print(self, obj):
		print(self.eval(obj))

	def assign(self, obj):
		name = self.eval(obj[0])
		value = self.eval(obj[1])
		op = obj[2]

		optional_transformer = self.transformers.get(name)
		if optional_transformer:
			value = self.eval_transform(optional_transformer, value)

		value = self.eval_assign_op(value, self.variables.get(name), op)

		self.variables[name] = value
		self.output.append("%s = %s" % (name, value))

	def transform(self, obj):
		target = self.eval(obj[0])
		pattern = obj[1]
		self.transformers[target] = pattern

	def eval_transform(self, pattern, values):
		def transform_one(value):
			if value:
				return self.from_esc2(re_subst.sub(value, pattern))
			else:
				return ""
		transformed = [transform_one(v) for v in values.split(" ")]
		return " ".join(transformed)

	def include(self, obj):
		paths = self.eval_path(self.eval(self.from_esc([obj])))
		for path in paths:
			old_rel_path = self.rel_path
			self.rel_path = rel_dir(path)
			parse(self, path)
			self.rel_path = old_rel_path

	def subninja(self, obj):
		paths = self.eval_path(self.eval(self.from_esc([obj])))
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
			# TODO: This one is strange.
			def repl(matchobj):
				return "${" + (matchobj.group(1) or matchobj.group(2)) + "}"
			return re_variable.sub(repl, value)
		else:
			return [self.to_esc(str) for str in value]

	# TODO: Code duplication sucks.
	def from_esc2(self, value):
		def repl(matchobj):
			return "${%s}" % (matchobj.group(1) or matchobj.group(2))
		return re_variable.sub(repl, value)

	def from_esc(self, value):
		if value == None:
			return None
		elif type(value) is str:
			if value.startswith("r\""):
				return value
			else:
				return value.replace("$\n", "").replace("$ ", " ").replace("$:", ":").replace("$$", "$")
		else:
			return [self.from_esc(str) for str in value]

