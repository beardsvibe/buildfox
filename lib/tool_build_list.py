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

# return build list for end_targets
def build_list(readonly_ir, end_targets):
	# build target -> build index dictionary
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

	# figure out what to build
	need_to_build = set()
	def all_deps(target):
		if target in targets:
			index = targets[target]
			need_to_build.add(index)
			build = readonly_ir.builds[index]
			deps = set(build.inputs_explicit).union(build.inputs_implicit).union(build.inputs_order)
			for dep in deps:
				all_deps(dep)
	for target in end_targets:
		all_deps(target)

	builds = []
	for i, build in enumerate(readonly_ir.builds):
		if i in need_to_build:
			builds.append(build)
	return builds

def variation_build_list(readonly_ir, variation = None):
	return build_list(readonly_ir, end_targets(readonly_ir, variation))