#!/usr/bin/env python

import argparse
import os
import json
#import renderapi
import random
import requests
import tifffile
from PIL import Image
from io import BytesIO
import numpy

def convert(value, numofdigits):

	strval = str(value)
	lenstr = len(strval)
	if lenstr > numofdigits:
		print ("Cannot create a string smaller than needed")
		exit(0)
		
	else:
		prefix = "0"*(numofdigits - lenstr)
		strval = prefix+strval
	#print strval
	return strval

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description = "Create Views for Movie")
    parser.add_argument('--inputStack',nargs='+',help='Name of input stack',type=str)
    parser.add_argument('--outputDirectory',nargs=1,help='Output directory',type=str)
    parser.add_argument('--scale',nargs=1,help='Scale of image',type=str)
    parser.add_argument('--firstz',nargs=1,help='First z value ',type=int)
    parser.add_argument('--lastz',nargs=1,help='Last z value ',type=int)
    parser.add_argument('--skip',nargs=1,help='Number of Sections to skip over ',type=int)
    

    args = parser.parse_args()

    inputStack = args.inputStack[0]
    outputDirectory = args.outputDirectory[0]
    scale = args.scale[0]
    firstz = args.firstz[0]
    lastz = args.lastz[0]

    print inputStack
    print scale
   

    if not os.path.isdir(outputDirectory):
	    os.makedirs(outputDirectory)

    z = firstz
    print z
    while z <= lastz:

        a = z
	#request_url = "http://ibs-forrestc-ux1.corp.alleninstitute.org:8082/render-ws/v1/owner/Sharmishtaas/project/M270907_Scnn1aTg2Tdt_13/stack/%s/z/%s/jpeg-image?scale=%s"%(inputStack,str(z),scale)
	request_url = "http://ibs-forrestc-ux1.corp.alleninstitute.org:8080/render-ws/v1/owner/Sharmishtaas/"
	#request_url = request_url+"project/M270907_Scnn1aTg2Tdt_13/stack/%s/z/%s/box/7000,18500,1000,1000,%s/jpeg-image"%(inputStack,str(z),scale)
	#request_url = request_url+"project/M270907_Scnn1aTg2Tdt_13/stack/%s/z/%s/box/3400,2900,1000,1000,%s/jpeg-image"%(inputStack,str(z),scale)
	#request_url = request_url+"project/M270907_Scnn1aTg2Tdt_13/stack/%s/z/%s/box/0,0,15000,35000,%s/jpeg-image"%(inputStack,str(z),scale)
	request_url = request_url+"project/M270907_Scnn1aTg2Tdt_13/stack/%s/z/%s/jpeg-image?scale=%s"%(inputStack,str(z),scale)

        print (request_url)
        session = requests.session()
        r = session.get(request_url)
        try:
    	    img = Image.open(BytesIO(r.content))
    	    array = numpy.asarray(img)
		
        except:
            print("Did not work!")
        #print (request_url)

	#boxparams=[1200,2000,4000,8600]
	#img = renderapi.get_image_data(inputStack,z,boxparams,scale)
    	

        outfilename = outputDirectory + "/Section_z_" + convert(z, 4) + ".jpg" 

        #tifffile.imsave(outfilename,array)
	im = Image.fromarray(array)
	im.save(outfilename)
        z = z+args.skip[0]
