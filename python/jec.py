import os
import tarfile
import tempfile
import itertools

from Base.Modules.baseModules import JetLepMetSyst

from analysis_tools.utils import import_root

ROOT = import_root()

class jecProviderRDFProducer(JetLepMetSyst):
    def __init__(self, isMC,
            jerInputFileName="Spring16_25nsV10_MC_PtResolution_AK4PFchs.txt",
            jec_sources=[], *args, **kwargs):

        self.isMC = isMC

        if self.isMC:
            self.jerInputArchivePath = os.environ['CMSSW_BASE'] + \
                "/src/PhysicsTools/NanoAODTools/data/jme/"
            self.jerTag = jerInputFileName[:jerInputFileName.find('_MC_') + len('_MC')]
            self.jerArchive = tarfile.open(
                self.jerInputArchivePath + self.jerTag + ".tgz", "r:gz")
            self.jerInputFilePath = tempfile.mkdtemp()
            self.jerArchive.extractall(self.jerInputFilePath)
            self.jerInputFileName = "RegroupedV2_%s_UncertaintySources_AK4PFchs.txt"\
                % self.jerTag
            assert(os.path.isfile(os.path.join(self.jerInputFilePath, self.jerInputFileName)))

            if "/libBaseModules.so" not in ROOT.gSystem.GetLibraries():
                ROOT.gSystem.Load("libBaseModules.so")
            base = "{}/{}/src/Base/Modules".format(
                os.getenv("CMT_CMSSW_BASE"), os.getenv("CMT_CMSSW_VERSION"))
            ROOT.gROOT.ProcessLine(".L {}/interface/jecProvider.h".format(base))

            self.jec_sources = jec_sources;
            jec_sources_str = ", ".join(['"%s"' % jec_source for jec_source in self.jec_sources])

            ROOT.gInterpreter.Declare(
                'auto jec_provider = jecProvider("%s", {%s});' % (
                    os.path.join(self.jerInputFilePath, self.jerInputFileName),
                    jec_sources_str
                )
            )
        super(jecProviderRDFProducer, self).__init__(self, *args, **kwargs)

    def run(self, df):
        if not self.isMC:
            return df, []
        branches = ["%s_%s" % (name, d) for (d, name) in itertools.product(
            ["up", "down"], ["jec_factor_%s" % jec_source for jec_source in self.jec_sources])]

        df = df.Define("jec_uncertainties", "jec_provider.get_jec_uncertainties("
            "nJet, Jet_pt%s, Jet_eta)" % self.jet_syst).Define(
            "jec_up", "jec_uncertainties[0]").Define("jec_down", "jec_uncertainties[1]")
        for ib, branch in enumerate(branches):
            if ib < len(self.jec_sources):
                df = df.Define(branch, "jec_up[%s]" % ib)
            else:
                df = df.Define(branch, "jec_down[%s]" % (ib - len(self.jec_sources)))
        return df, branches


def jecProviderRDF(**kwargs):
    """
    Module to compute jec uncertainty factors
    Note: UL2016_preVFP is not implemented

    :param: jec_sources: names of the systematic sources to consider. They depend on the year:

        - 2016: ``FlavorQCD``, ``RelativeBal``, ``HF``, ``BBEC1``, ``EC2``, ``Absolute``,\
        ``BBEC1_2016``, ``EC2_2016``, ``Absolute_2016``, ``HF_2016``, ``RelativeSample_2016``,\
        ``Total``

        - 2017: ``FlavorQCD``, ``RelativeBal``, ``HF``, ``BBEC1``, ``EC2``, ``Absolute``,\
        ``BBEC1_2017``, ``EC2_2017``, ``Absolute_2017``, ``HF_2017``, ``RelativeSample_2017``,\
        ``Total``

        - 2018: ``FlavorQCD``, ``RelativeBal``, ``HF``, ``BBEC1``, ``EC2``, ``Absolute``,\
        ``BBEC1_2018``, ``EC2_2018``, ``Absolute_2018``, ``HF_2018``, ``RelativeSample_2018``,\
        ``Total``

        Note: probably more are available, to be checked.
        Note: if none are specified as input, all the available from above will be computed

    :type jec_sources: list of str

    YAML sintaxis:

    .. code-block:: yaml

        codename:
            name: jecProviderRDF
            path: Base.Modules.jec
            parameters:
                year: self.config.year
                isMC: self.dataset.process.isMC
                jerTag: self.config.year
                isUL: self.dataset.has_tag('ul')
                jec_sources: []

    """

    isMC = kwargs.pop("isMC")
    isUL = kwargs.pop("isUL")
    year = kwargs.pop("year")
    jetType = kwargs.pop("jetType", "AK4PFchs")
    # jerTag = kwargs.pop("jerTag", "")
    jec_sources = kwargs.pop("jec_sources", [])

    jerTagsMC = {
        '2016': 'Summer16_07Aug2017_V11_MC',
        '2017': 'Fall17_17Nov2017_V32_MC',
        '2018': 'Autumn18_V19_MC',
        'UL2016_preVFP': 'Summer20UL16APV_JRV3_MC', # dummy
        'UL2016': 'Summer20UL16_JRV3_MC', # dummy
        'UL2017': 'Summer19UL17_V5_MC',
        'UL2018': 'Summer19UL18_V5_MC',
    }

    if isUL and year == 2016:
        raise ValueError("UL 2016 needs a further check")

    # if jerTag != "":
    jerTag = jerTagsMC["%s%s" % (("UL" if isUL else ""), year)]
    jerInputFileName = jerTag + "_PtResolution_" + jetType + ".txt"

    jec_sources_per_year = {
        2016: ["FlavorQCD", "RelativeBal", "HF", "BBEC1", "EC2", "Absolute", "BBEC1_2016",
            "EC2_2016", "Absolute_2016", "HF_2016", "RelativeSample_2016", "Total"],
        2017: ["FlavorQCD", "RelativeBal", "HF", "BBEC1", "EC2", "Absolute", "BBEC1_2017",
            "EC2_2017", "Absolute_2017", "HF_2017", "RelativeSample_2017", "Total"],
        2018: ["FlavorQCD", "RelativeBal", "HF", "BBEC1", "EC2", "Absolute", "BBEC1_2018",
            "EC2_2018", "Absolute_2018", "HF_2018", "RelativeSample_2018", "Total"]
    }

    if len(jec_sources) == 0:
        jec_sources = jec_sources_per_year[int(year)]
    else:
        for jec_source in jec_sources:
            assert jec_source in jec_sources_per_year[int(year)]

    return lambda: jecProviderRDFProducer(isMC, jerInputFileName, jec_sources, **kwargs)
