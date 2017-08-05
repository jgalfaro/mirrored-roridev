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
    print "-"*60
    print "Monitored System ID: ",jsonInstance["monitored_System_Ident"]
    print "Risk Profile ID: ",jsonInstance["riskProfile_Ident"]
    print "Snapshot ID: ",jsonInstance["snapshot_Ident"]

    #-------------------------------------------------------------------------------------------------------
    print "*"*80
    print "There are '",len(jsonInstance["detrimentalEvent"]),"' detrimental events defined in this Risk Profile's JSON instance."

    de_cou = 1
    for de in jsonInstance["detrimentalEvent"]:
        print "-"*60
        print "Information of Detrimental Event: ", de_cou
        traverse_de(de, "detrimentalEvent")
        de_cou += 1
    #-------------------------------------------------------------------------------------------------------
    print "*"*80
    print "There are '",len(jsonInstance["attackPathProgress"]),"' Attack Path Progress defined in this Risk Profile's JSON instance."

    app_cou = 1
    for app in jsonInstance["attackPathProgress"]:
        print "-"*60
        print "Information of Attack Path Progress: ", app_cou
        traverse_app(app, "attackPathProgress")
        app_cou += 1

    #-------------------------------------------------------------------------------------------------------
    print "*"*80
    print "There are '",len(jsonInstance["attackPath"]),"' Attack Path defined in this Risk Profile's JSON instance."

    index = 1
    for attack_path in jsonInstance["attackPath"]:
        print "-"*60
        print "Information of Attack Path: ", index
        print "Attack Path Action: ", attack_path["attackPath_Action"]
        print "Attack Path Identifier: ", attack_path["attackPath_Ident"]
        print "The current Attack Path is composed of '",len(attack_path["attackPathNodes"]),"' nodes"
        nod_count = 1
        for node in attack_path["attackPathNodes"]:
            print "-"*60
            print "Information about Node ",nod_count," in the Attack Path:"
            traverse_nodes(node, "attackPathNodes")
            nod_count +=1
        index += 1

    return


def traverse_de(data,prev_key):
    if isinstance(data,dict):
        for key, val in data.iteritems():
            printval = ""
            if not (isinstance(val,list) or isinstance(val,dict)):
                printval = ": "+str(val)

            if key == "proactiveElementaryRisk":
                print ">>>Proactive Elementary Risk Information<<<"
            elif key == "likelihood":
                print "   Likelihood:",printval
            elif key == "riskAssesmentProcess":
                print "   >>Risk Assesment Process Details<<"
            elif key == "engine":
                print "      Engine", printval
            elif key == "description":
                if prev_key == "riskAssesmentProcess":
                    print "      Description", printval
                elif prev_key == "detrimentalEvent":
                    print "Detrimental Event Description", printval
            elif key == "command":
                print "      Command",printval
            elif key == "impact_i":
                print "   Integrity Impact",printval
            elif key == "impact":
                print "   Impact Level",printval
            elif key == "impact_c":
                print "   Confidentiality Impact",printval
            elif key == "impact_a":
                print "   Availability Impact",printval
            elif key == "attackPath_Ident":
                print "   Attack Path ID",printval
            elif key == "automataBasedElementaryRisk":
                print ">>>Automata Based Elementary Risk Information<<<"
            elif key == "ongoingAttackPlan_Ident":
                if prev_key == "automataBasedElementaryRisk":
                    print "   >>>Ongoing Attack Plan Identifier List<<<"
                    for oapid in val:
                        print "      ", oapid
                elif prev_key == "queryBasedReactiveElementaryRisk":
                    print "   Ongoing Attack Plan Identifier:", val
            elif key == "success_Likelyhood":
                if prev_key == "automataBasedElementaryRisk":
                    print "   >>>Success Likelihood List<<<"
                    for suc in val:
                        print "      ", suc
                elif prev_key == "queryBasedReactiveElementaryRisk":
                    print "   Success Likelihood:", val
            elif key == "related_Business_Process_Ident":
                print "Related Business Process ID", printval
            elif key == "name":
                print "Detrimental Event Name", printval
            elif key == "queryBasedReactiveElementaryRisk":
                print ">>>Query Based Reactive Elementary Risk Information<<<"


            if isinstance(val,list) or isinstance(val,dict):
                traverse_de(val,key)

    elif isinstance(data,list):
        for val in data:
            traverse_de(val,prev_key)
    return


def traverse_app(data,prev_key):

    if isinstance(data,dict):
        for key, val in data.iteritems():
            printval = ""
            if not (isinstance(val,list) or isinstance(val,dict)):
                printval = ": "+str(val)

            if key == "mostAdvancedAttackPlan_Ident":
                print "Most Advanced Attack Plan ID",printval
            elif key == "attackPath_Ident":
                print "Attack Path ID",printval
            elif key == "attackPathProgress_Ident":
                print "Attack Path Progress ID",printval
            elif key == "lastCompromisedNode_Ident":
                print "Last Compromised Node ID:",printval
            elif key == "queryBasedOngoingAttack":
                print ">>Query Based Ongoing Attack Details<<"
            elif key == "exploitedEdge":
                print "   >>>Exploited Edge Information<<<"
            elif key == "occurrences":
                print "      Occurrences:", printval
            elif key == "normalizedAlert_Ident":
                if prev_key == "exploitedEdge":
                    print "      >>>Normalized Alert Identifier List<<<"
                    for norm in val:
                        print "         ", norm
            elif key == "exploitation_Time":
                if prev_key == "exploitedEdge":
                    print "      >>>Exploitation Time List<<<"
                    for exptime in val:
                        print "         ", exptime
                elif prev_key == "automataBasedOngoingAttackPlan":
                    print "   Exploitation Time", printval
            elif key == "lastCompromizedNode_Ident":
                print "   Last Compromized Node ID", printval
            elif key == "ongoingAttack_Ident":
                print "   Ongoing Attack ID", printval
            elif key == "automataBasedOngoingAttackPlan":
                print ">>>Automata Based Ongoing Attack Plan Details<<<"
            elif key == "ongoingAttackPlan_Id":
                print "   Ongoing Attack Plan ID", printval
            elif key == "normalizedAlert_Id":
                print "   >>>Normalized Alert ID List<<<"
                for norm in val:
                    print "      ", norm

            if isinstance(val,list) or isinstance(val,dict):
                traverse_app(val,key)

    elif isinstance(data,list):
        for val in data:
            traverse_app(val,prev_key)
    return


def traverse_nodes(data,prev_key):
    if isinstance(data,dict):
        for key, val in data.iteritems():
            printval = ""
            if not (isinstance(val,list) or isinstance(val,dict)):
                printval = ": "+str(val)

            if key == "ingress":
                print ">>>Ingress Node Information<<<"
            elif key == "interface_Ident":
                print "   Interface ID", printval
            elif key == "address":
                if not (isinstance(val,list) or isinstance(val,dict)):
                    print "      Address", printval
                elif prev_key == "ingress":
                    print "   >>>Ingress Node Address Information<<<"
                elif prev_key == "egress":
                    print "   >>>Egress Node Address Information<<<"
            elif key == "category":
                print "      IP Address Type", printval
            elif key == "ident":
                if prev_key == "address":
                    print "      Address ID", printval
                elif prev_key == "classification":
                    print "      Classification ID", printval
            elif key == "vlan_num":
                print "      VLAN Number", printval
            elif key == "vlan_name":
                print "      VLAN Name", printval
            elif key == "netmask":
                print "      Network Mask", printval
            elif key == "maxGainedPrivilege":
                print "Max Gained Privilege", printval
            elif key == "responsibleNodes":
                print ">>>Responsible Nodes<<<", printval
            elif key == "node_Ident":
                if prev_key == "attackPathNodes":
                    print "Node ID", printval
                elif prev_key == "responsibleNodes":
                    print "   >>>List of Responsible Nodes<<<"
            elif key == "node":
                print "      Node", printval
            elif key == "rank":
                print "      Rank", printval
            elif key == "attackPathNodeVulnerability":
                print ">>>Attack Path Node Vulnerability Information<<<"
            elif key == "portList":
                if prev_key == "attackPathNodeVulnerability":
                    print "   >>>Vulnerable Port List<<<"
                elif prev_key == "egress":
                    print "   >>>Egress Node Port List<<<"
            elif key == "portRange":
                print "      >>>Port Range<<<"
            elif key == "port":
                print "         Port", printval
            elif key == "ip_Protocol":
                print "         IP Protocol", printval
            elif key == "protocol":
                if prev_key == "attackPathNodeVulnerability":
                    print "   >>>Vulnerable Protocol Information<<<"
                elif prev_key == "egress":
                    print "   >>>Egress Node Protocol Information<<<"
            elif key == "version":
                print "      Version", printval
            elif key == "name":
                print "      Protocol Name", printval
            elif key == "classification":
                print "   >>>Vulnerability Classification<<<"
            elif key == "text":
                print "      Vulnerability Description", printval
            elif key == "exploited_Range":
                print "   Exploited Range of the Vulnerability", printval
            elif key == "egress":
                print ">>>Egress Node Information<<<"

            if (isinstance(val,list) or isinstance(val,dict)):
                traverse_nodes(val,key)
    elif isinstance(data,list):
        for val in data:
            traverse_nodes(val,prev_key)
    return



def main(argv):
    jsonInstanceURI = ''
    riskProfileJSONInstance = None
    try:
        opts, args = getopt.getopt(argv,"hi:",["ifile="])
    except getopt.GetoptError:
        print 'Usage: '
        print 'riskProfileParser.py -i <inputJSON>'
        sys.exit(2)

    if not opts:
        print 'Usage: '
        print 'riskProfileParser.py -i <inputJSON>'
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print 'riskProfileParser.py -i <inputJSON>'
            sys.exit()
        elif opt in ("-i", "--ifile"):
            jsonInstanceURI = arg

    if jsonInstanceURI != "":
        riskProfileJSONInstance = validateInputJSON(jsonInstanceURI)
        if riskProfileJSONInstance != False:
            traverseJSONInstance(riskProfileJSONInstance)
        else:
            print "The JSON file provided has a bad syntax!!!"
            return

if __name__ == "__main__":
    main(sys.argv[1:])
