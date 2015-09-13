# BuildFox

Minimalistic ninja generator

WIP document
 
### Manifest

BuildFox manifest is a super set to ninja manifest.

Core features are :

- variable filtering
- regex/wildcard file names

Example :

	# filtering	
	# value in filter could be wildcard or regex
	# TODO var-value-var-value separators
	filter var1:value_or_wildcard_or_regex var2:value_or_wildcard_or_regex
		var3 = value
		...
	
	# wildcard file names
	build *.exe: auto *.c

	# regex file names
	build r"\1\.exe": auto r"(.+)\.c"

