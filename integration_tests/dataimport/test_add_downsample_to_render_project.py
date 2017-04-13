from renderapps.dataimport.add_downsample_to_render_project import AddDownSample
import renderapi
from ..test_data import render_host,render_port, client_script_location,tilespec_file, tform_file
import pytest
import json 

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

@pytest.fixture(scope = "module")
def teststack(render_test_parameters):
    stack = 'teststack'
    render = renderapi.render.connect(**render_test_parameters)
    with open(tilespec_file, 'r') as f:
        ts_json = json.load(f)
    with open(tform_file, 'r') as f:
        tform_json = json.load(f)
    tilespecs = [renderapi.tilespec.TileSpec(json=ts) for ts in ts_json]
    tforms = [renderapi.transform.load_transform_json(td) for td in tform_json]
    
    renderapi.stack.create_stack(stack, render=render)
    renderapi.client.import_tilespecs(stack, tilespecs, sharedTransforms=tforms)

    yield stack
    renderapi.stack.delete_stack(stack, render=render)


def test_create_fast_stacks(render_test_parameters,teststack):
    test_parameters = { 
        "render":render_test_parameters,
        "input_stack":"teststack",
        "output_stack":"teststack_mm",
        "convert_to_8bit":False,
        "pool_size":5
    }
    mod = AddDownSample(input_data=test_parameters, args=[])
    mod.run()
    mod.logger.error("need to make a check that import worked")
    assert False
