# mask IR reading helpers

from collections import namedtuple

class BuildList(namedtuple("BuildList", ["indexes", "inputs"])):
	pass
class BuildNode(namedtuple("BuildNode", ["inputs", "index", "rule"])):
	pass
class BuildGraph(namedtuple("BuildGraph", ["graph"])):
	pass

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
	def build_list(self, targets, excluding = None):
		indexes = set()
		inputs = set()
		if isinstance(targets, str):
			def all_deps(targets):
				if (targets in self.targets) and (not excluding or targets not in excluding):
					indexes.add(self.targets.get(targets))
					for dep in self.inputs(targets):
						all_deps(dep)
				else:
					inputs.add(targets)
			all_deps(targets)
		else:
			for target in targets:
				build_list = self.build_list(target, excluding)
				indexes = indexes.union(build_list.indexes)
				inputs = inputs.union(build_list.inputs)

		return BuildList(indexes = indexes, inputs = inputs)

	# return BuildGraph({target: BuildNode(set(input), build_index, rule_name)})
	# excluding can be list of targets to exclude from tree or None
	def build_graph(self, targets, excluding = None):
		graph = {}
		def all_deps(target):
			if target in self.targets:
				index = self.targets.get(target)
				build = self.ir.builds[index]
				if (target in graph) and (graph.get(target).index != index):
					raise ValueError("two commands build " + target)
				graph[target] = BuildNode(inputs = set(build.inputs), index = index, rule = build.rule)
				for dep in self.inputs(target):
					if not excluding or dep not in excluding:
						all_deps(dep)
			else:
				graph[target] = BuildNode(inputs = set(), index = None, rule = None)
		if isinstance(targets, str):
			all_deps(targets)
		else:
			for target in targets:
				all_deps(target)
		return BuildGraph(graph = graph)

	# return [Build] from [indexes or targets]
	# optional - list of excluded targets
	def build_commands(self, indexes_or_targets, excluding = None):
		all_targets = set()
		all_indexes = set()

		for temp in indexes_or_targets:
			if isinstance(temp, str):
				all_targets.add(temp)
			else:
				all_indexes.add(temp)

		if len(all_targets):
			all_indexes = all_indexes.union(self.build_list(all_targets, excluding).indexes)

		# we must do this because builds in ir are topologically sorted already
		all_indexes = list(all_indexes)
		all_indexes.sort()

		builds = []
		for i in all_indexes:
			builds.append(self.ir.builds[i])
		return builds

	# return set(target_folders) from [Build]
	def target_folders(self, builds):
		return set.union(*[build.target_folders for build in builds])
