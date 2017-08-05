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
    print "-"*50
    print "ID of monitored System: ",jsonInstance["monitored_System_Ident"]
    print "Type of Attack Graph: ", jsonInstance["attackGraphType"]
    print "Snapshot ID: ", jsonInstance["snapshot_Ident"]
    print "Attack Graph composed of '",len(jsonInstance["attackPath"]),"' attack path"

    index = 1
    for attack_path in jsonInstance["attackPath"]:
        print "-"*50
        print "Information of Attack Path: ", index
        print "Attack Path Action: ", attack_path["attackPath_Action"]
        print "Attack Path Identifier: ", attack_path["attackPath_Ident"]
        print "The current Attack Path is composed of '",len(attack_path["attackPathNodes"]),"' nodes"
        nod_count = 1
        for node in attack_path["attackPathNodes"]:
            print "-"*50
            print "Information about Node ",nod_count," in the Attack Path:"
            traverse_nodes(node,"attackPathNodes")
            nod_count +=1
        index += 1

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
                print "   Interface ID:", printval
            elif key == "address":
                if not (isinstance(val,list) or isinstance(val,dict)):
                    print "      Address:", printval
                elif prev_key == "ingress":
                    print "   >>>Ingress Node Address Information<<<"
                elif prev_key == "egress":
                    print "   >>>Egress Node Address Information<<<"
            elif key == "category":
                print "      IP Address Type:", printval
            elif key == "ident":
                if prev_key == "address":
                    print "      Address ID:", printval
                elif prev_key == "classification":
                    print "      Classification ID:", printval
            elif key == "vlan_num":
                print "      VLAN Number:", printval
            elif key == "vlan_name":
                print "      VLAN Name:", printval
            elif key == "netmask":
                print "      Network Mask:", printval
            elif key == "maxGainedPrivilege":
                print "Max Gained Privilege", printval
            elif key == "responsibleNodes":
                print ">>>Responsible Nodes<<<", printval
            elif key == "node_Ident":
                if prev_key == "attackPathNodes":
                    print "Node ID:", printval
                elif prev_key == "responsibleNodes":
                    print "   >>>List of Responsible Nodes<<<"
            elif key == "node":
                print "      Node:", printval
            elif key == "rank":
                print "      Rank:", printval
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
                print "         Port:", printval
            elif key == "ip_Protocol":
                print "         IP Protocol:", printval
            elif key == "protocol":
                if prev_key == "attackPathNodeVulnerability":
                    print "   >>>Vulnerable Protocol Information<<<"
                elif prev_key == "egress":
                    print "   >>>Egress Node Protocol Information<<<"
            elif key == "version":
                print "      Version:", printval
            elif key == "name":
                print "      Protocol Name:", printval
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


def main(argv):
    jsonInstanceURI = ''
    AttackGraphJSONInstance = None
    try:
        opts, args = getopt.getopt(argv,"hi:",["ifile="])
    except getopt.GetoptError:
        print 'Usage: '
        print 'attackGraphParser.py -i <inputJSON>'
        sys.exit(2)

    if not opts:
        print 'Usage: '
        print 'attackGraphParser.py -i <inputJSON>'
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print 'attackGraphParser.py -i <inputJSON>'
            sys.exit()
        elif opt in ("-i", "--ifile"):
            jsonInstanceURI = arg

    if jsonInstanceURI != "":
        AttackGraphJSONInstance = validateInputJSON(jsonInstanceURI)
        if AttackGraphJSONInstance != False:
            traverseJSONInstance(AttackGraphJSONInstance)
        else:
            print "The JSON file provided has a bad syntax!!!"
            return

if __name__ == "__main__":
    main(sys.argv[1:])


