import os
from analysis_tools.utils import import_root

from PhysicsTools.NanoAODTools.postprocessing.modules.common.puWeightProducer import (
    puWeight_2016, puWeight_2017, puWeight_2018
)

ROOT = import_root()

def puWeight(**kwargs):
    isMC = kwargs.pop("isMC")
    year = int(kwargs.pop("year"))

    if not isMC:
        return lambda: DummyModule(**kwargs)
    else:
        if year == 2016:
            return puWeight_2016
        elif year == 2017:
            return puWeight_2017
        elif year == 2018:
            return puWeight_2018


class puWeightRDFProducer():
    def __init__(self, myfile, targetfile, myhist="pileup", targethist="pileup", name="puWeight",
            norm=True, verbose=False, nvtx_var="Pileup_nTrueInt", doSysVar=True, *args, **kwargs):
        self.name = name
        self.nvtx_var = nvtx_var
        self.doSysVar = doSysVar

        if "/libBaseModules.so" not in ROOT.gSystem.GetLibraries():
            ROOT.gSystem.Load("libBaseModules.so")
        base = "{}/{}/src/Base/Modules".format(
            os.getenv("CMT_CMSSW_BASE"), os.getenv("CMT_CMSSW_VERSION"))
        ROOT.gROOT.ProcessLine(".L {}/interface/puWeightinterface.h".format(base))
        
        ROOT.gInterpreter.Declare(
            'auto worker = puWeightinterface("%s", "%s", "%s", "%s", %s, %s);' % (
                myfile, targetfile, myhist, targethist, ("true" if norm else "false"),
                ("true" if verbose else "false"))
        )

        if self.doSysVar:
            ROOT.gInterpreter.Declare(
                'auto worker_plus = puWeightinterface("%s", "%s", "%s", "%s", %s, %s);' % (
                myfile, targetfile, myhist, targethist + "_plus", ("true" if norm else "false"),
                ("true" if verbose else "false"))
            )
            ROOT.gInterpreter.Declare(
                'auto worker_minus = puWeightinterface("%s", "%s", "%s", "%s", %s, %s);' % (
                myfile, targetfile, myhist, targethist + "_minus", ("true" if norm else "false"),
                ("true" if verbose else "false"))
            )

    def run(self, df):
        df = df.Define(self.name, "worker.get_weight(%s)" % self.nvtx_var)
        var_to_return = [self.name]
        
        if self.doSysVar:
            df = df.Define(self.name + "Up", "worker_plus.get_weight(%s)" % self.nvtx_var)
            df = df.Define(self.name + "Down", "worker_minus.get_weight(%s)" % self.nvtx_var)
            var_to_return += [self.name + "Up", self.name + "Down"]

        return df, var_to_return


class puWeightDummyRDFProducer():
    def run(self, df):
        return df, []


# define modules using the syntax 'name = lambda : constructor' to avoid having them loaded when not needed

pufile_mc2016 = "%s/src/PhysicsTools/NanoAODTools/python/postprocessing/data/pileup/pileup_profile_Summer16.root" % os.environ[
    'CMSSW_BASE']
pufile_data2016 = "%s/src/PhysicsTools/NanoAODTools/python/postprocessing/data/pileup/PileupData_GoldenJSON_Full2016.root" % os.environ[
    'CMSSW_BASE']
puWeight_2016RDF = lambda: puWeightRDFProducer(
    pufile_mc2016, pufile_data2016, "pu_mc", "pileup", verbose=False, doSysVar=True)
puAutoWeight_2016 = lambda: puWeightRDFProducer(
    "auto", pufile_data2016, "pu_mc", "pileup", verbose=False)

pufile_data2017 = "%s/src/PhysicsTools/NanoAODTools/python/postprocessing/data/pileup/PileupHistogram-goldenJSON-13tev-2017-99bins_withVar.root" % os.environ[
    'CMSSW_BASE']
pufile_mc2017 = "%s/src/PhysicsTools/NanoAODTools/python/postprocessing/data/pileup/mcPileup2017.root" % os.environ[
    'CMSSW_BASE']
puWeight_2017RDF = lambda: puWeightRDFProducer(
    pufile_mc2017, pufile_data2017, "pu_mc", "pileup", verbose=False, doSysVar=True)
puAutoWeight_2017 = lambda: puWeightRDFProducer(
    "auto", pufile_data2017, "pu_mc", "pileup", verbose=False)

pufile_data2018 = "%s/src/PhysicsTools/NanoAODTools/python/postprocessing/data/pileup/PileupHistogram-goldenJSON-13tev-2018-100bins_withVar.root" % os.environ[
    'CMSSW_BASE']
pufile_mc2018 = "%s/src/PhysicsTools/NanoAODTools/python/postprocessing/data/pileup/mcPileup2018.root" % os.environ[
    'CMSSW_BASE']
puWeight_2018RDF = lambda: puWeightRDFProducer(
    pufile_mc2018, pufile_data2018, "pu_mc", "pileup", verbose=False, doSysVar=True)
puAutoWeight_2018 = lambda: puWeightRDFProducer(
    "auto", pufile_data2018, "pu_mc", "pileup", verbose=False)

# Ultra legacy

# 2016
pufile_dataUL2016 = "%s/src/PhysicsTools/NanoAODTools/python/postprocessing/data/pileup/PileupHistogram-UL2016-100bins_withVar.root" % os.environ[
    'CMSSW_BASE']
pufile_mcUL2016 = "%s/src/PhysicsTools/NanoAODTools/python/postprocessing/data/pileup/mcPileupUL2016.root" % os.environ[
    'CMSSW_BASE']
puWeight_UL2016RDF = lambda: puWeightRDFProducer(
    pufile_mcUL2016, pufile_dataUL2016, "pu_mc", "pileup", verbose=False, doSysVar=True)
puAutoWeight_UL2016 = lambda: puWeightRDFProducer(
    "auto", pufile_dataUL2016, "pu_mc", "pileup", verbose=False)

# 2017
pufile_dataUL2017 = "%s/src/PhysicsTools/NanoAODTools/python/postprocessing/data/pileup/PileupHistogram-UL2017-100bins_withVar.root" % os.environ[
    'CMSSW_BASE']
pufile_mcUL2017 = "%s/src/PhysicsTools/NanoAODTools/python/postprocessing/data/pileup/mcPileupUL2017.root" % os.environ[
    'CMSSW_BASE']
puWeight_UL2017RDF = lambda: puWeightRDFProducer(
    pufile_mcUL2017, pufile_dataUL2017, "pu_mc", "pileup", verbose=False, doSysVar=True)
puAutoWeight_UL2017 = lambda: puWeightRDFProducer(
    "auto", pufile_dataUL2017, "pu_mc", "pileup", verbose=False)

# 2018
pufile_dataUL2018 = "%s/src/PhysicsTools/NanoAODTools/python/postprocessing/data/pileup/PileupHistogram-UL2018-100bins_withVar.root" % os.environ[
    'CMSSW_BASE']
pufile_mcUL2018 = "%s/src/PhysicsTools/NanoAODTools/python/postprocessing/data/pileup/mcPileupUL2018.root" % os.environ[
    'CMSSW_BASE']
puWeight_UL2018RDF = lambda: puWeightRDFProducer(
    pufile_mcUL2018, pufile_dataUL2018, "pu_mc", "pileup", verbose=False, doSysVar=True)
puAutoWeight_UL2018 = lambda: puWeightRDFProducer(
    "auto", pufile_dataUL2018, "pu_mc", "pileup", verbose=False)


def puWeightRDF(**kwargs):
    isMC = kwargs.pop("isMC")
    year = int(kwargs.pop("year"))

    if not isMC:
        return lambda: puWeightDummyRDFProducer()

    if year == 2016:
        return puWeight_2016RDF
    elif year == 2017:
        return puWeight_2017RDF
    elif year == 2018:
        return puWeight_2018RDF