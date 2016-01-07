#!/usr/bin/env python
from setuptools import setup
import sys

version = "0.2"
classifiers = [
	"Development Status :: 3 - Alpha",
	"Environment :: Console",
	"Intended Audience :: Developers",
	"Programming Language :: Python",
	"Programming Language :: Python :: 2.7",
	"Programming Language :: Python :: 3",
	"Programming Language :: Python :: 3.2",
	"Programming Language :: Python :: 3.3",
	"Programming Language :: Python :: 3.4",
	"Programming Language :: Python :: 3.5",
	"License :: OSI Approved :: MIT License",
	"Topic :: Software Development :: Build Tools"
]

setup(
	name="buildfox",
	version=version,
	description="Minimalistic ninja generator",
	long_description=None,
	classifiers=classifiers,
	keywords="buildfox bf ninja build tool c cpp",
	author="@beardsvibe",
	author_email="info@beardsvibe.com",
	url="https://github.com/beardsvibe/buildfox",
	license="https://github.com/beardsvibe/buildfox/blob/master/license",
	packages=["buildfox"],
	include_package_data=True,
	zip_safe=True,
	install_requires=[],
	tests_require=["unittest2"],
	entry_points={'console_scripts': ['bf=buildfox:main']}
)
