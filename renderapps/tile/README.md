# tile
modules for doing single tile level operations

### create_filtered_EM_images
This is a module for post-processing EM imagery that contains burn marks and diversity in image contrast.  It does a series of constrast normalization, median filtering, and clahe to produce a crisp even level of background. It was optimized on two of the Allen Institute's FESEM datasets taken on a Gemini 500 with mild levels of hyrdocarbon deposition (burn lines).  Probably useful as a general pattern for applying opencv based image processing steps on sets of tiles that are stored in render.

