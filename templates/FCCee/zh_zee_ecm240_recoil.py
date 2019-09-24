import ROOT
import collections

ana_tex = "e^{+}e^{-} #rightarrow ZH #rightarrow e^{+}e^{-} + X"

### variable list
variables = {
    "ptz":{"name":"zed_pt","title":"p_{T}^{Z} [GeV]","bin":150,"xmin":0,"xmax":300},
    "mz":{"name":"zed_m","title":"m_{Z} [GeV]","bin":125,"xmin":0,"xmax":250},
    "ptel_1":{"name":"el1_pt","title":"p_{T}^{el, max} [GeV]","bin":150,"xmin":0,"xmax":150},
    "ptel_2":{"name":"el2_pt","title":"p_{T}^{el, min} [GeV]","bin":150,"xmin":0,"xmax":150},

    "mrecoil":{"name":"recoil_m","title":"m_{Recoil} [GeV]","bin":100,"xmin":50,"xmax":150},
    "ptrecoil":{"name":"recoil_m","title":"p_{T}^{Recoil} [GeV]","bin":125,"xmin":0,"xmax":250},

    "met_pt":{"name":"met_pt","title":"met p_{T} [GeV]","bin":150,"xmin":0,"xmax":150},
    "met_sumet":{"name":"met_sumet","title":"met sum E_{T} [GeV]","bin":125,"xmin":0,"xmax":250},

}

variables2D = {}


colors = {}
colors['ZH'] = ROOT.kRed
colors['WW'] = ROOT.kBlue+1
colors['ZZ'] = ROOT.kGreen+2

signal_groups = collections.OrderedDict()
signal_groups['ZH'] = ['p8_ee_ZH_ecm240']

background_groups = collections.OrderedDict()
background_groups['WW'] = ['p8_ee_WW_ecm240']
background_groups['ZZ'] = ['p8_ee_ZZ_ecm240']

# global parameters
intLumi = 5.0e+06
delphesVersion = '3.4.2'
FCCee=True
Energy=240.0

uncertainties = []
uncertainties.append([0., 0.])
uncertainties.append([0.02, 0.0])
uncertainties.append([0.02, 0.02])
uncertainties.append([0.02, 0.10])

# the first time needs to be set to True
runFull = True

# base pre-selections
selbase = 'recoil_m>10.'
selopt  = 'zed_pt<65. && zed_m>70. && zed_m<100. && el1_pt<75.&& el2_pt<50. && met_pt<50.'
selbb   = 'nbjets==2'
seltautau   = 'ntaujets==2'
selWhadWhad   = 'nljets+ncjets==4'
selWhadWlep   = 'nljets+ncjets==2 && ((nele_recoil==1 &&  nmu==0) || (nele_recoil==0 &&  nmu==1) )'
selWlepWlep   = '(nele_recoil==2 &&  nmu==0) || (nele_recoil==0 &&  nmu==2) ||  (nele_recoil==1 &&  nmu==1)'
selWW  = selWhadWhad + '||' + selWhadWlep + '||' + selWlepWlep

# add list of event selections here if needed...

selections = collections.OrderedDict()
selections['ZH'] = []
selections['ZH'].append(selbase)
selections['ZH'].append(selopt)
selections['ZH'].append(selbb)
selections['ZH'].append(seltautau)
selections['ZH'].append(selWhadWhad)
selections['ZH'].append(selWhadWlep)
selections['ZH'].append(selWlepWlep)
selections['ZH'].append(selWW)
