# section_polygons
modules related to analyzing downsampled versions of section images of DAPI
stained sections, and using fluorescent glue to automatically find the outline of the section
Then subsequent modules that help you use those section polygons to filter point matches.

these modules should be used in conjugate with rendersection client or renderapps.materialize.make_downsample_image_stack
the idea is to establish a polygon ROI based upon automatic detection of the section boundaries, and then use those polygons
to filter out point matches.  There might be other workflows that might like similar type operations, and might define polygons automatically.
The polygons are defined in a json format the includes the images they were derived on, and enough information to express the points of the polygon
in terms of the world coordinates of the stack that was used to generate the imagery. 

### create_section_polygons
This module analyzes a folder of section images that were created from a stack to automatically detect the vertically (or horizontally) oriented section images.  With DAPI images and array tomography sections, it does a fairly good job of detecting sections (>90%) of sections are properly detected.  It depends critically that the levels of the downsampled image have been adjusted to maximize the contrast visible on the fluorescent glue that forms straight lines in the image, with 8 bit values near 255.  It also relies on the lines being straight, so it should only be done on montaged stacks and not raw stack, and probably not on stacks were sever non-linearities have been applied that might unstraighten those lines.

### fiji_edit_polygons_script
this is actually a jython script for FIJI which turns FIJI into a QC UI for the polygon images, it will load each polygon in a directory, you can edit the polygon, or draw a brand new one, then click the next button and the new json file will be saved to disk. 

### filter_pointmatches_with_polygons
this takes a set of polygons saved in a directory and matchcollection in the point match database, and filters out all point matches
that either start or end outside of the section polygons that have been defined.  point matches that exist outside regions (such as section boundaries) often have sharp discontinuities in their vector flows, and so its best not to include them when running a transformation solver.  This is one tool to filter out those unhelpful point matches programatically.

