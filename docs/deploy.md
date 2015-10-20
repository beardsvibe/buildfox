### How to deploy

- Make sure everything works, pass tests, etc
- Increment version in ```lib_version.py```
- Build module by running ```python deploy.py```
- Copy ```__init__.py``` to ```buildfox``` package folder in the repository
- Try ```python setup.py install``` and check that everything works by ```bf --selftest```. Afterwards uninstall it with ```pip uninstall -y buildfox```.
- Create a new tag.
- Edit GitHub release notes.
- Upload package to PyPI by running ```python setup.py sdist bdist_wininst upload```
