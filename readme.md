# BuildFox [![Build Status](https://travis-ci.org/beardsvibe/buildfox.svg?branch=master)](https://travis-ci.org/beardsvibe/buildfox) [![Coverage Status](https://coveralls.io/repos/beardsvibe/buildfox/badge.svg?branch=master&service=github)](https://coveralls.io/github/beardsvibe/buildfox?branch=master)

Minimalistic ninja generator

**This project is a WIP**

### Example

	build obj(*): auto *.cpp
	build app(helloworld): auto obj(*)

### Installation

- Get [ninja](https://martine.github.io/ninja/) (v1.3+ is supported, v1.6 is recommended)
- Get [python](https://www.python.org/) (v2.7+ is supported, v3.5 is recommended)
- Get [buildfox latest release](https://github.com/beardsvibe/buildfox/releases/download/v0.1-dev/buildfox)
- Put buildfox file in folder that accessible from PATH (optional)
- For *nix run ```chmod +x buildfox```
- For Windows add this to your terminal ```doskey buildfox=python buildfox $*```
- Run ```buildfox --selftest``` to make sure everything is ok
- Done !

### Usage

	buildfox
	ninja

### Resources

- [Manual](docs/manual.md)
