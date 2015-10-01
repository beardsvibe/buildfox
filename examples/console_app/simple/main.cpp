#include <stdio.h>
#include "test1.h"
#include "test2.h"
#include "test 3.h"

int main()
{
	#if defined(RELEASE)
		printf("hello real world !\n");
	#else
		printf("hello dev world !\n");
	#endif
	test1();
	test2();
	test3();
	return 0;
}