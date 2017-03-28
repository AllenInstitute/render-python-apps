import json
import argparse

class JsonModuleArgParseError(Exception):
    def __init___(self,dErrorArguments):
        Exception.__init__(self,"JsonModuleArgParseError raised with arguments {0}".format(dErrArguments))
        self.dErrorArguments = dErrorArguements

def merge(a, b, path=None):
    "merges b into a"
    if path is None: path = []
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                merge(a[key], b[key], path + [str(key)])
            elif a[key] == b[key]:
                pass # same leaf value
            elif b[key] is None:
                pass
            else:
                print 'setting',key
                a[key] = b[key]
                #raise Exception('Conflict at %s' % '.'.join(path + [str(key)]))
        else:
            if b[key] is None:
                pass
            else:
                print 'setting',key
                a[key] = b[key]
    return a

def default_args_to_dict(argsobj):
    d = {}
    argsdict = vars(argsobj)
    for field in argsdict.keys():
        parts = field.split('.')
        root = d
        for i in range(len(parts)):
            if i == (len(parts)-1):
                root[parts[i]]=argsdict.get(field,None)
            else:
                if parts[i] not in root.keys():
                    root[parts[i]]={}
                root=root[parts[i]]
    return d

class JsonRunnableModule():
    def __init__(self,parser,example_json={},args_to_dict=default_args_to_dict,validate_args=False):
        parser.add_argument('--inputJson',help='json based input argument file',type=str)
        self.argsobj = parser.parse_args()
        self.example_json = example_json
        if self.argsobj.inputJson is None:
            jsonargs = example_json
        else:
            jsonargs = json.load(open(self.argsobj.inputJson,'r'))

        argsdict = args_to_dict(self.argsobj)   
        self.args = merge(jsonargs,argsdict)
        if validate_args:
            self.validate_args()

    def run(self):
        print "running! with args"
        print json.dumps(self.args,indent=4)


    def validate_args(self):
        argsdict = vars(self.argsobj)
        fields = [field for field in argsdict.keys() if field != 'inputJson']
        for field in fields:
            parts = field.split('.')
            root = self.args
            for i in range(len(parts)):
                if i == (len(parts)-1):
                    arg=root.get(parts[i],None)
                    if arg is None:
                        raise JsonModuleArgParseError("%s not defined"%field)
                else:
                    root=root.get(parts[i],None)
                    if root is None:
                        raise JsonModuleArgParseError("%s not a section"%parts[:i])
import renderapi
class RenderModule(JsonRunnableModule):
    
    def __init__(self,parser,example_json={}):

        render_example ={
            "host":"ibs-forrestc-ux1",
            "port":8080,
            "owner":"Forrest",
            "project":"M247514_Rorb_1",
            "client_scripts":"/pipeline/render/render-ws-java-client/src/main/scripts"
        }
        if 'render' not in example_json.keys():
            example_json['render']=render_example

        parser.add_argument('--render.host',help='render host')
        parser.add_argument('--render.port',help='render port')
        parser.add_argument('--render.owner',help='render owner')
        parser.add_argument('--render.project',help='render project')
        parser.add_argument('--render.client_scripts',help='render client scripts directory')
        JsonRunnableModule.__init__(self,parser,example_json=example_json)
        self.render = renderapi.render.connect(**self.args['render'])

class GetZValuesForStack(RenderModule):
    """example of a subclassing my example JsonModule subclass"""
    def __init__(self, parser, *args,**kwargs):
        parser.add_argument('--stack',help="name of stack to get zvalues",type=str)
        RenderModule.__init__(self,parser,*args,**kwargs)

    def run(self):
        print "running with"
        print json.dumps(self.args,indent=4)
        zvalues=self.render.run(renderapi.stack.get_z_values_for_stack,self.args['stack'])
        print zvalues

class MyExampleModule(JsonRunnableModule):
    def __init__(self,parser,example_json=None):
        JsonRunnableModule.__init__(self,parser,example_json=example_json)
    def run(self):
        print "my own run method! with args"
        print json.dumps(self.args,indent=4)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = "This is an example dummy module")

    example_json = {
        'stack':'REGFLATDAPI_1_deconv'
    }
    module = GetZValuesForStack(parser,example_json=example_json)
    module.run()