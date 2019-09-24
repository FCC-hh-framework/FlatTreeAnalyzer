import ROOT, os, sys
from ROOT import *

####################
# make trees list
####################
if len(sys.argv)>1: path = sys.argv[1]
else : path = "./" 


#variable="Jet1_trk02_SD_Cor_m"
variable="mzp"
variable="mt"
variable="Jet1_pf04_eta"
#variable="h_mjj_l2"
#variable="Mj1j2_pf08_MetCorr"

lumi=3e+7
the_file = ""
Trees = []
for subdir, dirs, files in os.walk(path) :
  for File in files :
    if File.find("histos.root") >= 0 :
      the_file = os.path.join(subdir, File)
      Trees.append(the_file)

####################
# check the trees
####################
out_file = open("yield.txt","w")
for tree in Trees :
  print "check tree "+str(tree)
  rf = TFile(tree)
  sample_list=[]
  cut_list=[]
  # get histograms name
  for tkey in rf.GetListOfKeys():
    key = tkey.GetName()
    if key.find(variable)>=0 : 
      # form samples list
      print key
      str_hist=key.replace("_sel0_"+variable,"")
      if str_hist.find("_sel")<0: sample_list.append(str_hist)
      # form cuts list
      the_sample=sample_list[0]
      if key.find(the_sample+"_sel")>=0 :
        str_cut=key.replace(the_sample+"_","")
        str_cut=str_cut.replace("_"+variable,"")
        cut_list.append(str_cut)
  # get histogram numbers and fill table
  for cut in cut_list :
    out_file.write("_________________________________________ "+cut+" ______________________________________________\n")
    out_file.write("=============================================================================================\n")
    space=20
    word1="process"; word2="yield (30.0 ab-1)"; word3="stat. error"; word4="raw"
    out_file.write(word1.rjust(space)+word2.rjust(space)+word3.rjust(space)+word4.rjust(space)+"\n")
    out_file.write("-------------------------------------------------------------------------------------\n")
    for sample in sample_list :
      hist_name=sample+"_"+cut+"_"+variable
      hist = rf.Get(hist_name)
      error=ROOT.Double(0)
      integral = hist.IntegralAndError(-1, hist.GetNbinsX(), error)
      entries  = hist.GetEntries()
      # use proper lumi
      integral*=lumi
      error*=lumi
      word1=sample; word2=str(round(integral,1)); word3=str(round(error,1)); word4=str(int(entries))
      out_file.write(word1.rjust(space)+word2.rjust(space)+word3.rjust(space)+word4.rjust(space)+"\n")
    out_file.write("=============================================================================================\n\n\n")
  out_file.write("#############################################################################################\n\n")

out_file.close()

