__author__ = 'ender_al'

import wx
from wx import xrc
from wx.lib.pubsub import Publisher

from view.AIVView import AIVView
from model.AIV import AIV
from model.Equipment import Equipment
from decimal import *
from lib.utils import checkStringInputType

class AIVController:
    def __init__(self, app, parent):
        self.app = app
        self.OrganizationView = parent
        self.aiv_view = AIVView(self.OrganizationView.frame, self.app)

        #Load the buttons of the view
        self.btnOK = xrc.XRCCTRL(self.aiv_view.Dialog, 'aiv_btnok')
        btnCancel = xrc.XRCCTRL(self.aiv_view.Dialog, 'aiv_btncancel')

        # Call the onCancel method when window close
        self.aiv_view.Dialog.Bind(wx.EVT_CLOSE, self.onCancel)

        #Bind events to the buttons
        self.aiv_view.Dialog.Bind(wx.EVT_BUTTON, self.onAssignEquipmentAIV, self.btnOK)
        self.aiv_view.Dialog.Bind(wx.EVT_BUTTON, self.onCancel, btnCancel)

        #Bind Events to the items in the ToolBar
        self.aiv_view.Dialog.Bind(wx.EVT_TOOL, self.onEdit, id=xrc.XRCID('aiv_tooledit'))
        self.aiv_view.Dialog.Bind(wx.EVT_TOOL, self.onDelete, id=xrc.XRCID('aiv_tooldelete'))

        #Load the widget of check box to know if the total value will be given directly
        self.aiv_totalok = xrc.XRCCTRL(self.aiv_view.Dialog, 'aiv_checktotal')

        #Bind events to the checkbox
        self.aiv_view.Dialog.Bind(wx.EVT_CHECKBOX, self.onCheckBox, self.aiv_totalok)

        #Bind event when an item of the list of equipments is selected
        self.aiv_view.Dialog.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onEquipmentSelected, self.aiv_view.equipmentList)
        self.aiv_view.Dialog.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onEdit, self.aiv_view.equipmentOrganizationList)

        #Subscribe to the messages given by the model. In case of any change, the list of elements will be updated
        Publisher.subscribe(self.aivModified, 'aiv_created')
        Publisher.subscribe(self.aivModified, 'aiv_updated')
        Publisher.subscribe(self.aivModified, 'aiv_deleted')

        #ID of the Organization selected
        self.idOrganization = self.OrganizationView.getIDItemSelected()

        #Instance of the AIV, Equipment model
        self.aiv = AIV()
        self.equipment = Equipment()

        #Load the list of equipments in the view
        self.loadListOfEquipments()
        self.loadListOfEquipmentsOrganization()

        #Display the view
        self.aiv_view.Show()


    def aivModified(self, mensaje):
        self.loadListOfEquipments()
        self.loadListOfEquipmentsOrganization()


    def loadListOfEquipments(self):
        (error, list) = self.equipment.read_all()
        if error:
            msg= "Error reading the list of Equipments: \n" + list
            wx.MessageBox(msg)
            self.onCancel()
        else:
            self.aiv_view.loadListOfEquipments(list)


    def loadListOfEquipmentsOrganization(self):

        list_equ = []
        self.aiv.FK_Organization = self.idOrganization
        (error, list) = self.aiv.read_by_organization()
        if error:
            msg= "Error reading the list of equipments of the Organization: \n" + list
            wx.MessageBox(msg)
            self.onCancel()
        else:
            for aiv_entry in list:
                #Grab the FK_Equipment value from the query row
                self.equipment.id = aiv_entry[8]
                (error, value) = self.equipment.read()

                if error:
                    msg= "Error reading the values of the Equipment: \n" + value
                    wx.MessageBox(msg)
                    self.onCancel()
                else:
                    list_equ.append(value[0])
        self.aiv_view.loadListOfOrganizationEquipments(list_equ)
        return

    def onCheckBox(self,evt):
        if self.aiv_totalok.IsChecked():
            self.aiv_view.changeTextsInputs(True)
        else:
            self.aiv_view.changeTextsInputs(False)
        return

    def onEquipmentSelected(self,evt):
        #Change to the default value the OK button
        self.aiv_view.Dialog.Bind(wx.EVT_BUTTON, self.onAssignEquipmentAIV, self.btnOK)
        self.btnOK.SetLabel('Assign')
        #Reset the text fields
        self.aiv_view.clearTextsInputs()
        #And establish the default input mode (Total value will not be given)
        self.aiv_view.changeTextsInputs(False)
        self.aiv_totalok.SetValue(False)
        return

    def onAssignEquipmentAIV(self, evt):
        #Check if there is selected any item in the equipment list
        count = self.aiv_view.getItemCount(self.aiv_view.equipmentList)
        if (count == 0):
            wx.MessageBox("Please select an Equipment to assign an AIV value!")
        elif (count > 1):
            wx.MessageBox("Please select just one Equipment to assign an AIV value!")
        else:
            #Grab the id of the Equipment selected
            idEquipment = self.aiv_view.getIDItemSelected(self.aiv_view.equipmentList)
            self.aiv.FK_Equipment = idEquipment
            self.aiv.FK_Organization = self.idOrganization

            #Check if the Equipment is already assigned to the Organization
            (error, value) = self.aiv.read_by_equipment_organization()

            if error:
                msg= "Error reading the AIV value of the equipment: \n" + value
                wx.MessageBox(msg)
                self.onCancel()
            else:
                if not value:
                    if self.getAIVValuesFromView():
                        self.aiv.create()
                else:
                    wx.MessageBox("Equipment already assigned to the Organization!")
        return

    def getAIVValuesFromView(self):

        #Check if the user will give the Total Value or each single cost
        if self.aiv_totalok.GetValue():

            self.aiv.EC = self.aiv.SC = self.aiv.PC = self.aiv.RV = self.aiv.OC = 0
            self.aiv.Total = self.aiv_view.aiv_total.GetValue()
            #Check if the values provided have a valid format
            #------------------------------------
            list_val = [self.aiv.Total]
            if not checkStringInputType(list_val,"decimal"):
                wx.MessageBox("One of the inputs has an incorrect format")
                return False
            else:
                self.aiv.Total = Decimal(self.aiv.Total)

        else:
            self.aiv.EC = 0 if self.aiv_view.aiv_equipmentCost.GetValue() == "" else self.aiv_view.aiv_equipmentCost.GetValue()
            self.aiv.SC = 0 if self.aiv_view.aiv_serviceCost.GetValue() == "" else self.aiv_view.aiv_serviceCost.GetValue()
            self.aiv.PC = 0 if self.aiv_view.aiv_personnelCost.GetValue() == "" else self.aiv_view.aiv_personnelCost.GetValue()
            self.aiv.RV = 0 if self.aiv_view.aiv_resellCost.GetValue() == "" else self.aiv_view.aiv_resellCost.GetValue()
            self.aiv.OC = 0 if self.aiv_view.aiv_otherCost.GetValue() == "" else self.aiv_view.aiv_otherCost.GetValue()

            #Check if the values provided have a valid format
            #------------------------------------
            list_val = [self.aiv.EC, self.aiv.SC, self.aiv.PC, self.aiv.RV, self.aiv.OC]
            if not checkStringInputType(list_val,"decimal"):
                wx.MessageBox("One of the inputs has an incorrect format")
                return False
            else:
                self.aiv.EC = Decimal(self.aiv.EC)
                self.aiv.SC = Decimal(self.aiv.SC)
                self.aiv.PC = Decimal(self.aiv.PC)
                self.aiv.RV = Decimal(self.aiv.RV)
                self.aiv.OC = Decimal(self.aiv.OC)

            #AIV Calculation Following the given in Gustavo's Thesis
            self.aiv.Total = (self.aiv.EC + self.aiv.PC + self.aiv.SC + self.aiv.OC) - self.aiv.RV

        if self.aiv.Total == 0:
            wx.MessageBox("The value of AIV could not be zero!!")
            return False

        return True



    def onEdit(self, evt):
        #Check if any item in the list of equipments of the current organization is selected
        count = self.aiv_view.getItemCount(self.aiv_view.equipmentOrganizationList)
        if (count == 0):
            wx.MessageBox("Please select an Equipment of the Organization to edit the AIV value!")
        elif (count > 1):
            wx.MessageBox("Please select just one Equipment of the Organization to edit the AIV value!")
        else:
            #Grab the id of the Equipment selected
            idEquipment = self.aiv_view.getIDItemSelected(self.aiv_view.equipmentOrganizationList)
            self.aiv.FK_Equipment = idEquipment
            self.aiv.FK_Organization = self.idOrganization
            #Read the AIV values of the Equipment
            (error, value) = self.aiv.read_by_equipment_organization()
            if error:
                msg= "Error reading the AIV value of the equipment: \n" + value
                wx.MessageBox(msg)
                self.onCancel()
            else:
                #Change the behaviour of the OK button to call the method that will load the changes to the database
                self.btnOK.SetLabel('Edit AIV')
                self.aiv_view.Dialog.Bind(wx.EVT_BUTTON, self.editAIVValues, self.btnOK)

                self.aiv_view.loadAIVValues(value[0])
                self.aiv.id = value[0][0]
        return

    def editAIVValues(self, evt):

        #Load the Values from the View
        if self.getAIVValuesFromView():
            (error, values) = self.aiv.update()
            if error:
                msg= "Error editing the AIV values: \n" + values
                wx.MessageBox(msg)
                self.onCancel()
        return

    def onDelete(self, evt):
        count = self.aiv_view.getItemCount(self.aiv_view.equipmentOrganizationList)
        if (count == 0):
            wx.MessageBox("Please select an Equipment of the Organization to be deleted!")
        else:
            msg = "Proceed to delete "+str(count)+" elements?"
            del_confirm = wx.MessageDialog(None, msg, 'Delete Confirmation', wx.YES_NO | wx.ICON_QUESTION)
            if del_confirm.ShowModal() == wx.ID_NO:
                return

            item_list = self.aiv_view.getSetItemsSelected(self.aiv_view.equipmentOrganizationList)

            for id_equipment in item_list:
                self.aiv.FK_Equipment = id_equipment
                self.aiv.FK_Organization = self.idOrganization
                (error, values) = self.aiv.delete_by_organization_equipment()
                if error:
                    msg= "There was an error deleting the equipment of the organization: \n" + values
                    wx.MessageBox(msg)
                    self.onCancel()
                self.aiv_view.clearTextsInputs()
        return

    def onCancel(self,evt):
        self.aiv_view.Dialog.Destroy()