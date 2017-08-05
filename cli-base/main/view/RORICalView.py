__author__ = 'ender_al'
try:
    import wx
except ImportError:
    raise ImportError,"wxPython module is required"

from wx import xrc

class RORICalView(wx.Frame):

    def __init__(self, app):
        self.app = app
        self.res = self.app.res
        self.frame = self.res.LoadFrame(self.app.main_frame, 'RORICalFrame')
        self.frame.SetSize((700,470))

        #Organization List
        self.orgListChoice = xrc.XRCCTRL(self.frame, 'RORICal_orgList')

        #Incident List
        self.incidentList = xrc.XRCCTRL(self.frame, 'RORICal_incList')

        #Countermeasure List
        self.countermeasureList = xrc.XRCCTRL(self.frame, 'RORICal_couList')

        #Calculation Button
        self.calculationButton = xrc.XRCCTRL(self.frame, 'RORICal_calcBtn')
        self.calculationButton.Disable()
    #-------------------------------------------------------------------------------------------------------
    def show(self):
        self.frame.Show()

    #-------------------------------------------------------------------------------------------------------
    def loadListOfOrganizations(self,list):
        #Load list of Organization
        for organization in list:
            self.orgListChoice.Append(organization)
        return

    #-------------------------------------------------------------------------------------------------------
    def loadListOfIncidents(self,list):

        self.incidentList.SetSingleStyle(wx.LC_REPORT, True)
        self.incidentList.InsertColumn(0, 'Name', format=wx.LIST_FORMAT_LEFT,width=-1)

        #Load list of Incidents
        index = 0
        for incident in list:
            item = self.incidentList.InsertStringItem(index, str(incident[1]))
            self.incidentList.SetItemData(item, incident[0])

            index+=1

        self.incidentList.SetColumnWidth(0, wx.LIST_AUTOSIZE)

    #-------------------------------------------------------------------------------------------------------
    def loadListOfCountermeasures(self,list):
        self.countermeasureList.SetSingleStyle(wx.LC_REPORT, True)
        self.countermeasureList.InsertColumn(0, 'Name', format=wx.LIST_FORMAT_LEFT,width=-1)
        #Load list of Countermeasures
        index = 0
        for countermeasure in list:
            item = self.countermeasureList.InsertStringItem(index, str(countermeasure[1]))
            self.countermeasureList.SetItemData(item, countermeasure[0])
            index+=1

        self.countermeasureList.SetColumnWidth(0, wx.LIST_AUTOSIZE)


    #-------------------------------------------------------------------------------------------------------
    def getIncidentItemCount(self):
        return self.incidentList.GetSelectedItemCount()

    #-------------------------------------------------------------------------------------------------------
    def getIDIncidentItemSelected(self):
        itemIndex = self.incidentList.GetFirstSelected()
        return self.incidentList.GetItemData(itemIndex)

    #-------------------------------------------------------------------------------------------------------
    def getSetItemsSelected(self):
        id_list = []
        flag = True
        itemIndex = self.equipmentList.GetFirstSelected()
        id_list.append(self.equipmentList.GetItemData(itemIndex))
        while flag:
            itemIndex = self.equipmentList.GetNextSelected(itemIndex)
            if itemIndex != -1:
                id_list.append(self.equipmentList.GetItemData(itemIndex))
            else:
                flag = False

        return id_list

#-------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------

class RMDialog(wx.Dialog):
    """"""
    #----------------------------------------------------------------------
    def __init__(self,msg):
        """Constructor"""
        wx.Dialog.__init__(self, None, title="Missing RM Information!")

        lbl = wx.StaticText(self, label=msg)
        self.btn_discard = wx.Button(self, id=wx.ID_ANY, label="Discard")
        self.btn_av = wx.Button(self, id=wx.ID_ANY, label="Calculate with AV")
        self.btn_abort = wx.Button(self, id=wx.ID_ANY, label="Abort Calculation")
        self.icon = wx.ICON_ERROR

        diag_sizer = wx.BoxSizer(wx.VERTICAL)
        text_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)

        #text_sizer.Add(self.icon)
        text_sizer.Add(lbl, 0, wx.EXPAND | wx.ALL, 20)
        button_sizer.Add(self.btn_discard, 1, wx.ALL, 5)
        button_sizer.Add(self.btn_av, 1, wx.ALL, 5)
        button_sizer.Add(self.btn_abort, 1, wx.ALL, 5)

        diag_sizer.Add(text_sizer,0,wx.CENTER,5)
        diag_sizer.Add(button_sizer,0,wx.CENTER,5)
        self.SetSizer(diag_sizer)
        diag_sizer.Fit(self)

        self.btn_discard.Bind(wx.EVT_BUTTON, self.OnDiscard)
        self.btn_av.Bind(wx.EVT_BUTTON, self.OnAV)
        self.btn_abort.Bind(wx.EVT_BUTTON, self.OnAbort)

    def OnDiscard(self,evt):
        self.EndModal(0)

    def OnAV(self,evt):
        self.EndModal(1)

    def OnAbort(self,evt):
        self.EndModal(2)

#-------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------

class EFDialog(wx.Dialog):
    """"""
    #----------------------------------------------------------------------
    def __init__(self,cou_list):
        """Constructor"""
        wx.Dialog.__init__(self, None, title="EF values")

        lbl = wx.StaticText(self, label="Please introduce the EF values of the following Mitigation Actions:")
        self.textLabels = {}
        self.textFields = {}

        self.btn_OK = wx.Button(self, id=wx.ID_OK, label="OK")

        diag_sizer = wx.BoxSizer(wx.VERTICAL)
        text_sizer = wx.BoxSizer(wx.HORIZONTAL)
        gridSizer = wx.GridSizer(rows=len(cou_list), cols=2, hgap=5, vgap=5)

        for cou in cou_list:
            self.textLabels[cou['cou_id']] = wx.StaticText(self, label=cou['cou_name'])
            gridSizer.Add(self.textLabels[cou['cou_id']], 0, wx.EXPAND)
            self.textFields[cou['cou_id']] = wx.TextCtrl(self)
            gridSizer.Add(self.textFields[cou['cou_id']], 0, wx.ALIGN_RIGHT)

        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        text_sizer.Add(lbl, 0, wx.EXPAND | wx.ALL, 20)
        button_sizer.Add(self.btn_OK, 1, wx.ALL, 5)


        diag_sizer.Add(text_sizer,0,wx.CENTER,5)
        diag_sizer.Add(gridSizer,0,wx.CENTER,5)
        diag_sizer.Add(button_sizer,0,wx.CENTER,5)
        self.SetSizer(diag_sizer)
        diag_sizer.Fit(self)


#-------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------
class RORIResultsView(wx.Frame):

    def __init__(self, parent, app):
        self.app = app
        self.res = xrc.XmlResource('./xrc/RORI_Results.xrc')
        self.results_frame = self.res.LoadFrame(self.app.main_frame, 'RORIResults_Frame')


        self.results_frame.Bind(wx.EVT_BUTTON, self.onExit, id=xrc.XRCID('rori_exit1'))

        #Title
        self.title = xrc.XRCCTRL(self.results_frame, 'rori_title')

        #Lists
        self.individualList = xrc.XRCCTRL(self.results_frame, 'rori_listindividual')
        self.combinedList = xrc.XRCCTRL(self.results_frame, 'rori_listcombined')

        self.results_frame.SetSize((650,700))
        return

    def showResults(self):
        self.results_frame.Show()
        return

    def loadThresholdDialog(self):

        self.TDialog = wx.TextEntryDialog(self.results_frame, "Please Introduce a Threshold Value", defaultValue="0")
        self.TDialog.SetTitle("Combination Threshold")
        self.TDialog.SetToolTipString("Threshold is used to exclude from the combined evaluation all the Mitigation Actions which individual RORI index is bellow it's value.")
        self.TDialog.ShowModal()

        return
    #--------------------------------------------------------------------------------------------------------------
    def loadListIndividual(self,list, best):

        self.individualList.ClearAll()

        self.individualList.SetSingleStyle(wx.LC_REPORT, True)
        self.individualList.InsertColumn(0, 'ID', format=wx.LIST_FORMAT_LEFT,width=-1)
        self.individualList.InsertColumn(1, 'Name', format=wx.LIST_FORMAT_LEFT, width=-1)
        self.individualList.InsertColumn(2, 'Equipment', format=wx.LIST_FORMAT_LEFT, width=-1)
        self.individualList.InsertColumn(3, 'RORI', format=wx.LIST_FORMAT_LEFT, width=-1)

        #Load list of Incidents
        index = 0
        for rori_individual in list:
            item = self.individualList.InsertStringItem(index, str(rori_individual[4]))
            self.individualList.SetItemData(item, rori_individual[0])
            self.individualList.SetStringItem(index, 1, str(rori_individual[1]))
            self.individualList.SetStringItem(index, 2, str(rori_individual[2]))
            self.individualList.SetStringItem(index, 3, str(rori_individual[3]))

            if rori_individual[0] == best:
                self.individualList.SetItemBackgroundColour(index,wx.BLUE)
                self.individualList.SetItemTextColour(index, wx.WHITE)
            index+=1

        #Get the frame width to equally distribute the size of the list columns
        f_width, f_height = self.results_frame.GetSizeTuple()

        self.individualList.SetColumnWidth(0, f_width/4)
        self.individualList.SetColumnWidth(1, f_width/4)
        self.individualList.SetColumnWidth(2, f_width/4)
        self.individualList.SetColumnWidth(3, f_width/4)

    #--------------------------------------------------------------------------------------------------
    def loadListCombined(self,list, best):
        self.combinedList.SetSingleStyle(wx.LC_REPORT, True)
        self.combinedList.InsertColumn(0, 'Combinations', format=wx.LIST_FORMAT_LEFT,width=-1)
        self.combinedList.InsertColumn(1, 'ARC', format=wx.LIST_FORMAT_LEFT, width=-1)
        self.combinedList.InsertColumn(2, 'COV', format=wx.LIST_FORMAT_LEFT, width=-1)
        self.combinedList.InsertColumn(3, 'EF', format=wx.LIST_FORMAT_LEFT, width=-1)
        self.combinedList.InsertColumn(4, 'RM', format=wx.LIST_FORMAT_LEFT, width=-1)
        self.combinedList.InsertColumn(5, 'RORI index', format=wx.LIST_FORMAT_LEFT, width=-1)

        #Load list of Incidents
        index = 0
        for rori_combined in list:
            item = self.combinedList.InsertStringItem(index, str(rori_combined[0]))

            self.combinedList.SetStringItem(index, 1, str(rori_combined[1]))
            self.combinedList.SetStringItem(index, 2, str(rori_combined[2]))
            self.combinedList.SetStringItem(index, 3, str(rori_combined[3]))
            self.combinedList.SetStringItem(index, 4, str(rori_combined[4]))
            self.combinedList.SetStringItem(index, 5, str(rori_combined[5]))

            if index == best:
                self.combinedList.SetItemBackgroundColour(index,wx.BLUE)
                self.combinedList.SetItemTextColour(index, wx.WHITE)
            index+=1

        #Get the frame width to equally distribute the size of the list columns
        f_width, f_height = self.results_frame.GetSizeTuple()

        self.combinedList.SetColumnWidth(0, f_width/6)
        self.combinedList.SetColumnWidth(1, f_width/6)
        self.combinedList.SetColumnWidth(2, f_width/6)
        self.combinedList.SetColumnWidth(3, f_width/6)
        self.combinedList.SetColumnWidth(4, f_width/6)
        self.combinedList.SetColumnWidth(5, f_width/6)


    #-------------------------------------------------------------------------------------------------------
    def getIndividualItemCount(self):
        return self.individualList.GetSelectedItemCount()

    #-------------------------------------------------------------------------------------------------------
    def getItemsSelected(self):
        id_list = []
        flag = True
        itemIndex = self.individualList.GetFirstSelected()
        id_list.append(self.individualList.GetItemData(itemIndex))
        while flag:
            itemIndex = self.individualList.GetNextSelected(itemIndex)
            if itemIndex != -1:
                id_list.append(self.individualList.GetItemData(itemIndex))
            else:
                flag = False

        return id_list
    #--------------------------------------------------------------------------
    def selectAllItems(self,flag):

        count = self.individualList.GetItemCount()
        for index in range(0, count):
            self.individualList.Select(index,flag)

        self.individualList.SetFocus()

    #-------------------------------------------------------------------------------------------------------------
    def onExit(self, evt):
       self.results_frame.Destroy()


