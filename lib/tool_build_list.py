# misc tools for build lists

# return set of end targets for variation
def end_targets(readonly_ir, variation = None):
	# figure out end targets
	end_targets = set()
	for prj_name, project in readonly_ir.projects.items():
		for name, paths in project.variations.items():
			if (not variation) or (name == variation):
				end_targets = end_targets.union(set(paths))
	return end_targets

# build target to build index dictionary
def build_targets_dict(readonly_ir):
	targets = {}
	for i, build in enumerate(readonly_ir.builds):
		for target in build.targets_explicit:
			if target in targets:
				raise ValueError("multiple commands build " + target)
			targets[target] = i
		for target in build.targets_implicit:
			if target in targets:
				raise ValueError("multiple commands build " + target)
			targets[target] = i
	return targets

# return set of indexes in build list that are needed to be executed to get end targets
# also return set of all inputs
def needed_to_execute_indexes(readonly_ir, end_targets, targets_dict = None):
	if targets_dict is None:
		targets_dict = build_targets_dict(readonly_ir)

	need_to_execute_indexes = set()
	all_inputs = set()
	def all_deps(target):
		if target in targets_dict:
			index = targets_dict[target]
			need_to_execute_indexes.add(index)
			build = readonly_ir.builds[index]
			deps = set(build.inputs_explicit).union(build.inputs_implicit).union(build.inputs_order)
			for dep in deps:
				all_deps(dep)
		else:
			all_inputs.add(target)
	for target in end_targets:
		all_deps(target)

	return need_to_execute_indexes, all_inputs

# return list of builds from indexes
def needed_to_execute_builds(readonly_ir, need_to_execute_indexes):
	builds = []
	for i, build in enumerate(readonly_ir.builds):
		if i in need_to_execute_indexes:
			builds.append(build)
	return builds

# return build list for end_targets
def build_list(readonly_ir, end_targets):
	need_to_execute_indexes, all_inputs = needed_to_execute_indexes(readonly_ir, end_targets)
	builds = needed_to_execute_builds(readonly_ir, need_to_execute_indexes)
	return builds, all_inputs

# return build list for variation
def variation_build_list(readonly_ir, variation = None):
	return build_list(readonly_ir, end_targets(readonly_ir, variation))