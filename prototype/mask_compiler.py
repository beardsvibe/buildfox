# mask compiler
# accepts mask IR, generates list of shell commands with dependency information

from pprint import pprint
import mask_ir

text = """
k = d
rule a
  command = abc $in $out
  e = f

# test

build a.txt:test b.txt
  lol = wow
build c.txt:test d.txt

"""

class Namescope:
	def __init__(self):
		self.vars = []
		self.rules = []
		self.build = []

	def var(self, var):
		self.vars.append(var)

	def rule(self, rule):
		self.rules.append({var_index: len(self.vars), rule: rule})

	def build(self, build):
		self.build.append({var_index: len(self.vars), build: build})

	def compile(self):
		pass

namescope = Namescope()
parser = mask_ir.mask_ir_Parser()
ast = parser.parse(text, rule_name = "manifest", whitespace = "")

for expr in ast:
	if "to" in expr:
		namescope.var(expr)
	elif "name" in expr:
		namescope.var(expr)
	elif "rule_name" in expr:
		namescope.var(expr)
	else:
		print("unknown " + str(expr))

namescope.compile()