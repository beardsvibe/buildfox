# ------------------------------------ writing helper

def to_string(ir):
	return str(ir)

def to_file(filename, ir):
	with open(filename, "w") as f:
		f.write(to_string(ir))
