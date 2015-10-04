# BuildFox ninja generator

import os
import re
import copy
import collections
from lib_parser import parse
from lib_util import rel_dir, wildcard_regex, find_files

# match and capture variable and escaping pairs of $$ before variable name
re_var = re.compile("(?<!\$)((?:\$\$)*)\$({)?([a-zA-Z0-9_.-]+)(?(2)})")
re_alphanumeric = re.compile(r"\W+") # match valid parts of filename
re_subst = re.compile(r"(?<!\$)(?:\$\$)*\$\{param\}")
re_non_escaped_space = re.compile(r"(?<!\$)(?:\$\$)* +")

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
		if filename:
			with open(filename, "w") as f:
				f.write(self.text())
		else:
			print(self.text())

	def eval(self, text):
		if text == None:
			return None
		elif type(text) is str:
			raw = text.startswith("r\"")

			# first remove escaped sequences
			if not raw:
				text = text.replace("$\n", "").replace("$ ", " ").replace("$:", ":")

			# then do variable substitution
			def repl(matchobj):
				prefix = matchobj.group(1)
				name = matchobj.group(3)
				if matchobj.group(2):
					default = "${%s}" % name
				else:
					default = "$%s" % name
				return prefix + self.variables.get(name, default)
			text = re_var.sub(repl, text)

			# and finally fix escaped $ but escaped variables
			if not raw:
				text = text.replace("$$", "$")

			return text
		else:
			return [self.eval(str) for str in text]

	# evaluate and find files
	def eval_find_files(self, input, output = None):
		return find_files(self.eval(input),
						  self.eval(output),
						  rel_path = self.rel_path,
						  generated = self.context.generated)

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

	def eval_transform(self, name, values):
		transformer = self.transformers.get(name)
		if not transformer:
			return self.eval(values)

		def transform_one(value):
			if not value:
				return ""
			value = re_subst.sub(value, transformer)
			return self.eval(value)

		transformed = [transform_one(v) for v in re_non_escaped_space.split(values)]
		return " ".join(transformed)

	def write_assigns(self, assigns):
		local_scope = {}
		for assign in assigns:
			name = self.eval(assign[0])
			value = self.eval_transform(name, assign[1])
			op = assign[2]

			if name in local_scope:
				value = self.eval_assign_op(value, local_scope.get(name), op)
			else:
				value = self.eval_assign_op(value, self.variables.get(name, ""), op)

			self.output.append("  %s = %s" % (name, self.to_esc(value, simple = True)))
			local_scope[name] = value

	def on_comment(self, comment):
		self.output.append("#" + comment)

	def on_rule(self, obj, assigns):
		rule_name = self.eval(obj)
		self.output.append("rule " + rule_name)
		vars = {}
		for assign in assigns:
			name = self.eval(assign[0])
			# do not evaluate value here and also do not do any from_esc / to_esc here
			# just pass value as raw string to output
			# TODO but do we need eval_transform here ?
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

	def on_build(self, obj, assigns):
		inputs_explicit, targets_explicit = self.eval_find_files(obj[3], obj[0])
		targets_implicit = self.eval_find_files(obj[1])
		rule_name = self.eval(obj[2])
		inputs_implicit = self.eval_find_files(obj[4])
		inputs_order = self.eval_find_files(obj[5])

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

	def on_default(self, obj):
		paths = self.eval_find_files(obj)
		self.output.append("default " + " ".join(self.to_esc(paths)))

	def on_pool(self, obj, assigns):
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

	def on_auto(self, obj, assigns):
		outputs = self.eval(obj[0]) # this shouldn't be find_files !
		name = self.eval(obj[1])
		inputs = self.eval(obj[2]) # this shouldn't be find_files !
		self.auto_presets[name] = (inputs, outputs, assigns)

	def on_print(self, obj):
		print(self.eval(obj))

	def on_assign(self, obj):
		name = self.eval(obj[0])
		value = self.eval_transform(name, obj[1])
		op = obj[2]

		value = self.eval_assign_op(value, self.variables.get(name), op)

		self.variables[name] = value
		self.output.append("%s = %s" % (name, self.to_esc(value, simple = True)))

	def on_transform(self, obj):
		target = self.eval(obj[0])
		pattern = obj[1] # do not eval it here
		self.transformers[target] = pattern

	def on_include(self, obj):
		paths = self.eval_find_files([obj])
		for path in paths:
			old_rel_path = self.rel_path
			self.rel_path = rel_dir(path)
			parse(self, path)
			self.rel_path = old_rel_path

	def on_subninja(self, obj):
		paths = self.eval_find_files([obj])
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

	def to_esc(self, value, simple = False):
		if value == None:
			return None
		elif type(value) is str:
			value = value.replace("$", "$$")
			if not simple:
				value = value.replace(":", "$:").replace("\n", "$\n").replace(" ", "$ ")
			return value
		else:
			return [self.to_esc(str) for str in value]
