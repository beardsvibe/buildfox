# fox engine

from fox_parser2 import Parser
from pprint import pprint

core_file = "fox_core.fox"

output = ["# generated with love by buildfox"]

class Engine:
	def __init__(self):
		self.variables = {}

	# load core definitions
	def load_core(self):
		parser = Parser(self, core_file)
		parser.parse()

	def eval(self, text):
		return text

	# input can be string or list of strings
	def eval_path(self, inputs, outputs = None):
		if outputs:
			return inputs, outputs
		else:
			return inputs

	def eval_auto(self, inputs, outputs):
		return "auto", []

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

	def filter(self, obj): # return True/False
		return True
		#[(name, value)]

	def auto(self, obj, assigns):
		#pprint((obj, assigns))
		#(targets, rule, inputs)
		pass

	def assign(self, obj):
		name = self.eval(obj[0])
		value = obj[1]
		self.variables[name] = value

	def include(self, obj):
		path = self.eval_path(obj)
		parser = Parser(self, path)
		parser.parse()

	def subninja(self, obj):
		path = self.eval_path(obj)
		# TODO

e = Engine()
e.load_core()
p = Parser(e, "examples/fox_test.fox")
p.parse()

print("\n".join(output))