import shutil

class Environment:
	def __init__(self):
		self.vars = {
			"variation": "debug"
		}

		if shutil.which("cl") and shutil.which("link") and shutil.which("lib"):
			self.vars["toolset_msvc"] = "true"
		if shutil.which("clang"):
			self.vars["toolset_clang"] = "true"
		if shutil.which("gcc") and shutil.which("g++"):
			self.vars["toolset_gcc"] = "true"

		if self.vars.get("toolset_msvc"):
			self.vars["toolset"] = "msvc"
		elif self.vars.get("toolset_clang"):
			self.vars["toolset"] = "clang"
		elif self.vars.get("toolset_gcc"):
			self.vars["toolset"] = "gcc"
		else:
			raise ValueError("cant find any compiler")