# BuildFox ninja generator

import os
import glob

def selftest_setup():
	with open("__selftest_build.fox", "w") as f:
		f.write("""
build objects(__selftest_src): auto __selftest_src.cpp
build application(__selftest_app): auto objects(__selftest_src)
""")

	with open("__selftest_src.cpp", "w") as f:
		f.write("""
#include <iostream>
int main()
{
	std::cout << "Hello from test app !\\n";
	return 0;
}
""")

	return ("__selftest_build.fox", "__selftest_build.ninja", "__selftest_app")

def selftest_wipe():
	for filename in glob.glob("__selftest_*.*"):
		os.remove(filename)
	os.remove(".ninja_deps")
	os.remove(".ninja_log")
