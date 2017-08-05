__author__ = 'ender_al'

try:
    import wx
except ImportError:
    raise ImportError,"wxPython module is required"

from wx import xrc

class RestrictionView:
    def __init__(self, parent, app):
        self.Countermeasure = app.Countermeasure
        self.app = app
        self.Dialog = self.app.res.LoadDialog(parent, 'restrictionEditor')
        self.Dialog.SetSize((520,420))


        #Load the widgets that will load the list of all the countermeasures registered in the engine
        #and the list of restrictions belonging to the current countermeasure
        self.countermeasureList = xrc.XRCCTRL(self.Dialog, 'restriction_listcoun')
        self.restrictionList = xrc.XRCCTRL(self.Dialog, 'restriction_listrest')

    #-------------------------------------------------------------------------------------------------------
    def Show(self):
        self.Dialog.ShowModal()

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

        #Get the frame width to equally distribute the size of the list columns
        f_width, f_height = self.Dialog.GetSizeTuple()

        self.countermeasureList.SetColumnWidth(0, f_width/2)
        self.countermeasureList.SetColumnWidth(1, f_width/2)

    #-------------------------------------------------------------------------------------------------------
    def loadListOfRestrictions(self,list):

        self.restrictionList.SetSingleStyle(wx.LC_REPORT, True)
        self.restrictionList.InsertColumn(0, 'Name', format=wx.LIST_FORMAT_LEFT, width=-1)
        self.restrictionList.InsertColumn(1, 'Description', format=wx.LIST_FORMAT_LEFT, width=-1)

        #Load into the widget the values of the list
        index = 0
        for restriction in list:
            item = self.restrictionList.InsertStringItem(index, str(restriction[1]))
            self.restrictionList.SetItemData(item, restriction[0])

            self.restrictionList.SetStringItem(index, 1, str(restriction[2]))
            index+=1


        #Get the frame width to equally distribute the size of the list columns
        f_width, f_height = self.Dialog.GetSizeTuple()

        self.restrictionList.SetColumnWidth(0, f_width/2)
        self.restrictionList.SetColumnWidth(1, f_width/2)

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