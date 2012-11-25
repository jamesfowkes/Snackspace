import inspect
import os.path

def debugPrint(string):
	filepath = inspect.stack()[1][1]
	filename = os.path.basename(filepath)
	funcname = inspect.stack()[1][3]
	print("%s\\%s: %s" % (filename, funcname, string))
