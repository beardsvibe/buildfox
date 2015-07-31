# ------------------------------------ shell generator tool

def to_string(readonly_ir, variation = None):
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

	# figure out end targets
	end_targets = set()
	for prj_name, project in readonly_ir.projects.items():
		for name, paths in project.variations.items():
			if (not variation) or (name == variation):
				end_targets = end_targets.union(set(paths))

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

	# write commands
	output = ""
	for i, build in enumerate(readonly_ir.builds):
		if i in need_to_build:
			if build.rule == "phony":
				continue
			if build.rule not in readonly_ir.rules:
				raise ValueError("unknown rule " + build.rule)
			rule = readonly_ir.rules[build.rule]
			if "command" not in rule.variables:
				raise ValueError("rule " + build.rule + " doesn't have command variable")
			command = rule.evaluate("command", build)
			
			if "depfile" in rule.variables:
				print("TODO support depfile in to_shell")
			if "generator" in rule.variables:
				print("TODO support generator in to_shell") # is it even possible ?
			if "rspfile" in rule.variables:
				print("TODO support rspfile in to_shell")

			output += command + "\n"

	return output

def to_file(filename, readonly_ir, variation = None):
	with open(filename, "w") as f:
		f.write(to_string(readonly_ir, variation))
