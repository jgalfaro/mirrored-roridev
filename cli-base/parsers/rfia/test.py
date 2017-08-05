#!/usr/bin/python
import json
import sys,getopt

def validateInputJSON(uri):
    try:
        json_file = open(uri)
        js = json.load(json_file)
        print "Valid JSON File"
    except ValueError, e:
        return False

    return js

def traverseJSONInstance(jsonInstance):
    #Load Dummy File with detailed info about MA
    dummy_data = open('.dummy.txt')
    dummy_json = json.load(dummy_data)
    individual_list = []
    combined_list = []

    for results in jsonInstance['mitigationActions']:
        if "RORI_Combined" in results:
            ma_ids = (', ').join([ind['mitigationActionID'] for ind in results['individualEvaluation']])

            combined_list.append([ma_ids,results["RORI_Combined"]])
        else:
            for ind in results["individualEvaluation"]:
                for ma_data in dummy_json["RORI_MA"]:
                    if ma_data["id"] == ind["mitigationActionID"]:
                        ma_name = ma_data["name"]
                        break
                individual_list.append([ind["mitigationActionID"],ma_name,ind["enforcementPoint"],ind["RORI_Index"]])

    if len(individual_list)>0:
        print "\n--------------------------------------------------------------------------------"
        print "Individual Results"
        template = "{0:4}|{1:45}|{2:12}|{3:8}" # column widths: 8, 10, 15, 7, 10
        print template.format("ID", "NAME", "EQUIPMENT ID", "RORI") # header
        for rec in individual_list:
            msg = template.format(*rec)
            #if rec[4]==best_id:
            #    print msg + " <-- Best RORI index"
            #else:
            print msg
    if len(combined_list)>0:
        print "\n--------------------------------------------------------------------------------"
        print "Combined Results"
        template = "{0:20}|{1:8}"
        print template.format("Response Plans","RORI Index") # header
        index = 0
        for rec in combined_list:
            msg = template.format(*rec)
            #if index==best_id:
            #    print msg + " <-- Best RORI index"
            #else:
            #    print msg
            #index +=1
            print msg
        print "--------------------------------------------------------------------------------"


def main(argv):
    jsonInstanceURI = ''
    rfiaJSONInstance = None
    try:
        opts, args = getopt.getopt(argv,"hi:",["ifile="])
    except getopt.GetoptError:
        print 'Usage: '
        print 'srdJSONParser.py -i <inputJSON>'
        sys.exit(2)

    if not opts:
        print 'Usage: '
        print 'srdJSONParser.py -i <inputJSON>'
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print 'srdJSONParser.py -i <inputJSON>'
            sys.exit()
        elif opt in ("-i", "--ifile"):
            jsonInstanceURI = arg

    if jsonInstanceURI != "":
        rfiaJSONInstance = validateInputJSON(jsonInstanceURI)
        if rfiaJSONInstance != False:
            traverseJSONInstance(rfiaJSONInstance)
        else:
            print "The JSON file provided has a bad syntax!!!"
            return

if __name__ == "__main__":
    main(sys.argv[1:])

