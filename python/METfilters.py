from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from analysis_tools.utils import import_root

ROOT = import_root()

# extracted from
# https://twiki.cern.ch/twiki/bin/viewauth/CMS/MissingETOptionalFiltersRun2

class MetFilterProducer(Module):
    def __init__(self, isMC, year, *args, **kwargs):
        super(MetFilterProducer, self).__init__(*args, **kwargs)
        self.isMC = isMC
        self.year = int(year)

    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass

    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass

    def analyze(self, event):
        """process event, return True (go to next module) or False (fail, go to next event)"""
        flags = 0
        flags += (1 if event.Flag_goodVertices else 0)
        flags += (1 if event.Flag_globalSuperTightHalo2016Filter else 0)
        flags += (1 if event.Flag_HBHENoiseFilter else 0)
        flags += (1 if event.Flag_HBHENoiseIsoFilter else 0)
        flags += (1 if event.Flag_EcalDeadCellTriggerPrimitiveFilter else 0)
        flags += (1 if event.Flag_BadPFMuonFilter else 0)
        flags += (1 if event.Flag_eeBadScFilter and not self.isMC else 0)
        if hasattr(event, "Flag_ecalBadCalibFilterV2") and self.year != 2016:
            flags += (1 if event.Flag_ecalBadCalibFilterV2 else 0)
        else:
            flags += 1

        # all True -> Data
        if flags == 8:  
            return True
        # all True but one -> MC 
        elif flags == 7 and self.isMC:
            return True

        return False


def MetFilter(**kwargs):
    return lambda: MetFilterProducer(**kwargs)


class MetFilterRDFProducer():
    def __init__(self, isMC, year, *args, **kwargs):
        self.isMC = isMC
        self.year = int(year)
        
        ROOT.gInterpreter.Declare("""
            using VBool = const ROOT::RVec<bool>&;
            int pass_met(VBool met_flags) {
                int total_met = 0;
                for (size_t i = 0; i < met_flags.size(); i++) {
                    if (met_flags[i]) {
                        total_met ++;
                    }
                }
                return total_met;
            }
        """)

    def run(self, df):
        columnNames = list(df.GetColumnNames())
        flags = [
            "Flag_goodVertices", "Flag_globalSuperTightHalo2016Filter", "Flag_HBHENoiseFilter",
            "Flag_HBHENoiseIsoFilter", "Flag_EcalDeadCellTriggerPrimitiveFilter",
            "Flag_BadPFMuonFilter"
        ]
        if not self.isMC:
            flags.append("Flag_eeBadScFilter")
        else:
            flags.append("true")
        if "Flag_ecalBadCalibFilterV2" in columnNames and self.year != 2016:
            flags.append("Flag_ecalBadCalibFilterV2")
        else:
            flags.append("true")

        return df.Filter("pass_met({%s}) == 8" % ", ".join(flags)), []


def MetFilterRDF(**kwargs):
    return lambda: MetFilterRDFProducer(**kwargs)

