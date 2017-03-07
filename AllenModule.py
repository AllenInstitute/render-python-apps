import json
import argparse

def merge_two_dicts(x, y):
    """Given two dicts, merge them into a new dict as a shallow copy."""
    z = x.copy()
    z.update(y)
    return z

def args_to_dict(argsobj):
	fields=[a for a in dir(argsobj) if not a.startswith('__')]
	print fields
	
def JsonRunnableModule():
	def __init__(self,parser,example_json=None,args_to_dict=None):
		parser.add_argument('--inputJson',help='json based input argument file',type=str)
		argsobj = parser.parse_args()
	    
	    if args.inputJson is None:
	    	if example_json is None:
	    		raise 
	    	else:
		        jsonargs = example_json
	    else:
	        jsonargs = json.load(open(args.inputJson,'r'))

	    if args_to_dict is None:
		    argdict = vars(argsobj)
		else:
			argdict = args_to_dict(argsobj)


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description = "This is an example dummy module")
	parser.add_argument('--a',help='a level one arguments',type=str,default='bar')
	parser.add_argument('--subsection-a',help='a subsection argument',type=str,default='foo')
	parser.add_argument('--subsection-b',help='a subsection argument',type=str,default='foo2')
