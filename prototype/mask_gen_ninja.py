from pprint import pprint
import argparse

argsparser = argparse.ArgumentParser(description = "mask asm to ninja translator")
argsparser.add_argument("--input", required = True, help = "input mask asm file")
argsparser.add_argument("--output", required = True, help = "output ninja file")
args = vars(argsparser.parse_args())

with open(args["input"], "r") as f:
	import json
	asm = json.loads(f.read())

# very stupid thing just for proof of concept
# for proper implementation we need to find common lines to create as few rules as possible
output = ""
for i, command in enumerate(asm):
	output += "rule rule_" + str(i) + "\n"
	output += "  command = " + command["cmd"] + "\n"
	output += "build " + " ".join(command["touch"]) + ": rule_" + str(i) + " " + " ".join(command["depend_on"]) + "\n"

with open(args["output"], "w") as f:
	f.write(output)
