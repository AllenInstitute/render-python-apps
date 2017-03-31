import renderapi
import numpy as np
from functools import partial
import os
import pathos.multiprocessing as mp
from operator import itemgetter
import cv2
import tifffile
import argparse
import json
from renderapi.utils import stripLogger
import logging

example_json = {
    "render":{
        "host":"ibs-forrestc-ux1",
        "port":8080,
        "owner":"Forrest",
        "project":"M247514_Rorb_1",
        "client_scripts":"/pipeline/render/render-ws-java-client/src/main/scripts"
    },
    "stack":"ALIGNDAPI_1_deconv_filter_fix",
    "sectionImageDir":"/nas4/volumes/M247514_Rorb_1_ALIGNDAPI_1_deconv_filter_fix/dapi",
    "polygon_dir":"/nas3/data/M247514_Rorb_1/processed/shape_polygons2",
    "scale":.003,
    "isHorizontal":True
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = "import xml files for each Z to register EM to LM")
    parser.add_argument('--inputJson',help='json based input argument file',type=str)
    parser.add_argument('--verbose','-v',help='verbose logging',action='store_true')
    args = parser.parse_args()

    if args.inputJson is None:
        jsonargs = example_json
    else:
        jsonargs = json.load(open(args.inputJson,'r'))

    if args.verbose:
        stripLogger(logging.getLogger())
        logging.basicConfig(level=logging.DEBUG,stream=sys.stdout)
        logging.debug('verbose mode enabled!')

    stack = jsonargs['stack']
    sectionImageDir = jsonargs['sectionImageDir']
    jsonDir = jsonargs['polygon_dir']

    r = renderapi.render.connect(**jsonargs['render'])

    def find_section_boundaries(r,
                     stack,
                     image_cache_dir,
                     z,
                     minIntensity=None,
                     maxIntensity=None,
                     drho=200,
                     dtheta = 1*3.1459/180.0,
                     scale=.1,
                     plot=False,
                     isHorizontal=False):

        filepath = os.path.join(image_cache_dir,'%05d.tiff'%z)

        img = cv2.imread(filepath,cv2.CV_8UC1)
        img_bounds = r.run(renderapi.stack.get_bounds_from_z,stack,z)

        height = img_bounds['maxY']-img_bounds['minY']
        width = img_bounds['maxX']-img_bounds['minX']

        gray=img
        #return img
        #gray = cv2.rotate(gray,cv2.ROTATE_90_CLOCKWISE)
        thresh,edges = cv2.threshold(gray,100,255,cv2.THRESH_BINARY)
        lines=cv2.HoughLines(edges,3,np.pi/720,100)


        def ab_from_rhotheta(rho,theta):
            x1,x2,y1,y2 = xy_from_rhotheta(rho,theta)
            if x1==x2:
                a=None
                b=x1
            else:
                a = (y1-y2)/(x1-x2)
                b=y2-a*x2
            return (a,b)
        def xy_from_rhotheta(rho,theta):
                a=np.cos(theta)
                b=np.sin(theta)
                x0 = a*rho
                y0 = b*rho
                x1 = int(x0)
                y1 = int(y0)
                x2 = int(x0 - width*(-b))
                y2 = int(y0 - width*(a))
                return (x1,x2,y1,y2)
        def get_line_score_horizontal(img,line):
            from operator import itemgetter

            a,b=ab_from_rhotheta(line[0],line[1])

            if (a is None):
                return np.uint64(0)
            elif (a==0):
                return np.uint64(0)
            else:
                xmin=-b/a
                ymin=0
                xmax=(img.shape[0]-1-b)/a
                ymax=img.shape[0]-1

            x = np.round(np.linspace(xmin,xmax,img.shape[0]))
            y = np.round(np.linspace(ymin,ymax,img.shape[0]))
            if np.sum(x>=img.shape[1])>0:
                return np.uint64(0)
            if np.sum(x<0)>0:
                return np.uint64(0)
            if np.sum(y>=img.shape[0])>0:
                return np.uint64(0)
            if np.sum(y<0)>0:
                return np.uint64(0)
            vals = img[np.array(y,dtype=np.int),np.array(x,dtype=np.int)]
            return np.sum(vals)
        def get_line_score(img,line):
            from operator import itemgetter

            a,b=ab_from_rhotheta(line[0],line[1])

            if (a is None):
                xmin = b
                xmax = b
                ymin = 0
                ymax = img.shape[0]-1
            elif (a==0):
                return np.uint64(0)
            else:
                xmin=-b/a
                ymin=0
                xmax=(img.shape[0]-1-b)/a
                ymax=img.shape[0]-1

            x = np.round(np.linspace(xmin,xmax,img.shape[0]))
            y = np.round(np.linspace(ymin,ymax,img.shape[0]))
            if np.sum(x>=img.shape[1])>0:
                return np.uint64(0)
            if np.sum(x<0)>0:
                return np.uint64(0)
            if np.sum(y>=img.shape[0])>0:
                return np.uint64(0)
            if np.sum(y<0)>0:
                return np.uint64(0)
            vals = img[np.array(y,dtype=np.int),np.array(x,dtype=np.int)]
            return np.sum(vals)

        alllines = lines
        lines=lines[:,0,:]
        if isHorizontal:
            scores = [get_line_score_horizontal(img,line) for line in lines]
        else:
            scores = [get_line_score(img,line) for line in lines]

        lines = [line for score,line in sorted(zip(scores,lines),key=itemgetter(0),reverse=True)]
        if isHorizontal:
            lines = [line for line in lines if line[1]>(np.pi/2)*.8]
        line1 = lines[0]
        line2 = None

        l1x1,l1x2,l1y1,l1y2 = xy_from_rhotheta(line1[0],line1[1])

        for rho,theta in lines[1:]:
            x1,x2,y1,y2 = xy_from_rhotheta(rho,theta)
            if isHorizontal:
                rho_diff = np.abs(l1y1-y1)
            else:
                rho_diff = np.abs(l1x1-x1)
            if rho_diff>drho:
                if np.abs(line1[1]-theta)<dtheta:
                    line2 = np.array([rho,theta])
                    break

        coords = []
        a,b = ab_from_rhotheta(line1[0],line1[1])
        height = img.shape[0]
        width = img.shape[1]

        if isHorizontal:
            x1,x2,y1,y2 = xy_from_rhotheta(line1[0],line1[1])
            coords.append( (x1,y1))
            coords.append( (x2,y2))

            if line2 is not None:
                x1,x2,y1,y2 = xy_from_rhotheta(line2[0],line2[1])
                coords.append( (x2,y2))
                coords.append( (x1,y1))

            #if there isn't a second line we have to figure out
            #whether we have the right or left
            else:

                if (l1y1<(height-l1y1)):
                    #then we are closer to the bottom
                    coords.append((width,height))
                    coords.append((0,height))
                else:
                    coords.append((width,0))
                    coords.append((0,0))
        else:
            if a is None:
                coords.append((b,0))
                coords.append((b,height))
            elif a==0:
                coords.append((b,0))
                coords.append((b,height))
            else:
                coords.append( (-b/a,0))
                coords.append( ((height-b)/a,height))

            if line2 is not None:
                a,b = ab_from_rhotheta(line2[0],line2[1])
                if a is None:
                    coords.append((b,height))
                    coords.append( (b,0))
                elif a ==0:
                    coords.append((b,0))
                    coords.append((b,height))
                else:
                    coords.append( ((height-b)/a,height))
                    coords.append( (-b/a,0))
            #if there isn't a second line we have to figure out
            #whether we have the right or left
            else:
                if (l1x1<(width-l1x1)):
                    #then we are closer to the right
                    coords.append((width,height))
                    coords.append((width,0))
                else:
                    coords.append((0,height))
                    coords.append((0,0))
        coords = [((a/scale)+img_bounds['minX'],(b/scale)+img_bounds['minY']) for a,b in coords]
        if line2 is None:
            line2 = line1
        from shapely import geometry
        polyg = geometry.Polygon(coords)
        # if plot:
        #     x,y = polyg.boundary.xy
        #     f,ax = plt.subplots(1,1,figsize=(12,6))
        #     #ax.imshow(edges,cmap=plt.cm.gray)
        #     for rho,theta in (line1,line2):
        #        x1,x2,y1,y2 = xy_from_rhotheta(rho,theta)
        #        ax.plot(np.array([x1,x2])/scale+img_bounds['minX'],np.array([y1,y2])/scale + img_bounds['minY'],linewidth=1)
        #     ax.imshow(img,cmap=plt.cm.gray,extent=(img_bounds['minX'],img_bounds['maxX'],img_bounds['maxY'],img_bounds['minY']))
        #     #ax.imshow(img)
        #     plt.plot(x,y,'r')
        #     plt.tight_layout()

        jsonobj={}
        jsonobj['z']=z
        jsonobj['filepath']=filepath
        jsonobj['bounds']=img_bounds
        jsonobj['roi']=geometry.mapping(polyg)
        return jsonobj,alllines,img


    #jsonobj,alllines,img=find_section_boundaries(r,stack,jsonargs['sectionImageDir'],66,plot=True,isHorizontal=True)

    mypartial = partial(find_section_boundaries,r,stack,jsonargs['sectionImageDir'],isHorizontal=jsonargs['isHorizontal'],scale=jsonargs['scale'])
    zvalues = r.run(renderapi.stack.get_z_values_for_stack,stack)
    jsonresults = []
    for z in zvalues:
        jsonresults.append(mypartial(z))

    jsonresults=[result[0] for result in jsonresults]

    if not os.path.isdir(jsonDir):
        os.makedirs(jsonDir)

    for result,z in zip(jsonresults,zvalues):
        jsonfile = os.path.join(jsonDir,'polygon_%05d.json'%z)
        json.dump(result,open(jsonfile,'w'))
