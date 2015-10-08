#!/usr/bin/python3

import os
import sys
import json
import glob
import fnmatch
import argparse
import traceback
import subprocess
from pprint import pprint
from deepdiff import DeepDiff # pip install deepdiff

sys.path.append("..")
from lib_parser import parse
from lib_engine import Engine

class EngineMock:
	def __init__(self):
		self.output = []

	def fix_assigns(self, assign):
		return [list(t) for t in assign]

	def on_empty_lines(self, lines):
		self.output.append({
			"empty_lines": lines
		})

	def on_comment(self, comment):
		self.output.append({
			"comment": comment
		})

	def on_rule(self, obj, assigns):
		self.output.append({
			"rule": obj,
			"assigns": self.fix_assigns(assigns)
		})

	def on_build(self, obj, assigns):
		self.output.append({
			"build": obj[2],
			"targets_explicit": obj[0],
			"targets_implicit": obj[1],
			"inputs_explicit": obj[3],
			"inputs_implicit": obj[4],
			"inputs_order": obj[5],
			"assigns": self.fix_assigns(assigns)
		})

	def on_default(self, obj):
		self.output.append({
			"default": obj
		})

	def on_pool(self, obj, assigns):
		self.output.append({
			"pool": obj,
			"assigns": self.fix_assigns(assigns)
		})

	def filter(self, obj):
		self.output.append({
			"filter": [list(t) for t in obj]
		})

	def on_auto(self, obj, assigns):
		self.output.append({
			"auto": obj[1],
			"outputs": obj[0],
			"inputs": obj[2],
			"assigns": self.fix_assigns(assigns)
		})

	def on_print(self, obj):
		self.output.append({
			"print": obj
		})

	def on_assign(self, obj):
		self.output.append({
			"assign": list(obj)
		})

	def on_transform(self, obj):
		self.output.append({
			"transform": obj[0],
			"pattern": obj[1]
		})

	def on_include(self, obj):
		self.output.append({
			"include": obj
		})

	def on_subninja(self, obj):
		self.output.append({
			"subninja": obj
		})

def run_test(test_filename, print_json = False, print_ninja = False):
	print("-> Testing %s" % test_filename)
	try:
		json_filename = os.path.splitext(test_filename)[0] + ".json"
		json_exists = os.path.isfile(json_filename)
		if json_exists or print_json:
			engine = EngineMock()
			parse(engine, test_filename)
			if print_json:
				print("--- JSON ---------------------")
				print(json.dumps(engine.output, sort_keys = True, indent = "\t"))
				print("--- JSON END -----------------")
			if json_exists:
				with open(json_filename, "r") as f:
					reference = json.loads(f.read())
					if sys.version_info[0] < 3:
						def byteify(input):
							if isinstance(input, dict):
								return {byteify(key): byteify(value) for key,value in input.iteritems()}
							elif isinstance(input, list):
								return [byteify(element) for element in input]
							elif isinstance(input, unicode):
								return input.encode("utf-8")
							else:
								return input
						reference = byteify(reference)
				diff = DeepDiff(reference, engine.output)
				if diff:
					print("Results differ from reference:")
					pprint(diff)
					return False

		ninja_filename = os.path.splitext(test_filename)[0] + ".ninja"
		ninja_exists = os.path.isfile(ninja_filename)
		if ninja_exists or print_ninja:
			engine = Engine()
			engine.load(test_filename, logo = False)
			if print_ninja:
				print("--- NINJA --------------------")
				print(engine.text())
				print("--- NINJA END ----------------")
			if ninja_exists:
				with open(os.path.splitext(test_filename)[0] + ".ninja", "r") as f:
					reference = f.read()
				diff = DeepDiff(reference, engine.text())
				if diff:
					print("Results differ from reference:")
					pprint(diff)
					return False

		if not (json_exists or print_json or ninja_exists or print_ninja):
			print("json and ninja files are not present")
			return False

		return True
	except:
		err = sys.exc_info()[0]
		print("Exception error: %s" % err)
		traceback.print_exc()
		return False

def run_suite(args):
	results = []
	for test_filename in glob.glob(args.get("in")):
		result = run_test(test_filename.replace("\\", "/"), args.get("json"), args.get("ninja"))
		results.append(result)
		if args.get("failfast") and not result:
			break

	if not all(results):
		print("One or more tests from test suite failed")
		if not args.get("dry"):
			sys.exit(1)
	else:
		print("All suite tests are done.")

def find_files(directory, pattern):
	for root, dirs, files in os.walk(directory):
		for basename in files:
			if fnmatch.fnmatch(basename, pattern):
				filename = os.path.join(root, basename)
				yield filename

def build_examples(args):
	results = []
	for fox_file in find_files("../examples", "*.fox"):
		fox_file = fox_file.replace("\\", "/")
		print("-> Testing %s" % fox_file)
		def test_with_toolset(name):
			return not subprocess.call(["coverage", "run", "--source=..", "--parallel-mode",
				"../buildfox.py", "-i", fox_file, "toolset_%s=true" % name, "toolset=%s" % name])
		results.extend([test_with_toolset(name) for name in ["clang", "gcc", "msvc"]])
		if args.get("failfast") and not result:
			break

	if not all(results):
		print("One or more tests from examples failed")
		if not args.get("dry"):
			sys.exit(1)
	else:
		print("All examples tests are done.")

argsparser = argparse.ArgumentParser(description = "buildfox test suite")
argsparser.add_argument("-i", "--in", help = "Test inputs", default = "suite/*.fox")
argsparser.add_argument("--dry", action = "store_true",
	help = "Ignore tests failures", default = False, dest = "dry")
argsparser.add_argument("--json", action = "store_true",
	help = "Print json output from parser", default = False, dest = "json")
argsparser.add_argument("--ninja", action = "store_true", help = "Print ninja output from engine", default = False, dest = "ninja")
argsparser.add_argument("--fail-fast", action = "store_true",
	help = "Abort after first failure", default = False, dest = "failfast")
argsparser.add_argument("--no-suite", action = "store_false",
	help = "Do not run test suite", default = True, dest = "suite")
argsparser.add_argument("--no-examples", action = "store_false",
	help = "Do not build examples", default = True, dest = "examples")
args = vars(argsparser.parse_args())

# TODO clean up temporary ninja files in current working dir

if args.get("suite"):
	run_suite(args)

if args.get("examples"):
	build_examples(args)
