__author__ = 'ender_al'
# -*- coding: utf-8 *-*

import wx
import subprocess as sub
from wx import xrc
from lxml import etree
from view.GraphRepresentationView import GraphRepresentationView
from model.Organization import Organization
from model.Incident import Incident
from model.Countermeasure import Countermeasure
from model.RORICal import RORICal
import os

class GraphRepresentationController:

    def __init__(self, app):
       self.app = app
       self.Graph_view = GraphRepresentationView(app)

       #Menu Item
       self.Graph_view.frame.Bind(wx.EVT_MENU, self.onExit, id=xrc.XRCID('Graph_exit'))

       #Bind a method for each time an Organization is selected in the view
       self.Graph_view.frame.Bind(wx.EVT_CHOICE, self.onSelectedOrganization, self.Graph_view.orgListChoice)
       #List to save the ID of the organizations, it will be used to know which organization is selected from the
       #list of choices in the view
       self.orgListID = []

       #Bind a method for each time an Incident or Countermeasure is selected in the view
       self.Graph_view.frame.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onSelectedIncident, self.Graph_view.incidentList)
       #self.Graph_view.frame.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onSelectedCountermeasure, self.Graph_view.countermeasureList)
       self.Graph_view.frame.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onSelectedCountermeasure, self.Graph_view.countermeasureList)
       self.Graph_view.frame.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onSelectedCountermeasure, self.Graph_view.countermeasureList)
       #self.Graph_view.frame.Bind(wx.EVT_LIST_ITEM_FOCUSED, self.onSelectedCountermeasure, self.Graph_view.countermeasureList)

       #Bind a method when the Graphic button is pressed
       self.Graph_view.frame.Bind(wx.EVT_BUTTON, self.onGraphicalRepresentation, self.Graph_view.graphicButton)

       #Instance of model
       self.Organization = Organization()
       self.Incident = Incident()
       self.Countermeasure = Countermeasure()
       self.RORICal = RORICal()

       #IDs of the elements required to start the calculation of the RORI index
       self.idOrg = 0
       self.idInc = 0

       #List of incidents and countermeasures
       self.organization_name = []
       self.org_incidents = []
       self.inc_countermeasures = []

       #Load list of Organizations
       self.loadListOfOrganizations_controller()
       self.Graph_view.show()

    #------------------------------------------------------------------------------------------------------------
    def loadListOfOrganizations_controller(self):
        (error, values) = self.Organization.read_all()
        #List to be passed to the view with the names of the organizations
        orgNames = []
        if error:
            msg= "Error reading the list of Organizations: \n" + values
            wx.MessageBox(msg)
        else:
            #
            for organization in values:
                self.orgListID.append(organization[0])
                orgNames.append(organization[1])

            self.Graph_view.loadListOfOrganizations(orgNames)
            self.organization_name = orgNames

    #------------------------------------------------------------------------------------------------------------
    def onSelectedOrganization(self, evt):
        # Each time an Organization is selected in the view, grab its ID from the orgListID and display the list of
        # Incidents assigned to the Organization in the view
        self.idOrg = self.orgListID.__getitem__(self.Graph_view.orgListChoice.GetCurrentSelection())
        self.RORICal.idOrg = self.idOrg

        # Fetch the Incidents assigned to the Organization
        (error, values) = self.RORICal.readOrgInc()
        if error:
            msg= "Error reading the list of Incidents of the Organizations: \n" + values
            wx.MessageBox(msg)
        else:
            if not values:
                msg= "The Organization does not have any Incidents assigned"
                wx.MessageBox(msg)
                #If there are not Incidents assigned, clear the lists and disable the calculation button
                self.Graph_view.incidentList.ClearAll()
                self.Graph_view.countermeasureList.ClearAll()
                self.Graph_view.graphicButton.Disable()
            else:
                self.Graph_view.loadListOfIncidents(values)
                self.org_incidents = values

        return

    #------------------------------------------------------------------------------------------------------------
    def onSelectedIncident(self, evt):
        # Each time an Incident is selected in the view, grab its ID and display the list of
        # Countermeasures assigned

        count = self.Graph_view.getItemCount(self.Graph_view.incidentList)
        if (count > 1):
            wx.MessageBox("The graphical representation can be performed just on one Incident at a time!")
            self.Graph_view.countermeasureList.ClearAll()
        elif (count == 1):
            # Load information about countermeasures assigned to the selected Incident
            self.idInc = self.Graph_view.getIDItemSelected(self.Graph_view.incidentList)
            self.RORICal.idInc = self.idInc
            # Fetch the Countermeasures assigned to the Incident
            (error, values) = self.RORICal.readIncCou()
            if error:
                msg= "Error reading the list of Countermeasures assigned to the Incident: \n" + values
                wx.MessageBox(msg)
            else:
                if not values:
                    msg= "The Incident does not have any Countermeasures assigned"
                    wx.MessageBox(msg)
                    #If there are not Countermeasures assigned, clear the lists and disable the calculation button
                    self.Graph_view.countermeasureList.ClearAll()
                else:
                    # Enable the Calculation Button
                    self.Graph_view.loadListOfCountermeasures(values)
                    self.inc_countermeasures = values

        return

    #------------------------------------------------------------------------------------------------------------
    def onSelectedCountermeasure(self, evt):
        # Each time the elements in the countermeasure list have been selected/deselected enable/disable the graph button

        count = self.Graph_view.getItemCount(self.Graph_view.countermeasureList)
        if (count > 0):
            self.Graph_view.graphicButton.Enable()
        else:
            self.Graph_view.graphicButton.Disable()
        return

    #------------------------------------------------------------------------------------------------------------
    def onGraphicalRepresentation(self, evt):
        #Create the XML output file and passed it to the Attack Volume module
        xml_root = etree.Element("RORI_AV")
        xml_root.append(etree.Element("MODE", graphic="true"))
        #Create the Organization XML element
        xml_root.append(etree.Element("ORGANISATION", name="SCADA"))
        #Create the Incident XML element
        xml_inc = etree.SubElement(xml_root,'INCIDENTS')
        # ID incident selected
        id_inc = self.Graph_view.getIDItemSelected(self.Graph_view.incidentList)

        # ID countermeasures selected
        id_cou = self.Graph_view.getItemsSelected(self.Graph_view.countermeasureList)

        #Create the COUNTERMEASURES XML element
        xml_cou = etree.SubElement(xml_root,'COUNTERMEASURES')
        # Create countermeasure Sub-elements
        #<countermeasure id="C5" name="Enable Multiple Monitoring Indication" COV=""/>
        lcou = []
        for cou in self.inc_countermeasures:
            if cou[0] in id_cou:
                lcou.append(cou[4])
                etree.SubElement(xml_cou, "countermeasure", {'id':cou[4], 'name':cou[1], 'COV':""})

        # Create incident Sub-element
        for inc in self.org_incidents:
            if id_inc == inc[0]:
                etree.SubElement(xml_inc, "incident", {'id':inc[2], 'name':inc[1], 'id_countermeasure': (', '.join(lcou))})

        #Append the new XML elements to the XML root
        xml_root.append(xml_inc)
        xml_root.append(xml_cou)

        #Append the root to a XML document
        xml_doc = etree.ElementTree(xml_root)

        #print etree.tostring(xml_doc, pretty_print=True)

        # Write the output XML document
        #tstamp = datetime.now().__str__().replace(" ","_").replace(":","-").replace(".","-")
        xml_doc.write("./tmp/graphical_request.xml", pretty_print=True)

        #Call AV module
        try:
            #attack_volume = sub.Popen(["more", "./output.xml"], stdout=sub.PIPE,stderr=sub.PIPE)
            #output, errors = attack_volume.communicate()
            #print output
            #print errors
            #return_code = sub.call("more fk")
            #return_code = sub.check_call(["cat", "output.xml"])
            #sub.check_call(['ls' ,'-lh'])
            return_code = sub.call(['attack-volume', '-i', './tmp/graphical_request.xml', '-o', './tmp/graphical_output.xml'])
            if return_code != 0:
                wx.MessageBox('Error running the Attack Volume module')
                return
        except OSError as e:
            print "Error executing command: "
            print e
        return

    #------------------------------------------------------------------------------------------------------------
    def onGraphicalRepresentation_REAL(self, evt):
        #Create the XML output file and passed it to the Attack Volume module
        xml_root = etree.Element("RORI_AV")
        xml_root.append(etree.Element("MODE", graphic="true"))
        #Create the Organization XML element
        xml_root.append(etree.Element("ORGANISATION", name=self.organization_name.__getitem__(self.Graph_view.orgListChoice.GetCurrentSelection())))
        #Create the Incident XML element
        xml_inc = etree.SubElement(xml_root,'INCIDENTS')
        # ID incident selected
        id_inc = self.Graph_view.getIDItemSelected(self.Graph_view.incidentList)

        # ID countermeasures selected
        id_cou = self.Graph_view.getItemsSelected(self.Graph_view.countermeasureList)

        #Create the COUNTERMEASURES XML element
        xml_cou = etree.SubElement(xml_root,'COUNTERMEASURES')
        # Create countermeasure Sub-elements
        #<countermeasure id="C5" name="Enable Multiple Monitoring Indication" COV=""/>
        lcou = []
        for cou in self.inc_countermeasures:
            if cou[0] in id_cou:
                lcou.append(cou[4])
                etree.SubElement(xml_cou, "countermeasure", {'id':cou[4], 'name':cou[1], 'COV':""})

        # Create incident Sub-element
        for inc in self.org_incidents:
            if id_inc == inc[0]:
                etree.SubElement(xml_inc, "incident", {'id':inc[2], 'name':inc[1], 'id_countermeasure': (', '.join(lcou))})

        #Append the new XML elements to the XML root
        xml_root.append(xml_inc)
        xml_root.append(xml_cou)

        #Append the root to a XML document
        xml_doc = etree.ElementTree(xml_root)

        #print etree.tostring(xml_doc, pretty_print=True)

        # Write the output XML document
        #tstamp = datetime.now().__str__().replace(" ","_").replace(":","-").replace(".","-")
        xml_doc.write("./tmp/graphical_request.xml", pretty_print=True)

        #Call AV module
        try:
            #attack_volume = sub.Popen(["more", "./output.xml"], stdout=sub.PIPE,stderr=sub.PIPE)
            #output, errors = attack_volume.communicate()
            #print output
            #print errors
            #return_code = sub.call("more fk")
            #return_code = sub.check_call(["cat", "output.xml"])
            #sub.check_call(['ls' ,'-lh'])
            return_code = sub.call(['attack-volume', '-i', './tmp/graphical_request.xml', '-o', './tmp/graphical_output.xml'])
            if return_code != 0:
                wx.MessageBox('Error running the Attack Volume module')
                return
        except OSError as e:
            print "Error executing command: "
            print e
        return


    #------------------------------------------------------------------------------------------------------------
    def onExit(self, evt):
       self.Graph_view.frame.Destroy()
