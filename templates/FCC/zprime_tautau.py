import ROOT
import collections

ana_tex = "Z\'_{SSM} #rightarrow #tau^{+}#tau^{-}"

### variable list
variables = {
#    "met":{"name":"met_pt","title":"MET [GeV]","bin":50,"xmin":0,"xmax":1000},
#    "mzp":{"name":"Mj1j2_pf04","title":"m_{Z'} [TeV]","bin":150,"xmin":0,"xmax":30, "divide":1000},
#    "mzp_metcor":{"name":"Mj1j2_pf04_MetCorr","title":"m_{Z'} [TeV]","bin":150,"xmin":0,"xmax":30, "divide":1000},
#    "mzp_metcor2":{"name":"Mj1j2_pf04_MetCorr2","title":"m_{Z'} [TeV]","bin":150,"xmin":0,"xmax":30, "divide":1000},
    "mt":{"name":"mt","title":"m_{Z'}^{trans} [TeV]","bin":50,"xmin":0,"xmax":20, "divide":1000},
#    "dr":{"name":"dr","title":"#DeltaR(#tau_{1},#tau_{2})","bin":50,"xmin":0,"xmax":5},
#    "dphi":{"name":"dphi","title":"#DeltaPhi(#tau_{1},#tau_{2})","bin":50,"xmin":-4,"xmax":4},
#    "dphi_met":{"name":"dphi_met","title":"#DeltaPhi(Z',met)","bin":50,"xmin":-4,"xmax":4},
#    "pttau_1":{"name":"Jet1_pf04_pt","title":"p_{T}^{#tau, max} [TeV]","bin":50,"xmin":0.5,"xmax":10, "divide":1000},
#    "pttau_2":{"name":"Jet2_pf04_pt","title":"p_{T}^{#tau, min} [TeV]","bin":50,"xmin":0.5,"xmax":10, "divide":1000},
#    "etatau_1":{"name":"Jet1_pf04_eta","title":"#eta^{#tau, max}","bin":35,"xmin":-3.5,"xmax":3.5},
#    "etatau_2":{"name":"Jet2_pf04_eta","title":"#eta^{#tau, min}","bin":35,"xmin":-3.5,"xmax":3.5},
}

variables2D = {}


colors = {}
colors['m_{Z} = 2 TeV'] = ROOT.kRed
colors['m_{Z} = 4 TeV'] = ROOT.kRed
colors['m_{Z} = 5 TeV'] = ROOT.kRed
colors['m_{Z} = 6 TeV'] = ROOT.kRed
colors['m_{Z} = 8 TeV'] = ROOT.kRed
colors['m_{Z} = 10 TeV'] = ROOT.kRed
colors['m_{Z} = 12 TeV'] = ROOT.kRed
colors['m_{Z} = 14 TeV'] = ROOT.kRed
colors['m_{Z} = 15 TeV'] = ROOT.kRed
colors['m_{Z} = 16 TeV'] = ROOT.kRed
colors['m_{Z} = 18 TeV'] = ROOT.kRed
colors['m_{Z} = 20 TeV'] = ROOT.kRed
colors['m_{Z} = 25 TeV'] = ROOT.kRed
colors['m_{Z} = 30 TeV'] = ROOT.kRed
colors['m_{Z} = 35 TeV'] = ROOT.kRed
colors['m_{Z} = 40 TeV'] = ROOT.kRed
colors['Drell-Yan'] = ROOT.kGreen+2
colors['QCD'] = ROOT.kBlue+1

signal_groups = collections.OrderedDict()
signal_groups['m_{Z} = 2 TeV'] = ['p8_pp_ZprimeSSM_2TeV_ll']
signal_groups['m_{Z} = 4 TeV'] = ['p8_pp_ZprimeSSM_4TeV_ll']
signal_groups['m_{Z} = 5 TeV'] = ['p8_pp_ZprimeSSM_5TeV_ll']
signal_groups['m_{Z} = 6 TeV'] = ['p8_pp_ZprimeSSM_6TeV_ll']
signal_groups['m_{Z} = 8 TeV'] = ['p8_pp_ZprimeSSM_8TeV_ll']
signal_groups['m_{Z} = 10 TeV'] = ['p8_pp_ZprimeSSM_10TeV_ll']
signal_groups['m_{Z} = 12 TeV'] = ['p8_pp_ZprimeSSM_12TeV_ll']
signal_groups['m_{Z} = 14 TeV'] = ['p8_pp_ZprimeSSM_14TeV_ll']
signal_groups['m_{Z} = 15 TeV'] = ['p8_pp_ZprimeSSM_15TeV_ll']
signal_groups['m_{Z} = 16 TeV'] = ['p8_pp_ZprimeSSM_16TeV_ll']
signal_groups['m_{Z} = 18 TeV'] = ['p8_pp_ZprimeSSM_18TeV_ll']
signal_groups['m_{Z} = 20 TeV'] = ['p8_pp_ZprimeSSM_20TeV_ll']
signal_groups['m_{Z} = 25 TeV'] = ['p8_pp_ZprimeSSM_25TeV_ll']
signal_groups['m_{Z} = 30 TeV'] = ['p8_pp_ZprimeSSM_30TeV_ll']
signal_groups['m_{Z} = 35 TeV'] = ['p8_pp_ZprimeSSM_35TeV_ll']
signal_groups['m_{Z} = 40 TeV'] = ['p8_pp_ZprimeSSM_40TeV_ll']

background_groups = collections.OrderedDict()
background_groups['Drell-Yan'] =  ['mgp8_pp_tautau_5f_HT_1000_2000','mgp8_pp_tautau_5f_HT_2000_5000','mgp8_pp_tautau_5f_HT_5000_10000','mgp8_pp_tautau_5f_HT_10000_27000','mgp8_pp_tautau_5f_HT_27000_100000']
['mgp8_pp_tautau_lo','mgp8_pp_tautau_lo_PT_1000_2500']
background_groups['QCD'] = ['mgp8_pp_jj_5f_HT_1000_2000','mgp8_pp_jj_5f_HT_2000_5000','mgp8_pp_jj_5f_HT_5000_10000','mgp8_pp_jj_5f_HT_10000_27000','mgp8_pp_jj_5f_HT_27000_100000']


# global parameters
intLumi = 3.0e+07
delphesVersion = '3.4.2'

uncertainties = []
uncertainties.append([0., 0.])
uncertainties.append([0.02, 0.0])
uncertainties.append([0.02, 0.02])
uncertainties.append([0.02, 0.10])

# the first time needs to be set to True
runFull = False

# base pre-selections
#selbase = 'Jet1_pf04_pt > 1000. && Jet2_pf04_pt > 1000. && ntau>1'

selbase = 'weight_2tagex**Jet1_pf04_pt > 500. && Jet2_pf04_pt > 500.'
seleta = ' && abs(Jet1_pf04_eta) < 2.5 && abs(Jet2_pf04_eta) < 2.5'
seldr = ' && abs(dphi)>2.0 && dr>2.5 && dr<4. '
selhighm = '&& met_pt>300.'
sellowm = '&& met_pt>400. && dr<3.8 && abs(dphi)>2.4'
selmtcut0p5TeV=' && mt > 500.'
selmtcut1TeV=' && mt > 1000.'
selmtcut2TeV=' && mt > 2000.'
sel4TeV =selbase+seleta+' && abs(dphi)>2.4 && dr>2.5 && dr<3.5 && met_pt>400.'
sel6TeV =selbase+seleta+' && abs(dphi)>2.4 && dr>2.5 && dr<3.5 && met_pt>400.'
sel10TeV=selbase+seleta+' && abs(dphi)>2.4 && dr>2.7 && dr<4.0 && met_pt>300.'
sel12TeV=selbase+seleta+' && abs(dphi)>2.6 && dr>2.7 && dr<4.0 && met_pt>300.'
sel16TeV=selbase+seleta+' && abs(dphi)>2.7 && dr>2.7 && dr<4.0 && met_pt>300.'
sel20TeV=selbase+seleta+' && abs(dphi)>2.8 && dr>3.0 && dr<4.0 && met_pt>300.'

# add mass-dependent list of event selections here if needed...

selections = collections.OrderedDict()

selections['m_{Z} = 10 TeV'] = []
selections['m_{Z} = 10 TeV'].append(sel10TeV)
selections['m_{Z} = 10 TeV'].append(selbase+seleta)
#selections['m_{Z} = 10 TeV'].append(selbase+seleta+seldr)
#selections['m_{Z} = 10 TeV'].append(selbase+seleta+seldr+selhighm)
#selections['m_{Z} = 10 TeV'].append(sel10TeV)

#selections['m_{Z} = 2 TeV'] = []
#selections['m_{Z} = 2 TeV'].append(selbase+seleta)
#selections['m_{Z} = 2 TeV'].append(selbase+seleta+seldr)
#selections['m_{Z} = 2 TeV'].append(sel4TeV)

#selections['m_{Z} = 4 TeV'] = []
#selections['m_{Z} = 4 TeV'].append(selbase+seleta)
#selections['m_{Z} = 4 TeV'].append(selbase+seleta+seldr)
#selections['m_{Z} = 4 TeV'].append(sel4TeV)

#selections['m_{Z} = 6 TeV'] = []
#selections['m_{Z} = 6 TeV'].append(selbase+seleta)
#selections['m_{Z} = 6 TeV'].append(selbase+seleta+seldr)
#selections['m_{Z} = 6 TeV'].append(sel6TeV)

#selections['m_{Z} = 8 TeV'] = []
#selections['m_{Z} = 8 TeV'].append(selbase+seleta)
#selections['m_{Z} = 8 TeV'].append(selbase+seleta+seldr)
#selections['m_{Z} = 8 TeV'].append(sel6TeV)

#selections['m_{Z} = 10 TeV'] = []
#selections['m_{Z} = 10 TeV'].append(selbase+seleta)
#selections['m_{Z} = 10 TeV'].append(selbase+seleta+seldr)
#selections['m_{Z} = 10 TeV'].append(selbase+seleta+seldr+selhighm)
#selections['m_{Z} = 10 TeV'].append(sel10TeV)

#selections['m_{Z} = 12 TeV'] = []
#selections['m_{Z} = 12 TeV'].append(selbase+seleta)
#selections['m_{Z} = 12 TeV'].append(selbase+seleta+seldr)
#selections['m_{Z} = 12 TeV'].append(selbase+seleta+seldr+selhighm)
#selections['m_{Z} = 12 TeV'].append(sel12TeV)

#selections['m_{Z} = 14 TeV'] = []
#selections['m_{Z} = 14 TeV'].append(selbase+seleta)
#selections['m_{Z} = 14 TeV'].append(selbase+seleta+seldr)
#selections['m_{Z} = 14 TeV'].append(selbase+seleta+seldr+selhighm)
#selections['m_{Z} = 14 TeV'].append(sel12TeV)

#selections['m_{Z} = 16 TeV'] = []
#selections['m_{Z} = 16 TeV'].append(selbase+seleta)
#selections['m_{Z} = 16 TeV'].append(selbase+seleta+seldr)
#selections['m_{Z} = 16 TeV'].append(selbase+seleta+seldr+selhighm)
#selections['m_{Z} = 16 TeV'].append(sel16TeV)

#selections['m_{Z} = 18 TeV'] = []
#selections['m_{Z} = 18 TeV'].append(selbase+seleta)
#selections['m_{Z} = 18 TeV'].append(selbase+seleta+seldr)
#selections['m_{Z} = 18 TeV'].append(selbase+seleta+seldr+selhighm)
#selections['m_{Z} = 18 TeV'].append(sel16TeV)

#selections['m_{Z} = 20 TeV'] = []
#selections['m_{Z} = 20 TeV'].append(selbase+seleta)
#selections['m_{Z} = 20 TeV'].append(selbase+seleta+seldr)
#selections['m_{Z} = 20 TeV'].append(selbase+seleta+seldr+selhighm)
#selections['m_{Z} = 20 TeV'].append(sel20TeV)

#selections['m_{Z} = 25 TeV'] = []
#selections['m_{Z} = 25 TeV'].append(selbase+seleta)
#selections['m_{Z} = 25 TeV'].append(selbase+seleta+seldr)
#selections['m_{Z} = 25 TeV'].append(selbase+seleta+seldr+selhighm)
#selections['m_{Z} = 25 TeV'].append(sel20TeV)

#selections['m_{Z} = 30 TeV'] = []
#selections['m_{Z} = 30 TeV'].append(selbase+seleta)
#selections['m_{Z} = 30 TeV'].append(selbase+seleta+seldr)
#selections['m_{Z} = 30 TeV'].append(selbase+seleta+seldr+selhighm)
#selections['m_{Z} = 30 TeV'].append(sel20TeV)


weights = collections.OrderedDict()
