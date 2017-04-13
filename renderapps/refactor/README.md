These are modules which I believe are functional, but they should be refactored
to follow the same RenderModule patter foound in renderapps.module.template_module
to simplify their use from outside sources.  They are placed here as a queue to work on.

list
----
create_trakem2_subvolume_from_render.py
the older version of creating a subvolume in trakem2 from render. It works I believe, and has a couple features the new version doesn't have that yet, so i'm keeping it around in case those features need to be ported.