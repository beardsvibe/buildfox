
from collections import namedtuple

BuildList = namedtuple("BuildList", ["indexes", "inputs"])
BuildNode = namedtuple("BuildNode", ["inputs", "index", "rule"])
BuildGraph = namedtuple("BuildGraph", ["graph"])

# TODO BuildGraph should have methods like extracting sub graph, etc

class IRreader:
	def __init__(self, ir):
		self.ir = ir

		# {target_name: build_index}
		self.targets = {target: i for i, build in enumerate(self.ir.builds) for target in build.targets}

	# return {variation_name: set(target)}, list of all targets from all projects for a variation
	def all_variations(self):
		variations = {}
		for prj_name, prj_variations in self.ir.projects.items():
			for var_name, var_paths in prj_variations.items():
				if var_name in variations:
					variations[var_name] = variations[var_name].union(set(var_paths))
				else:
					variations[var_name] = set(var_paths)
		return variations

	# return set of end targets for required variation
	def end_targets(self, variation = None):
		all_variations = self.all_variations()
		if not variation:
			return list(all_variations.values())[0]
		elif variation in all_variations:
			return all_variations.get(variation)
		else:
			raise ValueError("can't find " + variation + " in variations")

	# return list of inputs for targets
	# targets can be string or set/list of strings
	def inputs(self, targets):
		if isinstance(targets, str):
			index = self.targets.get(targets)
			if index is None:
				return []
			return self.ir.builds[index].inputs
		else:
			inputs = []
			for target in targets:
				inputs += self.inputs(target)
			return inputs

	# return BuildList(set(build_indexes), set(inputs))
	# targets can be string or set/list of strings
	# later you can union this indexes with another build indexes to get summed list
	def build_list(self, targets):
		indexes = set()
		inputs = set()
		if isinstance(targets, str):
			def all_deps(targets):
				if targets in self.targets:
					indexes.add(self.targets.get(targets))
					for dep in self.inputs(targets):
						all_deps(dep)
				else:
					inputs.add(targets)
			all_deps(targets)
		else:
			for target in targets:
				build_list = self.build_list(target)
				indexes = indexes.union(build_list.indexes)
				inputs = inputs.union(build_list.inputs)

		return BuildList(indexes = indexes, inputs = inputs)

	# return BuildGraph({target: BuildNode(set(input), build_index, rule_name)})
	def build_graph(self, target):
		graph = {}
		def all_deps(target):
			if target in self.targets:
				index = self.targets.get(target)
				build = self.ir.builds[index]
				graph[target] = BuildNode(inputs = set(build.inputs), index = index, rule = build.rule)
				for dep in self.inputs(target):
					all_deps(dep)
			else:
				graph[target] = BuildNode(inputs = set(), index = None, rule = None)
		all_deps(target)
		return BuildGraph(graph = graph)

	# return [Build] from indexes
	def builds(self, indexes):
		builds = []
		for i, build in enumerate(self.ir.builds):
			if i in indexes:
				builds.append(build)
		return builds

