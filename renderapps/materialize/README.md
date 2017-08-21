# materialize

### download_volume

A module for creating materialized volumes of transformed images using the render service to make cutouts. Presently optimized to have a single image file produced per section.

### make_downsample_image_stack

A module that uses the render section client to produce a single downsampled image per section, using the bounding box each section when creating it. In the end, I want this to also upload a new stack to render that has these single tile images per section, with transforms that places the downsampled tile in the same coordinate system as the stack that was used to produce it.  This will be useful for a rough alignment pipeline, but presntly isn't completed, and now just makes the images, which can be used by the section_polygons.

