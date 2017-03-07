from RenderModule import RenderModule
import logging
import renderapi
import argparse

logger = logging.getLogger(__name__)

class MyModuleName(RenderModule):
    '''module to apply LM to EM transformations produced by make_EM_LM_registration_projects'''
    def __init__(self, parser, *args,**kwargs):

        RenderModule.__init__(self,parser,*args,**kwargs)

    def run(self):
        print 'running with'
        print json.dumps(self.args,indent=4)


if __name__ == '__main__':

    p = argparse.ArgumentParser(description="A generic parser description")
    example_json={
        "render":{
            "host":"ibs-forrestc-ux1",
            "port":8080,
            "owner":"Forrest",
            "project":"M247514_Rorb_1",
            "client_scripts":"/pipeline/render/render-ws-java-client/src/main/scripts"
        },
        "someparameters":"foo"
    }

    module = MyModuleName(p,example_json=example_json)
    module.run()

