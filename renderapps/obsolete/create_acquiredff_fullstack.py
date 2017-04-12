import argparse
import jsonschema
import json
import os
import subprocess
import copy
from tilespec import TileSpec,Layout,AffineModel
import numpy as np
import json


def num2str(num,digits):
    mystr=str(num)
    if digits>len(mystr):
        prefix = "0"* (digits-len(mystr))
        mystr = prefix + mystr
    return mystr


def updatejsonfilewithz(json_file,ch,rib,sess,sect,ffdir):
    ff_file=os.path.join(ffdir,'%s_rib%04dsess%04dsect%04d.json'%(ch,rib,sess,sect))
    
    with open(json_file) as json_data:
	stts = json.load(json_data)
    print(len(stts))
    with open(ff_file) as json_data:
	ffts = json.load(json_data)
    print(len(ffts))
    z = ffts[0]['z']
    for ts in stts:
	ts['z'] = z
    with open(json_file,'w') as outfile:
	json.dump(stts,outfile)


if __name__ == '__main__':
    raise(Exception('THIS NEEDS TO BE UPDATED FOR NEW API'))
    parser = argparse.ArgumentParser(description="Create Stitched Stack to be used for alignment")
    parser.add_argument('--rootDir', nargs=1, help='project directory', type=str)
    parser.add_argument('--firstStatetableNum', nargs=1, help='First State table Num', type=int)
    parser.add_argument('--lastStatetableNum', nargs=1, help='Last State table Num', type=int)
    parser.add_argument('--outputStack', nargs=1, help='Output Stack Prefix', type=str)
    parser.add_argument('--updateZval', dest='updateZval',help='Flag for updating z value from flatfield tilespecs',action='store_true',default=False)

    args = parser.parse_args()


    rootdir = args.rootDir[0]
	

    #get all statetablefiles
    statetablefiles=[]
    for x in range(args.firstStatetableNum[0], args.lastStatetableNum[0]+1):
        statetablefiles.append(rootdir+"/scripts_ff/statetable_"+num2str(x,4))

    print statetablefiles

    dflist = []
    for i in range(0,len(statetablefiles)):
	print statetablefiles[i]
        df_temp = pd.read_csv(statetablefiles[i])
        dflist.append(df_temp)


    df = pd.concat(dflist)

    
    ff_tilespec_dir = os.path.join(rootdir,'processed','flatfieldcorrected_tilespec')
    stitched_tilespec_dir = os.path.join(rootdir,'processed','stitched_tilespec_ff')
    stitched_transform_tilespec_dir = os.path.join(rootdir,'processed','stitched_transformspec_ff')

    my_env = os.environ.copy()
    client_scripts = '/pipeline/render/render-ws-java-client/src/main/scripts'

    baseurl = 'http://ibs-forrestc-ux1.corp.alleninstitute.org:8080/render-ws/v1'
    owner = 'Sharmishtaas'
    project = '%s'%os.path.split(rootdir)[1]
    project_params = ['--baseDataUrl',baseurl,'--owner',owner,'--project',project]

    print len(df)

    for ((ch,sess),group) in df.groupby(['ch_name','session']):
        #print sess

        #if (1 == 1):
        if (ch == "DAPI_1"):
            stackstr = args.outputStack[0]+'_'+ch


            cmd=[os.path.join(client_scripts,'manage_stacks.sh')]+\
                project_params+\
                ['--stack',stackstr,'--action','CREATE','--cycleNumber','1','--cycleStepNumber','3']

            proc=subprocess.Popen(cmd,env=my_env,stdout=subprocess.PIPE)
            proc.wait()
            print "created stack",stackstr



            for ((rib,sect),g2) in group.groupby(['ribbon','section']):
                print "rib = %s, sect = %s"%(str(rib),str(sect))
                if (rib > -1 ):
                #if (rib == 0) & (sect == 0):
                    json_file=os.path.join(stitched_tilespec_dir,'%s_rib%04dsess%04dsect%04d.json'%(ch,rib,sess,sect))
		    if (args.updateZval):
			print "Updating z value for %s!"%json_file
		    	updatejsonfilewithz(json_file,ch,rib,sess,sect,ff_tilespec_dir)
                    tform_file = os.path.join(stitched_transform_tilespec_dir,'rib%04dsess%04dsect%04d.json'%(rib,sess,sect))
                    print json_file
                    print tform_file

                    cmd=[os.path.join(client_scripts,'import_json.sh')]+ \
                        project_params +\
                        ['--stack',stackstr] +\
                        ['--transformFile',tform_file]+\
                        [json_file]



                    proc=subprocess.Popen(cmd,env=my_env,stdout=subprocess.PIPE)
                    proc.wait()


            cmd=[os.path.join(client_scripts,'manage_stacks.sh')]+\
                project_params +\
                ['--stack',stackstr,'--action','SET_STATE',\
                 '--stackState','COMPLETE']
            proc=subprocess.Popen(cmd,env=my_env,stdout=subprocess.PIPE)
            proc.wait()
            print "completed stack",stackstr
            url = baseurl + '/owner/' + owner + '/project/' + project + '/stack/' + stackstr + '/z/0/png-image?scale=.2'
            print 'example URL',url
