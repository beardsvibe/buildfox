# Compact IR format

### Intro

Some WIP stuff on better IR format

From [this](https://github.com/martine/ninja/blob/master/src/build_log_perftest.cc#L42-L61) we know :

	The average command length is 4.1 kB and there were 28674 commands in total,
	which makes for a total log size of ~120 MB (also counting output filenames).

Let's make some goals :

* Parse raw 120 MB shell script into compact IR format in less then 1 second on modern machine with SSD.
* Translate this compacted IR file into raw 120 MB shell script in less then 1 second on modern machine with SSD.
* Parsing and saving of compact IR file without need to reconstruct all data in memory before reading.
* Human readable format **???**
* Easily generated from existing build systems

### Gathering stuff

* Average command is long, but contains many common parts. In best case all arguments will be equal but filenames.
Many make-like build systems incorporate this as rules or macro.
* Programs can be divided into three types :
	* care about argument order
	* don't care about argument order
	* partially care about argument order
* We can't generally figure out if argument is filename or not (requires explicit knowledge about executed tool)

We can take split command line, take arguments, and find common sets. 
In some cases (mostly compilers\linkers) we can extract input and output filenames.

### Format structure
