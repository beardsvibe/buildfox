# BuildFox ninja generator

import re

MAJOR = 0
MINOR = 3
VERSION = "%d.%d" % (MAJOR, MINOR)

# Simple major.minor matcher
re_version = re.compile(r"^(\d+)\.(\d+)$")

def version_check(required_version):
	match = re_version.match(required_version)

	if match:
		required_major = int(match.group(1))
		required_minor = int(match.group(2))
	else:
		raise ValueError("Specified required version %s has incorrect format, for example correct format is 1.0" % required_version)

	if MAJOR > required_major:
		print("WARNING: BuildFox executable major version %s is greater than 'buildfox_required_version' (%s).\nVersions may be incompatible" % (VERSION, required_version))
	elif (required_major == MAJOR and required_minor > MINOR) or required_major > MAJOR:
		raise RuntimeError("BuildFox version %s is incompatible with the version required %s" % (VERSION, required_version))
