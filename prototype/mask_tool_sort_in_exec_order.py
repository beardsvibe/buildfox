from pprint import pprint
import argparse

argsparser = argparse.ArgumentParser(description = "sort mask asm commands in execution order")
argsparser.add_argument("--input", required = True, help = "input mask asm file")
argsparser.add_argument("--output", required = True, help = "output mask asm file")
args = vars(argsparser.parse_args())

with open(args["input"], "r") as f:
	import json
	asm = json.loads(f.read())

all_commands = []
touch_pool = {}

for command in asm:
	all_commands.append({"command": command, "processed": False, "working_on": False})
	for touch in command["touch"]:
		touch_pool[touch] = len(all_commands) - 1

output = []
def execute_cmd(command):
	global output
	if command["working_on"]:
		raise ValueError("circular dependency for " + dependecy)
	command["working_on"] = True

	for dependency in command["command"]["depend_on"]:
		if (dependency in touch_pool) and not (all_commands[touch_pool[dependency]]["processed"]):
			execute_cmd(all_commands[touch_pool[dependency]])

	command["processed"] = True
	output.append(command["command"])

for command in all_commands:
	if not command["processed"]:
		execute_cmd(command)

with open(args["output"], "w") as f:
	json.dump(output, f, sort_keys = True, indent = 4)
