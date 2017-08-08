import os
import json
from argschema import ArgSchema, ArgSchemaParser
from argschema.fields import Bool, Float, Int, Nested, Str
from argschema.schemas import DefaultSchema
import renderapi

class RenderParameters(DefaultSchema):
	host = Str(required=True,
		metadata={'description': ''})
	port = Int(required=True,
		metadata={'description': ''})
	owner = Str(required=True,
		metadata={'description': ''})
	project = Str(required=True,
		metadata={'description': ''})
	render_client_scripts = Str(required=True,
		metadata={'description': ''})

class TransformParameters(DefaultSchema):
	tf_type = Str(required=True,
		metadata={'description': ''})
	className = Str(required=True,
		metadata={'description': ''})
	dataString = Str(required=True,
		metadata={'description': ''})

class StackParameters(ArgSchema):
	render = Nested(RenderParameters)
	stack = Str(required=True,
		metadata={'description': ''})
	zs = Int(required=True,
		metadata={'description': ''})
	transform = Nested(TransformParameters)
	refId = Str(required=True,
		metadata={'description': ''})

class ApplyLensCorrection(ArgSchemaParser):
	def __init__(self, *args, **kwargs):
		super(ApplyLensCorrection, self).__init__(schema_type = 
			StackParameters, *args, **kwargs)

	def run(self):
		with open("lens_correction.json", "r") as json_file:
			tf = json.load(json_file)

		self.args['transform']['tf_type'] = tf['transform']['type']
		self.args['transform']['className'] = tf['transform']['className']
		self.args['transform']['dataString'] = tf['transform']['dataString']

		# Build stack from z(s) with lens correction

		output = {
			"render": {},
			"stack": "MONTAGESTACK",
			"refId": "8ccxdfs394875asdv"
		}

if __name__ == '__main__':

	example_input = {
		"render": {
			"host": "em-131fs",
			"port": 8080,
			"owner": "renderowner",
			"project": "SPECIMEN",
			"render_client_scripts": "/PATH/TO/CLIENTSCRIPTS/"
		},
		"stack": "MONTAGESTACK",
		"zs": 2201,
		"transform": {
			"tf_type": "",
			"className": "",
			"dataString": ""
		},
		"refId": "None"
	}

	module = ApplyLensCorrection(input_data = example_input)
	module.run()