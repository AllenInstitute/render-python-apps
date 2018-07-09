import argschema
from AnnotationJsonSchema import AnnotationFile
import renderapi
import numpy as np
import pandas as pd
from ..module.render_module import RenderParameters, RenderModule

example_input = {
    "render": {
        "host": "ibs-forrestc-ux1",
        "port": 8080,
        "owner": "Forrest",
        "project": "M247514_Rorb_1",
        "client_scripts": "/pipeline/render/render-ws-java-client/src/main/scripts"
    },
    "stack": "ALIGNEM_reg2",
    "csv_file": "/Users/forrestcollman/AnishCsvDetections/resultVol_3.txt",
    "json_file": "/Users/forrestcollman/AnishCsvDetections/resultVol_3.json",
}

class MakeAnnotationFileAnishParameters(RenderParameters):
    stack = argschema.fields.Str(required=True,
        description="name of render stack annotations were derived from")
    csv_file = argschema.fields.InputFile(required=True,
        description="path to csv file in anish's format")
    json_file = argschema.fields.OutputFile(required=True,
        description="location of output file to save annotation")
    pixel_size = argschema.fields.Float(required=False,default = 100.0/3.0)
 
class MakeAnnotationFileAnish(RenderModule):
    default_schema = MakeAnnotationFileAnishParameters

    def run(self):
        #open the csv file
        with open(self.args['csv_file'],'r') as fp:
            df = pd.DataFrame()
            indices = []
            coords = []

            for i,line in enumerate(fp):
                vals=np.array(map(int,line.split(',')[:-1]))
                N = len(vals)
                Np = N/3
                vals = np.reshape(vals,(Np,3))
                indices.append((i+1)*np.ones(vals.shape[0],np.uint64))
                coords.append(vals)
            coords = np.vstack(coords)
            df = pd.DataFrame(coords)
            df.columns=['x','y','z']
            df['ind']=np.hstack(indices)
        #find all the unique synapseIDs
        synapses = df.groupby('ind')
        for ind,dfg in synapses:
            zsections = dfg.groupby('z')
            for z,dfgz in zsections:
                print(dfgz)
            break
        #loop over them, constructing a dictionary according to AnnotationFile schema

        #save result to json_file


if __name__ == '__main__':
    mod = MakeAnnotationFileAnish(input_data = example_input, args=[])
    mod.run()

