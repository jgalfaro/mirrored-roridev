__author__ = 'ender_al'

try:
    import wx
except ImportError:
    raise ImportError,"wxPython module is required"

from wx import xrc

class AIVView:
    def __init__(self, parent, app):
        self.Organization = app.Organization
        self.app = app
        self.Dialog = self.app.res.LoadDialog(parent, 'AIVEditor')
        self.Dialog.SetSize((630,420))


        #Load the widgets that will load the list of all the equipments registered in the engine
        #and the list of equipments belonging to the organization
        self.equipmentList = xrc.XRCCTRL(self.Dialog, 'aiv_listequ')
        self.equipmentOrganizationList = xrc.XRCCTRL(self.Dialog, 'aiv_listequ-org')

        #Load the widgets related to the AIV

        self.aiv_equipmentCost = xrc.XRCCTRL(self.Dialog, 'aiv_textec')
        self.aiv_serviceCost = xrc.XRCCTRL(self.Dialog, 'aiv_textsc')
        self.aiv_personnelCost = xrc.XRCCTRL(self.Dialog, 'aiv_textpc')
        self.aiv_resellCost = xrc.XRCCTRL(self.Dialog, 'aiv_textrv')
        self.aiv_otherCost = xrc.XRCCTRL(self.Dialog, 'aiv_textoc')
        self.aiv_total = xrc.XRCCTRL(self.Dialog, 'aiv_texttotal')

        #Load the Check Button used to know if the total value will be given
        self.aiv_totalok = xrc.XRCCTRL(self.Dialog, 'aiv_checktotal')

        #Load the Button
        btnAssignEquipment = xrc.XRCCTRL(self.Dialog, 'aiv_btnok')
        btnAssignEquipment.SetLabel('Assign')



    def Show(self):
        self.Dialog.Show()

    def loadListOfEquipments(self,list):

        self.equipmentList.SetSingleStyle(wx.LC_REPORT, True)
        self.equipmentList.InsertColumn(0, 'Name', format=wx.LIST_FORMAT_LEFT, width=-1)
        self.equipmentList.InsertColumn(1, 'Type', format=wx.LIST_FORMAT_LEFT, width=-1)

        #Load into the widget the values of the list
        index = 0
        for equipment in list:
            item = self.equipmentList.InsertStringItem(index, str(equipment[1]))
            self.equipmentList.SetItemData(item, equipment[0])

            self.equipmentList.SetStringItem(index, 1, str(equipment[2]))
            index+=1

        self.equipmentList.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        self.equipmentList.SetColumnWidth(1, wx.LIST_AUTOSIZE)



    def loadListOfOrganizationEquipments(self,list):

        self.equipmentOrganizationList.SetSingleStyle(wx.LC_REPORT, True)
        self.equipmentOrganizationList.InsertColumn(0, 'Name', format=wx.LIST_FORMAT_LEFT, width=-1)
        self.equipmentOrganizationList.InsertColumn(1, 'Type', format=wx.LIST_FORMAT_LEFT, width=-1)

        #Load into the widget the values of the list
        index = 0
        for equipment in list:
            item = self.equipmentOrganizationList.InsertStringItem(index, str(equipment[1]))
            self.equipmentOrganizationList.SetItemData(item, equipment[0])

            self.equipmentOrganizationList.SetStringItem(index, 1, str(equipment[2]))
            index+=1

        self.equipmentOrganizationList.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        self.equipmentOrganizationList.SetColumnWidth(1, wx.LIST_AUTOSIZE)



    def getItemCount(self, widget):
        return widget.GetSelectedItemCount()



    def getIDItemSelected(self,widget):
        itemIndex = widget.GetFirstSelected()
        return widget.GetItemData(itemIndex)


    def getSetItemsSelected(self, widget):
        id_list = []
        flag = True
        itemIndex = widget.GetFirstSelected()
        id_list.append(widget.GetItemData(itemIndex))
        while flag:
            itemIndex = widget.GetNextSelected(itemIndex)
            if itemIndex != -1:
                id_list.append(widget.GetItemData(itemIndex))
            else:
                flag = False

        return id_list




    def loadAIVValues(self, values):
        #The 'values' variable has the following form
        """idAIV, EC, SC, PC, RV, OC, Total, FK_Organization, FK_Equipment"""
        if values[1] == values[2] == values[3] == values[4] == values[5] == 0.00:
            #wx.MessageBox("Es un total")
            self.aiv_totalok.SetValue(True)
            self.changeTextsInputs(True)
            self.aiv_total.SetValue(str(values[6]))
        else:
            self.changeTextsInputs(False)
            self.aiv_totalok.SetValue(False)
            #wx.MessageBox("Costos individuales")
            self.aiv_equipmentCost.SetValue(str(values[1]))
            self.aiv_serviceCost.SetValue(str(values[2]))
            self.aiv_personnelCost.SetValue(str(values[3]))
            self.aiv_resellCost.SetValue(str(values[4]))
            self.aiv_otherCost.SetValue(str(values[5]))
            self.aiv_total.SetValue(str(values[6]))



    def changeTextsInputs(self, is_total):
        #Disable the single costs text fields and enable the 'Total' text field if the user will provide the total cost
        # otherwise disable the 'Total' text fields and enable the single costs text field
        if is_total:

            self.clearTextsInputs()
            #Disable the cost text fields
            self.aiv_equipmentCost.Disable()
            self.aiv_serviceCost.Disable()
            self.aiv_personnelCost.Disable()
            self.aiv_resellCost.Disable()
            self.aiv_otherCost.Disable()
            #Enable the Total text field
            self.aiv_total.Enable()
        else:
            self.aiv_equipmentCost.Enable()
            self.aiv_serviceCost.Enable()
            self.aiv_personnelCost.Enable()
            self.aiv_resellCost.Enable()
            self.aiv_otherCost.Enable()
            self.aiv_total.Disable()
        return

    def clearTextsInputs(self):
        #Clear the Values in the cost text fields
        self.aiv_equipmentCost.SetValue("0.00")
        self.aiv_serviceCost.SetValue("0.00")
        self.aiv_personnelCost.SetValue("0.00")
        self.aiv_resellCost.SetValue("0.00")
        self.aiv_otherCost.SetValue("0.00")
        self.aiv_total.SetValue("0.00")

