#!/usr/bin/env python
from __future__ import division
import ROOT, collections, os, sys
from ROOT import TFile, TTree, TTreeFormula, gROOT, TH1D, TH2D, kRed, TLegend, THStack, TVector2,  TGraph, TMultiGraph
from math import sqrt
import warnings, re
from array import array

warnings.filterwarnings(action="ignore", category=RuntimeWarning, message="creating converter.*")
warnings.filterwarnings(action="ignore", category=RuntimeWarning, message="Deleting canvas.*")
warnings.filterwarnings(action="ignore", category=RuntimeWarning, message="Replacing existing*")

#_________________________________________
class CutSelector:

    #_____________________________________________________________________________________________________
    def __init__(self, tree, cuts):
        self.cuts = cuts
        self.formula = ROOT.TTreeFormula("Cut_formula", cuts, tree)

    #_____________________________________________________________________________________________________
    def evaluate(self, tree, event):
        # Important otherwise the vector is not loaded correctly
        self.formula.GetNdata()
        return self.formula.EvalInstance(event)

#_____________________________________________
class Process:

    #_____________________________________________________________________________________________________
    def __init__(self, name, tree="", nevents=-1, sumw=-1,xsec=-1., effmatch=1., kfactor=1.):

        self.name = name
        self.rt = tree
        self.n = nevents
        self.x = xsec # in pb
        self.e = effmatch
        self.k = kfactor
        self.s = sumw
        self.w = kfactor*xsec*effmatch/nevents #weight events /pb
        if sumw<nevents:
            self.w = kfactor*xsec*effmatch/sumw
        self.sv = collections.OrderedDict()
        self.sv2d = collections.OrderedDict()

    #_____________________________________________________________________________________________________
    def setName(self, name):
        self.name = name
        nsel = 0
        for s in self.sv.keys():
            selstr = 'sel{}'.format(int(nsel))
            nsel += 1
            for v in self.sv[s].keys():
              hname = '{}_{}_{}'.format(name, selstr, v)
              self.sv[s][v].SetName(hname)
        nsel = 0
        for s in self.sv2d.keys():
            selstr = 'sel{}'.format(int(nsel))
            nsel += 1
            for v in self.sv2d[s].keys():
              hname = '{}_{}_{}'.format(name, selstr, v)
              self.sv2d[s][v].SetName(hname)
        

    #_____________________________________________________________________________________________________
    def run(self, selections, dv, dv2d, ch='', name='', nevents=-1):
        # initialize dictionary selection: list of histograms
        if name=='':
            name = self.name
            nsel = 0
            for s in selections:
                self.sv[s] = collections.OrderedDict()
                self.sv2d[s] = collections.OrderedDict()
                selstr = 'sel{}'.format(int(nsel))
                nsel += 1

                for v in dv.keys() :
                    hname = '{}_{}_{}'.format(name, selstr, v)
                    self.sv[s][v] = TH1D(hname,hname+";"+dv[v]["title"]+";",dv[v]["bin"],dv[v]["xmin"],dv[v]["xmax"])
                    self.sv[s][v].Sumw2()

                for v in dv2d.keys() :
                    hname = '{}_{}_{}'.format(name, selstr, v)
                    self.sv2d[s][v] = TH2D(hname,hname+";"+dv2d[v]["titlex"]+";"+dv2d[v]["titley"]+";",
                                     dv2d[v]["binx"],dv2d[v]["xmin"],dv2d[v]["xmax"], 
                                     dv2d[v]["biny"],dv2d[v]["ymin"],dv2d[v]["ymax"], 
                                     ) 
                    self.sv2d[s][v].Sumw2()

        rf = TFile(self.rt)
        t = rf.Get("events")
        if nevents == -1:
            numberOfEntries = t.GetEntries()
            print 'running over the full entries  %i'%numberOfEntries
        else:
            numberOfEntries = nevents
            if t.GetEntries()<nevents:
                numberOfEntries = t.GetEntries()
                print 'running over the full entries  %i'%numberOfEntries
            else:
                print 'running over a subset of entries  %i'%numberOfEntries

        for s in selections:
            weighttrf_name=''
            weighttrfin_name=[]
            weighttrfless_name=[]

            sformula=s
            if '**' in s:
                s_split=s.split('**')
                sformula=s_split[1]
                weighttrf_name=s_split[0]
                weighttrf_name=weighttrf_name.strip()
                if 'tagin' in weighttrf_name:
                    nbtagex = int(filter(str.isdigit, weighttrf_name))
                    for i in range(nbtagex) :
                      weighttrfin_name.append('weight_%itagex'%(i))
                if 'tagless' in weighttrf_name:
                    nbtagex = int(filter(str.isdigit, weighttrf_name))
                    for i in range(nbtagex) :
                      weighttrfless_name.append('weight_%itagex'%(i))

            formula = TTreeFormula("",sformula,t)

            # loop over events
            print 'number of events:', numberOfEntries
            for entry in xrange(numberOfEntries) :
                if (entry+1)%500 == 0: 
                    sys.stdout.write( '... %i events processed ...\r'%(entry+1))
                    sys.stdout.flush()

                t.GetEntry(entry)
                weight = self.w * getattr(t,"weight")
                weighttrf=1.
                if weighttrf_name!='' and len(weighttrfin_name)==0 and len(weighttrfless_name)==0 :
                    weighttrf = getattr(t,weighttrf_name)
                elif weighttrf_name!='' and len(weighttrfin_name)!=0 and len(weighttrfless_name)==0 :
                    weighttrf = 1.
                    for i in weighttrfin_name :
                      weighttrf -= getattr(t,i)
                elif weighttrf_name!='' and len(weighttrfin_name)==0 and len(weighttrfless_name)!=0 :
                    weighttrf = 0.
                    for i in weighttrfless_name :
                      weighttrf += getattr(t,i)

                weight=weight*weighttrf
                # apply selection
                result  = formula.EvalInstance() 
                
                # fill histos on selected events
                if result > 0.:
                    for v in dv.keys():
                        divide=1
                        try:
                            divide=dv[v]["divide"]
                        except KeyError, e:
                            divide=1
                        self.sv[s][v].Fill(getattr(t,dv[v]["name"])/divide, weight)
                    for v in dv2d.keys():
                        self.sv2d[s][v].Fill(getattr(t,dv2d[v]["namex"]), getattr(t,dv2d[v]["namey"]), weight)

    #_____________________________________________________________________________________________________
    def getYields(self):
        yld = dict()
        for s in self.sv.keys():
            if not self.sv[s]:
                print 'you need to define at least one observable to run this analysis ...'
            # access random element to compute yield and error
            else:
                hist = self.sv[s].itervalues().next()
                # get values from first histograms
                err = ROOT.Double()      
                yld[s] = [hist.IntegralAndError(0, hist.GetNbinsX()+1, err), err]
        return yld

    #_____________________________________________________________________________________________________
    # necessary for adding processes 
    def add(self, other):
        for s in self.sv.keys():
            for v in self.sv[s].keys():
               self.sv[s][v].Add(other.sv[s][v])

#_____________________________________________________________________________________________________
def selectionDict(selections):
    
    seldict = collections.OrderedDict()
    for i in xrange(len(selections)):
       seldict[i] = selections[i]
    return seldict

#_____________________________________________________________________________________________________
def producePlots(param, block, sel, ops):

    selections = param.selections[sel]
    groups = block
    colors = param.colors
    variables = param.variables
    variables2D = param.variables2D
    unc = param.uncertainties 
    name = sel 
    lumi = param.intLumi
    version = param.delphesVersion 
    run_full = param.runFull
    analysisDir = ops.analysis_output
    MT = ops.MT
    latex_table=ops.latex_table
    no_plots=ops.no_plots
    nevents=ops.nevents
    
    analysisDir = formatted(analysisDir)
    name = formatted(name)
    
    print '======================================================================================'
    print '======================================================================================'
    print ''
    print 'Running full analysis:', name
    print ''
    print '======================================================================================'
    print '======================================================================================'
    
    proclist = []
    for label, listproc in groups.iteritems():
        for proc in listproc:
            proclist.append(proc)
    
    seldict = selectionDict(selections)
    selections = seldict.values()


    pdir = "{}/plots_{}/".format(analysisDir,name)
    rdir = "{}/root_{}/".format(analysisDir,name)

    # if analysis has not been ran before
    if run_full:

        if MT:  runAnalysisMT(proclist, selections, variables, variables2D, groups, name, nevents)
        else:   runAnalysis(proclist, selections, variables, variables2D, nevents)

       ### prepare outputs
        os.system("mkdir -p {}".format(pdir))
        os.system("mkdir -p {}".format(rdir))

        processes = []
        for label, procs in groups.items():
            mainproc = procs[0]
            mainproc.setName(label)
            if len(procs) > 0:
                for i in range(1,len(procs)):
                    mainproc.add(procs[i])
                processes.append(mainproc)

        hfile = ROOT.TFile("{}/histos.root".format(rdir),"RECREATE")
        saveHistos(processes, selections, variables, variables2D, hfile)
        hfile.Close()

    processes = groups.keys()
    hfile = ROOT.TFile("{}/histos.root".format(rdir))
    
    printYieldsFromHistos(processes, selections, variables, unc, lumi, hfile)
    if latex_table:
        printYieldsFromHistosAsLatexTable(processes, selections, variables, unc, lumi, hfile)

    if not no_plots:

        intLumiab = lumi/1e+06 
        lt = "FCC-hh Simulation (Delphes)"
        rt = "#sqrt{{s}} = 100 TeV,   L = {:.0f} ab^{{-1}}".format(intLumiab)

        try:
            helhc=param.HELHC
            if helhc:
                lt = "HE-LHC Simulation (Delphes)"
                rt = "#sqrt{{s}} = 27 TeV,   L = {:.0f} ab^{{-1}}".format(intLumiab)
        except :
            print 'Not HELHC'

        try:
            fccee=param.FCCee
            if fccee:
                lt = "FCC-ee Simulation (Delphes)"
                rt = "#sqrt{{s}} = {:.1f} GeV,   L = {:.0f} ab^{{-1}}".format(param.Energy,intLumiab)
        except :
            print 'Not HELHC'
        produceStackedPlots(processes, selections, variables, colors, lumi, pdir, lt, rt, False, False, hfile, param.ana_tex)
        produceStackedPlots(processes, selections, variables, colors, lumi, pdir, lt, rt, True, False, hfile, param.ana_tex)
        produceStackedPlots(processes, selections, variables, colors, lumi, pdir, lt, rt, False, True, hfile, param.ana_tex)
        produceStackedPlots(processes, selections, variables, colors, lumi, pdir, lt, rt, True, True, hfile, param.ana_tex)
        
        produceNormalizedPlots(processes, selections, variables, colors, lumi, pdir, lt, rt, False, hfile)
        produceNormalizedPlots(processes, selections, variables, colors, lumi, pdir, lt, rt, True, hfile)
        
        produce2DPlots(processes, selections, variables2D, colors, lumi, pdir, lt, rt, True, hfile)
        produce2DPlots(processes, selections, variables2D, colors, lumi, pdir, lt, rt, False, hfile)

    print '======================================================================================'
    print '======================================================================================'
    print ''
    print 'DONE'
    print ''
    print '======================================================================================'
    print '======================================================================================'


import multiprocessing as mp

#_____________________________________________________________________________________________________
def runMT_pool(args=('','','','','','')):
    proc,selections,variables,variables2D,sh,nev=args
    print "START %s" % (proc.name)
    proc.run(selections, variables, variables2D, proc.name, sh, nev)
    return proc
    print "END %s" % (proc.name)


#_____________________________________________________________________________________________________
def runAnalysisMT(listOfProcesses, selections, variables, variables2D, groups, name, nev):
    print 'NUMBER OF CORES    ',mp.cpu_count()
    print ''
    print 'Start looping on process trees:'
    print ''
    threads = []
    for proc in listOfProcesses:
        print '---------------------------'
        print proc.name
        print '---------------------------'
        print ''

        nsel = 0
        for s in selections:
            proc.sv[s] = collections.OrderedDict()
            proc.sv2d[s] = collections.OrderedDict()
            selstr = 'sel{}'.format(int(nsel))
            nsel += 1
            for v in variables.keys() :
                hname = '{}_{}_{}'.format(proc.name, selstr, v)
                proc.sv[s][v] = TH1D(hname,hname+";"+variables[v]["title"]+";",variables[v]["bin"],variables[v]["xmin"],variables[v]["xmax"])
                proc.sv[s][v].Sumw2()
                
            for v in variables2D.keys() :
                hname = '{}_{}_{}'.format(proc.name, selstr, v)
                proc.sv2d[s][v] = TH2D(hname,hname+";"+variables2D[v]["titlex"]+";"+variables2D[v]["titley"]+";",
                                     variables2D[v]["binx"],variables2D[v]["xmin"],variables2D[v]["xmax"], 
                                     variables2D[v]["biny"],variables2D[v]["ymin"],variables2D[v]["ymax"])
                proc.sv2d[s][v].Sumw2()


    #SOLUTION 1
        
        threads.append((proc, selections, variables, variables2D, name, nev))
    pool = mp.Pool(mp.cpu_count())
    histos_list = pool.map(runMT_pool,threads) 


    for label in groups:
        toadd=[]
        for p in groups[label]:
            for h in histos_list:
                if p.name==h.name:
                    toadd.append(h)
        groups[label]=toadd

#_____________________________________________________________________________________________________
def runAnalysis(listOfProcesses, selections, variables, variables2D, nevents):
    print ''
    print 'Start looping on process trees:'
    print ''
        
    for proc in listOfProcesses:
        print '---------------------------'
        print proc.name
        print '---------------------------'
        print ''
        proc.run(selections, variables, variables2D, nevents=nevents)


#____________________________________________________________________________________________________
def saveHistos(processes, selections, variables, variables2D, output):

    print ''
    print 'Saving histograms in', output.GetName(), 'file ...'
    for proc in processes:
        for sel in selections:
            for var in variables:
                output.cd()
                proc.sv[sel][var].Write()
            for var in variables2D:
                output.cd()
                proc.sv2d[sel][var].Write()

    print 'DONE'
    output.Close()

#_____________________________________________________________________________________________________
def significance(s, es, b, eb):
    if s == 0 and b == 0:
        return 0.
    else:
        return s/sqrt(s + (s*es)**2 + b + (b*eb)**2)

#_____________________________________________________________________________________________________
def dMuOverMu(s, es, b, eb):
    if s == 0:
        return 1000.
    else:
        return 100*sqrt(s + (s*es)**2 + b + (b*eb)**2)/s

#_____________________________________________________________________________________________________
def printYieldsFromHistos(processes, selections, variables, uncertainties, intLumi, hfile):

    print ''    
    nsel = 0
    for sel in selections:
        intLumiab = intLumi/1e+06 
        print ''    
        print '========================================================================================================================'
        print '         selection:', sel
        print '========================================================================================================================'

        print ''    
        print '{:>20} {:>12} ({:>4} {:>3}) {:>20} {:>12}'.format('process', 'yield', intLumiab, 'ab-1', 'stat. error', 'raw')
        print '    -------------------------------------------------------------------------------------'

        v = variables.keys()[0]
        selstr = 'sel{}'.format(int(nsel))
        nsel += 1
        
        nproc = 0
        b = 0
        eb = 0
        for p in processes:
            hname = '{}_{}_{}'.format(p, selstr, v)
            h = hfile.Get(hname)
            err = ROOT.Double()
            yld = h.IntegralAndError(0, h.GetNbinsX()+1, err)
            raw = h.GetEntries()

            yld *= intLumi
            err *= intLumi

            if nproc == 0:
                s = yld
                es = err
            else: 
                b += yld
                eb += (err**2)
                
            print '{:>20} {:>20} {:>20} {:>20}'.format(p, round(yld,1), round(err,1),int(raw))
            nproc += 1
        print '    -------------------------------------------------------------------------------------'
        print '{:>20} {:>20} {:>20}'.format('signal', round(s,3), round(sqrt(es),3))
        print '{:>20} {:>20} {:>20}'.format('background', round(b,3), round(sqrt(eb),3))

        print ''    
        print ''    

        # calculate significance and delta_mu/mu (uncertainty on the signal strength)
        print '{:>24} {:>15} {:>23} {:>22}'.format('(sig_s, sig_b) (%)', 'S/B', 'significance', 'dmu/mu (%)')
        print '    --------------------------------------------------------------------------------------------------'
        for unc in uncertainties:
            sign = significance(s, unc[0], b, unc[1])
            rel_unc = dMuOverMu(s, unc[0], b, unc[1])
            if b > 0:
                s_over_b = s/b
            else:
                s_over_b = 999
            print '{:>11} {:>7} {:>21} {:>20} {:>20}'.format(round(unc[0]*100.,1), round(unc[1]*100.,1), round(s_over_b,2), round(sign,2), round(rel_unc,2))

#_____________________________________________________________________________________________________
def printYieldsFromHistosAsLatexTable(processes, selections, variables, uncertainties, intLumi, hfile):

    print ''    
    nsel = 0
    for sel in selections:
        intLumiab = intLumi/1e+06 
        print ''    
        print '===================================================================================='
        print '         selection:', sel
        print '===================================================================================='

        print r'\begin{tabular} {cccc}'    
        print r'{:>20} & {:>12} ({:>4} {:>3}) & {:>20} & {:>12} \\'.format('process', 'yield', intLumiab, 'ab$^-1$', 'stat. error', 'raw')
        print '\hline'

        v = variables.keys()[0]
        selstr = 'sel{}'.format(int(nsel))
        nsel += 1
        
        nproc = 0
        b = 0
        eb = 0
        for p in processes:
            hname = '{}_{}_{}'.format(p, selstr, v)
            h = hfile.Get(hname)
            err = ROOT.Double()
            yld = h.IntegralAndError(0, h.GetNbinsX()+1, err)
            raw = h.GetEntries()

            yld *= intLumi
            err *= intLumi

            if nproc == 0:
                s = yld
                es = err
            else: 
                b += yld
                eb += (err**2)
                
            print r'{:>20} & {:>20} & {:>20} & {:>20} \\'.format(p.replace("_", r"\_"), round(yld,1), round(err,1),int(raw))
            nproc += 1
        print r'\hline'
        print r'{:>20} & {:>20} & {:>20}& \\'.format('signal', round(s,3), round(sqrt(es),3))
        print r'{:>20} & {:>20} & {:>20}& \\'.format('background', round(b,3), round(sqrt(eb),3))

        print r'\end{tabular}'    
        print ''    

        # calculate significance and delta_mu/mu (uncertainty on the signal strength)
        print '{:>24} {:>20} {:>20}'.format('(sig_s, sig_b) (%)', 'significance', 'dmu/mu (%)')
        print '    ------------------------------------------------------------'
        for unc in uncertainties:
            sign = significance(s, unc[0], b, unc[1])
            rel_unc = dMuOverMu(s, unc[0], b, unc[1])
            print '{:>11} {:>7} {:>21} {:>20}'.format(round(unc[0]*100.,1), round(unc[1]*100.,1), round(sign,2), round(rel_unc,2))


#___________________________________________________________________________
def formatted(string):
    string = string.replace("{", "")
    string = string.replace("}", "")
    string = string.replace(" ", "")
    string = string.replace("=", "_")
    string = string.replace("+", "_")
    string = string.replace(")", "_")
    string = string.replace("(", "_")
    string = string.replace("#", "_")

    string = string.replace("__", "_")
    string = string.replace("___", "_")
    string = string.replace("____", "_")
    string = string.replace("_____", "_")
    while string.startswith("_"):
       string = string[1:]
    while string.endswith("_"):
       string = string[:-1]

    finalstr = string
    return finalstr

#___________________________________________________________________________
def produce2DPlots(processes, selections, variables2D, colors, intLumi, pdir, lt, rt, logZ, hfile):

    print ''
    print 'Preparing 2D plots ...'

    gROOT.SetBatch(True)

    intLumiab = intLumi/1e+06 

    ff = "eps"

    logstr = ''
    if logZ:
       logstr = 'log'
    else:
       logstr = 'lin'

    nsel = 0
    for s in selections:
        selstr = 'sel{}'.format(int(nsel))
        nsel += 1
        for v in variables2D.keys() :
             i = 0

             for p in processes:
                 filename = '{}_{}_{}_{}'.format(p, v, selstr, logstr)
                 filename = formatted(filename)
                 hname = '{}_{}_{}'.format(p, selstr, v)
                 h = hfile.Get(hname)
                 hh = TH2D.Clone(h)
                 hh.Scale(intLumi)
                 draw2D(filename, lt, rt, ff, pdir, logZ, hh)
                 
    print 'DONE.'


#___________________________________________________________________________
def produceStackedPlots(processes, selections, variables, colors, intLumi, pdir, lt, rt, log, stacksig, hfile, ana_tex):
    
    print ''
    print 'Preparing stacked plots ...'

    gROOT.SetBatch(True)

    intLumiab = intLumi/1e+06 

    yl = "events"

    ff = "eps"

    logstr = ''
    if log:
       logstr = 'log'
    else:
       logstr = 'lin'
    
    stackstr = ''
    if stacksig:
       stackstr = 'stack'
    else:
       stackstr = 'nostack'

    hfile.cd()

    nsel = 0
    
    legsize = 0.04*float(len(processes))
    
    for s in selections:
        selstr = 'sel{}'.format(int(nsel))
        nsel += 1
        for v, dic in variables.iteritems() :
             histos = []
             i = 0

             filename = '{}_{}_{}_{}'.format(v, selstr, stackstr, logstr)

             leg = TLegend(0.58,0.86 - legsize,0.86,0.88)
             leg.SetFillColor(0)
             leg.SetFillStyle(0)
             leg.SetLineColor(0)
             leg.SetShadowColor(10)
             leg.SetTextSize(0.035)
             leg.SetTextFont(42)


             cols = []
             for p in processes:
                 hname = '{}_{}_{}'.format(p, selstr, v)
                 h = hfile.Get(hname)
                 hh = TH1D.Clone(h)
                 hh.Scale(intLumi)
                 
                 # rebin if needed
                 hh.Rebin(int(hh.GetNbinsX()/dic['bin']))

                 histos.append(hh)
                 cols.append(colors[p])
                 # fix names if needed
                 leg_name = p
                 if p.find('m_{Z}')>=0   : leg_name = p.replace('m_{Z}',  'm_{Z\'}'   )
                 if p.find('m_{RSG}')>=0 : leg_name = p.replace('m_{RSG}','m_{G_{RS}}')
                 if p.find('vv')>=0 : leg_name = p.replace('vv','VV (V=Z/W)')
                 if p.find('vj')>=0 : leg_name = p.replace('vj','Vj (V=Z/W)')
                 if p.find('tt')>=0 : leg_name = p.replace('tt','t#bar{t}')
                 if p.find('Drell-Yan')>=0 and ana_tex.find("e^")>=0:   leg_name = p.replace('Drell-Yan','pp #rightarrow Z/#gamma* #rightarrow e^{+}e^{-}')
                 if p.find('Drell-Yan')>=0 and ana_tex.find("mu^")>=0:  leg_name = p.replace('Drell-Yan','pp #rightarrow Z/#gamma* #rightarrow #mu^{+}#mu^{-}')
                 if p.find('Drell-Yan')>=0 and ana_tex.find("tau^")>=0: leg_name = p.replace('Drell-Yan','pp #rightarrow Z/#gamma* #rightarrow #tau^{+}#tau^{-}')
                 if i > 0: 
                     leg.AddEntry(hh,leg_name,"f")
                 else: 
                     leg.AddEntry(hh,leg_name,"l")
                 i+=1
             drawStack(filename, yl, leg, lt, rt, ff, pdir, log, stacksig, histos, cols, ana_tex)
    print 'DONE.'
#___________________________________________________________________________
def produceNormalizedPlots(processes, selections, variables, colors, intLumi, pdir, lt, rt, log, hfile):
    
    print ''
    print 'Preparing normalized plots ...'

    gROOT.SetBatch(True)

    intLumiab = intLumi/1e+06 

    yl = "Normalized Event Rate"

    ff = "eps"

    logstr = ''
    if log:
       logstr = 'log'
    else:
       logstr = 'lin'
    
    stackstr = ''

    hfile.cd()

    nsel = 0
    for s in selections:
        selstr = 'sel{}'.format(int(nsel))
        nsel += 1
        for v, dic in variables.iteritems() :
             histos = []
             i = 0

             filename = '{}_{}_{}'.format(v, selstr, logstr)
             
             leg = TLegend(0.60,0.65,0.90,0.88)
             leg.SetFillColor(0)
             leg.SetFillStyle(0)
             leg.SetLineColor(0)
             leg.SetShadowColor(10)
             leg.SetTextSize(0.035)
             leg.SetTextFont(42)


             cols = []
             for p in processes:
                 hname = '{}_{}_{}'.format(p, selstr, v)
                 h = hfile.Get(hname)
                 hh = TH1D.Clone(h)

                 # rebin if needed
                 hh.Rebin(int(hh.GetNbinsX()/dic['bin']))

                 if hh.Integral(0, hh.GetNbinsX()+1) > 0:
                     hh.Scale(1./hh.Integral(0, hh.GetNbinsX()+1))
                 histos.append(hh)
                 cols.append(colors[p])
                 leg.AddEntry(hh,p,"l")
                 i+=1
             drawNormalized(filename, yl, leg, lt, rt, ff, pdir, log, histos, cols)

    print 'DONE.'

#_____________________________________________________________________________________________________________
def drawStack(name, ylabel, legend, leftText, rightText, format, directory, logY, stacksig, histos, colors, ana_tex):

    canvas = ROOT.TCanvas(name, name, 600, 600) 
    canvas.SetLogy(logY)
    canvas.SetTicks(1,1)
    canvas.SetLeftMargin(0.14)
    canvas.SetRightMargin(0.08)
    
    # first retrieve maximum 
    sumhistos = histos[0].Clone()
    iterh = iter(histos)
    next(iterh)
    
    unit = 'GeV'
    if 'TeV' in str(histos[1].GetXaxis().GetTitle()):
        unit = 'TeV'
    
    if unit in str(histos[1].GetXaxis().GetTitle()):
        bwidth=sumhistos.GetBinWidth(1)
        if bwidth.is_integer():
            ylabel+=' / {} {}'.format(int(bwidth), unit)
        else:
            ylabel+=' / {:.1f} {}'.format(bwidth, unit)

    for h in iterh:
      sumhistos.Add(h)

    maxh = sumhistos.GetMaximum()
    minh = sumhistos.GetMinimum()

    if logY: 
       canvas.SetLogy(1)

    # define stacked histo
    hStack = ROOT.THStack("hstack","")

    # first plot backgrounds
         
    histos[1].SetLineWidth(0)
    histos[1].SetFillColor(colors[1])
    
    hStack.Add(histos[1])
    
    # now loop over other background (skipping first)
    iterh = iter(histos)
    next(iterh)
    next(iterh)
    
    k = 2
    for h in iterh:
       h.SetLineWidth(0)
       h.SetLineColor(ROOT.kBlack)
       h.SetFillColor(colors[k])
       hStack.Add(h)
       k += 1
    
    
    # finally add signal on top
    histos[0].SetLineWidth(3)
    histos[0].SetLineColor(colors[0])
    
    if stacksig:
        hStack.Add(histos[0])

    hStack.Draw("hist")

    # fix names if needed
    xlabel = histos[1].GetXaxis().GetTitle()
    if xlabel.find('m_{RSG}')>=0 : xlabel = xlabel.replace('m_{RSG}','m_{G_{RS}}')
    ## remove/adapt X title content (should be done in config)
    fix_str=" (pf04)"
    if xlabel.find(fix_str)>=0 : xlabel = xlabel.replace(fix_str,'')
    fix_str=" (pf08)"
    if xlabel.find(fix_str)>=0 : xlabel = xlabel.replace(fix_str,'')
    fix_str=" (pf08 metcor)"
    if xlabel.find(fix_str)>=0 : xlabel = xlabel.replace(fix_str,'')
    if ana_tex.find("Q*")>=0 :
      fix_str="Z'"
      if xlabel.find(fix_str)>=0 : xlabel = xlabel.replace(fix_str,'Q*')

    #hStack.GetXaxis().SetTitleFont(font)
    #hStack.GetXaxis().SetLabelFont(font)
    hStack.GetXaxis().SetTitle(xlabel)
    hStack.GetYaxis().SetTitle(ylabel)
    #hStack.GetYaxis().SetTitleFont(font)
    #hStack.GetYaxis().SetLabelFont(font)
    '''hStack.GetXaxis().SetTitleOffset(1.5)
    hStack.GetYaxis().SetTitleOffset(1.6)
    hStack.GetXaxis().SetLabelOffset(0.02)
    hStack.GetYaxis().SetLabelOffset(0.02)
    hStack.GetXaxis().SetTitleSize(0.06)
    hStack.GetYaxis().SetTitleSize(0.06)
    hStack.GetXaxis().SetLabelSize(0.06)
    hStack.GetYaxis().SetLabelSize(0.06)
    hStack.GetXaxis().SetNdivisions(505);
    hStack.GetYaxis().SetNdivisions(505);
    hStack.SetTitle("") '''

    hStack.GetYaxis().SetTitleOffset(1.95)
    hStack.GetXaxis().SetTitleOffset(1.40)
    
    #hStack.SetMaximum(1.5*maxh) 

    lowY=0.
    if logY:
        # old
        #highY=100000*maxh
        #lowY=0.000001*maxh
        # automatic
        highY=200.*maxh/ROOT.gPad.GetUymax()
        #
        threshold=0.5
        bin_width=hStack.GetXaxis().GetBinWidth(1)
        lowY=threshold*bin_width
        if ana_tex.find("Q*")>=0 : lowY=10.
        if ana_tex.find("tau^")>=0 :
          lowY=1.
          highY=220.*maxh/ROOT.gPad.GetUymax()
        if xlabel.find("Flow")>=0 : 
          lowY=100.
          highY=600.*maxh/ROOT.gPad.GetUymax()
        if xlabel.find("#tau_{")>=0:
          lowY=1000.
          highY=500.*maxh/ROOT.gPad.GetUymax()
        #
        hStack.SetMaximum(highY)
        hStack.SetMinimum(lowY)
    else:
        hStack.SetMaximum(2.0*maxh)
        hStack.SetMinimum(0.)


    escape_scale_Xaxis=False
    if xlabel.find("#tau_{")>=0: escape_scale_Xaxis=True
    #
    hStacklast = hStack.GetStack().Last()
    lowX_is0=True
    lowX=hStacklast.GetBinCenter(1)-(hStacklast.GetBinWidth(1)/2.)
    highX_ismax=False
    highX=hStacklast.GetBinCenter(hStacklast.GetNbinsX())+(hStacklast.GetBinWidth(1)/2.)
    #
    if escape_scale_Xaxis==False:
      for i_bin in xrange( 1, hStacklast.GetNbinsX()+1 ):
         bkg_val=hStacklast.GetBinContent(i_bin)
         sig_val=histos[0].GetBinContent(i_bin)
         if bkg_val/maxh>0.1 and i_bin<15 and lowX_is0==True :
           lowX_is0=False
           lowX=hStacklast.GetBinCenter(i_bin)-(hStacklast.GetBinWidth(i_bin)/2.)
           if ana_tex.find("e^")>=0 or ana_tex.find("mu^")>=0 : lowX+=1
         #
         val_to_compare=bkg_val
         if sig_val>bkg_val : val_to_compare=sig_val
         if val_to_compare<lowY and i_bin>15 and highX_ismax==False: 
           highX_ismax=True
           highX=hStacklast.GetBinCenter(i_bin)+(hStacklast.GetBinWidth(i_bin)/2.)
           highX*=1.1
    # protections
    if lowX<hStacklast.GetBinCenter(1)-(hStacklast.GetBinWidth(1)/2.) :
      lowX=hStacklast.GetBinCenter(1)-(hStacklast.GetBinWidth(1)/2.)
    if highX>hStacklast.GetBinCenter(hStacklast.GetNbinsX())+(hStacklast.GetBinWidth(1)/2.) :
      highX=hStacklast.GetBinCenter(hStacklast.GetNbinsX())+(hStacklast.GetBinWidth(1)/2.)
    if lowX>=highX :
      lowX=hStacklast.GetBinCenter(1)-(hStacklast.GetBinWidth(1)/2.)
      highX=hStacklast.GetBinCenter(hStacklast.GetNbinsX())+(hStacklast.GetBinWidth(1)/2.)
    hStack.GetXaxis().SetLimits(int(lowX),int(highX))

    if not stacksig:
        histos[0].Draw("same hist")
   
    #legend.SetTextFont(font) 
    legend.Draw() 
    
    Text = ROOT.TLatex()
    
    Text.SetNDC() 
    Text.SetTextAlign(31);
    Text.SetTextSize(0.04) 

    text = '#it{' + leftText +'}'
    
    Text.DrawLatex(0.90, 0.92, text) 

    rightText = re.split(",", rightText)
    text = '#bf{#it{' + rightText[0] +'}}'
    
    Text.SetTextAlign(12);
    Text.SetNDC(ROOT.kTRUE) 
    Text.SetTextSize(0.04) 
    Text.DrawLatex(0.18, 0.83, text)

    rightText[1]=rightText[1].replace("   ","")    
    text = '#bf{#it{' + rightText[1] +'}}'
    Text.SetTextSize(0.035) 
    Text.DrawLatex(0.18, 0.78, text)
    #Text.DrawLatex(0.18, 0.78, rightText[1])

    text = '#bf{#it{' + ana_tex +'}}'
    Text.SetTextSize(0.04)
    Text.DrawLatex(0.18, 0.73, text)

    canvas.RedrawAxis()
    #canvas.Update()
    canvas.GetFrame().SetBorderSize( 12 )
    canvas.Modified()
    canvas.Update()

    printCanvas(canvas, name, format, directory) 

#_____________________________________________________________________________________________________________
def drawNormalized(name, ylabel, legend, leftText, rightText, format, directory, logY, histos, colors):

    canvas = ROOT.TCanvas(name, name, 600, 600) 
    canvas.SetLogy(logY)
    canvas.SetTicks(1,1)
    canvas.SetLeftMargin(0.14)
    canvas.SetRightMargin(0.08)
    ROOT.gStyle.SetOptStat(0000000)    
    
    maxh = -999.
    i = 0
    imax = -999
    for h in histos:
        if h.GetMaximum() > maxh:
            maxh = h.GetMaximum()
            imax = i
        i += 1

    if logY:
       canvas.SetLogy(1)

    if maxh > 0:
        h = histos[imax]

        h.SetLineWidth(4)
        h.SetLineColor(colors[imax])

        h.GetYaxis().SetTitleOffset(1.90)
        h.GetXaxis().SetTitleOffset(1.40)
        h.GetXaxis().SetTitle(histos[imax].GetXaxis().GetTitle())
        h.GetYaxis().SetTitle(ylabel)

        '''h.GetXaxis().SetTitleFont(font)
        h.GetXaxis().SetLabelFont(font)
        h.GetYaxis().SetTitleFont(font)
        h.GetYaxis().SetLabelFont(font)
        h.GetXaxis().SetTitleOffset(1.5)
        h.GetYaxis().SetTitleOffset(1.6)
        h.GetXaxis().SetLabelOffset(0.02)
        h.GetYaxis().SetLabelOffset(0.02)
        h.GetXaxis().SetTitleSize(0.06)
        h.GetYaxis().SetTitleSize(0.06)
        h.GetXaxis().SetLabelSize(0.06)
        h.GetYaxis().SetLabelSize(0.06)
        h.GetXaxis().SetNdivisions(505)
        h.GetYaxis().SetNdivisions(505)'''
        h.SetTitle("") 
        h.Draw("hist") 

        if logY:
            h.SetMaximum(100*maxh)
            #h.SetMinimum(0.1*maxh)
        else:
            h.SetMaximum(2*maxh)
            h.SetMinimum(0.)

        i = 0
        for h in histos:
           
           if i == imax: 
               i += 1
               continue
               
           h.SetLineWidth(4)
           h.SetLineColor(colors[i])
           h.Draw('same hist')
           i += 1

        #legend.SetTextFont(font) 
        legend.Draw() 

        Text = ROOT.TLatex()

        Text.SetNDC() 
        Text.SetTextAlign(31)
        Text.SetTextSize(0.04)

        text = '#it{' + leftText +'}'

        Text.DrawLatex(0.90, 0.92, text) 

        name = name + '_norm'
        printCanvas(canvas, name, format, directory) 


#_____________________________________________________________________________________________________________
def draw2D(name, leftText, rightText, format, directory, logZ, histo):

    canvas = ROOT.TCanvas(name, name, 600, 600) 
    canvas.SetLogz(logZ)
    canvas.SetTicks(1,1)
    canvas.SetLeftMargin(0.14)
    canvas.SetRightMargin(0.14)
    ROOT.gStyle.SetOptStat(0000000)    

    histo.SetContour(999)

    histo.Draw('COLZ')

    histo.SetTitle("") 
    histo.GetYaxis().SetTitleOffset(1.90)
    histo.GetXaxis().SetTitleOffset(1.40)

    '''Tleft = ROOT.TLatex(0.23, 0.92, leftText) 
    Tleft.SetNDC(ROOT.kTRUE) 
    Tleft.SetTextAlign(11);
    Tleft.SetTextSize(0.035) 
    Tleft.SetTextFont(132) 
    
    Tright = ROOT.TText(0.90, 0.92, rightText) ;
    Tright.SetTextAlign(31);
    Tright.SetNDC(ROOT.kTRUE) 
    Tright.SetTextSize(0.035) 
    Tright.SetTextFont(132) 
    '''
    Text = ROOT.TLatex()    
    Text.SetNDC() 
    Text.SetTextAlign(31);
    Text.SetTextSize(0.04) 

    text = '#it{' + leftText +'}'
    
    Text.DrawLatex(0.90, 0.92, text) 

    rightText = re.split(",", rightText)
    text = '#color[1]{#bf{#it{' + rightText[0] +'}}}'
    
    Text.SetTextAlign(22);
    Text.SetNDC(ROOT.kTRUE) 
    Text.SetTextSize(0.04) 
    Text.DrawLatex(0.26, 0.86, text)
    
    text = '#color[1]{#bf{#it{' + rightText[1] +'}}}'
    Text.SetTextSize(0.035) 
    Text.DrawLatex(0.26, 0.81, text)
    #Text.DrawLatex(0.12, 0.78, rightText[1])
    
    
    canvas.RedrawAxis()
    #canvas.Update()
    canvas.GetFrame().SetBorderSize( 12 )
    canvas.Modified()
    canvas.Update()




    #Tleft.Draw('same') 
    #Tright.Draw('same') 
    printCanvas(canvas, name, format, directory) 



#____________________________________________________
def printCanvas(canvas, name, format, directory):

    if format != "":
        if not os.path.exists(directory) :
                os.system("mkdir "+directory)
        outFile = os.path.join(directory, name) + "." + format
        canvas.Print(outFile)
