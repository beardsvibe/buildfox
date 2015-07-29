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

pool_cl = []
pool_generic = []

import shlex
for i, command in enumerate(asm):
	cmd = shlex.split(command["cmd"])
	tool = os.path.splitext(os.path.basename(cmd[0]))[0].lower()
	program = cmd[0]

	# wip
	if tool == "cl":
		args = set()
		files = []
		output_files = []
		link = False
		link_args = set()
		link_files = []
		link_output_files = []

		for arg in cmd[1:]:
			if arg.startswith("/") or arg.startswith("-"):
				arg = "/" + arg[1:]
				if arg == "/link":
					link = True
					continue
				elif link == False and arg.startswith("/Fo"):
					output_files.append(arg[3:])
				elif link == True and arg.startswith("/out:"):
					link_output_files.append(arg[4:])
				elif link == False:
					args.add(arg)
				else:
					link_args.add(arg)
			else:
				if link == False:
					files.append(arg)
				else:
					link_files.append(arg)

		all = {
			"index": i,
			"program": program,
			"args": args,
			"files": files,
			"output_files": output_files,
			"link": link,
			"link_args": link_args,
			"link_files": link_files,
			"link_output_files": link_output_files
		}

		pool_cl.append(all)

	else:
		all = {
			"index": i,
			"program": program,
			"args": cmd[1:],
		}

		pool_generic.append(all) 



#with open(args["output"], "w") as f:
#	json.dump(output, f, sort_keys = True, indent = 4)
