# BuildFox ninja generator

import re

MAJOR = 1
MINOR = 0
VERSION = "%d.%d" % (MAJOR, MINOR)

# Simple major.minor matcher
re_version = re.compile(r"^(\d+)\.(\d+)$")

def parse(version):
	match = re_version.match(version)
	if match:
		return int(match.group(1)), int(match.group(2))
	else:
		return None

def check(required_version):
	required_major, required_minor = parse(required_version)
	if MAJOR > required_major:
		print("WARNING: buildfox executable major version (%s) is greater than 'buildfox_required_version' (%s).\nVersions may be incompatible." % (VERSION, required_version))
		return
	if (required_major == MAJOR and required_minor > MINOR) or required_major > MAJOR:
		raise RuntimeError("buildfox version (%s) is incompatible with the version required (%s)." % (VERSION, required_version))
