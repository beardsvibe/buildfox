# Qbs

Qbs language is very similar to QML.

All Qbs docs are a bit fuzzy so let's leave it like this for a while.

### Grammar

	import qbs 1.0

	Application {
		name: "helloworld"
		files: "main.cpp"
		Depends { name: "cpp" }
	}

	Product {
		property string craziness: "low"
	}

	import "CrazyProduct.qbs" as CrazyProduct
	CrazyProduct {
		craziness: "enormous"
		name: "hellocrazyworld"
		// ...
	}

	// apparently you can execute javascript here