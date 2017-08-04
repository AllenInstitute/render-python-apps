# render-python-apps

These are a set of python based processing modules that do a broad assortment of steps in various image processing workflows whose results are ultimately stored in render.  They make extensive use of the render-python library (www.github.com/fcollman/render-python) for reading metadata from render and sending it back.

# running a module
Each module is designed to be run using a common pattern for defining inputs that is setup using the argschema pattern.
www.github.com/AllenInstitute/argschema

module can be run in 3 different ways

1) passing parameters via command line parameters

        python -m renderapps.module.example_module\
        --render.host RENDERHOST_DNS_OR_IP\
        --render.port RENDERPORT\
        --render.owner OWNERNAME\
        --render.project PROJECTNAME\
        --render.client_scripts PATHTORENDERSCRIPTS \
        --param1 P1\
        --param2 P2

note for each module you can get help about the parameters by running
python -m renderapps.module.example_module --help

2) passing a json file from command line
python -m renderapps.module.example_module --input_json path_to_json_file

This will read the parameters from the json file passed in.  Note that command line arguments can be mixed with json definitions, and command line arguments overwrite parameters specified in the json.

3) calling the module from another python program

        from renderapps.module.example_module import ExampleModule

        module_parameters = {
            "render":{
                "host":"RENDERHOST",
                "port":RENDERPORT,
                "owner":"OWNERNAME",
                "project":"PROJECTNAME",
                "client_scripts":"PATHTORENDERSCRIPTS"
            },
            "param1":"P1",
            "param2":P2,
        }    

        mod = ExampleModule(input_data=module_parameters, args = [])
        mod.run()

Note that passing in args =[] will bypass the command line parsing.

No matter how the module is run, all input parameters will be validated using the schema which each module has defined using the marshmallow framework. 

# Repo Organization

The code is now organized in a sub-module structure arranged thematically by purpose.
You can (or will when we are done with documentation) find more detailed descriptions of each submodule in the subfolders. 

Here are the thematic areas

## dataimport
These modules are related to getting data into render, including if you'd like, the generation of downsampled mipmaped image.

## cross_modal_registration
modules for setting up trakem2 projects to register LM and EM data of the same sections.

## materialize
modules for creating images on disk of materialized versions of transformed data

## pointmatch
modules for making plots of point matches or doing operations on the pointmatch database

## registration
modules for dealing with situations where you have stacks that are registered,
meaning they all exist in the same space, and but you have a new transformed version of one of those stacks
but you'd like to bring the rest of the registered stacks along into the new space.

In particular this is useful for array tomography where you have many channels of sections that you must register
and then you must align the data across sections.

## section_polygons
modules related to analyzing downsampled versions of section images of DAPI
stained sections, and using fluorescent glue to automatically find the outline of the section
Then subsequent modules that help you use those section polygons to filter point matches.

## stack
modules related to doing bulk operations on a stack.

## stitching
modules related to stitching array tomography sections, meaning within a section 2d tile montageing.

## tile
modules related to doing single tile operations.

## TrakEM2
modules related to importing data from render>trakem2 and bringing it back again

## transfer
modules related to pushing render data between two render servers,
and/or between local storage and the cloud.

## wrinkle detection
start of work on a module to detect wrinkles in sections

# other folders

## module
the base module classes for writing argschema style modules
includes a template module example to work from

## obsolete
modules that were written with deprecated version of render python and would need to be rewritten in the new format
hopefully will go away over time.. leaving useful code here for now.

## refactor
modules that don't use the consistent argschema pattern and should be refactored
hopefully will go away as code is moved out of this..

# allen_utils
This is a folder of miscelaneous shell scripts and files that are specific to running render python related things at the allen.  they might be of interest but won't work in general for people outside of Synapse Biology at the Allen Institute.

# example_json
This is a folder of example json files that were used to run various modules, could be a useful reference.

# integration_tests
These should eventually contain tests for running against an integrated deployment environment, specifically configured to run inside an environment like the one specified here (https://github.com/fcollman/render-deploy/tree/test)

# notebooks
a set of ipython notebooks that show some more interactive use of render-python and render-python apps.  Mostly specific to the allen in terms of data sources, but perhaps still useful.

