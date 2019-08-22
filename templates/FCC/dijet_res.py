import ROOT
import collections

ana_tex = "Q* #rightarrow jj"

### variable list
variables = {

#        'Jet1_pf04_pt':{'name':'Jet1_pf04_pt','title':'Jet1 p_{T} [TeV]','bin':115,'xmin':2,'xmax':25, 'divide':1000},
#        'Jet1_pf04_eta':{'name':'Jet1_pf04_eta','title':'Jet1 #eta','bin':50,'xmin':-5.0,'xmax':5.0},
#
#        'Jet2_pf04_pt':{'name':'Jet2_pf04_pt','title':'Jet2 p_{T} [TeV]','bin':115,'xmin':2,'xmax':25, 'divide':1000},
#        'Jet2_pf04_eta':{'name':'Jet2_pf04_eta','title':'Jet2 #eta','bin':50,'xmin':-5.0,'xmax':5.0},
#
#        'Jet1_calo04_pt':{'name':'Jet1_calo04_pt','title':'Jet1 p_{T} [TeV]','bin':115,'xmin':2,'xmax':25, 'divide':1000},
#        'Jet1_calo04_eta':{'name':'Jet1_calo04_eta','title':'Jet1 #eta','bin':50,'xmin':-5.0,'xmax':5.0},
#
#        'Jet2_calo04_pt':{'name':'Jet2_calo04_pt','title':'Jet2 p_{T} [TeV]','bin':115,'xmin':2,'xmax':25, 'divide':1000},
#        'Jet2_calo04_eta':{'name':'Jet2_calo04_eta','title':'Jet2 #eta','bin':50,'xmin':-5.0,'xmax':5.0},
#
#        'rapiditySeparation_pf04':{'name':'rapiditySeparation_pf04','title':'Rapidity Separation','bin':50,'xmin':0.0,'xmax':5.0},
#        'pseudorapiditySeparation_pf04':{'name':'pseudorapiditySeparation_pf04','title':'pseudo Rapidity Separation','bin':50,'xmin':0.0,'xmax':10.0},
#
#        'transverseMomentumAsymmetry_pf_04':{'name':'transverseMomentumAsymmetry_pf04','title':'Transverse Momentum Asymmetry','bin':50,'xmin':0.0,'xmax':1.0},
#
        'Mj1j2_pf04' :{'name':'Mj1j2_pf04','title':'m_{Q*} [TeV] (pf04)','bin':40,'xmin':10.0,'xmax':50.0, 'divide':1000},
#        'Mj1j2_pf04_5p'  :{'name':'Mj1j2_pf04_5p','title':'m_{Q*} [TeV] (pf04)','bin':200,'xmin':10.0,'xmax':50.0, 'divide':1000},
#        'Mj1j2_pf04_10p' :{'name':'Mj1j2_pf04_10p','title':'m_{Q*} [TeV] (pf04)','bin':200,'xmin':10.0,'xmax':50.0, 'divide':1000},
#        'Mj1j2_pf04_15p' :{'name':'Mj1j2_pf04_15p','title':'m_{Q*} [TeV] (pf04)','bin':200,'xmin':10.0,'xmax':50.0, 'divide':1000},
#        'Mj1j2_pf04_20p' :{'name':'Mj1j2_pf04_20p','title':'m_{Q*} [TeV] (pf04)','bin':200,'xmin':10.0,'xmax':50.0, 'divide':1000},
#        'Mj1j2_calo04' :{'name':'Mj1j2_calo04','title':'m_{Q*} [TeV] (calo04)','bin':200,'xmin':10.0,'xmax':50.0, 'divide':1000},

        'Mj1j2_pf04_2t' :{'name':'Mj1j2_pf04_2t','title':'m_{Z\'} [TeV] (pf04)','bin':200,'xmin':10.0,'xmax':50.0, 'divide':1000},
        'Mj1j2_pf04_3t' :{'name':'Mj1j2_pf04_3t','title':'m_{Z\'} [TeV] (pf04)','bin':200,'xmin':10.0,'xmax':50.0, 'divide':1000},
        'Mj1j2_pf04_4t' :{'name':'Mj1j2_pf04_4t','title':'m_{Z\'} [TeV] (pf04)','bin':200,'xmin':10.0,'xmax':50.0, 'divide':1000},
        'Mj1j2_pf04_5t' :{'name':'Mj1j2_pf04_5t','title':'m_{Z\'} [TeV] (pf04)','bin':200,'xmin':10.0,'xmax':50.0, 'divide':1000},


}

variables2D = {}


colors = {}
colors['m_{Q*} = 10 TeV'] = ROOT.kRed
colors['m_{Q*} = 15 TeV'] = ROOT.kRed
colors['m_{Q*} = 20 TeV'] = ROOT.kRed
colors['m_{Q*} = 25 TeV'] = ROOT.kRed
colors['m_{Q*} = 30 TeV'] = ROOT.kRed
colors['m_{Q*} = 35 TeV'] = ROOT.kRed
colors['m_{Q*} = 40 TeV'] = ROOT.kRed
colors['m_{Q*} = 45 TeV'] = ROOT.kRed
colors['m_{Q*} = 50 TeV'] = ROOT.kRed
colors['QCD'] = ROOT.kGreen+2

signal_groups = collections.OrderedDict()

signal_groups['m_{Q*} = 15 TeV'] = ['p8_pp_ExcitedQ_15TeV_qq']
signal_groups['m_{Q*} = 20 TeV'] = ['p8_pp_ExcitedQ_20TeV_qq']
signal_groups['m_{Q*} = 25 TeV'] = ['p8_pp_ExcitedQ_25TeV_qq']
signal_groups['m_{Q*} = 30 TeV'] = ['p8_pp_ExcitedQ_30TeV_qq']
signal_groups['m_{Q*} = 35 TeV'] = ['p8_pp_ExcitedQ_35TeV_qq']
signal_groups['m_{Q*} = 40 TeV'] = ['p8_pp_ExcitedQ_40TeV_qq']
signal_groups['m_{Q*} = 45 TeV'] = ['p8_pp_ExcitedQ_45TeV_qq']
signal_groups['m_{Q*} = 50 TeV'] = ['p8_pp_ExcitedQ_50TeV_qq']

background_groups = collections.OrderedDict()

background_groups['QCD'] = [
'mgp8_pp_jj_5f_HT_2000_5000',
'mgp8_pp_jj_5f_HT_5000_10000',
'mgp8_pp_jj_5f_HT_10000_27000',
'mgp8_pp_jj_5f_HT_27000_100000']



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

# base pre-#selections
selbase = 'Jet1_calo04_pt > 3000. && Jet2_calo04_pt > 3000.'
sel1 = 'Jet1_calo04_pt > 3000. && Jet2_calo04_pt > 3000. && rapiditySeparation_pf04 < 1.5'

selections = collections.OrderedDict()
#selections['m_{Q*} = 15 TeV'] = []
#selections['m_{Q*} = 15 TeV'].append(selbase)
#selections['m_{Q*} = 15 TeV'].append(sel1)
#
#selections['m_{Q*} = 20 TeV'] = []
#selections['m_{Q*} = 20 TeV'].append(selbase)
#selections['m_{Q*} = 20 TeV'].append(sel1)
#
#selections['m_{Q*} = 25 TeV'] = []
#selections['m_{Q*} = 25 TeV'].append(selbase)
#selections['m_{Q*} = 25 TeV'].append(sel1)
#
#selections['m_{Q*} = 30 TeV'] = []
#selections['m_{Q*} = 30 TeV'].append(selbase)
#selections['m_{Q*} = 30 TeV'].append(sel1)
#
#selections['m_{Q*} = 35 TeV'] = []
#selections['m_{Q*} = 35 TeV'].append(selbase)
#selections['m_{Q*} = 35 TeV'].append(sel1)
#
selections['m_{Q*} = 40 TeV'] = []
selections['m_{Q*} = 40 TeV'].append(selbase)
selections['m_{Q*} = 40 TeV'].append(sel1)
#
#selections['m_{Q*} = 45 TeV'] = []
#selections['m_{Q*} = 45 TeV'].append(selbase)
#selections['m_{Q*} = 45 TeV'].append(sel1)
#
#selections['m_{Q*} = 50 TeV'] = []
#selections['m_{Q*} = 50 TeV'].append(selbase)
#selections['m_{Q*} = 50 TeV'].append(sel1)






