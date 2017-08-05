#!/usr/bin/python
__author__ = 'ender_al'

from WebServiceClient import SynchronousClient
import urllib
from datetime import datetime
import json


class GetNetworkInventory():
    def __init__(self):
        #self.url = "http://10.10.0.16:8184/pm"
        self.service = "getNetworkInventory"
        #self.parameters = {'monitoredSystem_Ident':'ReachMatrix_System_Ident','snapshotId':'ReachMatrix_snapshotId','reachabilityMatrixId':'ReachMatrix_Id'}
        self.parameters = {'monitoredSystemId':'AceaSim_Env'}
        #self.parameters = {'dataMap':{'networkInventoryId':'95592324-92a7-4ff9-8934-1269ac0c36a5'}}
        #self.parameters = {'dataMap':{'NETWORK_INVENTORY_ID':'95592324-92a7-4ff9-8934-1269ac0c36a5'}}
        self.path = '/var/PANOPTESEC/Jail/InputData/NetworkInventory'

    def sendRequest(self):
        print 'getNetworkInventory Interface'
        client = SynchronousClient()
        client.url = client.url+'/'+self.service
        client.post_data = self.parameters
        print 'Sending Get request to server using URL:',client.url
        print 'And with Parameters:', self.parameters
        client.post_request()
        if client.response.body == "ERROR- Item not found":
            print 'Error: The requested Network Inventory could not be found on the Server!!!'
            exit(1)
        elif client.response.body == "ERROR1-Connection to the database failed":
            print 'Error: The Server could not connect to the database!!!'
            exit(1)
        elif client.response.body == "ERROR1- Get function failed":
            print 'Error: The Server has found a problem in the Get function!!!'
            exit(1)
        else:#Everything OK from Server Side
            #print client.response.body
            try:
                json_response = json.loads(client.response.body) #Transform the Server String Response into a valid JSON instance
            except ValueError, e:
                print 'Error: The response returned by the server is not a Valid JSON instance!!!'
                exit(1)

        tstamp = datetime.now().__str__().replace(" ","_").replace(":","-").replace(".","-")
        json_path = self.path+"/"+"NetworkInventory"+"_"+tstamp+".json"

        with open(json_path,'w') as json_file:
            try:
                json_file.write(json.dumps(json_response, sort_keys=True, indent=4, separators=(',', ': ')))
                print 'Saving the Response on path:', json_path
            except ValueError, e:
                print 'Error: The Server Response could not be saved on:', json_path
                exit(1)


if __name__ == "__main__":
    interface = GetNetworkInventory()
    interface.sendRequest()



