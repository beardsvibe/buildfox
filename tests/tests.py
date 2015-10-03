# Parser test suite

import os
import sys
import json
import glob
import traceback
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

	def on_default(self, obj, assigns):
		self.output.append({
			"default": obj,
			"assigns": self.fix_assigns(assigns)
		})

	def on_pool(self, obj, assigns):
		self.output.append({
			"pool": obj,
			"assigns": self.fix_assigns(assigns)
		})

	def filter(self, obj):
		self.output.append({
			"filter": obj
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

any_failed = False
for test_filename in glob.glob("suite/*.in"):
	print("---------------------------------------- testing %s" % test_filename)
	try:
		with open(os.path.splitext(test_filename)[0] + ".json", "r") as f:
			reference = json.loads(f.read())
		engine = EngineMock()
		parse(engine, test_filename)
		diff = DeepDiff(reference, engine.output)
		if diff:
			print("results are differ from reference : ")
			pprint(diff)
			any_failed = True

		with open(os.path.splitext(test_filename)[0] + ".ninja", "r") as f:
			reference = f.read()
		engine = Engine()
		engine.load(test_filename, logo = False)
		diff = DeepDiff(reference, engine.text())
		if diff:
			print("results are differ from reference : ")
			pprint(diff)
			any_failed = True
	except:
		err = sys.exc_info()[0]
		print("exception error : %s" % err)
		traceback.print_exc()
		any_failed = True

# TODO clean up temporary ninja files in current working dir

if any_failed:
	print("one or more tests failed")
	sys.exit(1)
else:
	print("done")