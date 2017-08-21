import renderapi
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from functools import partial
import pathos.multiprocessing as mp
from matplotlib.patches import FancyArrowPatch, Circle, ConnectionStyle
import os
from ..module.render_module import RenderModule, RenderParameters
from json_module import InputFile,InputDir
import marshmallow as mm

parameters={
    "render":{
        "host":"ibs-forrestc-ux1",
        "port":8080,
        "owner":"Forrest",
        "project":"M247514_Rorb_1",
        "client_scripts":"/pipeline/render/render-ws-java-client/src/main/scripts"
    },
    "stack":"REGFLATSMALLFIXDAPI_1_deconv_CONS",
    "matchcollection":"M247514_Rorb_1_DAPI1_deconv_filter_fix2",
    "figdir":"/nas3/data/M247514_Rorb_1/processed/matchfigures",
    "dz":10,
    "minZ":0,
    "maxZ":101
}


class MakePointMatchPlotsParameters(RenderParameters):
    stack = mm.fields.Str(required=True,
        metadata={'description':'stack to use to make point match plots'})
    matchcollection = mm.fields.Str(required=True,
        metadata={'description':'match collection to use to make point match plots'})
    figdir = mm.fields.Str(required=True,
        metadata={'description':'directory to save images'})
    dz = mm.fields.Int(required=False,default=10,
        metadata={'description':'integer number of z planes away to make point match plots (default 10)'})
    minZ = mm.fields.Int(required=False,
        metadata={'description':'minimum Z to make plots for (default to whole stack)'})
    maxZ = mm.fields.Int(required=False,
        metadata={'description':'maximum Z to make plots for (default to whole stack)'})
    pool_size = mm.fields.Int(required=False,default=20,
        metadata={'description':'number of parallel threads to use'})

def make_plot(r,matchcollection,zvalues,figdir,item):
    section_p,section_q = item
    z_p = zvalues[section_p]
    z_q = zvalues[section_q]
    bounds_p = self.render.run(renderapi.stack.get_bounds_from_z,stack,z_p)
    #bounds_q = render.get_bounds_from_z(stack,z_q)
    allmatches = self.render.run(renderapi.pointmatch.get_matches_from_group_to_group,matchcollection,section_p,section_q)
    all_points_global_p = np.zeros((1,2))
    all_points_global_q = np.zeros((1,2))
    for matchobj in allmatches:
        points_local_p = np.array(matchobj['matches']['p'])
        points_local_q = np.array(matchobj['matches']['q'])

        t_p = self.render.run(renderapi.coordinate.local_to_world_coordinates_array,stack,points_local_p.T,matchobj['pId'],z_p)
        all_points_global_p=np.append(all_points_global_p,t_p,axis=0)

        t_q = self.render.run(renderapi.coordinate.local_to_world_coordinates_array,stack,points_local_q.T,matchobj['qId'],z_q)
        all_points_global_q=np.append(all_points_global_q,t_q,axis=0)

        #break
    all_points_global_p = all_points_global_p[1:,:]
    all_points_global_q = all_points_global_q[1:,:]
    all_points=np.concatenate([all_points_global_p,all_points_global_q],axis=1)
    width = bounds_p['maxX']-bounds_p['minX']
    height = bounds_p['maxY']-bounds_p['minY']
    wh_ratio = width*1.0/height
    if wh_ratio>1.0:
        f,ax=plt.subplots(1,1,figsize=(10,10/wh_ratio))
    else:
        f,ax=plt.subplots(1,1,figsize=(10*wh_ratio,10))

    #ax.imshow(lowmag_rg,extent=(bounds_p['minX'],bounds_p['maxX'],bounds_p['maxY'],bounds_p['minY']))
    ax.scatter(all_points[:,0],all_points[:,1],c='m',marker='o',s=5,linewidth=0)
    ax.quiver(all_points[:,0].T,all_points[:,1].T,
            all_points[:,2].T-all_points[:,0].T,
            all_points[:,3].T-all_points[:,1].T,
            color='m',
            angles='xy', scale_units='xy', scale=1)
    ax.set_xlim((bounds_p['minX'],bounds_p['maxX']))
    ax.set_ylim((bounds_p['maxY'],bounds_p['minY']))
    ax.set_aspect('equal')
    ax.set_title('%d_to_%d'%(z_p,z_q))
    #ax.autoscale(tight=True)
    plt.tight_layout()

    figpath = os.path.join(figdir,'%05d_to_%05d.png'%(z_p,z_q))

    f.savefig(figpath)
    plt.close(f)
    return figpath
    
class MakePointMatchPlots(RenderModule):
    def __init__(self,schema_type=None,*args,**kwargs):
        if schema_type is None:
            schema_type = MakePointMatchPlotsParameters
        super(MakePointMatchPlots,self).__init__(schema_type=schema_type,*args,**kwargs)
    def run(self):
        self.logger.error("NEEDS TESTING.. TALK TO FORREST IF BROKEN OR WORKS")
        stack = self.args['stack']
        zvals = np.array(self.render.run(renderapi.stack.get_z_values_for_stack,stack))
        minZ = self.args.get('minZ',np.min(zvals))
        maxZ = self.args.get('maxZ',mp.max(zvals))

        figdir='%s-%s-%s'%(self.args['figdir'],self.args['matchcollection'],self.args['stack'])
        if not os.path.isdir(figdir):
            os.makedirs(figdir)
        pool = mp.ProcessingPool(20)

        groups=self.render.run(renderapi.pointmatch.get_match_groupIds,self.args['matchcollection'])
        groups=np.array(map(int,groups))
        groups.sort()
        zvalues = {}
        for group in groups:
            z = self.render.run(renderapi.stack.get_z_value_for_section,self.args['stack'],group)
            if z is not None:
                zvalues[group]=int(z)

        
        items = []
        for group,z in zvalues.items():
            if (z>=minZ)&(z<=maxZ): 
                for k in range(self.args['dz']+1):
                    z2=z+k
                    group2 = [g for g in zvalues.keys() if zvalues[g]==z2]
                    if len(group2)>0:
                        group2=group2[0]
                        items.append((group,group2))

        mypartial= partial(make_plot,r,self.args['matchcollection'],zvalues,figdir)
        with renderapi.client.WithPool(self.args['pool_size']) as pool:
            res=pool.map(mypartial,items)

if __name__ == "__main__":
    mod = MakePointMatchPlots()
    mod.run()

