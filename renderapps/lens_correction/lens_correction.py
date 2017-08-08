import os
import json
import subprocess
from argschema import ArgSchema, ArgSchemaParser
from argschema.fields import Bool, Float, Int, Nested, Str
from argschema.schemas import DefaultSchema
import renderapi

class SIFTParameters(DefaultSchema):
    initialSigma = Float(required=True,
        metadata={'description': ''})
    steps = Int(required=True,
        metadata={'description': ''})
    minOctaveSize = Int(required=True,
        metadata={'description': ''})
    maxOctaveSize = Int(required=True,
        metadata={'description': ''})
    fdSize = Int(required=True,
        metadata={'description': ''})
    fdBins = Int(required=True,
        metadata={'description': ''})

class OtherParameters(DefaultSchema):
    rod = Float(required=True,
        metadata={'description': ''})
    maxEpsilon = Float(required=True,
        metadata={'description': ''})
    minInlierRatio = Float(required=True,
        metadata={'description': ''})
    minNumInliers = Int(required=True,
        metadata={'description': ''})
    expectedModelIndex = Int(required=True,
        metadata={'description': ''})
    multipleHypotheses = Bool(required=True,
        metadata={'description': ''})
    rejectIdentity = Bool(required=True,
        metadata={'description': ''})
    identityTolerance = Float(required=True,
        metadata={'description': ''})
    tilesAreInPlace = Bool(required=True,
        metadata={'description': ''})
    desiredModelIndex = Int(required=True,
        metadata={'description': ''})
    regularize = Bool(required=True,
        metadata={'description': ''})
    maxIterationsOptimize = Int(required=True,
        metadata={'description': ''})
    maxPlateauWidthOptimize = Int(required=True,
        metadata={'description': ''})
    dimension = Int(required=True,
        metadata={'description': ''})
    lambdaVal = Float(required=True,
        metadata={'description': ''})
    clearTransform = Bool(required=True,
        metadata={'description': ''})
    visualize = Bool(required=True,
        metadata={'description': ''})

class LensCorrectionParameters(ArgSchema):
    manifest_path = Str(required=True,
        metadata={'description': 'path to manifest file'})
    project_path = Str(required=True,
        metadata={'description': 'path to project directory'})
    SIFT_params = Nested(SIFTParameters)
    other_params = Nested(OtherParameters)

class LensCorrectionModule(ArgSchemaParser):
    def __init__(self, *args, **kwargs):
        super(LensCorrectionModule, self).__init__(schema_type = 
            LensCorrectionParameters, *args, **kwargs)

    def run(self):
        bsh_call = ["xvfb-run",
            "-a",
            "Fiji.app/ImageJ-linux64",
            "-Xms20g", "-Xmx20g", "-Xincgc",
            "-Dfile=" + self.args['manifest_path'],
            "-Ddir=" + self.args['project_path'],
            "-Disig=" + str(self.args['SIFT_params']['initialSigma']),
            "-Dsteps=" + str(self.args['SIFT_params']['steps']),
            "-Dminos=" + str(self.args['SIFT_params']['minOctaveSize']),
            "-Dmaxos=" + str(self.args['SIFT_params']['maxOctaveSize']),
            "-Dfdsize=" + str(self.args['SIFT_params']['fdSize']),
            "-Dfdbins=" + str(self.args['SIFT_params']['fdBins']),
            "-Drod=" + str(self.args['other_params']['rod']),
            "-Dmaxe=" + str(self.args['other_params']['maxEpsilon']),
            "-Dmir=" + str(self.args['other_params']['minInlierRatio']),
            "-Dmni=" + str(self.args['other_params']['minNumInliers']),
            "-Demi=" + str(self.args['other_params']['expectedModelIndex']),
            "-Dmh=" + str(self.args['other_params']['multipleHypotheses']),
            "-Dri=" + str(self.args['other_params']['rejectIdentity']),
            "-Dit=" + str(self.args['other_params']['identityTolerance']),
            "-Dtaip=" + str(self.args['other_params']['tilesAreInPlace']),
            "-Ddmi=" + str(self.args['other_params']['desiredModelIndex']),
            "-Dreg=" + str(self.args['other_params']['regularize']),
            "-Dmio=" + 
                str(self.args['other_params']['maxIterationsOptimize']),
            "-Dmpwo=" + 
                str(self.args['other_params']['maxPlateauWidthOptimize']),
            "-Ddim=" + str(self.args['other_params']['dimension']),
            "-Dlam=" + str(self.args['other_params']['lambdaVal']),
            "-Dctrans=" + str(self.args['other_params']['clearTransform']),
            "-Dvis=" + str(self.args['other_params']['visualize']),
            "--", "--no-splash",
            "run_lens_correction.bsh"]

        subprocess.call(bsh_call)
        
if __name__ == '__main__':
    with open("input_lens_correction.json", "r") as json_file:
        example_input = json.load(json_file)

    module = LensCorrectionModule(input_data = example_input)
    module.run()