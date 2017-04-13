from json_module import JsonModule,ModuleParameters
import marshmallow as mm

class NestedExampleParameters(ModuleParameters):
    a = mm.fields.Str(required=True,metadata={'description':'help statement for parameter nested.a'})
    b = mm.fields.Int(required=True,metadata={'description':'help statement for parameter nested.b'})
  
class ExampleParameters(ModuleParameters):
    nested = mm.fields.Nested(NestedExampleParameters)
    c = mm.fields.Int(required=False, default=0,
                      metadata={'description':'help statement for parameter c'})

class ExampleModule(JsonModule):
    def __init__(self,*args,**kwargs):
        super(ExampleModule,self).__init__(schema_type = ExampleParameters,*args,**kwargs)
        print self.args
        #do some setup stuff here for your module making use of self.args dictionary
    def run(self):
        #run your module
        self.logger.info("my module is starting")
        print self.args['nested']['a']
        print self.args['nested']['b']
        print self.args['c']

if __name__ == '__main__':
    example_input={
        "nested":{
            "a":"a value",
            "b":100,
        },
        "c":1
    }
    module = ExampleModule(input_data=example_input)
    module.run()
