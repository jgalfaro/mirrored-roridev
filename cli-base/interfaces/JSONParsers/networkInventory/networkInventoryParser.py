#!/usr/bin/python
__author__ = 'ender_al'
import json
import sys,getopt,os

import ijson


def getRealPath():
    #Get Real System Path where this script relies
    dir_path = os.path.realpath(__file__).split('/')
    dir_path.pop()
    dir_path = "/".join(dir_path)
    return dir_path+'/'


def traverseJSON(path):
    print 'Parsing info from Network Inventory File:',path

    with open(path) as json_file:
        parser = ijson.parse(json_file)
        devices=1

        for prefix, event, value2 in parser:
            if type(value2) == str:
                value = value2.encode("utf-8")
            else:
                value = value2
            #----------------------------------------
            if prefix.endswith("monitored_System_Ident"):
                print 'Monitored System ID:', value
            #----------------------------------------
            elif prefix.endswith("deployedAccessControlPolicyId"):
                print 'Deployed Access Control Policy ID:', value
            #----------------------------------------
            elif prefix.endswith("networkInventory_Ident"):
                print 'Network Inventory ID:', value
            #----------------------------------------
            elif prefix == "devices":
                if value is not None:
                    print 'Device "',devices,'" with ID:', value
                    devices+=1
            #----------------------------------------
            elif prefix.endswith("networkInterfaces"):
                if event == 'start_array' or event ==  'start_map':
                    print ' '*len(prefix.split('.'))+'--- Network Interfaces Information ---'
            #----------------------------------------
            elif prefix.endswith("networkInterfaces.item.name"):
                if value is not None:
                    print ' '*len(prefix.split('.'))+'Interface Name:', value
            #----------------------------------------
            elif prefix.endswith("mediaInterface"):
                if event == 'start_array' or event ==  'start_map':
                    print ' '*len(prefix.split('.'))+'Media Interface Information'
            #----------------------------------------
            elif prefix.endswith("mediaInterface.macAddress"):
                if event == 'start_array' or event ==  'start_map':
                    print ' '*len(prefix.split('.'))+'MAC Address Information'
            #----------------------------------------
            elif prefix.endswith("mediaInterface.macAddress.macAddress"):
                if value is not None:
                    print ' '*len(prefix.split('.'))+'MAC Address:', value
            #----------------------------------------
            elif prefix.endswith("mediaInterface.macAddress.vendor"):
                if value is not None:
                    print ' '*len(prefix.split('.'))+'MAC Address Vendor:', value
            #----------------------------------------
            elif prefix.endswith("mediaInterface.vlan_Ident"):
                if value is not None:
                    print ' '*len(prefix.split('.'))+'VLAN Ident:', value
            #----------------------------------------
            elif prefix.endswith("mediaInterface.link_encap"):
                if value is not None:
                    print ' '*len(prefix.split('.'))+'Link Encapsulation:', value
            #----------------------------------------
            elif prefix.endswith("iPInterface"):
                if event == 'start_array' or event ==  'start_map':
                    print ' '*len(prefix.split('.'))+'IP Interface Information'
            #----------------------------------------
            elif prefix.endswith("iPInterface.dnsSuffix"):
                if value is not None:
                    print ' '*len(prefix.split('.'))+'DNS Suffix:', value
            #----------------------------------------
            elif prefix.endswith("iPInterface.description"):
                if value is not None:
                    print ' '*len(prefix.split('.'))+'Description:', value
            #----------------------------------------
            elif prefix.endswith("iPInterface.ipAddresses"):
                if event == 'start_array' or event ==  'start_map':
                    print ' '*len(prefix.split('.'))+'IP Interface Addresses Information'
            #----------------------------------------
            elif prefix.endswith("iPInterface.ipAddresses.item"):
                continue
            #----------------------------------------
            elif prefix.endswith("iPInterface.ipAddresses.item.address"):
                if value is not None:
                    print ' '*len(prefix.split('.'))+'Address:', value
            #----------------------------------------
            elif prefix.endswith("iPInterface.ipAddresses.item.iPPorts"):
                if event == 'start_array' or event ==  'start_map':
                    print ' '*len(prefix.split('.'))+'IP Ports Information'
            #----------------------------------------
            elif prefix.endswith("iPInterface.ipAddresses.item.iPPorts.item"):
                continue
            #----------------------------------------
            elif prefix.endswith("iPInterface.ipAddresses.item.iPPorts.item.number"):
                if value is not None:
                    print ' '*len(prefix.split('.'))+'Port Number:', value
            #----------------------------------------
            elif prefix.endswith("iPInterface.ipAddresses.item.iPPorts.item.service"):
                if event == 'start_array' or event ==  'start_map':
                    print ' '*len(prefix.split('.'))+'Service Port Information'
            #----------------------------------------
            elif prefix.endswith("iPInterface.ipAddresses.item.iPPorts.item.service.namePID"):
                if value is not None:
                    print ' '*len(prefix.split('.'))+'Name PID:', value
            #----------------------------------------
            elif prefix.endswith("iPInterface.ipAddresses.item.iPPorts.item.service.name"):
                if value is not None:
                    print ' '*len(prefix.split('.'))+'Service Name:', value
            #----------------------------------------
            elif prefix.endswith("patches"):
                if event == 'start_array' or event ==  'start_map':
                    print ' '*len(prefix.split('.'))+'Patches Information'
            #----------------------------------------
            elif prefix.endswith("patches.item"):
                continue
            #----------------------------------------
            elif prefix.endswith("patches.item.severity"):
                if value is not None:
                    print ' '*len(prefix.split('.'))+'Severity:', value
            #----------------------------------------
            elif prefix.endswith("patches.item.title"):
                if value is not None:
                    print ' '*len(prefix.split('.'))+'Patches Title:', value
            #----------------------------------------
            elif prefix.endswith("patches.item.url"):
                if value is not None:
                    print ' '*len(prefix.split('.'))+'Patch URL:', value
            #----------------------------------------
            elif prefix.endswith("patches.item.date"):
                if value is not None:
                    print ' '*len(prefix.split('.'))+'Date:', value
            #----------------------------------------
            elif prefix.endswith("patches.item.reference"):
                if value is not None:
                    print ' '*len(prefix.split('.'))+'Reference:', value
            #----------------------------------------
            elif prefix.endswith("patches.item.fileUrl"):
                if value is not None:
                    print ' '*len(prefix.split('.'))+'File URL:', value
            #----------------------------------------
            elif prefix.endswith("patches.item.fileName"):
                if value is not None:
                    print ' '*len(prefix.split('.'))+'File Name:', value
            #----------------------------------------
            elif prefix.endswith("patches.item.installParameter"):
                if value is not None:
                    print ' '*len(prefix.split('.'))+'Install Parameter:', value
            #----------------------------------------
            elif prefix.endswith("patches.item.installed"):
                if value is not None:
                    print ' '*len(prefix.split('.'))+'The Patch is Installed?:', value
            #----------------------------------------
            elif prefix.endswith("patches.item.isDeployable"):
                if value is not None:
                    print ' '*len(prefix.split('.'))+'The Patch is deployable?:', value
            #----------------------------------------
            elif prefix.endswith("patches.item.fileDigest"):
                if value is not None:
                    print ' '*len(prefix.split('.'))+'File Digest:', value
            #----------------------------------------
            elif prefix.endswith("patches.item.isUninstallable"):
                if value is not None:
                    print ' '*len(prefix.split('.'))+'The Patch is Uninstallable:', value
            #----------------------------------------
            elif prefix.endswith("patches.item.uninstallCommand"):
                if value is not None:
                    print ' '*len(prefix.split('.'))+'Uninstall Command:', value
            #----------------------------------------
            elif prefix.endswith("iPInterface.ipAddresses.item.iPPorts.item.service.runningState"):
                if value is not None:
                    print ' '*len(prefix.split('.'))+'Service Running State:', value
            #----------------------------------------
            elif prefix.endswith("iPInterface.ipAddresses.item.iPPorts.item.service.description"):
                if value is not None:
                    print ' '*len(prefix.split('.'))+'Service Description:', value
            #----------------------------------------
            elif prefix.endswith("iPInterface.ipAddresses.item.iPPorts.item.service.type"):
                if value is not None:
                    print ' '*len(prefix.split('.'))+'Service Type:', value
            #----------------------------------------
            elif prefix.endswith("iPInterface.ipAddresses.item.iPPorts.item.service.ipPortId"):
                if value is not None:
                    print ' '*len(prefix.split('.'))+'Service Port ID:', value
            #----------------------------------------
            elif prefix.endswith("user"):
                if event == 'start_array' or event ==  'start_map':
                    print ' '*len(prefix.split('.'))+'Users Information'
            #----------------------------------------
            elif prefix.endswith("user.item"):
                continue
            #----------------------------------------
            elif prefix.endswith("user.item.role"):
                if value is not None:
                    print ' '*len(prefix.split('.'))+'User Role:', value
            #----------------------------------------
            elif prefix.endswith("user.item.name"):
                if value is not None:
                    print ' '*len(prefix.split('.'))+'User name:', value
            #----------------------------------------
            elif prefix.endswith("user.item.fullName"):
                if value is not None:
                    print ' '*len(prefix.split('.'))+'User Full Name:', value
            #----------------------------------------
            elif prefix.endswith("user.item.group"):
                if value is not None:
                    print ' '*len(prefix.split('.'))+'User Group:', value
            #----------------------------------------
            elif prefix.endswith("iPInterface.ipAddresses.item.iPPorts.item.transportProtocol"):
                if value is not None:
                    print ' '*len(prefix.split('.'))+'IP Port Transport Protocol:', value
            #----------------------------------------
            elif prefix.endswith("iPInterface.ipAddresses.item.iPPorts.item.description"):
                if value is not None:
                    print ' '*len(prefix.split('.'))+'IP Port Description:', value
            #----------------------------------------
            elif prefix.endswith("iPInterface.ipAddresses.item.iPPorts.item.ipPortId"):
                if value is not None:
                    print ' '*len(prefix.split('.'))+'IP Port ID:', value
            #----------------------------------------
            elif prefix.endswith("iPInterface.ipAddresses.item.iPPorts.item.state"):
                if value is not None:
                    print ' '*len(prefix.split('.'))+'IP Port State:', value
            #----------------------------------------
            elif prefix.endswith("iPInterface.ipAddresses.item.version"):
                if value is not None:
                    print ' '*len(prefix.split('.'))+'IP Address version:', value
            #----------------------------------------
            elif prefix.endswith("iPInterface.ipAddresses.item.subnet_mask"):
                if value is not None:
                    print ' '*len(prefix.split('.'))+'IP Address Subnet Mask:', value
            #----------------------------------------
            elif prefix.endswith("iPInterface.defaultGatewayAddress"):
                if value is not None:
                    print ' '*len(prefix.split('.'))+'IP Interface Default Gateway Address:', value
            #----------------------------------------
            elif prefix.endswith("location"):
                if event == 'start_array' or event ==  'start_map':
                    print ' '*len(prefix.split('.'))+'Device Location Information:', value
            #----------------------------------------
            elif prefix.endswith("location.name"):
                if value is not None:
                    print ' '*len(prefix.split('.'))+'Device Location Name:', value
            #----------------------------------------
            elif prefix.endswith("location.position"):
                continue
            #----------------------------------------
            elif prefix.endswith("location.position.x"):
                if value is not None:
                    print ' '*len(prefix.split('.'))+'Position in X axis:', value
            #----------------------------------------
            elif prefix.endswith("location.position.y"):
                if value is not None:
                    print ' '*len(prefix.split('.'))+'Position in Y axis:', value
            #----------------------------------------
            elif prefix.endswith("location.position.z"):
                if value is not None:
                    print ' '*len(prefix.split('.'))+'Position in Z axis:', value
            #----------------------------------------
            elif prefix.endswith("location.position.type"):
                if value is not None:
                    print ' '*len(prefix.split('.'))+'Position Type:', value
            #----------------------------------------
            elif prefix.endswith("hostName"):
                if value is not None:
                    print ' '*len(prefix.split('.'))+'Device hostname:', value
            #----------------------------------------
            elif prefix.endswith("node_Ident"):
                if value is not None:
                    print ' '*len(prefix.split('.'))+'Network Node ID:', value
            #----------------------------------------
            elif prefix.endswith("routingTable"):
                if event == 'start_array' or event ==  'start_map':
                    print ' '*len(prefix.split('.'))+'Routing Table Information'
            #----------------------------------------
            elif prefix.endswith("routingTable.item"):
                continue
            #----------------------------------------
            elif prefix.endswith("routingTable.item.iface"):
                if event == 'start_array' or event ==  'start_map':
                    print ' '*len(prefix.split('.'))+'Routing Table Interface Information'
            #----------------------------------------
            elif prefix.endswith("routingTable.item.iface.name"):
                if value is not None:
                    print ' '*len(prefix.split('.'))+'Interface Name:', value
            #----------------------------------------
            elif prefix.endswith("routingTable.item.ref"):
                if value is not None:
                    print ' '*len(prefix.split('.'))+'Reference:', value
            #----------------------------------------
            elif prefix.endswith("routingTable.item.metric"):
                if value is not None:
                    print ' '*len(prefix.split('.'))+'Route Metric:', value
            #----------------------------------------
            elif prefix.endswith("routingTable.item.use"):
                if value is not None:
                    print ' '*len(prefix.split('.'))+'Route Use:', value
            #----------------------------------------
            elif prefix.endswith("routingTable.item.destination"):
                if value is not None:
                    print ' '*len(prefix.split('.'))+'Route Destination:', value
            #----------------------------------------
            elif prefix.endswith("routingTable.item.flags"):
                if value is not None:
                    print ' '*len(prefix.split('.'))+'Route Flags:', value
            #----------------------------------------
            elif prefix.endswith("routingTable.item.gateway"):
                if value is not None:
                    print ' '*len(prefix.split('.'))+'Route Gateway:', value
            #----------------------------------------
            elif prefix.endswith("routingTable.item.mask"):
                if value is not None:
                    print ' '*len(prefix.split('.'))+'Route Network Mask:', value
            #----------------------------------------
            elif prefix.endswith("type"):
                if value is not None:
                    print ' '*len(prefix.split('.'))+'Device Type:', value
            #----------------------------------------
            elif prefix.endswith("firmware"):
                if event == 'start_array' or event ==  'start_map':
                    print ' '*len(prefix.split('.'))+'Firmware Information'
            #----------------------------------------
            elif prefix.endswith("firmware.item"):
                continue
            #----------------------------------------
            elif prefix.endswith("firmware.item.name"):
                if value is not None:
                    print ' '*len(prefix.split('.'))+'Firmware Name:', value
            #----------------------------------------
            elif prefix.endswith("firmware.item.version"):
                if value is not None:
                    print ' '*len(prefix.split('.'))+'Firmware Version:', value
            #----------------------------------------
            elif prefix.endswith("operatingSystem"):
                if event == 'start_array' or event ==  'start_map':
                    print ' '*len(prefix.split('.'))+'Operating System Information'
            #----------------------------------------
            elif prefix.endswith("operatingSystem.item"):
                continue
            #----------------------------------------
            elif prefix.endswith("operatingSystem.item.application"):
                if event == 'start_array' or event ==  'start_map':
                    print ' '*len(prefix.split('.'))+'Application Information'
            #----------------------------------------
            elif prefix.endswith("operatingSystem.item.application.item"):
                continue
            #----------------------------------------
            elif prefix.endswith("operatingSystem.item.application.item.namePID"):
                if value is not None:
                    print ' '*len(prefix.split('.'))+'Application PID:', value
            #----------------------------------------
            elif prefix.endswith("operatingSystem.item.application.item.name"):
                if value is not None:
                    print ' '*len(prefix.split('.'))+'Application Name:', value
            #----------------------------------------
            elif prefix.endswith("operatingSystem.item.driver"):
                if event == 'start_array' or event ==  'start_map':
                    print ' '*len(prefix.split('.'))+'Driver Information'
            #----------------------------------------
            elif prefix.endswith("operatingSystem.item.driver.item"):
                continue
            #----------------------------------------
            elif prefix.endswith("operatingSystem.item.driver.item.date"):
                if value is not None:
                    print ' '*len(prefix.split('.'))+'Driver Date:', value
            #----------------------------------------
            elif prefix.endswith("operatingSystem.item.driver.item.provider"):
                if value is not None:
                    print ' '*len(prefix.split('.'))+'Driver Provider:', value
            #----------------------------------------
            elif prefix.endswith("operatingSystem.item.driver.item.version"):
                if value is not None:
                    print ' '*len(prefix.split('.'))+'Driver Version:', value
            #----------------------------------------
            elif prefix.endswith("operatingSystem.item.osClass"):
                if value is not None:
                    print ' '*len(prefix.split('.'))+'Operating System Class:', value
            #----------------------------------------
            elif prefix.endswith("operatingSystem.item.osClass.generation"):
                if value is not None:
                    print ' '*len(prefix.split('.'))+'Generation:', value
            #----------------------------------------
            elif prefix.endswith("operatingSystem.item.osClass.vendor"):
                if value is not None:
                    print ' '*len(prefix.split('.'))+'Vendor:', value
            #----------------------------------------
            elif prefix.endswith("operatingSystem.item.osClass.family"):
                if value is not None:
                    print ' '*len(prefix.split('.'))+'OS Family:', value
            #----------------------------------------
            elif prefix.endswith("operatingSystem.item.osClass.type"):
                 if value is not None:
                    print ' '*len(prefix.split('.'))+'OS Type:', value
            #----------------------------------------
            elif prefix.endswith("vulnerabilityList"):
                if event == 'start_array' or event ==  'start_map':
                    print ' '*len(prefix.split('.'))+'Vulnerability List Information'
            #----------------------------------------
            elif prefix.endswith("vulnerabilityList.vulnerability_Ident"):
                continue
            #----------------------------------------
            elif prefix.endswith("vulnerabilityList.vulnerability_Ident.item"):
                 if value is not None:
                    print ' '*len(prefix.split('.'))+'Vulnerability ID:', value
            #----------------------------------------
            elif prefix.endswith("snapshot_Ident"):
                print 'Snapshot ID:', value

def traverseJSON3(path):
    print 'Parsing info from Network Inventory File:',path

    with open(path) as json_file:
        parser = ijson.parse(json_file)
        devices=1
        notomado=0
        list_notomado=[]
        list_prefix = []
        for prefix, event, value in parser:
            if prefix == "monitored_System_Ident":
                print 'Monitored System ID:', value
            elif prefix == "deployedAccessControlPolicyId":
                print 'Deployed Access Control Policy ID:', value
            elif prefix == "networkInventory_Ident":
                print 'Network Inventory ID:', value
            elif prefix == "snapshot_Ident":
                print 'Snapshot ID:', value
            elif prefix == "devices":
                if value is not None:
                    print 'Device "',devices,'" with ID:', value
                    devices+=1
            elif prefix.endswith(".networkInterfaces"):
                print "Device Network Interfaces Informations", value
                #print prefix
                #print event
            elif prefix.endswith('.networkInterfaces.item.name'):
                print "Network Interface Name", value
                print prefix

            elif (prefix, event) == ('earth', 'map_key'):
                #stream.write('<%s>' % value)
                continent = value
            elif prefix.endswith('.name'):
                #tream.write('<object name="%s"/>' % value)
                #print "'dd"
                continue
            elif (prefix, event) == ('earth.%s', 'end_map'):
                #stream.write('</%s>' % continent)
                #print "fff"
                continue
            else:
                notomado+=1
                list_notomado.append(prefix)

        print "Cuantos no tomados:", notomado
        print list_notomado


def traverseJSON2(path):
    print 'Parsing info from Network Inventory File:',path

    with open(path) as json_file:
        list_prefix = []
        """parser = ijson.parse(json_file)
        for prefix, event, value in parser:
            if prefix not in list_prefix:
                print prefix
                list_prefix.append(prefix)"""

        for line in json_file:
            if line not in list_prefix:
                print '#----------------------------------------\nelif prefix.endswith("'+line.replace('\n',"'):\n    continue")
                list_prefix.append(line)


def main(argv):
    jsonInstanceURI = ''
    jsonSchemaURI = getRealPath()+"NetworkInventoryJsonSchema.txt"
    networkInventoryActionSchema = None
    networkInventoryJSONInstance = None
    try:
        opts, args = getopt.getopt(argv,"hi:",["ifile="])
    except getopt.GetoptError:
        print 'Usage: '
        print 'networkInventoryParser.py -i <inputJSON>'
        sys.exit(2)

    if not opts:
        print 'Usage: '
        print 'networkInventoryParserParser.py -i <inputJSON>'
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print 'networkInventoryParserParser.py -i <inputJSON>'
            sys.exit()
        elif opt in ("-i", "--ifile"):
            jsonInstanceURI = arg

    """if jsonInstanceURI != "":
        networkInventoryActionSchema = validateJSONSchema(jsonSchemaURI)
        if networkInventoryActionSchema != False:
            networkInventoryJSONInstance = validateInputJSON(jsonInstanceURI, networkInventoryActionSchema)
            if networkInventoryJSONInstance != False:
                traverseJSONInstance(networkInventoryJSONInstance)
            else:
                exit(1)
        else:
            exit(1)
    else:
        exit(1)"""

    if jsonInstanceURI != "":
        traverseJSON(jsonInstanceURI)
    else:
        exit(1)

if __name__ == "__main__":
    main(sys.argv[1:])

