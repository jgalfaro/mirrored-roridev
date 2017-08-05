#!/usr/bin/python
__author__ = 'ender_al'

from WebServiceClient import SynchronousClient
import urllib
from datetime import datetime
import json


class RiskProfileInterface():
    def __init__(self):
        self.url = "http://localhost:8888"
        self.service = "getProactiveRiskProfile"
        self.parameters = {'monitoredSystem_Ident':'RiskProfile_System_Ident','snapshotId':'RiskProfile_snapshotId','riskProfileId':'RiskProfile_Id'}
        self.path = '/tmp/PANOPTESEC_InputData/RiskProfile'

    def sendRequest(self):
        print 'getProactiveRiskProfile Interface'
        client = SynchronousClient()
        client.url = self.url+'/'+self.service+'?'+urllib.urlencode(self.parameters)
        print 'Sending Get request to server using URL:',client.url
        client.get_request()
        print 'Server Response:\n',client.response.body
        try:
            json_response = json.loads(client.response.body) #Transform the Server String Response into a valid JSON instance
        except ValueError, e:
            print 'Error: The response returned by the server is not a Valid JSON instance!!!'
            exit(1)

        tstamp = datetime.now().__str__().replace(" ","_").replace(":","-").replace(".","-")
        json_path = self.path+"/"+"ReachMatrix"+"_"+tstamp+".json"

        with open(json_path,'w') as json_file:
            try:
                json_file.write(json.dumps(json_response, sort_keys=True, indent=4, separators=(',', ': ')))
                print 'Saving the Response on path:', json_path
            except ValueError, e:
                print 'Error: The Server Response could not be saved on:', json_path
                exit(1)


if __name__ == "__main__":
    interface = RiskProfileInterface()
    interface.sendRequest()



