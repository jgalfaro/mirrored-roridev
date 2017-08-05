__author__ = 'ender_al'

import wx
from wx import xrc
from wx.lib.pubsub import Publisher

from view.ALEView import ALEView
from model.ALE import ALE
from model.Incident import Incident
from decimal import *
from lib.utils import checkStringInputType

class ALEController:
    def __init__(self, app, parent):
        self.app = app
        self.OrganizationView = parent
        self.ale_view = ALEView(self.OrganizationView.frame, self.app)

        #Load the buttons of the view
        self.btnOK = xrc.XRCCTRL(self.ale_view.Dialog, 'ale_btnok')
        btnCancel = xrc.XRCCTRL(self.ale_view.Dialog, 'ale_btncancel')

        # Call the onCancel method when window close
        self.ale_view.Dialog.Bind(wx.EVT_CLOSE, self.onCancel)

        #Bind events to the buttons
        self.ale_view.Dialog.Bind(wx.EVT_BUTTON, self.onAssignIncidentALE, self.btnOK)
        self.ale_view.Dialog.Bind(wx.EVT_BUTTON, self.onCancel, btnCancel)

        #Bind Events to the items in the ToolBar
        self.ale_view.Dialog.Bind(wx.EVT_TOOL, self.onEdit, id=xrc.XRCID('ale_tooledit'))
        self.ale_view.Dialog.Bind(wx.EVT_TOOL, self.onDelete, id=xrc.XRCID('ale_tooldelete'))

        #Load the widget of check box to know if the total value will be given directly
        self.ale_totalok = xrc.XRCCTRL(self.ale_view.Dialog, 'ale_checktotal')

        #Bind events to the checkbox
        self.ale_view.Dialog.Bind(wx.EVT_CHECKBOX, self.onCheckBox, self.ale_totalok)

        #Bind event when an item of the list of incidents is selected
        self.ale_view.Dialog.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onIncidentSelected, self.ale_view.incidentList)
        self.ale_view.Dialog.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onEdit, self.ale_view.incidentOrganizationList)

        #Subscribe to the messages given by the model. In case of any change, the list of elements will be updated
        Publisher.subscribe(self.aleModified, 'ale_created')
        Publisher.subscribe(self.aleModified, 'ale_updated')
        Publisher.subscribe(self.aleModified, 'ale_deleted')

        #ID of the Organization selected
        self.idOrganization = self.OrganizationView.getIDItemSelected()

        #Instance of the ALE, Incident model
        self.ale = ALE()
        self.incident = Incident()

        #Filters
        self.GUIincidents = []
        self.GUIorg_incidents = []
        self.txtFilter1 = xrc.XRCCTRL(self.ale_view.Dialog, 'ALE_txtfilter1')
        self.btnFilter1 = xrc.XRCCTRL(self.ale_view.Dialog, 'ALE_btnfilter1')
        self.txtFilter2 = xrc.XRCCTRL(self.ale_view.Dialog, 'ALE_txtfilter2')
        self.btnFilter2 = xrc.XRCCTRL(self.ale_view.Dialog, 'ALE_btnfilter2')
        self.ale_view.Dialog.Bind(wx.EVT_BUTTON, self.onFilter1, self.btnFilter1)
        self.ale_view.Dialog.Bind(wx.EVT_TEXT_ENTER, self.onFilter1, self.txtFilter1)
        self.ale_view.Dialog.Bind(wx.EVT_BUTTON, self.onFilter2, self.btnFilter2)
        self.ale_view.Dialog.Bind(wx.EVT_TEXT_ENTER, self.onFilter2, self.txtFilter2)

        #Load the list of incidents in the view
        self.loadListOfIncidents()
        self.loadListOfIncidentsOrganization()

        #Display the view
        self.ale_view.Show()

    #------------------------------------------------------------------------------------------------------------
    def aleModified(self, mensaje):
        self.loadListOfIncidents()
        self.loadListOfIncidentsOrganization()

    #------------------------------------------------------------------------------------------------------------
    def loadListOfIncidents(self):
        (inc_error, inc_list) = self.incident.read_all()
        if inc_error:
            msg= "Error reading the list of Detrimental Events: \n" + inc_list
            wx.MessageBox(msg)
            self.onCancel(True)
        else:
            #Exclude from the list of incidents those already assigned to the Organization
            list_inc = []

            self.ale.FK_Organization = self.idOrganization
            (ale_error, ale_list) = self.ale.read_by_organization()
            if ale_error:
                msg= "Error reading the list of Detrimental Events assigned to the Organization: \n" + ale_list
                wx.MessageBox(msg)
                self.onCancel(True)
            else:
                inc_org = [] #list to save the IDs of the Incidents assigned to the Organization
                for ale_entry in ale_list:
                    # self.ale.read_by_organization() returns a sequence of tuples, each tuple has the following form:
                    # (idALE, LA, LD, LR, LP, LREC, LRPC, OL, CI, ARO, Total, FK_Incident, FK_Organization)
                    inc_org.append(ale_entry[11]) #Append to the list the Incident ID

                for inc_entry in inc_list:
                    # self.incident.read_all() returns a sequence of tuples, each tuple has the following form:
                    # (idIncident, Name, Description, Risk_Level)
                    if not inc_entry[0] in inc_org: # Don't include the incidents already assigned
                        list_inc.append(inc_entry)

            self.GUIincidents = list_inc
            self.ale_view.loadListOfIncidents(list_inc)

    #------------------------------------------------------------------------------------------------------------
    def loadListOfIncidentsOrganization(self):

        list_inc = []
        self.ale.FK_Organization = self.idOrganization
        (error, list) = self.ale.read_by_organization()
        if error:
            msg= "Error reading the list of Detrimental Events of the Organization: \n" + list
            wx.MessageBox(msg)
            self.ale_view.Dialog.Close()
        else:
            for ale_entry in list:
                #Grab the FK_Incident value from the query row
                #each returned tuple has the following values (idALE, LA, LD, LR, LP, LREC, LRPC, OL, CI, ARO, Total, FK_Incident, FK_Organization)
                self.incident.id = ale_entry[11]
                (error, value) = self.incident.read()

                if error:
                    msg= "Error reading the values of the Detrimental Event: \n" + value
                    wx.MessageBox(msg)
                    self.ale_view.Dialog.Close()
                else:
                    if value:
                        list_inc.append(value[0])
        self.GUIorg_incidents = list_inc
        self.ale_view.loadListOfOrganizationIncidents(list_inc)
        return

    #-------------------------------------------------------------------------------------------------------
    def onFilter1(self,event):
        new_list = []
        string = self.txtFilter1.GetValue().upper()
        if string !="":
            for item in self.GUIincidents:
                for sub_item in item:
                    if type(sub_item) is str:
                        if any([string in sub_item.upper()]):
                            new_list.append(item)
                            break
            self.ale_view.loadListOfIncidents(new_list)
        else:
            self.ale_view.loadListOfIncidents(self.GUIincidents)
    #-------------------------------------------------------------------------------------------------------
    def onFilter2(self,event):
        new_list = []
        string = self.txtFilter2.GetValue().upper()
        if string !="":
            for item in self.GUIorg_incidents:
                for sub_item in item:
                    if type(sub_item) is str:
                        if any([string in sub_item.upper()]):
                            new_list.append(item)
                            break
            self.ale_view.loadListOfOrganizationIncidents(new_list)
        else:
            self.ale_view.loadListOfOrganizationIncidents(self.GUIorg_incidents)
    #------------------------------------------------------------------------------------------------------------
    def onCheckBox(self,evt):
        if self.ale_totalok.IsChecked():
            self.ale_view.changeTextsInputs(True)
        else:
            self.ale_view.changeTextsInputs(False)
        return

    #------------------------------------------------------------------------------------------------------------
    def onIncidentSelected(self,evt):
        #Change to the default value the OK button
        self.ale_view.Dialog.Bind(wx.EVT_BUTTON, self.onAssignIncidentALE, self.btnOK)
        self.btnOK.SetLabel('Assign')
        self.btnOK.Enable()
        #Reset the text fields
        self.ale_view.clearTextsInputs()
        #And establish the default input mode (Total value will not be given)
        self.ale_view.changeTextsInputs(False)
        self.ale_totalok.SetValue(False)
        self.ale_view.ale_totalok.Enable()

        return

    #------------------------------------------------------------------------------------------------------------
    def onAssignIncidentALE(self, evt):
        #Check if there is selected any item in the incident list
        count = self.ale_view.getItemCount(self.ale_view.incidentList)
        if (count == 0):
            wx.MessageBox("Please select a Detrimental Event to assign an ALE value!")
        elif (count > 1):
            wx.MessageBox("Please select just one Detrimental Event to assign an ALE value!")
        else:
            #Grab the id of the Incident selected
            idIncident = self.ale_view.getIDItemSelected(self.ale_view.incidentList)
            self.ale.FK_Incident = idIncident
            self.ale.FK_Organization = self.idOrganization

            #Check if the Incident is already assigned to the Organization
            (error, value) = self.ale.read_by_incident_organization()

            if error:
                msg= "Error reading the ALE value of the Detrimental Event: \n" + value
                wx.MessageBox(msg)
                self.ale_view.Dialog.Close()
            else:
                if not value:
                    if self.getALEValuesFromView():
                        self.ale.create()
                else:
                    wx.MessageBox("Detrimental Event already assigned to the Organization!")
        #Send a message to update the view of list of organizations
        Publisher.sendMessage("organization_updated", None)
        return

    #------------------------------------------------------------------------------------------------------------
    def getALEValuesFromView(self):

        #Check if the user will give the Total value of ALE or each single cost and loss
        if self.ale_totalok.GetValue():
            # idALE, LA, LD, LR, LP, LREC, LRPC, OL, CI, ARO, Total, FK_Incident, FK_Organization
            self.ale.LA = self.ale.LD = self.ale.LR = self.ale.LP = self.ale.LREC = self.ale.LRPC = self.ale.OL = self.ale.CI = 0
            self.ale.ARO = self.ale_view.ale_ARO.GetValue()
            self.ale.Total = self.ale_view.ale_total.GetValue()
            #Check if the values provided have a valid format
            #------------------------------------
            list_val = [self.ale.Total, self.ale.ARO]
            if not checkStringInputType(list_val,"decimal"):
                wx.MessageBox("One of the inputs has an incorrect format")
                return False
            else:
                self.ale.ARO = Decimal(self.ale.ARO)
                self.ale.Total = Decimal(self.ale.Total) * self.ale.ARO

        else:
            self.ale.LA = 0 if self.ale_view.ale_lossAssets.GetValue() == "" else self.ale_view.ale_lossAssets.GetValue()
            self.ale.LD = 0 if self.ale_view.ale_lossData.GetValue() == "" else self.ale_view.ale_lossData.GetValue()
            self.ale.LR = 0 if self.ale_view.ale_lossReputation.GetValue() == "" else self.ale_view.ale_lossReputation.GetValue()
            self.ale.LP = 0 if self.ale_view.ale_legalProcedures.GetValue() == "" else self.ale_view.ale_legalProcedures.GetValue()
            self.ale.LREC = 0 if self.ale_view.ale_LREC.GetValue() == "" else self.ale_view.ale_LREC.GetValue()
            self.ale.LRPC = 0 if self.ale_view.ale_LRPC.GetValue() == "" else self.ale_view.ale_LRPC.GetValue()
            self.ale.OL = 0 if self.ale_view.ale_OL.GetValue() == "" else self.ale_view.ale_OL.GetValue()
            self.ale.CI = 0 if self.ale_view.ale_CI.GetValue() == "" else self.ale_view.ale_CI.GetValue()
            self.ale.ARO = 0 if self.ale_view.ale_ARO.GetValue() == "" else self.ale_view.ale_ARO.GetValue()

            #Check if the values provided have a valid format
            #------------------------------------
            list_val = [self.ale.LA,self.ale.LD,self.ale.LR,self.ale.LP,self.ale.LREC,self.ale.LRPC,self.ale.OL, self.ale.CI, self.ale.ARO]
            if not checkStringInputType(list_val,"decimal"):
                wx.MessageBox("One of the inputs has an incorrect format")
                return False
            else:
                self.ale.LA = Decimal(self.ale.LA)
                self.ale.LD = Decimal(self.ale.LD)
                self.ale.LR = Decimal(self.ale.LR)
                self.ale.LP = Decimal(self.ale.LP)
                self.ale.LREC = Decimal(self.ale.LREC)
                self.ale.LRPC = Decimal(self.ale.LRPC)
                self.ale.OL = Decimal(self.ale.OL)
                self.ale.CI = Decimal(self.ale.CI)
                self.ale.ARO = Decimal(self.ale.ARO)

            #ALE Calculation Following the given in Gustavo's Thesis
            self.ale.Total = ((self.ale.LA + self.ale.LD + self.ale.LR + self.ale.LP + self.ale.LREC + self.ale.LRPC + self.ale.OL) - self.ale.CI) * self.ale.ARO

        if self.ale.ARO == 0:
            wx.MessageBox("The Annual Rate of Occurrence cannot be zero!!")
            return False

        if self.ale.Total == 0:
            wx.MessageBox("The value of ALE could not be zero!!")
            return False

        return True

    #------------------------------------------------------------------------------------------------------------
    def onEdit(self, evt):
        #Check if any item in the list of incidents of the current organization is selected
        count = self.ale_view.getItemCount(self.ale_view.incidentOrganizationList)

        if (count == 0):
            wx.MessageBox("Please select a Detrimental Event of the Organization to edit the ALE value!")
        elif (count > 1) and not isinstance(evt,wx.ListEvent):
            wx.MessageBox("Please select just one Detrimental Event of the Organization to edit the ALE value!")
        else:
            #Grab the id of the Incident selected
            idIncident = self.ale_view.getIDItemSelected(self.ale_view.incidentOrganizationList)
            self.ale.FK_Incident = idIncident
            self.ale.FK_Organization = self.idOrganization
            #Read the ALE values of the Incident
            (error, value) = self.ale.read_by_incident_organization()
            if error:
                msg= "Error reading the ALE value of the Detrimental Event: \n" + value
                wx.MessageBox(msg)
                self.ale_view.Dialog.Close()
            else:
                self.ale_view.loadALEValues(value[0])
                self.ale.id = value[0][0]

                #When Called from the Edit button,change the behaviour of the OK button
                # to call the method that will load the changes to the database
                # If is called from the list just show the results and disable the button
                self.btnOK.SetLabel('Edit ALE')
                if isinstance(evt, wx.ListEvent):

                    self.ale_view.ale_lossAssets.Disable()
                    self.ale_view.ale_lossData.Disable()
                    self.ale_view.ale_lossReputation.Disable()
                    self.ale_view.ale_legalProcedures.Disable()
                    self.ale_view.ale_LREC.Disable()
                    self.ale_view.ale_LRPC.Disable()
                    self.ale_view.ale_OL.Disable()
                    self.ale_view.ale_CI.Disable()
                    self.ale_view.ale_ARO.Disable()
                    self.ale_view.ale_total.Disable()
                    self.ale_view.ale_totalok.Disable()

                    self.btnOK.Disable()
                else:
                    self.btnOK.Enable()
                    self.ale_view.ale_totalok.Enable()
                    self.ale_view.Dialog.Bind(wx.EVT_BUTTON, self.editALEValues, self.btnOK)

        #Send a message to update the view of list of organizations
        Publisher.sendMessage("organization_updated", None)
        return

    #------------------------------------------------------------------------------------------------------------
    def editALEValues(self, evt):

        #Load the Values from the View
        if self.getALEValuesFromView():
            (error, values) = self.ale.update()
            if error:
                msg= "Error editing the ALE values: \n" + values
                wx.MessageBox(msg)
                self.ale_view.Dialog.Close()
        return

    #------------------------------------------------------------------------------------------------------------
    def onDelete(self, evt):
        count = self.ale_view.getItemCount(self.ale_view.incidentOrganizationList)
        if (count == 0):
            wx.MessageBox("Please select a Detrimental Event of the Organization to be deleted!")
        else:
            msg = "Proceed to delete "+str(count)+" elements?"
            del_confirm = wx.MessageDialog(None, msg, 'Delete Confirmation', wx.YES_NO | wx.ICON_QUESTION)
            if del_confirm.ShowModal() == wx.ID_NO:
                return

            item_list = self.ale_view.getSetItemsSelected(self.ale_view.incidentOrganizationList)

            for id_incident in item_list:
                self.ale.FK_Incident = id_incident
                self.ale.FK_Organization = self.idOrganization
                (error, values) = self.ale.delete_by_organization_incident()
                if error:
                    msg= "There was an error deleting the Detrimental Event of the organization: \n" + values
                    wx.MessageBox(msg)
                    self.ale_view.Dialog.Close()
                self.ale_view.clearTextsInputs()

        #Send a message to update the view of list of organizations
        Publisher.sendMessage("organization_updated", None)
        return

    #------------------------------------------------------------------------------------------------------------
    def onCancel(self,evt):
        self.ale_view.Dialog.Destroy()
