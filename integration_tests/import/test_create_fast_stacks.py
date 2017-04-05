from renderapps.dataimport.create_fast_stacks import CreateFastStack
import renderapi
from ..test_data import render_host,render_port, client_script_location,tilespec_file, tform_file
import pytest



@pytest.fixture(scope='module')
def render_test_parameters():
    render_test_parameters = {
            'host': render_host,
            'port': 8080,
            'owner': 'test_coordinate',
            'project': 'test_coordinate_project',
            'client_scripts': client_script_location
    }
    return render_test_parameters


def test_create_fast_stacks(render_test_parameters):
    test_parameters = { 
        "render":render_test_parameters,
        "statetableFile":"",
        "projectDirectory":"",
        "outputStackPrefix":"",
        "pool_size":5
    }
    mod = CreateFastStack(input_data = test_parameters)

    mod.run()