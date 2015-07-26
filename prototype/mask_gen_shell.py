from pprint import pprint
import argparse

argsparser = argparse.ArgumentParser(description = "mask asm to shell translator")
argsparser.add_argument("--input", required = True, help = "input mask asm file")
argsparser.add_argument("--output", required = True, help = "output shell file")
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

output = ""
def write_cmd(command):
	global output
	if command["working_on"]:
		raise ValueError("circular dependency for " + dependecy)
	command["working_on"] = True

	for dependency in command["command"]["depend_on"]:
		if (dependency in touch_pool) and not (all_commands[touch_pool[dependency]]["processed"]):
			write_cmd(all_commands[touch_pool[dependency]])

	command["processed"] = True
	output += command["command"]["cmd"] + "\n"

for command in all_commands:
	if not command["processed"]:
		write_cmd(command)

with open(args["output"], "w") as f:
	f.write(output)
