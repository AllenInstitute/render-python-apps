# stitching
modules that involve 2-d tile montaging of many tiles/frames/images covering a single section
(just to maximize terms used and minimize confusion)

### detect_and_drop_stitching_mistakes
This is a module which attempts to automatically find mistakes in stitching by comparing the locations of tiles before stitching the the location of tiles after stitching.  It finds overlapping tile pairs (before stitching) which are now farther apart than a certain threshold.  Then by analyzing a graph where vertices are tiles and edges are all such tile pair correpondances, find the largest connected component, and drop all tiles
that are not in that connected component.  A useful QC step to run on stitching algorithms that does not depend on the method that was used to calculate the stitching.
TODO: produce an output list of dropped tiles in order to optionally drive fallback strategies.

### remove_outer_tiles
this is a simple module which simply drops all the outer tiles on a particular section. This can be useful for automating images of ribbons where the edge tiles are most problematic in drive a rough alignment process as they contain nearby sections.

### create_montage_pointmatches_in_place
This is a module for converting a set of tile layouts into a putative set of within section point matches.  It simply assumes that all tiles are placed correctly, and calculates the "local" coordinates within overlapping images which correspond in the now "stitched" stack.
It does this by simply writing down a grid of points that span that overlapping region with a specific spacing.
WARNING: this puts point matches in the point match database based upon TRUE local raw coordinates, and not "post-lens correction" local coordinates
as was the original janelia pipeline.  Using EMAligner to solve for tile solutions when you have montage point matches and cross section point matches with different "local" coordinate systems is likely to produce poor results.  Synapse Biology at the Allen is presently calculating point matches in true raw local coordinates, and makes ure EMAligner only receives tiles with a single Affine transformation containing all the non-alignment transformations that must be done to that tile.  We need to iron this issue out in a more general way to support a larger diversity of frameworks.  See pending render issue request.

This module is useful if you have a success cross correlation (or any other non-point match) based image stitching pipeline and don't want to switch to a point match based system.



