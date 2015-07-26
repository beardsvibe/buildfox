from pprint import pprint
import argparse

argsparser = argparse.ArgumentParser(description = "mask asm to shell translator")
argsparser.add_argument("--input", required = True, help = "input sorted mask asm file")
argsparser.add_argument("--output", required = True, help = "output shell file")
args = vars(argsparser.parse_args())

with open(args["input"], "r") as f:
	import json
	asm = json.loads(f.read())

output = ""
for command in asm:
	output += command["cmd"] + "\n"

with open(args["output"], "w") as f:
	f.write(output)
