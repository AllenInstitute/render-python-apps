# stack
modules for doing global operations on stacks, general utilities

### apply_global_affine_to_stack
simply appends a global affine transform to every tile in a state.  Useful for flipping stacks,  for translating stacks,  for manual fits of global transformations between two stacks, or for changing the overall determinant/scale factor of a set of stacks.

### consolidate_render_transforms
This attempt to reduce the number of transforms applied to each stack by composing together transformation.  Right now, this only really works with affine transforms, though polynomial could be completed soon.  This is important before using the EMAligner presently, because it makes assumptions about the structure of the transformations.  (see outstanding issue in render we are working), present work around is to oonform to the EMAligner standard of 1 or 0 lens transformations, and then 1 other transform bring the tile to world).  EMaligner will replace the last transform.

### copy_stack_metadata 
This takes the metadata from stack a and copies it over onto other stacks.  Useful if you accidently deleted metadata or want to normalize the stackresolution across a set of stacks.

### flip_stack_by_raw_image_flip
This takes a render stack and saves new images to disk that are flipped vertically.  Useful for importing data that needs to be vertically flipped for some reason as render sometimes has issues with negative determinant transformations.

### merge_render_stacks
This takes all the tiles from two stacks, and makes a single stack with all tiles from both stack, matchin on z value.  The is useful for registering together two EM stacks, as you can run the tilepair client on the merged stack to find the tiles that you should look for point matches between, assuming they are close to registered.

### regex_replace_filenames
This uses a regular expresssion to update the filenames for all tiles in a stack. this can be useful when moving tiles around storage systems, or if you use some other mechanism to edit the location of tiles, or produce new images somehow.

### rename_sectionIds
This was a simple module to rename the sectionIds in a stack according to their z value.  Was useful for fixing stacks with no sectionIds in their layouts as they are needed for running point match operations.

### set_stack_levels
This sets the min and maxIntensity of each tile in the stack to a specific value.  Useful for minimizing the pain of 16>8 bit coverting or making the ndviz link of a stack look a certain way by default without having to adjust min/max sliders.
