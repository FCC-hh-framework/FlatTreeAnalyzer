#!/usr/bin/env python
import subprocess, glob, optparse, json, ast, os, sys, collections, warnings, ROOT
from tools import producePlots, Process, formatted
from pprint import pprint
import ntpath
import importlib
import yaml
import commands
import time

#__________________________________________________________
def file_exist(myfile):
    import os.path
    if os.path.isfile(myfile): return True
    else: return False

#_____________________________________________________________________________
def options():
    parser = optparse.OptionParser(description="analysis parser")
    parser.add_option('-n', '--analysis_name', dest='analysis_name', type=str, default='')
    parser.add_option('-c', '--heppy_cfg', dest='heppy_cfg', type=str, default='')
    parser.add_option('-j', '--proc_file_json', dest='proc_file_json', type=str, default='/afs/cern.ch/work/h/helsens/public/FCCDicts/procDict.json')
    parser.add_option('-t', '--heppy_tree_dir', dest='heppy_tree_dir', type=str, default='')
    parser.add_option('-o', '--analysis_output', dest='analysis_output', type=str, default='')
    parser.add_option('-p', '--param_file', dest='param_file', type=str, default='')
    parser.add_option('-m', '--multi_threading', dest='MT', default=False, action='store_true')
    parser.add_option('-l', '--latex_table', dest='latex_table', default=False, action='store_true')
    parser.add_option('--no_plots', dest='no_plots', default=False, action='store_true')
    parser.add_option('--nev', dest='nevents', type=int, default='-1')
    parser.add_option('--force', dest='force', default=False, action='store_true')

    parser.add_option('--lsf', dest='lsf', default=False, action='store_true')
    parser.add_option('-q', '--queue', dest='queue', type=str, default='1nh')
    parser.add_option('--clean', dest='clean', default=False, action='store_true')

    # run on single selection
    parser.add_option('--sel', dest='sel', type=str, default='')

    return parser.parse_args()

#______________________________________________________________________________
def main():
    
    ops, args = options()

    args = split_comma_args(args)

    # give this analysis a name
    analysisName = ops.analysis_name

    # heppy analysis configuration
    heppyCfg = ops.heppy_cfg

    # process dictionary
    processDict = ops.proc_file_json

    # heppy trees location directory
    treeDir = ops.heppy_tree_dir

    # analysis dir
    analysisDir = ops.analysis_output

    # param file
    paramFile = ops.param_file

    module_path = os.path.abspath(paramFile)
    module_dir = os.path.dirname(module_path)
    base_name = os.path.splitext(ntpath.basename(paramFile))[0]

    sys.path.insert(0, module_dir)
    param = importlib.import_module(base_name)

    # tree location
    treePath = '/heppy.FCChhAnalyses.{}.TreeProducer.TreeProducer_1/tree.root'.format(analysisName)
    if "FCCee" in processDict:
        treePath = '/FCCeeAnalyses.{}.TreeProducer.TreeProducer_1/tree.root'.format(analysisName)

    #multi-threading
    MT = ops.MT

    #lsf
    lsf = ops.lsf
    queue = ops.queue

    # selection
    sel = ops.sel

    # check if output dir exists already
    '''if ops.force and not ops.clean:
        print 'removing {}'.format(analysisDir)
        processCmd('rm -rf {}'.format(analysisDir))
        os.makedirs(analysisDir)

    elif os.path.exists(analysisDir) and not ops.clean and not ops.sel:
        print ''
        sys.exit('Output dir: "'+analysisDir+'" exists. To overwrite existing dir run with --force option')
    ''' 

    # retrieve list of processes from heppy cfg
    processes = []
    with open(heppyCfg) as f:
        lines = f.readlines()
        for l in lines:
            if 'splitFactor' in l:
                processes.append(l.rsplit('.', 1)[0])

    #processes = [c.name for c in heppyCfg.selectedComponents]

    with open(processDict) as f:
        procDict = json.load(f)
    
    # run on single signal hypothesis, also used in lsf btach submission
    if sel:
        block = collections.OrderedDict()
        formBlock(processes, procDict, param.signal_groups,param.background_groups, sel, treeDir, treePath, block, ops.nevents)
        producePlots(param, block, sel, ops)

    elif not lsf:
        if MT:
            runMT(processes, procDict, param, treeDir, treePath, analysisDir, MT, ops)
        else:
            for sh in param.selections.keys():

                block = collections.OrderedDict()

                formBlock(processes, procDict, param.signal_groups,param.background_groups,sh, treeDir, treePath, block, ops.nevents)

            ### run analysis
                producePlots(param, block, sh, ops)

    else:
        runLSF(processes, procDict, param, treeDir, treePath, analysisDir, ops)

import multiprocessing as mp
#_____________________________________________________________________________________________________
def runMT(processes, procDict, param, treeDir, treePath, analysisDir, MT, ops):
    threads = []
    for sh in param.selections.keys():

        block = collections.OrderedDict()
        formBlock(processes, procDict, param.signal_groups,param.background_groups,sh, treeDir, treePath, block, ops.nevents)
        thread = mp.Process(target=runMT_join,args=(block, param, sh,analysisDir, MT, ops ))
        thread.start()
        threads.append(thread)
    for proc in threads:
        proc.join()

#_____________________________________________________________________________________________________
def runMT_join(block, param, sh, analysisDir, MT, ops):
    print "START %s" % (sh)
    producePlots(param, block, sh, ops)    
    print "END %s" % (sh)

#_____________________________________________________________________________________________________
def runLSF(processes, procDict, param, treeDir, treePath, analysisDir, ops):


    # clean if asked for it
    if ops.clean:
        print 'Cleaning LSF for {} jobs...'.format(ops.analysis_output)
        processCmd('rm -rf BatchOutput/{} LSF*'.format(ops.analysis_output))
        sys.exit('cleaned up everything.')

    # first thing is to check whether previous submission (if any) succeeded
    selection_list_4sub = []
    nbad = 0
    for sh in param.selections.keys():
        selname = formatted(sh)
        outseldir = 'sel_'+selname
        name_batch_dir = 'BatchOutput/{}/{}'.format(ops.analysis_output, outseldir)
        rootfile = name_batch_dir + '/root_'+selname+'/histos.root'
        
        if not os.path.isfile(rootfile) or not isValidROOTfile(rootfile) or not getsize(rootfile):
            selection_list_4sub.append(sh)
            nbad += 1
    
    # keep submitting until nbad = 0
    if nbad > 0:
        print ' '
        print ' =========  Submitting {} jobs on {} queue ========='.format(nbad, ops.queue)

        jobCount=0
        for sh in selection_list_4sub:

            block = collections.OrderedDict()
            formBlock(processes, procDict, param.signal_groups,param.background_groups,sh, treeDir, treePath, block, ops.nevents)
            selname = formatted(sh)

            dummyscript="""
    unset LD_LIBRARY_PATH
    unset PYTHONHOME
    unset PYTHONPATH
    mkdir job
    cd job

    cp -r DUMMYHOMEDIR/init.sh .
    cp -r DUMMYHOMEDIR/bin .
    cp -r DUMMYHOMEDIR/templates .

    source ./init.sh

    python bin/analyze.py -n DUMMYANALYSISNAME -c DUMMYHEPPYCFG -t DUMMYTREELOCATION -p DUMMYTEMPLATEFILE -j DUMMYJSONFILE -o DUMMYOUTSELDIR --sel 'DUMMYSEL' -m --nev DUMMYNEVTS --no_plots

    mkdir -p DUMMYHOMEDIR/BatchOutput/DUMMYOUTDIR/DUMMYOUTSELDIR
    cp -r DUMMYOUTSELDIR DUMMYHOMEDIR/BatchOutput/DUMMYOUTDIR
            """

            outseldir = 'sel_'+selname

            # replace relevant parts in script and dump into file
            dummyscript = dummyscript.replace('DUMMYHOMEDIR', os.getcwd())
            dummyscript = dummyscript.replace('DUMMYANALYSISNAME', ops.analysis_name)
            dummyscript = dummyscript.replace('DUMMYHEPPYCFG', os.path.abspath(ops.heppy_cfg))
            dummyscript = dummyscript.replace('DUMMYTREELOCATION', os.path.abspath(ops.heppy_tree_dir))
            dummyscript = dummyscript.replace('DUMMYTEMPLATEFILE', os.path.abspath(ops.param_file))
            dummyscript = dummyscript.replace('DUMMYJSONFILE', os.path.abspath(ops.proc_file_json))
            dummyscript = dummyscript.replace('DUMMYOUTSELDIR', outseldir)
            dummyscript = dummyscript.replace('DUMMYSEL', sh)
            dummyscript = dummyscript.replace('DUMMYNEVTS', str(ops.nevents))
            dummyscript = dummyscript.replace('DUMMYOUTDIR', ops.analysis_output)
            script = dummyscript

            name_batch_dir = 'BatchOutput/{}/{}'.format(ops.analysis_output, outseldir)
            if not os.path.exists(name_batch_dir):
                os.makedirs(name_batch_dir)

            scriptdir = name_batch_dir+'/cfg/'
            if not os.path.exists(scriptdir):
                os.makedirs(scriptdir)

            with open('script.sh', "w") as f:
               f.write(script)
            processCmd('chmod u+x script.sh')
            processCmd('mv script.sh {}'.format(scriptdir))

            script = scriptdir+'script.sh'
            print 'Submitting job '+str(jobCount+1)+' out of '+str(len(selection_list_4sub))

            cmd = 'bsub -o '+name_batch_dir+'/std/STDOUT -e '+name_batch_dir+'/std/STDERR -q '+ops.queue
            cmd +=' -J '+outseldir+' "'+os.path.abspath(script)+'" '

            # submitting jobs
            output = processCmd(cmd)
            while ('error' in output):
                time.sleep(1.0);
                output = processCmd(cmd)
                if ('error' not in output):
                    print 'Submitted after retry - job '+str(jobCount+1)

            jobCount += 1
        
    # no bad job is found, can thus collect output
    else:
        print '================================================================'
        print 'Submission was successful, now collecting output ...'
        print ''
            
        # 1 root file per signal hypothesis, simply copy in properly name dir
        # and run producePlots with runFull = false
        for sh in param.selections.keys():
            selname = formatted(sh)
            outseldir = 'sel_'+selname
            name_batch_dir = 'BatchOutput/{}/{}'.format(ops.analysis_output, outseldir)
            root_dir = '{}/root_{}'.format(name_batch_dir,selname)
            cmd = 'cp -r {} {}'.format(root_dir,ops.analysis_output)
            
            local_root_dir = '{}/root_{}'.format(ops.analysis_output,selname)
            
            print local_root_dir
            
            # collecting files
            if not os.path.exists(local_root_dir):
                processCmd(cmd)
            
            # run analysis on histos
            block = collections.OrderedDict()
            formBlock(processes, procDict, param.signal_groups,param.background_groups,sh, treeDir, treePath, block, ops.nevents)
            
	    param.runFull = False
            producePlots(param, block, sh, ops)

#______________________________________________________________________________
def formBlock(processes, procdict, sb, bb, shyp, treedir, treepath, block, nevents):
    
    for label, procs in sb.iteritems():
       if label == shyp:
           block[shyp] = fillBlock(procs, processes, procdict, treedir, treepath, nevents)
    for label, procs in bb.iteritems():
       block[label] = fillBlock(procs, processes, procdict, treedir, treepath, nevents)

#______________________________________________________________________________
def fillBlock(procs, processes, procdict, treedir, treepath, nevents):
     blocklist = []
     for procstr in procs:
         for pname in processes:
             # fix new call name format in FCChhAnalyses/.../analysis.py
             if pname.find("sample.")>=0 : pname=pname.replace("sample.","")
             # fix commented names in lists
             if pname.find("#")>=0 : continue
             if procstr == pname:
                 xsec = procdict[pname]['crossSection']
                 nev = procdict[pname]['numberOfEvents']
                 if nevents>0: nev=nevents
                 sumw = procdict[pname]['sumOfWeights']
                 eff = procdict[pname]['matchingEfficiency']
                 kf = procdict[pname]['kfactor']
                 matched_xsec = xsec*eff
                 tree = '{}/{}/{}'.format(os.path.abspath(treedir), pname, treepath)
                 
                 #read from heppy yaml file job efficiency       
                 filestr = os.path.abspath(treedir) + '/' + pname + '/processing.yaml'
                 corrFac = 1.

                 if not file_exist(filestr):
                     blocklist.append(Process(pname,tree,nev,sumw,xsec,eff,kf))
                     continue

                 with open(filestr, 'r') as stream:
                     try:
                        dico = yaml.load(stream)
                        try:
                            dico['processing']
                            corrFac *= float(dico['processing']['nfiles'])/dico['processing']['ngoodfiles']
                        except TypeError, e:
                            print 'I got a  TypeError - reason "%s"' % str(e)
                     except yaml.YAMLError as exc:
                        print(exc)                 
                 sumw *= corrFac
                 nev *= corrFac    
                 blocklist.append(Process(pname,tree,nev,sumw,xsec,eff,kf))
     return blocklist

#______________________________________________________________________________
def split_comma_args(args):
    new_args = []
    for arg in args:
        new_args.extend( arg.split(',') )
    return new_args

#____________________________________________________________________________________________________________
### processing the external os commands
def processCmd(cmd, quite = 0):
    status, output = commands.getstatusoutput(cmd)
    if (status !=0 and not quite):
        print 'Error in processing command:\n   ['+cmd+']'
        print 'Output:\n   ['+output+'] \n'
    return output

#_____________________________________________________________
def isValidROOTfile(infile):
    valid = True
    with warnings.catch_warnings(record=True) as was:
        f=ROOT.TFile.Open(infile)
        ctrlstr = 'probably not closed'
        for w in was:
            if ctrlstr in str(w.message):
                valid = False
    return valid


#__________________________________________________________
def getsize(f):
    exist=os.path.isfile(f)
    if exist:
        size = os.path.getsize(f)
        return size
    return -1

#______________________________________________________________________________
if __name__ == '__main__': 
    main()
