#!/usr/bin/python
__author__ = 'ender_al'
import json
import jsonschema
import sys,getopt,os

def getRealPath():
    #Get Real System Path where this script relies
    dir_path = os.path.realpath(__file__).split('/')
    dir_path.pop()
    dir_path = "/".join(dir_path)
    return dir_path+'/'

def validateJSONSchema(uri):
    try:
        JSONSchema = json.load(open(uri))
        jsonschema.Draft4Validator.check_schema(JSONSchema)
        print 'The file "',uri,'" is a valid JSON Schema (Draft4)'
    except jsonschema.SchemaError:
        print 'Error: The file "',uri,'" has bad JSON Schema Syntax!!!'
        return False
    except ValueError:
        print 'Error: The file "',uri,'" has bad JSON Schema Syntax!!!'
        return False
    except IOError:
        print 'Error: The file "',uri,'" does not exist!!!'
        return False
    return JSONSchema


def validateInputJSON(uri,JSONSchema):
    #First Validate the JSON file given as an input
    try:
        json_file = open(uri)
        js = json.load(json_file)
        print 'The file "',uri,'" is a valid JSON File'
    except ValueError, e:
        print 'Error: The file "',uri,'" is not a valid JSON File!!!'
        return False
    except IOError:
        print 'Error: The file "',uri,'" does not exist!!!'
        return False

    #Then Check if its compliant to the Schema
    """
    try:
        jsonschema.validate(js, JSONSchema)
        print 'The input JSON is a valid instance of the given JSON Schema'
    except ValueError:
        print 'Error: The Input JSON is not a valid instance of the JSON Schema!'
        return False
    except jsonschema.ValidationError as e:
        print 'Error: The Input JSON is not a valid instance of the JSON Schema!'
        print e.message
        return False
    """

    return js

def traverseJSONInstance(jsonInstance):
    print "-------------------------------------------------------------------------"
    print "Monitored System ID: ",jsonInstance["monitored_System_Ident"]
    print "Reachability Matrix ID: ", jsonInstance["reachabilityMatrix_Ident"]
    print "Snapshot ID: ", jsonInstance["snapshot_Ident"]
    print "Reachability Matrix composed of '",len(jsonInstance["node"]),"' nodes"


    nod_cou = 1
    for node in jsonInstance["node"]:
        print "-------------------------------------------------------------------------"
        print "Information of Node: ", nod_cou
        if "vulnerabilityList" in node:
            print "Type: Internal Node"
        else:
            print "Type: External Node"
        traverse_nodes(node, "node")
        nod_cou += 1

    return


def traverse_nodes(data,prev_key):
    if isinstance(data,dict):
        for key, val in data.iteritems():
            printval = ""
            if not (isinstance(val,list) or isinstance(val,dict)):
                printval = ": "+str(val)

            if key == "node_Ident":
                if not (isinstance(val,list) or isinstance(val,dict)):
                    if prev_key == "node":
                        print "Node's ID:", printval
                    elif prev_key == "communicatingNode":
                        print "      Communicating Node ID:", printval
                else:
                    print "          List of Node ID"
            elif key == "name":
                if prev_key == "node":
                    print "Node's Name:", printval
                elif prev_key == "location":
                    print "  Location Name:", printval
                elif prev_key == "protocol":
                    print "           Protocol Name:", printval
                elif prev_key == "nodeInterface":
                    print "   Node's Interface Name:", printval
            elif key == "location":
                print ">>Node's Location Details<<"
            elif key == "position":
                print "  Node's position"
            elif key == "x":
                print "    X coordinate:", printval
            elif key == "y":
                print "    Y coordinate:", printval
            elif key == "z":
                print "    Z coordinate:", printval
            elif key == "type":
                if prev_key == "node":
                    print "Node Type:", printval
                elif prev_key == "position":
                    print "    Position Type:", printval
            elif key == "initialAccessLevel":
                print "Node's Initial Access Level:", printval
            elif key == "nodeInterface":
                print ">>Node's Interface Information<<"
            elif key == "communicatingNode":
                print "   >>Communicating Node Information<<"
            elif key == "address":
                if not (isinstance(val,list) or isinstance(val,dict)):
                    print "      Address:", printval
                else:
                    if prev_key == "communicatingNode":
                        print "      >>Communicating Node Address Information<<"
                    if prev_key == "nodeInterface":
                        print "   >>Node Interface Address Information<<"
            elif key == "netmask":
                print "      Network Mask:", printval
            elif key == "vlan_num":
                print "      VLAN Number:", printval
            elif key == "ident":
                print "      Identifier:", printval
            elif key == "category":
                print "      IP Address Type", printval
            elif key == "vlan_name":
                print "      VLAN Name:", printval
            elif key == "responsiblePath":
                print "      >>Responsible Path Information<<"
            elif key == "protocolList":
                print "        >>Protocol List Information<<"
            elif key == "protocol":
                print "         Protocol Info"
            elif key == "version":
                print "           Version:", printval
            elif key == "responsibleNodeList":
                print "        >>Responsible Node List Information<<"
            elif key == "node":
                print "            Node:", printval
            elif key == "rank":
                print "            Rank:", printval
            elif key == "portList":
                print "        >>Port List Information<<"
            elif key == "portRange":
                print "          Port Range"
            elif key == "port":
                print "            Port:", printval
            elif key == "ip_Protocol":
                print "            IP Protocol:", printval
            elif key == "vulnerabilityList":
                print ">>Vulnerability List Information<<"
            elif key == "vulnerability_Ident":
                print "   Vulnerability Identifier List"
                for vulnerability in val:
                    print "    ", vulnerability
            elif key == "interface_Ident":
                print "   Node's Interface ID:", printval
            elif key == "network_Ident":
                print "   Node's Interface Network ID:", printval

            if isinstance(val,list) or isinstance(val,dict):
                traverse_nodes(val,key)

    elif isinstance(data,list):
        for val in data:
            traverse_nodes(val,prev_key)


def main(argv):
    jsonInstanceURI = ''
    jsonSchemaURI = getRealPath()+"ReachabilityMatrixJsonSchema.txt"
    reachabilityMatrixJSONSchema = None
    reachabilityMatrixJSONInstance = None
    try:
        opts, args = getopt.getopt(argv,"hi:",["ifile="])
    except getopt.GetoptError:
        print 'Usage: '
        print 'reachabilityMatrixParser.py -i <inputJSON>'
        sys.exit(2)

    if not opts:
        print 'Usage: '
        print 'reachabilityMatrixParser.py -i <inputJSON>'
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print 'reachabilityMatrixParser.py -i <inputJSON>'
            sys.exit()
        elif opt in ("-i", "--ifile"):
            jsonInstanceURI = arg

    if jsonInstanceURI != "":
        reachabilityMatrixJSONSchema = validateJSONSchema(jsonSchemaURI)
        if reachabilityMatrixJSONSchema != False:
            reachabilityMatrixJSONSchema = validateInputJSON(jsonInstanceURI, reachabilityMatrixJSONSchema)
            if reachabilityMatrixJSONSchema != False:
                traverseJSONInstance(reachabilityMatrixJSONSchema)
            else:
                exit(1)
        else:
            exit(1)

if __name__ == "__main__":
    main(sys.argv[1:])

