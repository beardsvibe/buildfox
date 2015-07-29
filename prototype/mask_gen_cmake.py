# this one doesn't really work yet

from pprint import pprint
import argparse

argsparser = argparse.ArgumentParser(description = "mask asm to cmake translator")
argsparser.add_argument("--input", required = True, help = "input sorted mask asm file")
argsparser.add_argument("--output", required = True, help = "output cmake file")
args = vars(argsparser.parse_args())

with open(args["input"], "r") as f:
	import json
	asm = json.loads(f.read())

# very stupid thing just for proof of concept
output = "cmake_minimum_required(VERSION 2.8)\n"
for command in asm:
	output += "execute_process(COMMAND \"" + command["cmd"].replace("\"", "\\\"").replace("\\", "\\\\") + "\")\n"

with open(args["output"], "w") as f:
	f.write(output)
