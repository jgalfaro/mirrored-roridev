#!/usr/bin/python
__author__ = 'ender_al'

import sys, getopt
from controller.RORI_SRDController import RORI_SRD

def main(argv):
    oname = None
    oid = None
    dename = None
    deid = None
    allc = None
    avg = None
    threshold = None
    listofma = None
    bestma = False
    bestrp = False
    jsonout = False
    jsonfilename = None

    #-----------------------
    # Usage Message
    usagemsg = 'Usage rori_srd.py [options]'
    usagemsg +='\nOrganization and Detrimental Event Options (At least Name or ID of each one should be given):'
    usagemsg +="\n     --oname 	'Name Of Org'	- Name of the Organization"
    usagemsg +='\n     --oid   	IDOfOrg		- ID of the Organization'
    usagemsg +="\n     --dename 	'Name Of DE'  	- Name of the Detrimental Event"
    usagemsg +='\n     --deid   	IDOfDE		- ID of the Detrimental Event'
    usagemsg +='\nCombination Criteria Options:'
    usagemsg +='\n     --all   			- (Default Criteria) All mitigation actions assigned to the Detrimental Event will be combined'
    usagemsg +='\n     --avg 	  		- Only mitigation actions with RORI Index over the average of all individual RORI index given will be combined'
    usagemsg +='\n     --treshold Value  		- Only mitigation actions with individual RORI index over the given threshold will be combined'
    usagemsg +="\n     --listofma  'listofMA'  	- A list of comma separated IDs of MA assigned to the Detrimental Event to be combined ex: M1,M2,M3"
    usagemsg +='\nFiltrage options:'
    usagemsg +='\n     --BestMA   		- Display only the best Mitigation Action from individual RORI evaluation'
    usagemsg +='\n     --BestRP	  		- Display only the best Response Plan from the combined RORI evaluation'
    usagemsg +='\nOutput options:'
    usagemsg +='\n     --json           - Generate a JSON file with the results (to be used only with BestMA or BestRP options)'


    try:
        opts, args = getopt.getopt(argv,"h",["oname=","oid=","dename=","deid=","all","threshold=","avg","listofma=","BestMA","BestRP","json"])
    except getopt.GetoptError:
        print usagemsg
        sys.exit(2)
    comb = 0
    if len(opts) == 0:
        print "[ERROR] No parameters given"
        print usagemsg
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print usagemsg
            sys.exit()
        elif opt in ("--oname"):
            oname = arg
        elif opt in ("--oid"):
            oid = arg
        elif opt in ("--dename"):
            dename = arg
        elif opt in ("--deid"):
            deid = arg
        elif opt in ("--all"):
            allc = True
            comb += 1
        elif opt in ("--avg"):
            avg = True
            comb += 1
        elif opt in ("--threshold"):
            threshold = arg
            comb += 1
        elif opt in ("--listofma"):
            listofma = arg
            comb += 1
        elif opt in ("--BestMA"):
            bestma = True
        elif opt in ("--BestRP"):
            bestrp = True
        elif opt in ("--json"):
            jsonout = True
            #if arg:
            #    jsonfilename = arg

    if comb > 1:
        print "[ERROR] Only one Combination Criteria option should be established"
        sys.exit(2)


    #Create Instance of RORI Calculation
    rori_srd = RORI_SRD(oid,oname,deid,dename)
    r = rori_srd.checkParameters()
    if r == 1:
        sys.exit(r)
    rori_srd.BestMA = bestma
    rori_srd.BestRP = bestrp
    rori_srd.JSON = jsonout
    #Perform Individual Evaluation
    rori_srd.rori_ind = rori_srd.performIndividualEvaluation()
    if rori_srd.rori_ind != 1:
        # Perform the Default Combined Evaluation based on the Combination Criteria given
        if allc: #All MA
            rori_srd.SelectedCriteria = 0
        elif avg:#MA above average
            rori_srd.SelectedCriteria = 1
        elif listofma:
            rori_srd.SelectedCriteria = 2
            listofma = listofma.split(",")
        elif threshold:
            rori_srd.SelectedCriteria = 3
            rori_srd.CombinationThreshold = threshold

        rori_srd.applyCombinationCriteria(listofma)

        if rori_srd.JSON:
            rori_srd.generateJSONOutput()
    else:
        print "Error performing the RORI evaluation!!!"
        sys.exit(1)

if __name__ == "__main__":
   main(sys.argv[1:])