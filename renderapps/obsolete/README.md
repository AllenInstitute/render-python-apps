These programs make use of the old version of the renderapi, they need to be refactored to be functional.
Most also need to use the newer pattern of using a RenderModule to handle parameter settings.
The code might contains useful patterns, so i am keeping it here, with hopes we will move it
slowly out of this folder and into functioning code again or else decide that things can be deleted.

apply_alignment_from_render_stack
this was useful for applying trakem2 style alignments where there was 1 transform per section
that brings the stack from a registered space to an aligned space.
In order to apply alignments to other channels in that registered space that were not necessarily registered with the original
you had to derive a raw>aligned transformation for those other imaging sessions.

This became obsolete when we moved to EMAligner, which had different transforms per tile
and we had to develop a more general way to apply alignments.  Which are represented by the new registration modules
though they are less intelligent about consolidating transforms, which might be more efficent storage
and validation wise.  Could be reasons to keep this around for people doing trakem2 alignments on AT data.
presently broken on newer renderapi.

apply_TEM2_to_render_stack
This was the take a trakem2 project and create a render stack out of it.  Was useful for expressing the results of that alignment in render.
The new to>from trakem2 modules take care of this now, but they are less intelligent about consolidating transforms, so perhaps this functionality should be revived or incorporated somehow in the new modules.

apply_ztransforms_to_render_stack
This was for taking a set of transformation made by apply_TEM2_to_render_stack and applying them to another stack.  again, this functionality is taken over by the newer registration modules.

create_acquirdiff_fullstack
this was more like a script for importing only the new data in a statetable without having to import the full statetable... its rather specific to array_tomography and how things are done at the allen right now, we need something of this functionality when we have streaming injest working, but I don't think this is that useful right now.

create_json_from_xml
this is for taking a trakem2 project and making a branch new render stack.  It would be useful if you were starting out with Trakem2 projects and you needed some custom code for creating tileIds from the filepaths.  Could be a useful pattern for some people, but it hasn't been refactored with the new api and pattern.  I've forgotten what the copy was for.

create_stitched_fullstack
this was for taking json files that were creating by the stitching module and importing them into render.  This is now deprecated I think.

create_views
this was an earlier version of making a download_volume with fewer options, though it had some smarter default tricks for parameters that should be reincorporated.

create_xml_from_tilespecs
this was a script for making render stacks from json files.

deletestack
this was a simple command line program for deleting a stack, sort of too easy to have a module for now.

