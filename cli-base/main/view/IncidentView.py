__author__ = 'ender_al'
# -*- coding: utf-8 *-*

try:
    import wx
except ImportError:
    raise ImportError,"wxPython module is required"

from wx import xrc

class IncidentView(wx.Frame):

    def __init__(self, app):
        self.app = app
        self.res = self.app.res
        self.frame = self.res.LoadFrame(self.app.main_frame, 'IncidentFrame')
        self.frame.SetSize((730,460))

    #-------------------------------------------------------------------------------------------------------
    def show(self):
        self.frame.Show()

    #-------------------------------------------------------------------------------------------------------
    def loadListOfIncidents(self,list):
        self.incidentList = xrc.XRCCTRL(self.frame, 'incidentList')
        self.incidentList.SetSingleStyle(wx.LC_REPORT, True)
        self.incidentList.InsertColumn(0, 'Name', format=wx.LIST_FORMAT_LEFT,width=-1)
        self.incidentList.InsertColumn(1, 'Description', format=wx.LIST_FORMAT_LEFT, width=-1)
        self.incidentList.InsertColumn(2, 'Risk Level', format=wx.LIST_FORMAT_LEFT, width=-1)
        self.incidentList.InsertColumn(3, 'Assigned Mitigation Actions', format=wx.LIST_FORMAT_LEFT, width=-1)

        #Load list of Incidents
        index = 0
        for incident in list:
            item = self.incidentList.InsertStringItem(index, str(incident[1]))
            self.incidentList.SetItemData(item, incident[0])
            self.incidentList.SetStringItem(index, 1, str(incident[2]))
            self.incidentList.SetStringItem(index, 2, incident[3])
            self.incidentList.SetStringItem(index, 3, incident[4])

            index+=1

        #Get the frame width to equally distribute the size of the list columns
        f_width, f_height = self.frame.GetSizeTuple()

        self.incidentList.SetColumnWidth(0, f_width/4)
        self.incidentList.SetColumnWidth(1, f_width/4)
        self.incidentList.SetColumnWidth(2, f_width/4)
        self.incidentList.SetColumnWidth(3, f_width/4)

    #-------------------------------------------------------------------------------------------------------
    def getOptimalListSize(self, listCtrl):

        item = -1
        num_col = listCtrl.GetColumnCount()
        max_val_col = [0 for k in xrange(num_col)]

        #Get the pixel values for a character in the control list by the font used
        dc = wx.WindowDC(listCtrl)
        item_font = listCtrl.GetItemFont(listCtrl.GetNextItem(item, wx.LIST_NEXT_ALL, wx.LIST_STATE_DONTCARE))
        font_width = item_font.GetPixelSize().GetWidth()

        #Number of characters that can be shown in the default size of the frame
        f_width,f_height = self.frame.GetSizeTuple()
        max_char = f_width/font_width

        #Get the maximum number of characters of the items in each column
        while 1:
            item = listCtrl.GetNextItem(item, wx.LIST_NEXT_ALL, wx.LIST_STATE_DONTCARE)
            if item == -1:
                break

            for col in xrange(num_col):
                col_val = max_val_col[col]
                item_text = len(listCtrl.GetItem(item,col).GetText())

                if item_text > col_val:
                    max_val_col.pop(col)
                    max_val_col.insert(col,item_text)

        total_col = sum(max_val_col)

        i=0
        res_char = max_char

        for val_col in max_val_col:
            col_percentage = (val_col * 100.0)/total_col
            opt_val = int((col_percentage * max_char)/100)

            if opt_val > res_char:
                max_val_col.pop(i)
                max_val_col.insert(i,res_char)
            else:
                max_val_col.pop(i)
                max_val_col.insert(i,opt_val)
            res_char = res_char - opt_val
            i=+1

        return max_val_col

    #-------------------------------------------------------------------------------------------------------
    def getItemCount(self):
        return self.incidentList.GetSelectedItemCount()

    #-------------------------------------------------------------------------------------------------------
    def getIDItemSelected(self):
        itemIndex = self.incidentList.GetFirstSelected()
        return self.incidentList.GetItemData(itemIndex)

    #-------------------------------------------------------------------------------------------------------
    def getSetItemsSelected(self):
        id_list = []
        flag = True
        itemIndex = self.incidentList.GetFirstSelected()
        id_list.append(self.incidentList.GetItemData(itemIndex))
        while flag:
            itemIndex = self.incidentList.GetNextSelected(itemIndex)
            if itemIndex != -1:
                id_list.append(self.incidentList.GetItemData(itemIndex))
            else:
                flag = False
        return id_list

#-------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------
class IncidentEditorView:
    def __init__(self, parent, app, add=True):
        self.Incident = app.Incident
        self.app = app
        self.Dialog = self.app.res.LoadDialog(parent, 'incidentEditor')
        self.Dialog.SetSize((340,250))
        btnAddIncident = xrc.XRCCTRL(self.Dialog, 'incident_btnedit')

        self.incident_textIDRef = xrc.XRCCTRL(self.Dialog, 'incident_textIDRef')
        self.incident_textmsg = xrc.XRCCTRL(self.Dialog, 'incident_txtmsg')

        self.incident_textname = xrc.XRCCTRL(self.Dialog, 'incident_textname')
        self.incident_textdescription = xrc.XRCCTRL(self.Dialog, 'incident_textdescription')
        self.incident_risklevel = xrc.XRCCTRL(self.Dialog, 'incident_risklevel')
        if(add):
            btnAddIncident.SetLabel('Add')
        else:
            btnAddIncident.SetLabel('Save')

    #-------------------------------------------------------------------------------------------------------
    def Show(self):
        self.Dialog.ShowModal()

    #-------------------------------------------------------------------------------------------------------
    def loadIncident(self, name, description, risk, IDRef):
        self.incident_textIDRef.SetValue(IDRef)
        self.incident_textname.SetValue(name)
        self.incident_textdescription.SetValue(description)
        if risk == "L":
            self.incident_risklevel.SetStringSelection('Low')
        elif risk == "M":
            self.incident_risklevel.SetStringSelection('Medium')
        elif risk == "H":
            self.incident_risklevel.SetStringSelection('High')

#-------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------
class IncidentCountermeasureEditorView:
    def __init__(self, parent, app, add=True):
        self.Incident = app.Incident
        self.app = app
        self.Dialog = self.app.res.LoadDialog(parent, 'incCouEditor')
        self.Dialog.SetSize((600,580))

        #Load the widgets that will load the list of all the countermeasures registered in the engine
        #and the list of restrictions belonging to the current countermeasure
        self.countermeasureList = xrc.XRCCTRL(self.Dialog, 'incCou_listcoun')
        self.incCouList = xrc.XRCCTRL(self.Dialog, 'incCou_listincCou')

    #-------------------------------------------------------------------------------------------------------
    def Show(self):
        self.Dialog.Show()

    #-------------------------------------------------------------------------------------------------------
    def loadListOfCountermeasures(self,list):

        self.countermeasureList.SetSingleStyle(wx.LC_REPORT, True)
        self.countermeasureList.InsertColumn(0, 'Name', format=wx.LIST_FORMAT_LEFT, width=-1)
        self.countermeasureList.InsertColumn(1, 'Description', format=wx.LIST_FORMAT_LEFT, width=-1)

        #Load into the widget the values of the list
        index = 0
        for countermeasure in list:
            item = self.countermeasureList.InsertStringItem(index, str(countermeasure[1]))
            self.countermeasureList.SetItemData(item, countermeasure[0])

            self.countermeasureList.SetStringItem(index, 1, str(countermeasure[2]))
            index+=1

        #Get the frame width to incally distribute the size of the list columns
        f_width, f_height = self.Dialog.GetSizeTuple()

        self.countermeasureList.SetColumnWidth(0, f_width/2)
        self.countermeasureList.SetColumnWidth(1, f_width/2)

    #-------------------------------------------------------------------------------------------------------
    def loadListOfIncCou(self,list):

        self.incCouList.SetSingleStyle(wx.LC_REPORT, True)
        self.incCouList.InsertColumn(0, 'Name', format=wx.LIST_FORMAT_LEFT, width=-1)
        self.incCouList.InsertColumn(1, 'Description', format=wx.LIST_FORMAT_LEFT, width=-1)

        #Load into the widget the values of the list
        index = 0
        for restriction in list:
            item = self.incCouList.InsertStringItem(index, str(restriction[1]))
            self.incCouList.SetItemData(item, restriction[0])

            self.incCouList.SetStringItem(index, 1, str(restriction[2]))
            index+=1


        #Get the frame width to incally distribute the size of the list columns
        f_width, f_height = self.Dialog.GetSizeTuple()

        self.incCouList.SetColumnWidth(0, f_width/2)
        self.incCouList.SetColumnWidth(1, f_width/2)

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
