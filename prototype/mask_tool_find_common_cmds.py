from pprint import pprint
import argparse
import os

argsparser = argparse.ArgumentParser(description = "find command calls in mask asm commands")
argsparser.add_argument("--input", required = True, help = "input mask asm file")
#argsparser.add_argument("--output", required = True, help = "output mask asm file")
args = vars(argsparser.parse_args())

with open(args["input"], "r") as f:
	import json
	asm = json.loads(f.read())

for command in asm:
	cmd = command["cmd"].split()
	tool = os.path.splitext(os.path.basename(cmd[0]))[0].lower()

	# wip
	if tool == "cl":
		program = cmd[0]
		args = {}
		files = []
		link = False
		link_args = {}
		link_files = []

		for arg in cmd[1:]:
			if arg.startswith("/"):
				if arg == "/link":
					link = True
					continue
				if link == False:
					if arg not in args:
						args[arg] = True
				else:
					if arg not in link_args:
						link_args[arg] = True
			else:
				if link == False:
					files.append(arg)
				else:
					link_files.append(arg)

	print(cmd)



#with open(args["output"], "w") as f:
#	json.dump(output, f, sort_keys = True, indent = 4)
