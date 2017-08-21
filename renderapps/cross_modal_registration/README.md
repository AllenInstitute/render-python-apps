# cross_modal_registration
modules for facilitating registration of LM and EM data.

### make_EM_LM_registration_projects/import_EM_registration_projects

These two modules work together to create TrakEM2 projects to assist in manually registering light microscopy and electron microscopy data from the same stack, though in principle this module can be used to register two sets of images of the same section taken with any modality. 

The first makes a set of trakem2 projects where the LM tiles of a section are loaded on section 0 and the EM tiles are loaded on section 1.

The assumption is that prior to this step, the LM and EM data has been well enough registered using stage coordinates that you can load in a single field of view into TrakEM2 and have it be practical to load a single field of view.  It also assumes that the transformations of both projects have been set such that scale=1.0 equates to a resolution that is high enough to perform registration accurately.  I would reccomend using a determinant such that scale=1.0 is the resolution of the EM.  Note you can use renderapps.stack.apply_global_affine_to_stack to make this so.

Note, it is important that you do not change the TrakEm2 bounding box, or move the tiles on z=0, because the reimport module does not update the positions of those LM tiles upon reimport, so even if the TrakEm2 project looks registered, it will not be once data is reimported. (TODO reimport module should check that the bounding box is consistent and the transformations of the LM tiles have not been altered from when they were created and provide a warning or error) This is because TrakEM2 has difficulty supporting very large layers, and does not support negative coordinate spaces, so the relative locaiton of 0,0 in trakem2 space compared to render space is stored in the parameters that were used to run both components of the step.  Therefore you need to run both the creation and the re-importing steps using EXACTLY the same json file so that a consistent book
As such I do not reccomend running this with command line arguments, but rather with json files or passing in a dictionary from another script.  

You can view detailed descriptions about each of the parameters by running module with --help.  

I would reccomend using ndviz to determine the approximate coordinates in the stack that are needed for to register any particular stack.   Otherwise, I would reccomend writing a meta script to create parameters for running this module, deriving the bounds by querying render for the bounding box of the EM tile you are interested in registering.
