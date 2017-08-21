



### create_trakem2_subvolume_from_render.py
This program works in conjunction with reimport_trakem2_to_render.py to create a trakem2 project from a specific bounding box within a render stack.   It should work with any transforms supported by both render and trakem2. 

to run

python -m renderapps.dataimport.create_trakem2_subvolume_from_render.py --inputJson INPUTJSONFILE

an example INPUTJSONFILE is given in test_input_json.json, an annotated version is below

{
	"inputStack":"EM_fix", #the name of the stack to import
	"minX":190000, #mins and maxes of the bounding box
	"minY":90000, 
	"maxX":225424,
	"maxY":123142,
	"host":"ibs-forrestc-ux1", #render host
	"port":8080, #render port
	"owner":"Forrest", #render owner
	"project":"M247514_Rorb_1", #render project
	"minZ":0, #z bounds in bounding box
	"maxZ":50,
	"doChunk":false, #should you split up the Z into 50% overlapping chunks? (i have not tested this set to True yet)
	"chunkSize":50, #how big should those chunks be
	"outputXMLdir":"/nas3/data/M247514_Rorb_1/processed/TEMprojects/" #what directory should i save the trakem2 projects and json files to
}

There will be a subfolder off of outputXMLdir titled "{minZ}-{maxZ}" with a project.xml file that can be opened in trakem2.
Note, only tiles within the bounds will exist in the project, and if you reset the bounding box in trakem2 you will lose the ability to place tiles back where they were in the original render space, so don't do that!

Right now it uses mipmap level 0 tiles, but could be modified to load other mipmaplevels.

### reimport_trakem2_to_render.py
This is the inverse to create_trakem2_subvolume_from_render.py
to run
python reimport_trakem2_to_render.py --inputJson INPUTJSONFILE --outputJson OUTPUTJSONFILE

the input json file should be the same that was used to create the trakem2 project, as it will re-download the tilespecs and ONLY MODIFY THE TRANSFORMATIONS of those tilespecs using the transforms found in the trakem2 file.  it also uses the bounds specified in the JSON file to shift the tiles back to their correct global render location.

outputJson contains a few more options, and an example is given in test_output_json.json

{
	"outputStack":"EM_fix_stitched", #name of the stack to output (haven't made this naming work for chunks yet)
	"renderHome":"/pipeline/render" #location of a render git repo, where it has been compiled using mvn.. it will find the Converter.java program in a standard location off of this directory, and use it to make the first json files.
}

NOTE: both of these programs require the render-python interface to be available to python.
www.github.com/fcollman/render-python.

### ImportTrakEM2Annotations
This is a program for extracting area list annotations in TrakEM2 and converting them to a json format
where each area list is expressed as a set of local tile coordinates, in a nested json schema that is specified in AnnotationJsonSchema.  This is meant to facilitate transforming annotations done in TrakEM2 of an alignment that might later be updated by render, the idea is that annotations can get stored in a local tile coordinate version, and then transformed to a world coordinate version using the render coordinate mapping service.

### MakeTrakEM2QCFigures
This is a small program written to make summary figures of TrakEM2 annotations in order to draw the attention of a manual QC process to annotations that might be false merges by sorting them according to their total bounding box size, and showing a 2d summary plot of their profiles.

## Other Files

### trakem2utils
Basic python functions for interacting with trakem2 xml files.

### header.xml
Template trakem2 header xml

### layerset.xml
Template trakem2 layerset xml 

### ImportTrakEM2Annotations.ipynb 
The ipython notebook used to develop the ImportTrakEM2Annotation module


