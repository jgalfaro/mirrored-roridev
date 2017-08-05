#!/usr/bin/python
__author__ = 'ender_al'

from WebServiceClient import SynchronousClient
import urllib
from datetime import datetime
import json


class GetReachibilityMatrix():
    def __init__(self):
        #self.url = "http://localhost:8888"
        self.service = "getReachabilityMatrix"
        #Payload form {"monitoredSystemId":"AceaSim_Env", "snapshotId":"xxxx", "dataMap":{"NETWORK_INVENTORY_ID":"xxxxx"}}
        #self.parameters = {'monitoredSystem_Ident':'ReachMatrix_System_Ident','snapshotId':'ReachMatrix_snapshotId','reachabilityMatrixId':'ReachMatrix_Id'}
        self.parameters = {'monitoredSystemId':'AceaSim_Env'}
        self.path = '/var/PANOPTESEC/Jail/InputData/ReachabilityMatrix'

    def sendRequest(self):
        print 'getReachabilityMatrix Interface'
        client = SynchronousClient()
        #client.url = self.url+'/'+self.service+'?'+urllib.urlencode(self.parameters)
        client.url = client.url+'/'+self.service
        client.post_data = self.parameters
        print 'Sending Get request to server using URL:',client.url
        print 'And with Parameters:', self.parameters
        #client.get_request()
        client.post_request()
        if client.response.body == "ERROR- Item not found":
            print 'Error: The requested Reachability Matrix could not be found on the Server!!!'
            exit(1)
        elif client.response.body == "ERROR1-Connection to the database failed":
            print 'Error: The Server could not connect to the database!!!'
            exit(1)
        elif client.response.body == "ERROR1- Get function failed":
            print 'Error: The Server has found a problem in the Get function!!!'
            exit(1)
        else:#Everything OK from Server Side
            #print 'Server Response:\n',client.response.body
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
    interface = GetReachibilityMatrix()
    interface.sendRequest()



