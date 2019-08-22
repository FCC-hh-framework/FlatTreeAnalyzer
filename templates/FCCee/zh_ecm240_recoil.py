import ROOT
import collections

ana_tex = "e^{+}e^{-} #rightarrow ZH #rightarrow #mu^{+}#mu^{-} + X"

### variable list
variables = {
    "ptz":{"name":"zed_pt","title":"p_{T}^{Z} [GeV]","bin":150,"xmin":0,"xmax":300},
    "mz":{"name":"zed_m","title":"m_{Z} [GeV]","bin":125,"xmin":0,"xmax":250},
    "ptmu_1":{"name":"mu1_pt","title":"p_{T}^{#mu, max} [GeV]","bin":150,"xmin":0,"xmax":150},
    "ptmu_2":{"name":"mu2_pt","title":"p_{T}^{#mu, min} [GeV]","bin":150,"xmin":0,"xmax":150},

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

uncertainties = []
uncertainties.append([0., 0.])
uncertainties.append([0.02, 0.0])
uncertainties.append([0.02, 0.02])
uncertainties.append([0.02, 0.10])

# the first time needs to be set to True
runFull = True

# base pre-selections
selbase = 'recoil_m>10.'
selopt  = 'zed_pt<65. && zed_m>70. && zed_m<100. && mu1_pt<75.&& mu2_pt<50. && met_pt<50.'
# add mass-dependent list of event selections here if needed...

selections = collections.OrderedDict()
selections['ZH'] = []
selections['ZH'].append(selbase)
selections['ZH'].append(selopt)

