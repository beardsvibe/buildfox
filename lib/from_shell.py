# very very dumb version

from lib.maskfile import Rule, Build, Project, IR

def from_string(text):
	ir = IR()

	project = Project("all", {"all": []})
	for line in text.split("\n"):
		if not len(line):
			continue

		index = len(ir.builds)
		rule_name = "rule_" + str(index)
		rule_vars = {"command": line}
		build_target = "__phony_" + str(index)
		project.variations["all"].append(build_target)

		ir.rules[rule_name] = Rule(rule_name, rule_vars)
		build = Build()
		build.rule = rule_name
		build.targets_explicit = [build_target]
		ir.builds.append(build)

	ir.projects[project.name] = project
	return ir

def from_file(filename):
	with open(filename, "r") as f:
		return from_string(f.read())
