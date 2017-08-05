#!/usr/bin/python
__author__ = 'ender_al'

from WebServiceClient import SynchronousClient
import urllib
from datetime import datetime
import json
import sys, getopt


class processResponsePlan():
    def __init__(self):
        self.url = "http://localhost:8888"
        self.service = "processResponsePlan"
        self.parameters = {'snapshotId':'Test_snapshotId','responsePlanId':'test_responsePlanId'}
        self.path = '/tmp/PANOPTESEC_InputData/MissionGraph'
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
        print '*** processResponsePlan Interface ***'
        client = SynchronousClient()
        client.url = self.url+'/'+self.service+'?'+urllib.urlencode(self.parameters)
        client.post_data = self.post_data
        print 'Sending POST request to server using URL:',client.url
        client.post_request()
        print 'Server Response:\n',client.response.body
        try:
            json_response = json.loads(client.response.body) #Transform the Server String Response into a valid JSON instance
        except ValueError, e:
            print 'Error: The response returned by the server is not a Valid JSON instance!!!'
            exit(1)

        tstamp = datetime.now().__str__().replace(" ","_").replace(":","-").replace(".","-")
        json_path = self.path+"/"+"MissionGraph"+"_"+tstamp+".json"

        with open(json_path,'w') as json_file:
            try:
                json_file.write(json.dumps(json_response, sort_keys=True, indent=4, separators=(',', ': ')))
                print 'Saving the Response on path:', json_path
            except ValueError, e:
                print 'Error: The Server Response could not be saved on:', json_path
                exit(1)

def main(argv):
    jsonURI = ''
    try:
        opts, args = getopt.getopt(argv,"hi:",["ifile="])
    except getopt.GetoptError:
        print 'Usage: '
        print 'processResponsePlan.py -i <inputJSON>'
        sys.exit(2)

    if not opts:
        print 'Usage: '
        print 'processResponsePlan.py -i <inputJSON>'
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print 'processResponsePlan.py -i <inputJSON>'
            sys.exit()
        elif opt in ("-i", "--ifile"):
            jsonURI = arg

    interface = processResponsePlan()
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