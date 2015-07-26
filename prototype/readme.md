# mask prototype

So what's going on here ?

* **mask_compiler.py** translates mask IR (similar to ninja) into **unsorted mask asm**
* **mask\_tool\_sort\_in\_exec\_order.py** generates **sorted mask asm** from **unsorted mask asm**
* **mask\_gen\_ninja.py** translates **mask asm** into **ninja build file**
* **mask\_gen\_shell.py** translates **sorted mask asm** into **shell script**

> What is mask IR ?

Read previous proposal

> What is mask asm ?

mask asm is a json with structure :

	[
		{
			"cmd": "%command_line%",
			"depend_on": [ "%file%", "%file%", ... ]
			"touch": [ "%file%", "%file%", ... ]
		}
		...
	]

