__author__ = 'ender_al'

try:
    import wx
except ImportError:
    raise ImportError,"wxPython module is required"

from wx import xrc

class AEVView:
    def __init__(self, parent, app):
        self.Organization = app.Organization
        self.app = app
        self.Dialog = self.app.res.LoadDialog(parent, 'AEVEditor')
        self.Dialog.SetSize((680,580))


        #Load the widgets that will load the list of all the equipments registered in the engine
        #and the list of equipments belonging to the organization
        self.equipmentList = xrc.XRCCTRL(self.Dialog, 'aev_listequ')
        self.equipmentOrganizationList = xrc.XRCCTRL(self.Dialog, 'aev_listequ-org')

        #Load the widgets related to the AEV

        self.aev_equipmentCost = xrc.XRCCTRL(self.Dialog, 'aev_textec')
        self.aev_serviceCost = xrc.XRCCTRL(self.Dialog, 'aev_textsc')
        self.aev_personnelCost = xrc.XRCCTRL(self.Dialog, 'aev_textpc')
        self.aev_resellCost = xrc.XRCCTRL(self.Dialog, 'aev_textrv')
        self.aev_otherCost = xrc.XRCCTRL(self.Dialog, 'aev_textoc')
        self.aev_number = xrc.XRCCTRL(self.Dialog, 'aev_textnumber')
        self.aev_total = xrc.XRCCTRL(self.Dialog, 'aev_texttotal')

        #Load the Check Button used to know if the total value will be given
        self.aev_totalok = xrc.XRCCTRL(self.Dialog, 'aev_checktotal')

        #Load the Button
        btnAssignEquipment = xrc.XRCCTRL(self.Dialog, 'aev_btnok')
        btnAssignEquipment.SetLabel('Assign')

    #-------------------------------------------------------------------------------------------------------
    def Show(self):
        self.Dialog.Show()

    #-------------------------------------------------------------------------------------------------------
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

    #-------------------------------------------------------------------------------------------------------
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

    #-------------------------------------------------------------------------------------------------------
    def getItemCount(self, widget):
        return widget.GetSelectedItemCount()

    #-------------------------------------------------------------------------------------------------------
    def getIDItemSelected(self,widget):
        itemIndex = widget.GetFirstSelected()
        return widget.GetItemData(itemIndex)

    #-------------------------------------------------------------------------------------------------------
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

    #-------------------------------------------------------------------------------------------------------
    def loadAEVValues(self, values):
        #The 'values' variable has the following form
        """idAEV, EC, SC, PC, RV, OC, NEquipments, Total, FK_Organization, FK_Equipment"""
        if values[1] == values[2] == values[3] == values[4] == values[5] == 0.00:
            #wx.MessageBox("Es un total")
            self.aev_totalok.SetValue(True)
            self.changeTextsInputs(True)
            #Display the "Number of Equipments" value from the values array
            self.aev_number.SetValue(str(values[6]))
            #Display the "Total" AVE from the values array
            self.aev_total.SetValue(str(values[7]/values[6]))
        else:
            self.changeTextsInputs(False)
            self.aev_totalok.SetValue(False)
            #wx.MessageBox("Costos individuales")
            self.aev_equipmentCost.SetValue(str(values[1]))
            self.aev_serviceCost.SetValue(str(values[2]))
            self.aev_personnelCost.SetValue(str(values[3]))
            self.aev_resellCost.SetValue(str(values[4]))
            self.aev_otherCost.SetValue(str(values[5]))
            self.aev_number.SetValue(str(values[6]))
            self.aev_total.SetValue(str(values[7]))

    #-------------------------------------------------------------------------------------------------------
    def changeTextsInputs(self, is_total):
        #Disable the single costs text fields and enable the 'Total' text field if the user will provide the total cost
        # otherwise disable the 'Total' text fields and enable the single costs text field
        if is_total:
            self.clearTextsInputs()
            #Disable the cost text fields
            self.aev_equipmentCost.Disable()
            self.aev_serviceCost.Disable()
            self.aev_personnelCost.Disable()
            self.aev_resellCost.Disable()
            self.aev_otherCost.Disable()
            #Enable the Total and Number of Equipments text fields
            self.aev_number.Enable()
            self.aev_total.Enable()
        else:
            self.aev_equipmentCost.Enable()
            self.aev_serviceCost.Enable()
            self.aev_personnelCost.Enable()
            self.aev_resellCost.Enable()
            self.aev_otherCost.Enable()
            self.aev_number.Enable()
            self.aev_total.Disable()
        return

    #-------------------------------------------------------------------------------------------------------
    def clearTextsInputs(self):
        #Clear the Values in the cost text fields
        self.aev_equipmentCost.SetValue("0.00")
        self.aev_serviceCost.SetValue("0.00")
        self.aev_personnelCost.SetValue("0.00")
        self.aev_resellCost.SetValue("0.00")
        self.aev_otherCost.SetValue("0.00")
        self.aev_number.SetValue("0")
        self.aev_total.SetValue("0.00")

