#!/usr/bin/python
__author__ = 'ender_al'

from WebServiceClient import SynchronousClient
import urllib
import json
import sys, getopt


class SendSRDEnforceableResponsePlan():
    def __init__(self):
        self.url = "http://10.10.0.16:8194/srd"
        self.service = "sendSRDEnforceableResponsePlan"
        #Payload= {"monitoredSystemId":"AceaSim_Env", "snapshotId":"xxxx", "dataMap":{"RESPONSE_PLAN_ID":"xxxxx","RESPONSE_PLAN":"JSON"}}
        #self.parameters = {'monitoredSystemId':'AceaSim_Env','snapshotId':'10/29/2015 10:48:07',"dataMap":{"RESPONSE_PLAN_ID":"RP-SRD-ID-012345"}}
        self.parameters = {'monitoredSystemId':'','snapshotId':'',"dataMap":{"RESPONSE_PLAN_ID":"","RESPONSE_PLAN":""}}
        #ContentType= ("application/json")
        self.post_data = None

    def validateInputJSON(self,uri):
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
        return js

    def sendRequest(self):
        print '*** sendSRDEnforceableResponsePlan Interface ***'
        client = SynchronousClient()
        #client.url = self.url+'/'+self.service+'?'+urllib.urlencode(self.parameters)
        client.url = self.url+'/'+self.service

        # Getting the Right ID from the JSON File
        self.parameters['monitoredSystemId'] = self.post_data["monitored_System_Ident"]
        self.parameters['snapshotId'] = self.post_data["snapshot_Ident"]
        self.parameters['dataMap']["RESPONSE_PLAN_ID"] = self.post_data["responsePlanID"]
        self.parameters['dataMap']["RESPONSE_PLAN"] = self.post_data

        client.post_data = self.parameters
        print client.post_data
        print 'Sending POST request to server using URL:',client.url
        client.post_request()
        #print 'Server Response:\n',client.response
        print 'Server Response Body:\n',client.response.body

def main(argv):
    jsonURI = ''
    try:
        opts, args = getopt.getopt(argv,"hi:",["ifile="])
    except getopt.GetoptError:
        print 'Usage: '
        print 'SendSRDEnforceableResponsePlan.py -i <inputJSON>'
        sys.exit(2)

    if not opts:
        print 'Usage: '
        print 'SendSRDEnforceableResponsePlan.py -i <inputJSON>'
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print 'SendSRDEnforceableResponsePlan.py -i <inputJSON>'
            sys.exit()
        elif opt in ("-i", "--ifile"):
            jsonURI = arg

    interface = SendSRDEnforceableResponsePlan()

    if jsonURI != "":
        jsonInstance = interface.validateInputJSON(jsonURI)
        if jsonInstance != False:
            interface.post_data = jsonInstance
            interface.sendRequest()
        else:
            exit(1)
    else:
        exit(1)


if __name__ == "__main__":
    main(sys.argv[1:])