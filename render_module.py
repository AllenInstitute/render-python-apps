from json_module import JsonModule,ModuleParameters,InputDir
import marshmallow as mm
import renderapi
import os
import subprocess

class RenderClientParameters(mm.Schema):
    host = mm.fields.Str(required=True,metadata={'description':'render host'})
    port = mm.fields.Int(required=True,metadata={'description':'render post integer'})
    owner = mm.fields.Str(required=True,metadata={'description':'render default owner'})
    project = mm.fields.Str(required=True,metadata={'description':'render default project'})
    client_scripts = mm.fields.Str(required=True,metadata={'description':'path to render client scripts'})
    memGB = mm.fields.Str(required=False,default='5G',metadata={'description':'string describing java heap memory (default 5G)'})

class RenderParameters(ModuleParameters):
    render = mm.fields.Nested(RenderClientParameters)

class RenderTrakEM2Parameters(RenderParameters):
    renderHome = InputDir(required=True,metadata={'description':'root path of standard render install'})


class TEM2ProjectTransfer(RenderTrakEM2Parameters):
    minX = mm.fields.Int(required=True,metadata={'description':'minimum x'})
    minY = mm.fields.Int(required=True,metadata={'description':'minimum y'})
    maxX = mm.fields.Int(required=True,metadata={'description':'maximum x'})
    maxY = mm.fields.Int(required=True,metadata={'description':'maximum y'})
    minZ = mm.fields.Int(required=False,metadata={'description':'minimum z'})
    maxZ = mm.fields.Int(required=False,metadata={'description':'maximum z'})
    inputStack = mm.fields.Str(required=True,metadata={'description':'stack to import from'})
    outputStack = mm.fields.Str(required=True,metadata={'description':'stack to output to'})
    outputXMLdir = mm.fields.Str(required=True,metadata={'description':'path to save xml files'})
    doChunk = mm.fields.Boolean(required=False,default=False,metadata={'description':'split the input into chunks'})
    chunkSize = mm.fields.Int(required=False,default=50,metadata={'description':'size of chunks'})

class EMLMRegistrationParameters(TEM2ProjectTransfer):
    LMstack = mm.fields.Str(required=True,metadata={'description':'name of LM stack to use for registration'})
    minX = mm.fields.Int(required=False,metadata={'description':'minimum x (default to EM stack bounds)'})
    minY = mm.fields.Int(required=False,metadata={'description':'minimum y (default to EM stack bounds)'})
    maxX = mm.fields.Int(required=False,metadata={'description':'maximum x (default to EM stack bounds)'})
    maxY = mm.fields.Int(required=False,metadata={'description':'maximum y (default to EM stack bounds)'})
    minZ = mm.fields.Int(required=False,metadata={'description':'minimum z (default to EM stack bounds)'})
    maxZ = mm.fields.Int(required=False,metadata={'description':'maximum z (default to EM stack bounds)'})



class RenderModule(JsonModule):
    def __init__(self,schema_type=None,*args,**kwargs):
        if schema_type is None:
            schema_type = RenderParameters
        super(RenderModule,self).__init__(schema_type = schema_type,*args,**kwargs)
        self.render=renderapi.render.connect(**self.args['render'])

class TrakEM2RenderModule(RenderModule):
    def __init__(self,schema_type=None,*args,**kwargs):
        if schema_type is None:
            schema_type = RenderTrakEM2Parameters
        super(TrakEM2RenderModule,self).__init__(schema_type=schema_type,*args,**kwargs)
        jarDir = os.path.join(self.args['renderHome'],'render-app','target')
        self.renderjarFile = next(os.path.join(jarDir,f) for f in os.listdir(jarDir) if f.endswith('jar-with-dependencies.jar'))
        self.trakem2cmd = ['java','-cp',renderjarFile,'org.janelia.alignment.trakem2.Converter']


    def convert_trakem2_project(self,xmlFile,projectPath,json_path):
        cmd = self.trakem2cmd + ['%s'%xmlFile,'%s'%projectPath,'%s'%json_path]
        proc=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        while proc.poll() is None:
            line = proc.stdout.readline()
            if 'ERROR' in line:
                self.logger.error(line)
            else:    
                self.logger.debug(line)
        while proc.poll() is None:
            line = proc.stdout.readline()
            if 'ERROR' in line:
                self.logger.error(line)
            else:
                self.logger.debug(line)    



if __name__ == '__main__':
    example_input={
        "render":{
            "host":"ibs-forrestc-ux1",
            "port":8080,
            "owner":"NewOwner",
            "project":"H1706003_z150",
            "client_scripts":"/pipeline/render/render-ws-java-client/src/main/scripts"
        }
    }
    module = RenderModule(input_data=example_input)
    module.run()

    bad_input={
        "render":{
            "host":"ibs-forrestc-ux1",
            "port":'8080',
            "owner":"Forrest",
            "project":"H1706003_z150",
            "client_scripts":"/pipeline/render/render-ws-java-client/src/main/scripts"
        }
    }
    module = RenderModule(input_data=bad_input)
    module.run()