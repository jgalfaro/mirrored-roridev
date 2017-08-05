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

    return js

def traverseJSONInstance(jsonInstance):
    print "-------------------------------------------------------------------------"
    print "Monitored System ID: ",jsonInstance["monitored_System_Ident"]
    print "There are '",len(jsonInstance["mitigationAction"]),"' mitigation action in this JSON instance."

    ma_cou = 1
    for ma in jsonInstance["mitigationAction"]:
        print "-------------------------------------------------------------------------"
        print "Information of Mitigation Action: ", ma_cou
        traverse_nodes(ma, "mitigationAction")
        ma_cou += 1

    return


def traverse_nodes(data,prev_key):
    if isinstance(data,dict):
        for key, val in data.iteritems():
            printval = ""
            if not (isinstance(val,list) or isinstance(val,dict)):
                printval = ": "+str(val)

            if key == "mitigationAction_Ident":
                print "Mitigation Action ID: ", printval
            elif key == "orBacTemplates":
                print ">>OrBac Templates Information<<"
            elif key == "extractorProcess":
                print "   >>Extractor Process Details<<"
            elif key == "engine":
                print "      Engine:",printval
            elif key == "description":
                if prev_key == "extractorProcess":
                    print "      Description:", printval
                elif prev_key == "mitigationAction":
                    print "Mitigation Action Description:", printval
            elif key == "command":
                print "      Command:",printval
            elif key == "scope":
                if prev_key == "orBacTemplates":
                    print "   OrBac Template Scope:", printval
                elif prev_key == "mitigationAction":
                    print "Mitigation Scope:", printval
            elif key == "type":
                if prev_key == "orBacTemplates":
                    print "   OrBac Template Type:", printval
                elif prev_key == "mitigationAction":
                    print "Mitigation Action Type:", printval
                elif prev_key == "parameter":
                    print "      Parameter Type:", printval
            elif key == "annualResponseCost":
                print ">>Annual Response Cost Information<<"
            elif key=="totalCost":
                print "   Total Cost:",printval
            elif key == "name":
                if prev_key == "mitigationAction":
                    print "Mitigation Action Name:", printval
                elif prev_key == "parameter":
                    print "      Parameter Name:", printval
                elif prev_key == "consequences":
                    print "   Consequences Name:", printval
            elif key == "consequences":
                print ">>Consequences Information<<"
            elif key == "negation":
                print "   Negation:",printval
            elif key == "anticorrelator_Kind":
                print "   Anticorrelator Kind:",printval
            elif key == "parameter":
                print "   >>Parameters Information<<"
            elif key == "value":
                print "      Value:",printval
            elif key == "enforcementPoints":
                print ">>Enforcement Points Information<<"
            elif key == "ident":
                print "   Identifier:", printval

            if isinstance(val,list) or isinstance(val,dict):
                traverse_nodes(val,key)

    elif isinstance(data,list):
        for val in data:
            traverse_nodes(val,prev_key)


def main(argv):
    jsonInstanceURI = ''
    jsonSchemaURI = getRealPath()+"AuthorizedMitigationActionJsonSchema.txt"
    authorizedMitigationActionSchema = None
    authorizedMitigationActionJSONInstance = None
    try:
        opts, args = getopt.getopt(argv,"hi:",["ifile="])
    except getopt.GetoptError:
        print 'Usage: '
        print 'authorizedMitigationActionParser.py -i <inputJSON>'
        sys.exit(2)

    if not opts:
        print 'Usage: '
        print 'authorizedMitigationActionParser.py -i <inputJSON>'
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print 'authorizedMitigationActionParser.py -i <inputJSON>'
            sys.exit()
        elif opt in ("-i", "--ifile"):
            jsonInstanceURI = arg

    if jsonInstanceURI != "":
        authorizedMitigationActionSchema = validateJSONSchema(jsonSchemaURI)
        if authorizedMitigationActionSchema != False:
            authorizedMitigationActionSchema = validateInputJSON(jsonInstanceURI, authorizedMitigationActionSchema)
            if authorizedMitigationActionSchema != False:
                traverseJSONInstance(authorizedMitigationActionSchema)
            else:
                exit(1)
        else:
            exit(1)
    else:
        exit(1)

if __name__ == "__main__":
    main(sys.argv[1:])

