# Parser test suite

import sys
import json

sys.path.append("..")

from lib_parser import parse

class EngineMock:
	def __init__(self):
		self.output = []

	def on_comment(self, comment):
		self.output.append({"comment": comment})

	def on_rule(self, obj, assigns):
		self.output.append({"rule": obj, "assigns": assigns})

	def on_build(self, obj, assigns):
		self.output.append({
			"build": obj[2],
			"targets_explicit": obj[0],
			"targets_implicit": obj[1],
			"inputs_explicit": obj[3],
			"inputs_implicit": obj[4],
			"inputs_order": obj[5],
			"assigns": assigns
		})

	def on_default(self, obj, assigns):
		self.output.append({"default": obj, "assigns": assigns})

	def on_pool(self, obj, assigns):
		self.output.append({"pool": obj, "assigns": assigns})

	def filter(self, obj):
		self.output.append({"filter": obj})

	def on_auto(self, obj, assigns):
		self.output.append({"auto": obj[1], "outputs": obj[0], "inputs": obj[2], "assigns": assigns})

	def on_print(self, obj):
		self.output.append({"print": obj})

	def on_assign(self, obj):
		self.output.append({"assign": obj})

	def on_transform(self, obj):
		self.output.append({"transform": obj[0], "pattern": obj[1]})

	def on_include(self, obj):
		self.output.append({"include": obj})

	def on_subninja(self, obj):
		self.output.append({"subninja": obj})
