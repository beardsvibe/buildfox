# mask to shell exporter

import os
from lib.mask_esc import to_esc_shell
from lib.mask_irreader import IRreader

def to_string(ir, args = None):
	# figure out everything
	ir_reader = IRreader(ir)
	end_targets = ir_reader.end_targets(args.get("variation"))
	builds = ir_reader.build_commands(end_targets)
	target_folders = ir_reader.target_folders(builds)

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
		command = ir.evaluate(build, "command")

		if "depfile" in variables:
			print("TODO support depfile in to_shell")
		if "generator" in variables:
			print("TODO support generator in to_shell")
		if "rspfile" in variables:
			print("TODO support rspfile in to_shell")

		output += command + "\n"

	return output

def to_file(filename, ir, args = None):
	with open(filename, "w") as f:
		f.write(to_string(ir, args))
