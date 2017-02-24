import renderapi
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from functools import partial
import pathos.multiprocessing as mp
from matplotlib.patches import FancyArrowPatch, Circle, ConnectionStyle
import argparse
import os
from renderapi.utils import stripLogger
import json
import logging
import sys

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = "import xml files for each Z to register EM to LM")
    parser.add_argument('--inputJson',help='json based input argument file',type=str)
    parser.add_argument('--verbose','-v',help='verbose logging',action='store_true')
    args = parser.parse_args()

    jsonargs = json.load(open(args.inputJson,'r'))
    stack = jsonargs['stack']
    r = renderapi.Render(**jsonargs['render'])
    if args.verbose:
        stripLogger(logging.getLogger())
        logging.basicConfig(level=logging.DEBUG,stream=sys.stdout)
        logging.debug('verbose mode enabled!')


    figdir='%s-%s-%s'%(jsonargs['figdir'],jsonargs['matchcollection'],jsonargs['stack'])
    if not os.path.isdir(figdir):
        os.makedirs(figdir)
    pool = mp.ProcessingPool(20)

    groups=r.run(renderapi.pointmatch.get_match_groupIds,jsonargs['matchcollection'])
    groups=np.array(map(int,groups))
    groups.sort()
    zvalues = {}
    for group in groups:
        z = r.run(renderapi.stack.get_z_value_for_section,jsonargs['stack'],group)
        if z is not None:
            zvalues[group]=int(z)


    items = []
    for group,z in zvalues.items():
        if (z>=jsonargs['minZ'])&(z<=jsonargs['maxZ']): 
            for k in range(jsonargs['dz']+1):
                z2=z+k
                group2 = [g for g in zvalues.keys() if zvalues[g]==z2]
                if len(group2)>0:
                    group2=group2[0]
                    items.append((group,group2))

    def make_plot(r,matchcollection,zvalues,figdir,item):
        section_p,section_q = item
        z_p = zvalues[section_p]
        z_q = zvalues[section_q]
        bounds_p = r.run(renderapi.stack.get_bounds_from_z,stack,z_p)
        #bounds_q = render.get_bounds_from_z(stack,z_q)
        allmatches = r.run(renderapi.pointmatch.get_matches_from_group_to_group,matchcollection,section_p,section_q)
        all_points_global_p = np.zeros((1,2))
        all_points_global_q = np.zeros((1,2))
        for matchobj in allmatches:
            points_local_p = np.array(matchobj['matches']['p'])
            points_local_q = np.array(matchobj['matches']['q'])

            t_p = r.run(renderapi.coordinate.local_to_world_coordinates_array,stack,points_local_p.T,matchobj['pId'],z_p)
            all_points_global_p=np.append(all_points_global_p,t_p,axis=0)

            t_q = r.run(renderapi.coordinate.local_to_world_coordinates_array,stack,points_local_q.T,matchobj['qId'],z_q)
            all_points_global_q=np.append(all_points_global_q,t_q,axis=0)

            #break
        all_points_global_p = all_points_global_p[1:,:]
        all_points_global_q = all_points_global_q[1:,:]
        all_points=np.concatenate([all_points_global_p,all_points_global_q],axis=1)
        f,ax=plt.subplots(1,1,figsize=(10,30))
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
        print figpath
        f.savefig(figpath)
        plt.close(f)
      

    mypartial= partial(make_plot,r,jsonargs['matchcollection'],zvalues,figdir)
    res=pool.map(mypartial,items)
    #for item in items:
    #    mypartial(item)
    #    break