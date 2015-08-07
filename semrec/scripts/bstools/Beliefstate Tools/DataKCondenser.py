from LogReader import LogReader
import math
import json
import pickle


class DataKCondenser:
    def __init__(self):
        self.rdrLog = LogReader()
        
    def condenseData(self, strPath):
        dataOwl = None
        
        log = self.rdrLog.loadLog(strPath)
        dataOwl = log.getOwlData()
        
        self.tti = dataOwl["task-tree-individuals"]
        owlMeta = dataOwl["metadata"]
        owlAnnot = dataOwl["annotation"]
        
        if owlMeta:
            result = {"Toplevel" : self.condenseNodes("", owlMeta.subActions())};
            
            with open("out_k.json", "wb") as f:
                json.dump(result, f)
            
            # with open("generalized_model.pkl", "wb") as f:
            #     pickle.dump({"model" : result,
            #                  "parameters" : owlAnnot.annotatedParameterTypes()},
            #                 f, pickle.HIGHEST_PROTOCOL)
        else:
            print "No meta data in file!"
    
    def condenseNodes(self, strParentNode, arrNodes, nLevel = 0):
        arrTypes = {}
        arrIndividuals = {}
        
        for strNode in arrNodes:
            owlNode = self.tti[strNode]
            
            result = self.condenseNodes(strNode, owlNode.subActions(), nLevel + 1)
            if not owlNode.taskContext() in arrTypes:
                arrTypes[owlNode.taskContext()] = result
            else:
                arrTypes[owlNode.taskContext()] = self.unifyResults(arrTypes[owlNode.taskContext()], result)
        
        return {"subTypes" : arrTypes}
    
    def unifyResults(self, res1, res2):
        unified = {"subTypes" : {}}
        
        for ressub1 in res1["subTypes"]:
            if ressub1 in res2["subTypes"]:
                unified["subTypes"][ressub1] = self.unifyResults(res1["subTypes"][ressub1],
                                                                 res2["subTypes"][ressub1])
            else:
                unified["subTypes"][ressub1] = res1["subTypes"][ressub1]
        
        for ressub2 in res2["subTypes"]:
            if not ressub2 in res1["subTypes"]:
                unified["subTypes"][ressub2] = res2["subTypes"][ressub2]
        
        return unified
