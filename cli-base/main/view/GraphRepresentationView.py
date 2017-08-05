__author__ = 'ender_al'
try:
    import wx
except ImportError:
    raise ImportError,"wxPython module is required"

from wx import xrc

class GraphRepresentationView(wx.Frame):

    def __init__(self, app):
        self.app = app
        self.res = self.app.res
        self.frame = self.res.LoadFrame(self.app.main_frame, 'GraphFrame')
        self.frame.SetSize((700,470))

        #Organization List
        self.orgListChoice = xrc.XRCCTRL(self.frame, 'Graph_orgList')

        #Incident List
        self.incidentList = xrc.XRCCTRL(self.frame, 'Graph_incList')

        #Countermeasure List
        self.countermeasureList = xrc.XRCCTRL(self.frame, 'Graph_couList')

        #Graphic Button
        self.graphicButton = xrc.XRCCTRL(self.frame, 'Graph_callAVbtn')
        self.graphicButton.Disable()
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
        self.countermeasureList.InsertColumn(0, 'ID', format=wx.LIST_FORMAT_LEFT,width=-1)
        self.countermeasureList.InsertColumn(1, 'Name', format=wx.LIST_FORMAT_LEFT,width=-1)

        #Load list of Countermeasures
        index = 0
        for countermeasure in list:
            item = self.countermeasureList.InsertStringItem(index, str(countermeasure[4]))
            self.countermeasureList.SetItemData(item, countermeasure[0])
            self.countermeasureList.SetStringItem(index, 1, str(countermeasure[1]))
            index+=1

        self.countermeasureList.SetColumnWidth(0, wx.LIST_AUTOSIZE_USEHEADER)
        self.countermeasureList.SetColumnWidth(1, wx.LIST_AUTOSIZE)


    #-------------------------------------------------------------------------------------------------------
    def getItemCount(self, list_instance):
        return list_instance.GetSelectedItemCount()

    #-------------------------------------------------------------------------------------------------------
    def getIDItemSelected(self, list_instance):
        itemIndex = list_instance.GetFirstSelected()
        return list_instance.GetItemData(itemIndex)

    #-------------------------------------------------------------------------------------------------------
    def getItemsSelected(self, list_instance):
        id_list = []
        flag = True
        itemIndex = list_instance.GetFirstSelected()
        id_list.append(list_instance.GetItemData(itemIndex))
        while flag:
            itemIndex = list_instance.GetNextSelected(itemIndex)
            if itemIndex != -1:
                id_list.append(list_instance.GetItemData(itemIndex))
            else:
                flag = False

        return id_list
