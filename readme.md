# BuildFox [![Build Status](https://travis-ci.org/beardsvibe/buildfox.svg?branch=master)](https://travis-ci.org/beardsvibe/buildfox) [![Build status](https://ci.appveyor.com/api/projects/status/kj1pa6f94889mxna/branch/master?svg=true)](https://ci.appveyor.com/project/jimon/buildfox/branch/master) [![Coverage Status](https://coveralls.io/repos/beardsvibe/buildfox/badge.svg?branch=master&service=github)](https://coveralls.io/github/beardsvibe/buildfox?branch=master)

Minimalistic ninja generator

**This project is a WIP**

### Example

	build obj(*): auto *.cpp
	build app(helloworld): auto obj(*)

### Usage

Building project

	bf && ninja

Generating IDE solution

	bf --ide vs # this will autoselect proper version of vs
	bf --ide vs2012
	bf --ide vs2013
	bf --ide vs2015
	bf --ide qtcreator
	bf --ide cmake # for cmake based IDE's
	bf --ide make # useful in some cases

### Resources

- [Manual](docs/manual.md)

### Installation

- Get [ninja](https://martine.github.io/ninja/) (v1.3+ is supported, v1.6 is recommended)
- Get [python](https://www.python.org/) (v2.7+ is supported, v3.5 is recommended)
- Run ```pip install buildfox```
- If pip installs locally (for example on Ubuntu) you need to add ```export PATH=$PATH:/home/$USER/.local/bin/``` to .bashrc
- Run ```bf --selftest``` to make sure everything is ok
- Done!

### Using from source

- Make alias ```bf``` for ```python buildfox.py``` command
	- On Windows it's ```doskey bf=python %path_to_the_repo%\buildfox.py $*```
- Run ```bf --selftest``` to make sure everything is ok
- Done!
