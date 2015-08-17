# mask ir file

import re
from collections import namedtuple
from lib.mask_esc import to_esc, to_esc_iter, to_esc_shell

# variables are based on ninja variables :
# command
# depfile
# deps
# msvc_deps_prefix
# description
# generator
# restat
# rspfile
# rspfile_content

# ------------------------------------------------------------------------------

BuildList = namedtuple("BuildList", ["indexes", "inputs"])

BuildBase = namedtuple("BuildBase", [
	"rule",
	"targets_explicit",
	"targets_implicit",
	"inputs_explicit",
	"inputs_implicit",
	"inputs_order"
])

class Build(BuildBase):
	@property
	def targets(self):
		return self.targets_explicit + self.targets_implicit

	@property
	def inputs(self):
		return self.inputs_explicit + self.inputs_implicit + self.inputs_order

# ------------------------------------------------------------------------------

class IR:
	def __init__(self):
		# {rule_name: {variable_name: variable_value}}
		self.rules = {}

		# [Build]
		# [(rule_name, (targets_explicit, targets_implicit), (inputs_explicit, inputs_implicit, inputs_order))]
		self.builds = []

		# {project_name: {variation_name: [target]}}
		self.projects = {}

	def add_rule(self, name, variables):
		self.rules[name] = variables

	def add_project(self, name, variations):
		self.projects[name] = variations

	def add_build(self, rule_name, targets_explicit, targets_implicit = [],
			inputs_explicit = [], inputs_implicit = [], inputs_order = []):
		build = Build(
			rule = rule_name,
			targets_explicit = targets_explicit,
			targets_implicit = targets_implicit,
			inputs_explicit = inputs_explicit,
			inputs_implicit = inputs_implicit,
			inputs_order = inputs_order
		)
		self.builds.append(build)

	# return rule variable name in context of particular build command
	def evaluate(self, rule_name, var_name, build):
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
		return re.sub("\${([a-zA-Z0-9_.-]+)}", repl, self.rules[rule_name][var_name])

	# return list of rules string representation
	def repr_rules(self):
		for name, variables in self.rules.items():
			yield "rule %s%s" % (
				name,
				"\n  " + "\n  ".join(["%s = %s" % (k, to_esc(v, escape_space = False)) for k, v in variables.items()]) if len(variables) else ""
			)

	# return list of builds string representation
	def repr_builds(self):
		for build in self.builds:
			yield "build %s%s:%s %s%s%s" % (
				" ".join(to_esc_iter(build.targets_explicit)),
				" | " + " ".join(to_esc_iter(build.targets_implicit)) if len(build.targets_implicit) else "",
				build.rule,
				" ".join(to_esc_iter(build.inputs_explicit)),
				" | " + " ".join(to_esc_iter(build.inputs_implicit)) if len(build.inputs_implicit) else "",
				" || " + " ".join(to_esc_iter(build.inputs_order)) if len(build.inputs_order) else ""
			)

	# return list of projects string representation
	def repr_projects(self):
		for name, variations in self.projects.items():
			variables = [k + " = " + " ".join(to_esc_iter(v)) for k, v in variations.items()]
			yield "project %s%s\n" % (
				name,
				"\n  " + "\n  ".join(variables) if len(variations) else ""
			)

	def __repr__(self):
		rules = "\n".join(self.repr_rules())
		builds = "\n".join(self.repr_builds())
		projects = "\n".join(self.repr_projects())
		return "\n".join(filter(len, [rules, builds, projects]))

# ------------------------------------------------------------------------------

class IRreader:
	def __init__(self, ir):
		self.ir = ir

		# {target_name: build_index}
		self.targets = {target: i for i, build in enumerate(self.ir.builds) for target in build.targets}

		# {variation_name: set(target)}, list of all targets from all projects for a variation
		self.variations = {}
		for prj_name, prj_variations in self.ir.projects.items():
			for var_name, var_paths in prj_variations.items():
				if var_name in self.variations:
					self.variations[var_name] = self.variations[var_name].union(set(var_paths))
				else:
					self.variations[var_name] = set(var_paths)

		from pprint import pprint
		pprint(self.targets)
		pprint(self.variations)
		g = self.build_list("ninja.exe")
		pprint(g)
		#pprint(self.builds(g[0]))

	# return list of inputs for target
	def inputs(self, target):
		return self.ir.builds[self.targets.get(target)].inputs

	# return BuildList(set(build_indexes), set(inputs))
	# later you can union this indexes with another build indexes to get summed list
	def build_list(self, target):
		indexes = set()
		inputs = set()
		def all_deps(target):
			if target in self.targets:
				indexes.add(self.targets.get(target))
				for dep in self.inputs(target):
					all_deps(dep)
			else:
				inputs.add(target)
		all_deps(target)
		return BuildList(indexes = indexes, inputs = inputs)

	# return BuildGraph(set(targets),  )
	def build_graph(self, target):
		pass

	# return [Build] from indexes
	def builds(self, indexes):
		builds = []
		for i, build in enumerate(self.ir.builds):
			if i in indexes:
				builds.append(build)
		return builds

