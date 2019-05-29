import numpy as np
import renderapi
import json
import numpy as np
from ..module.render_module import RenderModule, RenderParameters
from ..shapely import tilespec_to_bounding_box_polygon
import argschema
import os
from PIL import Image
from RansacAffineModel import RansacAffineModel
import cv2
from renderapi.transform import AffineModel
from functools import partial
from renderapi.client import import_jsonfiles_parallel
from renderapi.client import pointMatchClient
from renderapi.transform import AffineModel, RigidModel
from renderapi.client import FeatureExtractionParameters, MatchDerivationParameters,SiftPointMatchOptions
from skimage.feature import register_translation

example_parameters  = {
    "render":{
        "host": "10.128.24.33",
        "port":80,
        "owner":"Small_volumes_2018",
        "project":"M367240_D_SSTPV_smallvol",
        "client_scripts":"/pipeline/render/render-ws-java-client/src/main/scripts"
    },
    "matchcollection":"REG_FF_S03_DAPI3_to_S01_DAPI1",
    "referenceStack": "RT_STI_FF_S01_DAPI_1",
    "stack": "RT_STI_FF_S03_DAPI_3",
    "outputStack": "REG_FF_S03_DAPI_3_pytesting",
    "section": 306,
    "pointx": -1,
    "pointy": -1,
    "filter": False,
    "scale": 0.2,
    "maxEpsilon": 2,
    "steps":5 ,
    "useGross": False,
    "SIFTminScale": 0.4,
    "SIFTmaxScale": 0.85,
    "minOctaveSize": 1600,
    "maxOctaveSize": 2000,
    "modelType": 1,
    "percentSaturated": 0.7,
    "initialSigma": 2.5,
    "tileId": "",
    "pool_size": 4
    #"contrastEnhance" : false,
    #"tileDistance" : 1000 
}


class CalculateRegistrationParameters(RenderParameters):
    referenceStack = argschema.fields.Str(required=True,
        description="Stack to Register to")
    stack = argschema.fields.Str(required=True,
        description='Stack to Register')
    referenceStackChannel = argschema.fields.Str(required=False, default="",
        description="Channel on reference stack to use for registration")
    stackChannel = argschema.fields.Str(required=False, default="",
        description='Channel on stack to use for registration')
    outputStack = argschema.fields.Str(required=True,
        description="Output Stack to save results")
    matchcollection = argschema.fields.Str(required=True,
        description="Match Collection to store point matches")
    section = argschema.fields.Int(required=True,
        description="Section z value")
    initialSigma = argschema.fields.Float(required=False, default = 1.6,
        description="Initial Sigma value for SIFT")
    epsilon = argschema.fields.Float(required=False, default = 2,
        description="Epsilon value for ransac")
    SIFTminScale = argschema.fields.Float(required=False, default = 0.5,
        description="SIft min scale")
    SIFTmaxScale = argschema.fields.Float(required=False, default = 0.85,
        description="Sift max scale")
    scale = argschema.fields.Float(required=False, default = 0.1,
        description="Scale for initial gross alignment")
    percentSaturated = argschema.fields.Float(required=False, default = 0.9,
        description="Percent to saturate image before feature extraction")
    pointx = argschema.fields.Int(required=False, default = 0,
        description="Point to find tileId")
    pointy = argschema.fields.Int(required=False, default = 0,
        description="Point to find tileId")
    steps = argschema.fields.Int(required=False, default = 5,
        description="Number of SIFT steps")
    filter = argschema.fields.Bool(required=False, default=True,
        description="Apply render filter on images before feature extraction")
    useGross = argschema.fields.Bool(required=False, default=True,
        description="Use Gross registration estimate only")
    model = argschema.fields.Int(required=False, default = 1,
        description="1=Translation, 2= Rigid")
    minOctaveSize = argschema.fields.Int(required=False, default = 1600,
        description="Minimum Octave Size")
    maxOctaveSize = argschema.fields.Int(required=False, default = 2000,
        description="Maximum Octave Size")
    tileId = argschema.fields.Str(required=False, default = "",
        description="TileId to register")
    pool_size = argschema.fields.Int(required=False,default=20,
        description='number of parallel processes (default 20)')
    output_dir = argschema.fields.Str(required=False, default = "/nas5/ForSharmi/registrationtest",
        description='Directory to write gross image files')
    grossRefStack = argschema.fields.Str(required=False, default = "tempGrossStack1",
        description='Temp stack name for lowres reference stack')
    grossStack = argschema.fields.Str(required=False, default = "tempGrossStack2",
        description='Temp stack name for lowres stack')
    

def get_transform_distance(tform1,tform2):
    #just checking the translation distance
    return 0
    
def adjust_outliers(tilespecs,M):
    M = M.invert()
    
    for t in tilespecs:
        distance = get_transform_distance(M, t.tform)
        if distance > 100:
            t.tform = M
            
def register_with_NCC(I1,I2):
    A = register_translation(I1,I2,upsample_factor=4)
    print(A[0])

    
def downsample_z(render,stack,output_dir,scale,project,tagstr,Z,channel):

    z = Z[0]
    newz = Z[1]

    args=['--stack', stack,
          '--scale',str(scale),
          '--rootDirectory',output_dir ,
          str(z)]


    print args
    print project

    stackbounds = renderapi.stack.get_stack_bounds(stack,render=render)
    sectionbounds = renderapi.stack.get_bounds_from_z(stack,z,render=render)

    cx1 = (stackbounds['minX'] - stackbounds['maxX'])/2
    cy1 = (stackbounds['minY'] - stackbounds['maxY'])/2

    cx2 = (sectionbounds['minX'] - sectionbounds['maxX'])/2
    cy2 = (sectionbounds['minY'] - sectionbounds['maxY'])/2

    dx = sectionbounds['minX']
    dy = sectionbounds['minY']

    #bb = renderapi.image.get_bb_image(stack, z, stackbounds['minX'], stackbounds['minY'], width, height, scale, render=render)

    print("This is z: %d" % z)
    print("Stackbounds: %s" % stackbounds)
    print("Sectionbounds: %s" % sectionbounds)

    tilespecdir = os.path.join(output_dir,project,stack,'sections_at_%s'%str(scale),'tilespecs_%s'%tagstr)
    if os.path.exists(tilespecdir):
		print "Path Exists!"
    else:
		os.makedirs(tilespecdir)

    [q,r] = divmod(z,1000)
    s = int(r/100)

    directory = os.path.join(output_dir,project,stack,'sections_at_%s'%str(scale),'%03d'%q,"%d"%s)
    if not os.path.exists(directory):
		os.makedirs(directory)

    filename = os.path.join(output_dir,project,stack,'sections_at_%s'%str(scale),'%03d'%q,"%d"%s,'%s.tif'%str(float(z)))

    #if not os.path.isfile(filename):
    renderapi.client.renderSectionClient(stack, output_dir, [z], scale=str(scale), render=render, channel=channel, format='tif', doFilter=False, fillWithNoise=False)

    tilespecs = renderapi.tilespec.get_tile_specs_from_z(stack,z,render=render)
    t = tilespecs[0]
    d = t.to_dict()
    print(d)
    d['channels'] = []
    d['mipmapLevels']['0']['imageUrl'] = filename
    d['minIntensity'] = 0
    d['maxIntensity'] = 255
    d['width'] = stackbounds['maxX']*scale
    d['height'] = stackbounds['maxY']*scale
    d['z'] = newz
    scstr = str(1/scale)
    d['transforms']['specList'][0]['dataString'] = "%s 0.0000000000 0.0000000000 %s %d %d"%(scstr, scstr, 0.0,0.0)
    t.from_dict(d)
    allts = [t]
    tilespecfilename = os.path.join(output_dir,project,stack,'sections_at_%s'%str(scale),'tilespecs_%s'%tagstr,'tilespec_%04d.json'%z)
    print tilespecfilename
    fp = open(tilespecfilename,'w')
    json.dump([ts.to_dict() for ts in allts] ,fp,indent=4)
    fp.close()
    return tilespecfilename



def find_tile_pair(render, ref_stack, ts, M):
    ts_geom = tilespec_to_bounding_box_polygon(ts)

    width = ts.width
    height = ts.height
    minx = ts.minX
    miny = ts.minY
    p = {}
    p['id']=ts.tileId
    p['groupId']=ts.layout.sectionId

    paired = render.run(renderapi.tilespec.get_tile_specs_from_box,ref_stack,ts.z,minx,miny,width,height)
    overlap_tuples = []
    for ts2 in paired:

        ts2_geom = tilespec_to_bounding_box_polygon(ts2)
        overlap = ts_geom.intersection(ts2_geom)
        frac_overlap = overlap.area/ts_geom.area
        overlap_tuples.append((ts2,frac_overlap))
    sorted_overlaps_tuples = sorted(overlap_tuples,key= lambda x: x[1])

    #print ts.tileId,sorted_overlaps_tuples[0][1],sorted_overlaps_tuples[-1][1]
    ts2 = sorted_overlaps_tuples[-1][0]
    q = {}
    q['id']=ts2.tileId
    q['groupId']=ts2.layout.sectionId
    pair = {'p':p,'q':q}
    #print sorted_overlaps_tuples,ts2.tileId,ts.tileId
    return pair,sorted_overlaps_tuples[-1][1]


def find_overlapping_tiles (render,referenceStack,stack,z,M,overlap_thresh):
    all_ts = render.run(renderapi.tilespec.get_tile_specs_from_z,stack,z)
    pairs = []
    for ts in all_ts:
        ts.tforms.append(M) #apply the gross registration
        pair,overlap = find_tile_pair(render,referenceStack,ts,M)
        print(pair['p']['id'], pair['q']['id'], overlap)
        if overlap > overlap_thresh:
            pairs.append(pair)
    return pairs

def find_overlapping_tiles_hack (render,referenceStack,stack,z,M,overlap_thresh):
    all_ts = render.run(renderapi.tilespec.get_tile_specs_from_z,referenceStack,z)
    pairs = []
    for ts in all_ts:
        ts.tforms.append(M) #apply the gross registration
        pair,overlap = find_tile_pair(render,stack,ts,M)
        #print pair['p']['id'],pair['q']['id'],overlap
        #if overlap > overlap_thresh:
        #    pairs.append(pair)
        t = ts.tileId
        pair['q']['id'] = pair['p']['id']
        #pair['p']['id'] = t
        pair['p']['id'] = '2' + t[1:] # force change to tile in session 2 (hack)
        pairs.append(pair)

    return pairs


def convert_M2tform(M):
    tform = AffineModel(M00=M[0][0],
                        M10=M[1][0],
                        M01=M[0][1],
                        M11=M[1][1],
                        B0=M[0][2],
                        B1=M[1][2])
    return tform

def compute_SIFT(img1,img2,outImg,sc):

    print ("Computing sift")
	# Initiate SIFT detector

    sift = cv2.xfeatures2d.SIFT_create(sigma=1.6,nOctaveLayers=3)

	# find the keypoints and descriptors with SIFT
    kp1, des1 = sift.detectAndCompute(img1,None)
    kp2, des2 = sift.detectAndCompute(img2,None)

	# BFMatcher with default params
    bf = cv2.BFMatcher()
    matches = bf.knnMatch(des1,des2, k=2)
    print(len(matches))


	# Apply ratio test
    good = []
    goodpts = []
    for m,n in matches:
        if m.distance < 0.4*n.distance:
            good.append([m])
            goodpts.append(m)
    if outImg !="":
		#visualize matches
        img3 = cv2.drawMatchesKnn(img1,kp1,img2,kp2,good,None,flags=4)
        cv2.imwrite(outImg,img3)

    print(len(goodpts))
    if len(goodpts)>3:
        src_pts = np.float32([ kp1[m.queryIdx].pt  for m in goodpts ])
        dst_pts = np.float32([ kp2[m.trainIdx].pt  for m in goodpts ])
        M = cv2.estimateRigidTransform(src_pts, dst_pts,True)
        model = RansacAffineModel()

        r = RansacAffineModel()
        M = RansacAffineModel.A_from_ransac(r,src_pts.T,dst_pts.T,model)[0]
    else:
        print("Not enough matches are found !")
        M = [[1.0 ,0.0, 0.0],[0.0, 1.0, 0.0]]

    #adjust to scale
    M[0][2] = M[0][2]/sc
    M[1][2] = M[1][2]/sc

    print M
    return convert_M2tform(M)




def calculate_gross_registration(render, referenceStack,stack,z,sc):
    print ("Calculating Gross Registration")
    print (referenceStack,stack,z,sc)
    try:
        I1 = renderapi.image.get_section_image(referenceStack, z, scale=sc,filter=True,render=render)
        I2 = renderapi.image.get_section_image(stack,z,scale=sc, filter=True,render=render)
    except:
        print("Something wrong with the input! Either your stack name or owner/project is incorrect!")

    M = compute_SIFT(I1,I2,"test.tif",sc)
    return M

def process_tile(render,stack,referenceStack,pairs,index):
    pair = pairs[index]
    I1 = renderapi.image.get_tile_image_data(stack, pair['p']['id'], excludeAllTransforms=True, render=render,img_format='png')
    I2 = renderapi.image.get_tile_image_data(referenceStack, pair['q']['id'], excludeAllTransforms=True, render=render,img_format='png')
    sift = cv2.xfeatures2d.SIFT_create(sigma=1.6,nOctaveLayers=5)
    [kp1, des1] = sift.detectAndCompute(I1,None)
    #kp2, des2 = sift.detectAndCompute(I2,None)


    #M = compute_SIFT(I1,I2,"testtile.png",1.0)
    #cv2.imwrite("tilestack.tif",I1)
    #cv2.imwrite("tilerefstack.tif",I2)
    ts = renderapi.tilespec.get_tile_spec(stack, pair['p']['id'],render=render)
    print ts.tforms
    #print M
    print type(ts.tforms)
    #print type(M)
    #ts.tforms.append(M)
    return ts

def register_pairs(render, pairs, stack, referenceStack, pool_size):

    #pairs = [pairs[7]]
    #indices = range(0,len(pairs))
    #mypartial = partial(process_tile,render,stack,referenceStack,pairs)
    #with renderapi.client.WithPool(pool_size) as pool:
    #        tilespecs = pool.map(mypartial,indices)

    #return tilespecs

    #mypartial = partial(process_tile,render,stack,referenceStack)
    #with renderapi.client.WithPool(pool_size) as pool:
#        tilespecs = pool.map(mypartial,newpairs)
#    #tilespecs = np.array(tilespecs)
#    alltilespecs = []
#    for item in tilespecs:
#        alltilespecs.append(item)
#    print(type(alltilespecs))
#    return alltilespecs



    newpairs = [pairs[8]]
    tilespecs = []
    index = 0
    #for pair in newpairs:
    #        ts = process_tile(render,stack,referenceStack,pair)
    for i in range(0,5):
        pair = pairs[i]
        print (index)
        I1 = renderapi.image.get_tile_image_data(stack, pair['p']['id'], excludeAllTransforms=True, render=render)
        I2 = renderapi.image.get_tile_image_data(referenceStack, pair['q']['id'], excludeAllTransforms=True, render=render)
        M = compute_SIFT(I1,I2,"",1.0)
        cv2.imwrite("tilestack.tif",I1)
        cv2.imwrite("tilerefstack.tif",I2)
        print(stack)
        print(pair['p']['id'])
        ts = renderapi.tilespec.get_tile_spec(stack, pair['p']['id'],render=render)
        ts.tforms.append(M)
        #transforms.append(M)
        tilespecs.append(ts)
        index =index + 1
    return tilespecs

def upload_tilespecs(render,tempStack,tilespecs):
    renderapi.stack.create_stack(tempStack,render=render)
    renderapi.stack.set_stack_state(tempStack, state='LOADING',render=render)
    renderapi.client.import_tilespecs(tempStack, tilespecs, render=render)
    renderapi.stack.set_stack_state(tempStack, state='COMPLETE',render=render)
   

def upload_tilespecs_and_extract(render,tempStack,tilespecs,steps,SIFTminScale,SIFTmaxScale, matchcollection,tileIds,filterflag):
    #renderapi.stack.create_stack(tempStack,render=render)
    #renderapi.stack.set_stack_state(tempStack, state='LOADING',render=render)
    #renderapi.client.import_tilespecs(tempStack, tilespecs, render=render)
    #renderapi.stack.set_stack_state(tempStack, state='COMPLETE',render=render)
    
    #sift parameters FeatureExtractionParameters, MatchDerivationParameters,SiftPointMatchOptions

    s = SiftPointMatchOptions(SIFTsteps=steps,SIFTminScale=SIFTminScale,SIFTmaxScale=SIFTmaxScale)


    try:
        p = pointMatchClient(tempStack, matchcollection, [tileIds], 
                    filter=filterflag,
                    excludeAllTransforms=True,
                    sift_options=s,
                    render=render)

    except (Exception):
        print "No point matches found"
        raise

def pmclient_register(render,stack,stackChannel,referenceStack,referenceStackChannel,steps,filterflag,SIFTminScale,SIFTmaxScale,matchcollection,pair):
    ts1 = renderapi.tilespec.get_tile_spec(stack,pair['p']['id'],render=render)
    ts2 = renderapi.tilespec.get_tile_spec(referenceStack,pair['q']['id'],render=render)
    tempStack = "%s_%s"%(pair['p']['id'],pair['q']['id'])
    ts1.z = 0
    ts2.z = 1
    tilespecs = [ts1,ts2]
    tileIds = [pair['p']['id'],pair['q']['id']]
  
    s = SiftPointMatchOptions(SIFTsteps=steps,SIFTminScale=SIFTminScale,SIFTmaxScalex=SIFTmaxScale,renderScale=0.5)

    try:
        p = pointMatchClient(stack, matchcollection, [tileIds], stack2=referenceStack,
                    filter=filterflag,
                    excludeAllTransforms=True,
                    stackChannels=stackChannel,
                    stack2Channels=referenceStackChannel,
                    sift_options=s,
                    render=render)

    except (Exception):
        print "No point matches found"
        raise


def dump_images(render,pair,stack,referenceStack):
    I1 = renderapi.image.get_tile_image_data(stack, pair['p']['id'], excludeAllTransforms=True, render=render)
    I2 = renderapi.image.get_tile_image_data(referenceStack, pair['q']['id'], excludeAllTransforms=True, render=render)
    I3 = np.concatenate((I1,I2),axis=1)
    pname = "%s_%s.png"%(pair['p']['id'], pair['q']['id'])
    cv2.imwrite(pname,I3)


def register_tiles(render,
                                 src_stack,
                                 dst_stack,
                                 matchCollection,
                                 num_local_transforms,
                                 Transform,pairs,M,useGross):
    print src_stack,dst_stack,matchCollection,num_local_transforms
    tilespecs_p = renderapi.tilespec.get_tile_specs_from_stack(src_stack, render=render)
    tilespecs_q = renderapi.tilespec.get_tile_specs_from_stack(dst_stack, render=render)
    tilespecs_res = []
    finaltforms = []
    for pair in pairs:
        pid = pair['p']['id']
        pgroup = pair['p']['groupId']
        qid = pair['q']['id']
        qgroup = pair['q']['groupId']
        try:
            match = renderapi.pointmatch.get_matches_from_tile_to_tile(matchCollection, pgroup, pid,qgroup, qid, render=render)[0]

            if match['qId']==pid:
                pid = match['qId']
                qid = match['pId']
                p_pts = np.array(match['matches']['q']).T
                q_pts = np.array(match['matches']['p']).T
            else:
                pid = match['pId']
                qid = match['qId']
                p_pts = np.array(match['matches']['p']).T
                q_pts = np.array(match['matches']['q']).T

            tsp = next(ts for ts in tilespecs_p if ts.tileId == pid)
            tsq = next(ts for ts in tilespecs_q if ts.tileId == qid)
            tforms = tsq.tforms[num_local_transforms:]
            dst_pts = renderapi.transform.estimate_dstpts(tforms,q_pts)
            p_pts_global = renderapi.transform.estimate_dstpts(tsp.tforms[num_local_transforms:],p_pts)
            final_tform = Transform()
            final_tform.estimate(p_pts,dst_pts)

            #print final_tform
            finaltforms.append(final_tform)
            model = RansacAffineModel()
            #r = RansacAffineModel()
            #ransacM = RansacAffineModel.A_from_ransac(r,p_pts.T,dst_pts.T,model,match_threshold=3)[0]
            #print ransacM
            #tsp.tforms=tsp.tforms[0:num_local_transforms]+[final_tform]
            #tsp.tforms=tsp.tforms[0:num_local_transforms]+[M]
            if useGross == True:
                tsp.tforms=[M] + tsq.tforms[0:num_local_transforms]
            else:
                tsp.tforms=[final_tform] + tsq.tforms[0:num_local_transforms]
                #tsp.tforms=[convert_M2tform(ransacM)] + tsq.tforms[0:num_local_transforms]
            tilespecs_res.append(tsp)
        except(Exception):
            #tsp = next(ts for ts in tilespecs_p if ts.tileId == pid)
            #tilespecs_res.append(tsp)
            raise
            print ('Not adding tilespec')

    return tilespecs_res,final_tform

def get_pairs_for_tileIds(pairs,tileIds):
    newpairs = []
    for pair in pairs:
        if (pair['p']['id'] in tileIds ) | (pair['q']['id'] in tileIds ):
            newpairs.append(pair)

    return newpairs

def calculate_gross_registration_render(render, referenceStack, referenceStackChannel, stack, stackChannel, sc, project, z, output_dir, grossRefStack, grossStack, filterflag):
    tagstr = 'scaled'
    jsonfiles1 = []
    jsonfiles2 = []
    tilespecfile1 = downsample_z(render,referenceStack,output_dir,sc,project,tagstr,[z,z], referenceStackChannel)
    jsonfiles1.append(tilespecfile1)

    tilespecfile2 = downsample_z(render,stack,output_dir,sc,project,tagstr,[z,z], stackChannel)
    jsonfiles2.append(tilespecfile2)

    renderapi.stack.create_stack(grossRefStack,render=render)
    renderapi.client.import_jsonfiles_parallel(grossRefStack,jsonfiles1,render=render)
    renderapi.stack.create_stack(grossStack,render=render)
    renderapi.client.import_jsonfiles_parallel(grossStack,jsonfiles2,render=render)

    M = convert_M2tform([[1.0 ,0.0, 0.0],[0.0, 1.0, 0.0]])
    pairs = find_overlapping_tiles (render,grossRefStack,grossStack,z,M,0.0)
    pmclient_register(render,grossStack,None,grossRefStack,None,3,filterflag,0.3,1.0,"grossRegmatches",pairs[0])
    tilespecs,tform = register_tiles(render,grossStack,grossRefStack,
                                     "grossRegmatches",
                                     1,
                                     RigidModel,pairs,M,False)
    tform.M[0,2] = tform.M[0,2] /sc
    tform.M[1,2] = tform.M[1,2] /sc
    
    return tform

class CalculateRegistration(RenderModule):
    def __init__(self,schema_type=None,*args,**kwargs):
        if schema_type is None:
            schema_type = CalculateRegistrationParameters
        super(CalculateRegistration,self).__init__(schema_type=schema_type,*args,**kwargs)

    def run(self):
        referenceStack = self.args['referenceStack']
        stack = self.args['stack']
        referenceStackChannel = self.args['referenceStackChannel']
        stackChannel = self.args['stackChannel']
        outputStack = self.args['outputStack']
        sc = self.args['scale']
        z = self.args['section']
        pool_size = self.args['pool_size']
        tileId = self.args['tileId']
        pointx = self.args['pointx']
        pointy = self.args['pointy']
        filterflag = self.args['filter']
        steps = self.args['steps']
        SIFTminScale = self.args['SIFTminScale']
        SIFTmaxScale = self.args['SIFTmaxScale']
        useGross = self.args['useGross']
        matchcollection =self.args['matchcollection']
        project = self.args['render']['project']
        output_dir = self.args['output_dir']
        grossRefStack = self.args['grossRefStack']
        grossStack = self.args['grossStack']

        print ("This is len tile id: %d"%len(self.args['tileId']))

        #downsample sections for gross alignment
        M = calculate_gross_registration_render(self.render, referenceStack, referenceStackChannel, stack, stackChannel, sc, project, z,
            output_dir, grossRefStack, grossStack, filterflag)
        M =M.invert()
        print (M)
        
        #S = renderapi.stack.get_stack_sectionData(stack,render = self.render)
        #print S[0]

        #S = renderapi.stack.get_stack_sectionData(referenceStack,render = self.render)
        #print S[0]

        #find overlapping pairs
        print("Now finding overlapping tile pairs...............")
        pairs = find_overlapping_tiles (self.render,referenceStack,stack,z,M,0.5)
        #pairs = find_overlapping_tiles_hack (self.render,referenceStack,stack,z,M,0.5)

        # EAP: Do we need this? It seems like an alternate way to find overlapping data.
        if (pointx > 0) & (pointy > 0) :
            point = [pointx,pointy]
            print(point)
            offset = 10
            ts = renderapi.tilespec.get_tile_specs_from_minmax_box(stack,z,point[0]-offset, point[0] + offset, point[1] - offset, point[1] + offset, render=self.render)
            tileIds = []
            for t in ts:
                    tileIds.append(t.tileId)
            pairs = get_pairs_for_tileIds(pairs,tileIds)

        for p in pairs:
            print p['p']['id'],p['q']['id']


        if len(pairs) < 1:
            print("No tile pairs to register!")
            exit(0)


        #calculate point matches
        mypartial = partial(pmclient_register,self.render,stack,stackChannel,referenceStack,referenceStackChannel,steps,filterflag, SIFTminScale,SIFTmaxScale,matchcollection)
        with renderapi.client.WithPool(pool_size) as pool:
            pool.map(mypartial,pairs)

        tilespecs,finaltform = register_tiles(self.render,stack,referenceStack,
                                        matchcollection,
                                        1,
                                        RigidModel,pairs,M,useGross)
        
        # The outlier code does not work currently.
        # tilespecs = adjust_outliers(tilespecs,M)

        upload_tilespecs(self.render,outputStack,tilespecs)


if __name__ == "__main__":
    mod = CalculateRegistration(input_data=example_parameters)
    mod.run()
