# BuildFox [![Build Status](https://travis-ci.org/beardsvibe/buildfox.svg?branch=master)](https://travis-ci.org/beardsvibe/buildfox) [![Build status](https://ci.appveyor.com/api/projects/status/kj1pa6f94889mxna/branch/master?svg=true)](https://ci.appveyor.com/project/jimon/buildfox/branch/master) [![Coverage Status](https://coveralls.io/repos/beardsvibe/buildfox/badge.svg?branch=master&service=github)](https://coveralls.io/github/beardsvibe/buildfox?branch=master)

Minimalistic ninja generator

**This project is a WIP**

### Example

	build obj(*): auto *.cpp
	build app(helloworld): auto obj(*)

### Usage

	bf && ninja

### Resources

- [Manual](docs/manual.md)

### Installation

- Get [ninja](https://martine.github.io/ninja/) (v1.3+ is supported, v1.6 is recommended)
- Get [python](https://www.python.org/) (v2.7+ is supported, v3.5 is recommended)
- Get [buildfox latest release](https://github.com/beardsvibe/buildfox/releases/download/v0.1-dev/bf)
- Put bf file in folder that accessible from PATH (optional)
- For *nix run ```chmod +x bf```
- For Windows add this to your terminal ```doskey bf=python %path_to_buildfox%/bf $*```
- Run ```bf --selftest``` to make sure everything is ok
- Done!

### Building from source

- Go to tools directory
- Run ```python deploy.py```
- You will get bf file in tools folder
- Run ```bf --selftest``` to make sure everything is ok
- Done!
