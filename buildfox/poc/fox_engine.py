# fox core

from fox_parser2 import Parser
from pprint import pprint

class Engine:
	def __init__(self):
		pass

	def rule(self, obj, assigns):
		pprint((obj, assigns))
	def build(self, obj, assigns):
		pprint((obj, assigns))
	def default(self, obj, assigns):
		pprint((obj, assigns))
	def pool(self, obj, assigns):
		pprint((obj, assigns))
	def include(self, obj, assigns):
		pprint((obj, assigns))
	def subninja(self, obj, assigns):
		pprint((obj, assigns))
	def filter(self, obj): # return True/False
		return True
	def auto(self, obj, assigns):
		pprint((obj, assigns))
	def assign(self, obj):
		pprint(obj)

e = Engine()
p = Parser(e, "fox_core.fox")
p.parse()