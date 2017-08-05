__author__ = 'ender_al'

try:
    import wx
except ImportError:
    raise ImportError,"wxPython module is required"

from wx import xrc

class ALEView:
    def __init__(self, parent, app):
        self.Organization = app.Organization
        self.app = app
        self.Dialog = self.app.res.LoadDialog(parent, 'ALEEditor')
        self.Dialog.SetSize((680,580))


        #Load the widgets that will load the list of all the incidents registered in the engine
        #and the list of incidents belonging to the organization
        self.incidentList = xrc.XRCCTRL(self.Dialog, 'ale_listinc')
        self.incidentOrganizationList = xrc.XRCCTRL(self.Dialog, 'ale_listinc-org')

        #Load the widgets related to the ALE

        self.ale_lossAssets = xrc.XRCCTRL(self.Dialog, 'ale_textla')
        self.ale_lossData = xrc.XRCCTRL(self.Dialog, 'ale_textld')
        self.ale_lossReputation = xrc.XRCCTRL(self.Dialog, 'ale_textlr')
        self.ale_legalProcedures = xrc.XRCCTRL(self.Dialog, 'ale_textlp')
        self.ale_LREC = xrc.XRCCTRL(self.Dialog, 'ale_textlrec')
        self.ale_LRPC = xrc.XRCCTRL(self.Dialog, 'ale_textlrpc')
        self.ale_OL = xrc.XRCCTRL(self.Dialog, 'ale_textol')
        self.ale_CI = xrc.XRCCTRL(self.Dialog, 'ale_textci')
        self.ale_ARO = xrc.XRCCTRL(self.Dialog, 'ale_textaro')
        self.ale_total = xrc.XRCCTRL(self.Dialog, 'ale_texttotal')

        #Load the Check Button used to know if the total value will be given
        self.ale_totalok = xrc.XRCCTRL(self.Dialog, 'ale_checktotal')

        #Load the Button
        btnAssignIncident = xrc.XRCCTRL(self.Dialog, 'ale_btnok')
        btnAssignIncident.SetLabel('Assign')

    #-------------------------------------------------------------------------------------------------------
    def Show(self):
        self.Dialog.Show()

    #-------------------------------------------------------------------------------------------------------
    def loadListOfIncidents(self,list):

        self.incidentList.SetSingleStyle(wx.LC_REPORT, True)
        self.incidentList.InsertColumn(0, 'Name', format=wx.LIST_FORMAT_LEFT,width=-1)
        self.incidentList.InsertColumn(1, 'Description', format=wx.LIST_FORMAT_LEFT, width=-1)
        self.incidentList.InsertColumn(2, 'Risk Level', format=wx.LIST_FORMAT_LEFT, width=-1)

        #Load list of Incidents
        index = 0
        for incident in list:
            item = self.incidentList.InsertStringItem(index, str(incident[1]))
            self.incidentList.SetItemData(item, incident[0])
            self.incidentList.SetStringItem(index, 1, str(incident[2]))

            if incident[3] == 'L':
                self.incidentList.SetStringItem(index, 2, "Low")
            elif incident[3] == 'M':
                self.incidentList.SetStringItem(index, 2, "Medium")
            elif incident[3] == 'H':
                self.incidentList.SetStringItem(index, 2, "High")
            index+=1


        self.incidentList.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        self.incidentList.SetColumnWidth(1, wx.LIST_AUTOSIZE_USEHEADER)
        self.incidentList.SetColumnWidth(2, wx.LIST_AUTOSIZE_USEHEADER)

    #-------------------------------------------------------------------------------------------------------
    def loadListOfOrganizationIncidents(self,list):

        self.incidentOrganizationList.SetSingleStyle(wx.LC_REPORT, True)
        self.incidentOrganizationList.InsertColumn(0, 'Name', format=wx.LIST_FORMAT_LEFT, width=-1)
        self.incidentOrganizationList.InsertColumn(1, 'Description', format=wx.LIST_FORMAT_LEFT, width=-1)
        self.incidentOrganizationList.InsertColumn(2, 'Risk Level', format=wx.LIST_FORMAT_LEFT, width=-1)

        #Load into the widget the values of the list
        index = 0
        for incident in list:
            item = self.incidentOrganizationList.InsertStringItem(index, str(incident[1]))
            self.incidentOrganizationList.SetItemData(item, incident[0])
            self.incidentOrganizationList.SetStringItem(index, 1, str(incident[2]))


            if incident[3] == 'L':
                self.incidentOrganizationList.SetStringItem(index, 2, "Low")
            elif incident[3] == 'M':
                self.incidentOrganizationList.SetStringItem(index, 2, "Medium")
            elif incident[3] == 'H':
                self.incidentOrganizationList.SetStringItem(index, 2, "High")
            index+=1

        self.incidentOrganizationList.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        self.incidentOrganizationList.SetColumnWidth(1, wx.LIST_AUTOSIZE_USEHEADER)
        self.incidentOrganizationList.SetColumnWidth(2, wx.LIST_AUTOSIZE_USEHEADER)

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
    def loadALEValues(self, values):
        #The 'values' variable has the following form
        # idALE, LA, LD, LR, LP, LREC, LRPC, OL, CI, ARO, Total, FK_Incident, FK_Organization
        # the following condition will check if all the values related to losses and and costs (LA, LD, LR, LP, LREC, LRPC, OL, CI) are equal to zero
        # In that case it means that the user had gave the total ALE value
        if values[1] == values[2] == values[3] == values[4] == values[5] == values[6] == values[7] == values[8] == 0.00:
            #wx.MessageBox("Es un total")
            self.ale_totalok.SetValue(True)
            self.changeTextsInputs(True)
            #Display the "Annual Rate of Occurrence" value from the values array
            self.ale_ARO.SetValue(str(values[9]))
            #Display the "Total" ALE from the values array
            self.ale_total.SetValue(str(values[10]))
        else:
            #The user had gave individual losses and costs values
            self.changeTextsInputs(False)
            self.ale_totalok.SetValue(False)

            self.ale_lossAssets.SetValue(str(values[1]))
            self.ale_lossData.SetValue(str(values[2]))
            self.ale_lossReputation.SetValue(str(values[3]))
            self.ale_legalProcedures.SetValue(str(values[4]))
            self.ale_LREC.SetValue(str(values[5]))
            self.ale_LRPC.SetValue(str(values[6]))
            self.ale_OL.SetValue(str(values[7]))
            self.ale_CI.SetValue(str(values[8]))
            self.ale_ARO.SetValue(str(values[9]))

            self.ale_total.SetValue(str(values[10]))

    #-------------------------------------------------------------------------------------------------------
    def changeTextsInputs(self, is_total):
        #Disable the single costs text fields and enable the 'Total' text field if the user will provide the total cost
        # otherwise disable the 'Total' text fields and enable the single costs text field
        if is_total:

            self.clearTextsInputs()
            #Disable the cost text fields
            self.ale_lossAssets.Disable()
            self.ale_lossData.Disable()
            self.ale_lossReputation.Disable()
            self.ale_legalProcedures.Disable()
            self.ale_LREC.Disable()
            self.ale_LRPC.Disable()
            self.ale_OL.Disable()
            self.ale_CI.Disable()

            #Enable the Total and Annual Rate of Occurrence text field
            self.ale_ARO.Enable()
            self.ale_total.Enable()
        else:
            self.ale_lossAssets.Enable()
            self.ale_lossData.Enable()
            self.ale_lossReputation.Enable()
            self.ale_legalProcedures.Enable()
            self.ale_LREC.Enable()
            self.ale_LRPC.Enable()
            self.ale_OL.Enable()
            self.ale_CI.Enable()
            self.ale_ARO.Enable()
            #Disable the Total text field
            self.ale_total.Disable()
        return

    #-------------------------------------------------------------------------------------------------------
    def clearTextsInputs(self):
        #Clear the Values in the Losses and costs text fields
        self.ale_lossAssets.SetValue("0.00")
        self.ale_lossData.SetValue("0.00")
        self.ale_lossReputation.SetValue("0.00")
        self.ale_legalProcedures.SetValue("0.00")
        self.ale_LREC.SetValue("0.00")
        self.ale_LRPC.SetValue("0.00")
        self.ale_OL.SetValue("0.00")
        self.ale_CI.SetValue("0.00")
        self.ale_ARO.SetValue("0")
        self.ale_total.SetValue("0.00")

