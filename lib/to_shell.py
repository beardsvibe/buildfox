# ------------------------------------ shell generator tool

import os
from lib.maskfile import to_esc_shell
from lib.tool_build_list import variation_build_list

def to_string(readonly_ir, args = None):
	# get list of what we need to build
	variation = args["variation"]
	builds, all_inputs = variation_build_list(readonly_ir, variation)

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

def to_file(filename, readonly_ir, args = None):
	with open(filename, "w") as f:
		f.write(to_string(readonly_ir, args))
