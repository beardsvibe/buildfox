# shell to mask ir
# very very dumb version

from lib.mask_ir import IR

def from_string(text):
	ir = IR()

	all_targets = []
	for line in text.split("\n"):
		if not len(line):
			continue

		index = len(ir.builds)
		rule_name = "rule_" + str(index)
		rule_vars = {"command": line}
		build_target = "__phony_" + str(index)
		all_targets.append(build_target)

		ir.add_rule(rule_name, rule_vars)
		ir.add_build(rule_name = rule_name, targets_explicit = [build_target])

	ir.add_project("all", {"all": all_targets})
	return ir

def from_file(filename):
	with open(filename, "r") as f:
		return from_string(f.read())
