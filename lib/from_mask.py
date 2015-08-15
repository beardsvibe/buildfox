# mask IR is very similar to ninja format
# so we just reuse ninja parser :)

import string
from lib.tool_ninja_parser import ninja_Parser
from lib.mask_ir import Build, Project, IR
from lib.mask_esc import from_esc, from_esc_iter

def from_string(text):
	parser = ninja_Parser(parseinfo = False)
	ast = parser.parse(text, "manifest", trace = False, whitespace = string.whitespace, nameguard = True)
	ir = IR()
	mode = 0

	for expr in ast:
		if "rule" in expr:
			if mode != 0:
				raise ValueError("incorrect order in mask")
			name = expr["rule"]
			vars = {var["assign"]: from_esc(var["value"]) for var in expr["vars"]}
			ir.add_rule(name, vars)
		elif "build" in expr:
			if mode == 0:
				mode = 1
			if mode != 1:
				raise ValueError("incorrect order in mask")
			build = Build()
			build.rule = expr["build"]
			build.targets_explicit	= list(filter(len, from_esc_iter(expr["targets_explicit"])))
			build.targets_implicit	= list(filter(len, from_esc_iter(expr["targets_implicit"] or [])))
			build.inputs_explicit	= list(filter(len, from_esc_iter(expr["inputs_explicit"] or [])))
			build.inputs_implicit	= list(filter(len, from_esc_iter(expr["inputs_implicit"] or [])))
			build.inputs_order		= list(filter(len, from_esc_iter(expr["inputs_order"] or [])))
			ir.builds.append(build)
		elif "project" in expr:
			if mode == 1:
				mode = 2
			if mode != 2:
				raise ValueError("incorrect order in mask")
			mode = 2
			name = expr["project"]
			variations = {var["assign"]: list(var["value"]) for var in expr["vars"]}
			ir.projects[name] = Project(name, variations)

	return ir

def from_file(filename):
	with open(filename, "r") as f:
		return from_string(f.read())
