import os
from lib.mask_esc import to_esc_shell
from lib.tool_build_list import variation_build_list

def to_string(ir, args = None):
	# get list of what we need to build
	variation = args["variation"]
	builds, all_inputs = variation_build_list(ir, variation)

	# figure out target folders
	target_folders = set()
	for build in builds:
		for path in build.targets_explicit + build.targets_implicit:
			dir = os.path.dirname(path)
			if len(dir):
				target_folders.add(dir)

	# write commands
	output = ""
	for folder in target_folders:
		output += "mkdir " + to_esc_shell(folder) + "\n"
	for build in builds:
		if build.rule == "phony":
			continue
		if build.rule not in ir.rules:
			raise ValueError("unknown rule " + build.rule)
		variables = ir.rules[build.rule]
		if "command" not in variables:
			raise ValueError("rule " + build.rule + " doesn't have command variable")
		command = ir.evaluate(build.rule, "command", build)

		if "depfile" in variables:
			print("TODO support depfile in to_shell")
		if "generator" in variables:
			print("TODO support generator in to_shell") # is it even possible ?
		if "rspfile" in variables:
			print("TODO support rspfile in to_shell")

		output += command + "\n"

	return output

def to_file(filename, ir, args = None):
	with open(filename, "w") as f:
		f.write(to_string(ir, args))
