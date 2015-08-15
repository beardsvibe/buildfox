# TODO we parse $\n sequence incorrectly : we don't skip whitespace after newline

import re
import string
import hashlib
from lib.tool_ninja_parser import ninja_Parser
from lib.maskfile import from_esc, from_esc_iter, Rule, Build, Project, IR

class Namescope():
	def __init__(self):
		self.ir = IR()
		self.vars = [] # array of tuples (name, value)
		self.rules = {} # dict of key = name, value = (vars_scope_index, vars_array), vars_array - array of tuples (name, value)
		self.builds = [] # array of tuples (vars_scope_index, name, targets, inputs, inputs, inputs, vars_array), vars_array - array of tuples (name, value)
		self.defaults = [] # array of tuples (vars_scope_index, targets)

	def get_scoped_vars(self, expr):
		return [(var_expr["assign"], from_esc(var_expr["value"])) for var_expr in expr["vars"]]

	def process(self, text):
		parser = ninja_Parser(parseinfo = False)
		ast = parser.parse(text, "manifest", trace = False, whitespace = string.whitespace, nameguard = True)

		for expr in ast:
			if "assign" in expr:
				var = (expr["assign"], from_esc(expr["value"]))
				self.vars.append(var)
				#print(name + " = " + value)
			elif "rule" in expr:
				name = expr["rule"]
				rule = (
					len(self.vars),
					self.get_scoped_vars(expr)
				)
				if name in self.rules:
					raise ValueError("redefinition of rule '" + name + "'")
				self.rules[name] = rule
				#print(rule)
			elif "build" in expr:
				build = (
					len(self.vars),
					expr["build"],
					list(filter(len, from_esc_iter(expr["targets_explicit"]))),
					list(filter(len, from_esc_iter(expr["inputs_explicit"] or []))),
					list(filter(len, from_esc_iter(expr["inputs_implicit"] or []))),
					list(filter(len, from_esc_iter(expr["inputs_order"] or []))),
					self.get_scoped_vars(expr)
				)
				self.builds.append(build)
				#print(build)
			elif "defaults" in expr:
				default = (
					len(self.vars),
					list(filter(len, from_esc_iter(expr["defaults"]))),
				)
				self.defaults.append(default)
				#print(default)
			elif "pool" in expr:
				print("TODO pool")
			elif "include" in expr:
				print("TODO include")
			elif "subninja" in expr:
				print("TODO subninja")
			else:
				raise ValueError("unknown ast expr " + str(expr))

	def evaluate_text(self, text, scope):
		def repl(matchobj):
			name = matchobj.group(1) or matchobj.group(2)
			#print("! '" + name + "'")
			if name in ["in", "out", "in_newline"]:
				return "${" + name + "}"
			elif name in scope:
				return scope[name]
			else:
				return ""
		return re.sub("\${([a-zA-Z0-9_.-]+)}|\$([a-zA-Z0-9_-]+)", repl, text)

	def build_ir(self, end_targets = None, parent_vars = {}):
		# expand all vars
		scope = parent_vars
		vars = []
		for var in self.vars:
			name = var[0]
			value = self.evaluate_text(var[1], scope)
			scope[name] = value
			vars.append((name, value))

		# expand all build vars
		builds = []
		for build in self.builds:
			name = build[1]
			build_scope = dict(parent_vars, **{v[0]: v[1] for v in vars[:build[0]]}) # TODO optimize this
			targets = [self.evaluate_text(t, build_scope) for t in build[2]]
			inputs0 = [self.evaluate_text(t, build_scope) for t in build[3]]
			inputs1 = [self.evaluate_text(t, build_scope) for t in build[4]]
			inputs2 = [self.evaluate_text(t, build_scope) for t in build[5]]
			build_vars = {}
			for var in build[6]:
				var_name = var[0]
				value = self.evaluate_text(var[1], build_scope)
				build_scope[var_name] = value
				build_vars[var_name] = value
			builds.append((name, targets, inputs0, inputs1, inputs2, build_vars))

		# figure out end targets
		if end_targets == None:
			end_targets = []
			for default in self.defaults:
				default_scope = dict(parent_vars, **{v[0]: v[1] for v in vars[:default[0]]}) # TODO optimize this
				for path in default[1]:
					end_targets.append(self.evaluate_text(path, default_scope))

		# build target -> build index dictionary
		targets = {}
		for i, build in enumerate(builds):
			for target in build[1]:
				if target in targets:
					raise ValueError("multiple commands build " + target)
				targets[target] = i

		# figure out build order
		ordered_builds = []
		ordered_builds_set = set()
		def sort_build(target):
			if target not in targets:
				return
			index = targets[target]
			build = builds[index]
			for input in build[2] + build[3] + build[4]: # all inputs
				sort_build(input)
			if index not in ordered_builds_set:
				ordered_builds.append(index)
				ordered_builds_set.add(index)
		for target in end_targets:
			sort_build(target)

		# now it's time to build rule set
		# IR doesn't support shadowing so we need to clone rules each time when build try to shadow vars
		rules = {}
		for b in ordered_builds:
			build = builds[b]
			base_rule_name = build[0]
			rule_name = base_rule_name

			# generate new rule name if we have vars in build
			if len(build[5]):
				all_vars = "\n".join([var[0] + "=" + var[1] for var in build[5]])
				rule_name += "_" + hashlib.md5(all_vars.encode("utf-8")).hexdigest()

			if rule_name in rules:
				continue

			if base_rule_name not in self.rules:
				print(build)
				raise ValueError("can't find rule named '" + base_rule_name + "'")

			rule = self.rules[base_rule_name]

			# prepare rule scope
			rule_scope = dict(parent_vars, **{v[0]: v[1] for v in vars[:rule[0]]}) # TODO optimize this
			if len(build[5]):
				rule_scope = dict(rule_scope, **build[5])

			# evaluate vars
			rule_vars = {}
			for var in rule[1]:
				name = var[0]
				value = self.evaluate_text(var[1], rule_scope)
				rule_scope[name] = value
				rule_vars[name] = value

			rules[rule_name] = rule_vars

			# change rule name in build command
			if base_rule_name != rule_name:
				build = (rule_name, build[1], build[2], build[3], build[4], build[5])
				builds[b] = build

		# generate IR
		for name, rule in rules.items():
			self.ir.rules[name] = Rule(name, rule)

		for b in ordered_builds:
			build = builds[b]
			ir_build = Build()
			ir_build.rule = build[0]
			ir_build.targets_explicit = build[1]
			ir_build.inputs_explicit = build[2]
			ir_build.inputs_implicit = build[3]
			ir_build.inputs_order = build[4]
			self.ir.builds.append(ir_build)

		project = Project("default", {"default": end_targets})
		self.ir.projects[project.name] = project

def from_string(text):
	namescope = Namescope()
	namescope.process(text)
	namescope.build_ir()
	return namescope.ir

def from_file(filename):
	with open(filename, "r") as f:
		return from_string(f.read())