# TODO: fix up renderapi calls
#
# DONE step 1: write down transform from EM stage to LM stage
# 	Get transform from FIBICS xml file
#
# DONE step 2: estimate EM stage bounding box for each EM tile
#     i have the center location each time in EM stage coodinates, and could calculate the corners
# DONE step 3: transform those EM stage bounding boxes to LM stage bounding boxes
#     i have transformed those centers back to LM coordinates.. lm_coord
#
# 	4a) estimate stage coordinates of center of LM bounding box for EM image
#         DONE
#
# 	4b) find section that corresponds
#         DONE
#
# 	4c) find LM tile that has the closest stage coordinate to the center of bounding box
#         DONE
#
# 	4d)  Using that tiles transformation, its stage coordinates, and its size, estimate the pixel locations of the corners of the LM bounding box that corresponds with the EM image.  Calculate the affine transformation that places the EM image corners to those locations on this section.
#         DONE
#

#
# step 6: write code that produces tile specs that package EM tile paths, EM mask paths, and transforms from step 4 into a tilespec file.
#


# ## step 1: write down transform from EM stage to LM stage

import xmltodict
import collections
import os
import numpy as np
import renderapi
from ..module.render_module import RenderParameters, RenderModule
from argschema.fields import InputFile, Str
from atlas_utils import make_tile_masks, process_siteset, find_node_by_field, AtlasTransform


class ImportAtlasSchema(RenderParameters):
    project_path = InputFile(required=True,
                             description='Atlas a5proj file with data to import')
    LM_dataset_name = Str(required=True, default='test',
                          description='Name of light microscopy dataset within atlas file')
    site_name = Str(required=True,
                    description="name of site within Atlas file to import")
    output_stack = Str(required=True,
                       description="name of stack to save into render")
    LM_stack = Str(required=True, default='ACQDAPI_1',
                   description="Name of LM stack in render that was imported into atlas and whose coordinate system the EM tiles will be registered to")


example_parameters = {
    "render": {
        "host": "ibs-forrestc-ux1",
        "port": 8080,
        "owner": "Forrest",
        "project": "M247514_Rorb_1",
        "client_scripts": "/pipeline/render/render-ws-java-client/src/main/scripts"
    },
    'project_path': '/nas/data/M247514_Rorb_1/EMraw/ribbon0000/M247514_Rorb_1_Ribbon0000_take2.a5proj',
    'LM_dataset_name': 'test',
    'site_name': 'Site 3',
    'output_stack': 'EMSite3RAW',
    'lm_stack': 'ACQDAPI_1'
}

if __name__ == '__main__':
    mod = RenderModule(input_data=example_parameters,
                       schema_type=ImportAtlasSchema)

    project_path = mod.args['project_path']
    project_dir, project_file = os.path.split(project_path)
    project_base = os.path.splitext(project_file)[0]
    print project_base, project_dir
    with open(project_path) as fd:
        doc = xmltodict.parse(fd.read())
    project = doc['F-BioSEM-Project']['BioSemProject']



    projname = project_path.split(os.path.sep)[-4]
    assert (mod.render.DEFAULT_PROJECT == projname)

    # find the light dataset name
    dataset = find_node_by_field(doc, 'Name', mod.args['LM_dataset_name'])
    imported_data = find_node_by_field(doc, 'Name', 'Imported Data')

    # get the important transforms from atlas file
    # transform from EM data>root
    at = AtlasTransform(dataset['ParentTransform'])
    # transform from LMdata > root
    id_at = AtlasTransform(imported_data['ParentTransform'])

    # get the list of sitesets
    if type(project['AtlasCarrier']['SectionSet']) == collections.OrderedDict:
        sectionsets = [project['AtlasCarrier']['SectionSet']]
    else:
        sectionsets = project['AtlasCarrier']['SectionSet']
    sectionset = sectionsets[0]
    numsections = len(sectionset['Section'])
    sitesets = project['AtlasCarrier']['SiteSet']
    print("analyzing sectionset:%s numsections:%d" %
          (sectionset['Name'], numsections))
    sitesets = [siteset for siteset in sitesets if siteset['LinkedToUID']
                == sectionset['UID']]
    print("found %d linked site sets" % len(sitesets))

    # process the target site, making a tilespec that estimates its place in the
    # coordinate system of the
    for siteset in sitesets:
        if siteset['Name'] == mod.args['site_name']:
            print 'in', siteset['Name']
            json_files = process_siteset(mod.render,
                                         siteset,
                                         sectionset,
                                         project,
                                         project_path,
                                         at,
                                         lm_stack=mod.args['LM_stack'])

    # step 5: write conversion of EM tiles to EM tiles + masks
    #     DONE, first try was writing as LZW, binary bit depth with imagemagik convert, very small on disk
    #     we will see if render is ok with them
    for siteset in sitesets:
        if siteset['Name'] == mod.args['site_name']:
            print 'in', siteset['Name']
            # uncomment to make masks and flipped images
            make_tile_masks(siteset, sectionset, project, project_dir)

    # step 7: upload those tilespecs to the render database as a new channel stack (ACQEM)
    output_stack = mod.args['output_stack']
    renderapi.stack.create_stack(output_stack, render=mod.render)
    renderapi.client.import_jsonfiles_parallel(output_stack, json_files)
