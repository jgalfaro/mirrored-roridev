__author__ = 'ender_al'

import wx
from wx import xrc
from wx.lib.pubsub import Publisher

from view.AEVView import AEVView
from model.AEV import AEV
from model.Equipment import Equipment
from decimal import *
from lib.utils import checkStringInputType

class AEVController:
    def __init__(self, app, parent):
        self.app = app
        self.OrganizationView = parent
        self.aev_view = AEVView(self.OrganizationView.frame, self.app)

        #Load the buttons of the view
        self.btnOK = xrc.XRCCTRL(self.aev_view.Dialog, 'aev_btnok')
        btnCancel = xrc.XRCCTRL(self.aev_view.Dialog, 'aev_btncancel')

        # Call the onCancel method when window close
        self.aev_view.Dialog.Bind(wx.EVT_CLOSE, self.onCancel)

        #Bind events to the buttons
        self.aev_view.Dialog.Bind(wx.EVT_BUTTON, self.onAssignEquipmentAEV, self.btnOK)
        self.aev_view.Dialog.Bind(wx.EVT_BUTTON, self.onCancel, btnCancel)

        #Bind Events to the items in the ToolBar
        self.aev_view.Dialog.Bind(wx.EVT_TOOL, self.onEdit, id=xrc.XRCID('aev_tooledit'))
        self.aev_view.Dialog.Bind(wx.EVT_TOOL, self.onDelete, id=xrc.XRCID('aev_tooldelete'))

        #Load the widget of check box to know if the total value will be given directly
        self.aev_totalok = xrc.XRCCTRL(self.aev_view.Dialog, 'aev_checktotal')

        #Bind events to the checkbox
        self.aev_view.Dialog.Bind(wx.EVT_CHECKBOX, self.onCheckBox, self.aev_totalok)

        #Bind event when an item of the list of equipments is selected
        self.aev_view.Dialog.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onEquipmentSelected, self.aev_view.equipmentList)
        self.aev_view.Dialog.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onEdit, self.aev_view.equipmentOrganizationList)

        #Subscribe to the messages given by the model. In case of any change, the list of elements will be updated
        Publisher.subscribe(self.aevModified, 'aev_created')
        Publisher.subscribe(self.aevModified, 'aev_updated')
        Publisher.subscribe(self.aevModified, 'aev_deleted')

        #ID of the Organization selected
        self.idOrganization = self.OrganizationView.getIDItemSelected()

        #Instance of the AEV, Equipment model
        self.aev = AEV()
        self.equipment = Equipment()


        #Filters
        self.GUIequipments = []
        self.GUIorg_equipments = []
        self.txtFilter1 = xrc.XRCCTRL(self.aev_view.Dialog, 'AEV_txtfilter1')
        self.btnFilter1 = xrc.XRCCTRL(self.aev_view.Dialog, 'AEV_btnfilter1')
        self.txtFilter2 = xrc.XRCCTRL(self.aev_view.Dialog, 'AEV_txtfilter2')
        self.btnFilter2 = xrc.XRCCTRL(self.aev_view.Dialog, 'AEV_btnfilter2')
        self.aev_view.Dialog.Bind(wx.EVT_BUTTON, self.onFilter1, self.btnFilter1)
        self.aev_view.Dialog.Bind(wx.EVT_TEXT_ENTER, self.onFilter1, self.txtFilter1)
        self.aev_view.Dialog.Bind(wx.EVT_BUTTON, self.onFilter2, self.btnFilter2)
        self.aev_view.Dialog.Bind(wx.EVT_TEXT_ENTER, self.onFilter2, self.txtFilter2)


        #Load the list of equipments in the view
        self.loadListOfEquipments()
        self.loadListOfEquipmentsOrganization()

        #Display the view
        self.aev_view.Show()

    #------------------------------------------------------------------------------------------------------------
    def aevModified(self, msg):
        self.loadListOfEquipments()
        self.loadListOfEquipmentsOrganization()

    #------------------------------------------------------------------------------------------------------------
    def loadListOfEquipments(self):
        (equ_error, equ_list) = self.equipment.read_all()
        if equ_error:
            msg= "Error reading the list of PEPs: \n" + equ_list
            wx.MessageBox(msg)
            self.onCancel(True)
        else:
            #Exclude from the list of equipments those already assigned to the Organization
            list_equ = []
            self.txtFilter1.SetValue("")

            self.aev.FK_Organization = self.idOrganization
            (aev_error, aev_list) = self.aev.read_by_organization()
            if aev_error:
                msg= "Error reading the list of PEPs assigned to the Organization: \n" + aev_list
                wx.MessageBox(msg)
                self.onCancel(True)
            else:
                equ_org = [] #list to save the IDs of the Equipments assigned to the Organization
                for aev_entry in aev_list:
                    # self.aev.read_by_organization() returns a sequence of tuples, each tuple has the following form:
                    # (idAEV, EC, SC, PC, RV, OC, NEquipments, Total, FK_Organization, FK_Equipment)
                    equ_org.append(aev_entry[9]) #Append to the list the Equipment ID

                for equ_entry in equ_list:
                    # self.equipment.read_all() returns a sequence of tuples, each tuple has the following form:
                    # (idEquipment, Name, Type)
                    if not equ_entry[0] in equ_org: # Don't include the equipments already assigned
                        list_equ.append(equ_entry)

            self.GUIequipments = list_equ
            self.aev_view.loadListOfEquipments(list_equ)

    #------------------------------------------------------------------------------------------------------------
    def loadListOfEquipmentsOrganization(self):

        list_equ = []
        self.aev.FK_Organization = self.idOrganization
        (error, list) = self.aev.read_by_organization()
        if error:
            msg= "Error reading the list of PEPs of the Organization: \n" + list
            wx.MessageBox(msg)
            self.onCancel(True)
        else:
            self.txtFilter2.SetValue("")
            for aev_entry in list:
                #Grab the FK_Equipment value from the query row
                self.equipment.id = aev_entry[9]
                (error, value) = self.equipment.read()

                if error:
                    msg= "Error reading the values of the PEP: \n" + value
                    wx.MessageBox(msg)
                    self.onCancel(True)
                else:
                    if value:
                        list_equ.append(value[0])

        self.GUIorg_equipments = list_equ
        self.aev_view.loadListOfOrganizationEquipments(list_equ)
        return

    #-------------------------------------------------------------------------------------------------------
    def onFilter1(self,event):
        new_list = []
        string = self.txtFilter1.GetValue().upper()
        if string !="":
            for item in self.GUIequipments:
                for sub_item in item:
                    if type(sub_item) is str:
                        if any([string in sub_item.upper()]):
                            new_list.append(item)
                            break
            self.aev_view.loadListOfEquipments(new_list)
        else:
            self.aev_view.loadListOfEquipments(self.GUIequipments)
    #-------------------------------------------------------------------------------------------------------
    def onFilter2(self,event):
        new_list = []
        string = self.txtFilter2.GetValue().upper()
        if string !="":
            for item in self.GUIorg_equipments:
                for sub_item in item:
                    if type(sub_item) is str:
                        if any([string in sub_item.upper()]):
                            new_list.append(item)
                            break
            self.aev_view.loadListOfOrganizationEquipments(new_list)
        else:
            self.aev_view.loadListOfOrganizationEquipments(self.GUIorg_equipments)
    #------------------------------------------------------------------------------------------------------------
    def onCheckBox(self,evt):
        if self.aev_totalok.IsChecked():
            self.aev_view.changeTextsInputs(True)
        else:
            self.aev_view.changeTextsInputs(False)
        return

    #------------------------------------------------------------------------------------------------------------
    def onEquipmentSelected(self,evt):
        #Change to the default value the OK button
        self.aev_view.Dialog.Bind(wx.EVT_BUTTON, self.onAssignEquipmentAEV, self.btnOK)
        self.btnOK.SetLabel('Assign')
        self.aev_totalok.Enable()
        self.btnOK.Enable()
        #Reset the text fields
        self.aev_view.clearTextsInputs()
        #And establish the default input mode (Total value will not be given)
        self.aev_view.changeTextsInputs(False)
        self.aev_totalok.SetValue(False)
        self.aev_view.aev_totalok.Enable()

        return

    #------------------------------------------------------------------------------------------------------------
    def onAssignEquipmentAEV(self, evt):
        #Check if there is selected any item in the equipment list
        count = self.aev_view.getItemCount(self.aev_view.equipmentList)
        if (count == 0):
            wx.MessageBox("Please select a PEP to assign an AEV value!")
        elif (count > 1):
            wx.MessageBox("Please select just one PEP to assign an AEV value!")
        else:
            #Grab the id of the Equipment selected
            idEquipment = self.aev_view.getIDItemSelected(self.aev_view.equipmentList)
            self.aev.FK_Equipment = idEquipment
            self.aev.FK_Organization = self.idOrganization

            #Check if the Equipment is already assigned to the Organization
            (error, value) = self.aev.read_by_equipment_organization()

            if error:
                msg= "Error reading the AEV value of the PEP: \n" + value
                wx.MessageBox(msg)
                self.onCancel(True)
            else:
                if not value:
                    if self.getAEVValuesFromView():
                        self.aev.create()
                else:
                    wx.MessageBox("PEP already assigned to the Organization!")
        #Send a message to update the view of list of organizations
        Publisher.sendMessage("organization_updated", None)
        return

    #------------------------------------------------------------------------------------------------------------
    def getAEVValuesFromView(self):

        #Check if the user will give the Total Value or each single cost
        if self.aev_totalok.GetValue():

            self.aev.EC = self.aev.SC = self.aev.PC = self.aev.RV = self.aev.OC = 0
            self.aev.NEquipments = self.aev_view.aev_number.GetValue()
            self.aev.Total = self.aev_view.aev_total.GetValue()
            #Check if the values provided have a valid format
            #------------------------------------
            list_val = [self.aev.Total, self.aev.NEquipments]
            if not checkStringInputType(list_val,"decimal"):
                wx.MessageBox("One of the inputs has an incorrect format")
                return False
            else:
                self.aev.NEquipments = Decimal(self.aev.NEquipments)
                self.aev.Total = Decimal(self.aev.Total) * self.aev.NEquipments

        else:
            self.aev.EC = 0 if self.aev_view.aev_equipmentCost.GetValue() == "" else self.aev_view.aev_equipmentCost.GetValue()
            self.aev.SC = 0 if self.aev_view.aev_serviceCost.GetValue() == "" else self.aev_view.aev_serviceCost.GetValue()
            self.aev.PC = 0 if self.aev_view.aev_personnelCost.GetValue() == "" else self.aev_view.aev_personnelCost.GetValue()
            self.aev.RV = 0 if self.aev_view.aev_resellCost.GetValue() == "" else self.aev_view.aev_resellCost.GetValue()
            self.aev.OC = 0 if self.aev_view.aev_otherCost.GetValue() == "" else self.aev_view.aev_otherCost.GetValue()
            self.aev.NEquipments = 0 if self.aev_view.aev_number.GetValue() == "" else self.aev_view.aev_number.GetValue()

            #Check if the values provided have a valid format
            #------------------------------------
            list_val = [self.aev.EC, self.aev.SC, self.aev.PC, self.aev.RV, self.aev.OC, self.aev.NEquipments]
            if not checkStringInputType(list_val,"decimal"):
                wx.MessageBox("One of the inputs has an incorrect format")
                return False
            else:
                self.aev.EC = Decimal(self.aev.EC)
                self.aev.SC = Decimal(self.aev.SC)
                self.aev.PC = Decimal(self.aev.PC)
                self.aev.RV = Decimal(self.aev.RV)
                self.aev.OC = Decimal(self.aev.OC)
                self.aev.NEquipments = Decimal(self.aev.NEquipments)

            #AEV Calculation Following the given in Gustavo's Thesis
            self.aev.Total = ((self.aev.EC + self.aev.PC + self.aev.SC + self.aev.OC) - self.aev.RV) * self.aev.NEquipments

        if self.aev.NEquipments == 0:
            wx.MessageBox("The number of PEPs could not be zero!!")
            return False

        if self.aev.Total == 0:
            wx.MessageBox("The value of AEV could not be zero!!")
            return False

        return True


    #------------------------------------------------------------------------------------------------------------
    def onEdit(self, evt):
        #Check if any item in the list of equipments of the current organization is selected
        count = self.aev_view.getItemCount(self.aev_view.equipmentOrganizationList)

        if (count == 0):
            wx.MessageBox("Please select a PEP of the Organization to edit the AEV value!")
        elif (count > 1) and not isinstance(evt,wx.ListEvent):
            wx.MessageBox("Please select just one PEP of the Organization to edit the AEV value!")
        else:
            #Grab the id of the Equipment selected
            idEquipment = self.aev_view.getIDItemSelected(self.aev_view.equipmentOrganizationList)
            self.aev.FK_Equipment = idEquipment
            self.aev.FK_Organization = self.idOrganization
            #Read the AEV values of the Equipment
            (error, value) = self.aev.read_by_equipment_organization()
            if error:
                msg= "Error reading the AEV value of the PEP: \n" + value
                wx.MessageBox(msg)
                self.onCancel(True)
            else:
                self.aev_view.loadAEVValues(value[0])
                self.aev.id = value[0][0]

                #When Called from the Edit button,change the behaviour of the OK button
                # to call the method that will load the changes to the database
                # If is called from the list just show the results and disable the button
                self.btnOK.SetLabel('Edit AEV')
                if isinstance(evt, wx.ListEvent):
                    self.btnOK.Disable()
                    self.aev_view.aev_equipmentCost.Disable()
                    self.aev_view.aev_serviceCost.Disable()
                    self.aev_view.aev_personnelCost.Disable()
                    self.aev_view.aev_resellCost.Disable()
                    self.aev_view.aev_otherCost.Disable()
                    self.aev_view.aev_number.Disable()
                    self.aev_view.aev_total.Disable()
                    self.aev_view.aev_totalok.Disable()
                else:
                    self.btnOK.Enable()
                    self.aev_view.aev_totalok.Enable()
                    self.aev_view.Dialog.Bind(wx.EVT_BUTTON, self.editAEVValues, self.btnOK)

        #Send a message to update the view of list of organizations
        Publisher.sendMessage("organization_updated", None)
        return

    #------------------------------------------------------------------------------------------------------------
    def editAEVValues(self, evt):

        #Load the Values from the View
        if self.getAEVValuesFromView():
            (error, values) = self.aev.update()
            if error:
                msg= "Error editing the AEV values: \n" + values
                wx.MessageBox(msg)
                self.onCancel(True)
        return

    #------------------------------------------------------------------------------------------------------------
    def onDelete(self, evt):
        count = self.aev_view.getItemCount(self.aev_view.equipmentOrganizationList)
        if (count == 0):
            wx.MessageBox("Please select a PEP of the Organization to be deleted!")
        else:
            msg = "Proceed to delete "+str(count)+" elements?"
            del_confirm = wx.MessageDialog(None, msg, 'Delete Confirmation', wx.YES_NO | wx.ICON_QUESTION)
            if del_confirm.ShowModal() == wx.ID_NO:
                return

            item_list = self.aev_view.getSetItemsSelected(self.aev_view.equipmentOrganizationList)

            for id_equipment in item_list:
                self.aev.FK_Equipment = id_equipment
                self.aev.FK_Organization = self.idOrganization
                (error, values) = self.aev.delete_by_organization_equipment()
                if error:
                    msg= "There was an error deleting the PEP of the organization: \n" + values
                    wx.MessageBox(msg)
                    self.onCancel(True)
                self.aev_view.clearTextsInputs()

        #Send a message to update the view of list of organizations
        Publisher.sendMessage("organization_updated", None)
        return

    #------------------------------------------------------------------------------------------------------------
    def onCancel(self,evt):
        self.aev_view.Dialog.Destroy()
