import renderapi
from renderapi.utils import stripLogger
from JsonRunnableModule import JsonRunnableModule
import logging
import sys

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
        parser.add_argument('--verbose','-v',help='display verbose output',action='store_true')
        JsonRunnableModule.__init__(self,parser,example_json=example_json)
        self.render = renderapi.render.connect(**self.args['render'])
        if self.args['verbose']:
            stripLogger(logging.getLogger())
            logging.basicConfig(level=logging.DEBUG,stream=sys.stdout)
            logging.debug('verbose mode enabled!')