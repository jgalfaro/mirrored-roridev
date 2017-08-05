__author__ = 'ender_al'
# -*- coding: utf-8 *-*

try:
    import wx
except ImportError:
    raise ImportError,"wxPython module is required"

from wx import xrc

class CountermeasureView(wx.Frame):

    def __init__(self, app):
        self.app = app
        self.res = self.app.res
        self.frame = self.res.LoadFrame(self.app.main_frame, 'CountermeasureFrame')
        self.frame.SetSize((730,460))

    #-------------------------------------------------------------------------------------------------------
    def show(self):
        self.frame.Show()

    #-------------------------------------------------------------------------------------------------------
    def loadListOfCountermeasures(self,list):
        self.countermeasureList = xrc.XRCCTRL(self.frame, 'countermeasureList')
        self.countermeasureList.SetSingleStyle(wx.LC_REPORT, True)
        self.countermeasureList.InsertColumn(0, 'Name', format=wx.LIST_FORMAT_LEFT,width=-1)
        self.countermeasureList.InsertColumn(1, 'Description', format=wx.LIST_FORMAT_LEFT, width=-1)
        self.countermeasureList.InsertColumn(2, 'RM (%)', format=wx.LIST_FORMAT_LEFT, width=-1)
        self.countermeasureList.InsertColumn(3, 'ARC', format=wx.LIST_FORMAT_LEFT, width=-1)
        self.countermeasureList.InsertColumn(4, 'Restrictions', format=wx.LIST_FORMAT_LEFT, width=-1)

        #Load list of Countermeasures
        index = 0
        for countermeasure in list:
            item = self.countermeasureList.InsertStringItem(index, str(countermeasure[1]))
            self.countermeasureList.SetItemData(item, countermeasure[0])
            self.countermeasureList.SetStringItem(index, 1, str(countermeasure[2]))
            self.countermeasureList.SetStringItem(index, 2, str(countermeasure[3]))
            self.countermeasureList.SetStringItem(index, 3, str(countermeasure[4]))
            self.countermeasureList.SetStringItem(index, 4, str(countermeasure[5]))
            index+=1

        #Get the frame width to equally distribute the size of the list columns
        f_width, f_height = self.frame.GetSizeTuple()

        self.countermeasureList.SetColumnWidth(0, f_width/5)
        self.countermeasureList.SetColumnWidth(1, f_width/5)
        self.countermeasureList.SetColumnWidth(2, f_width/5)
        self.countermeasureList.SetColumnWidth(3, f_width/5)
        self.countermeasureList.SetColumnWidth(4, f_width/5)

    #-------------------------------------------------------------------------------------------------------
    def getItemCount(self):
        return self.countermeasureList.GetSelectedItemCount()

    #-------------------------------------------------------------------------------------------------------
    def getIDItemSelected(self):
        itemIndex = self.countermeasureList.GetFirstSelected()
        return self.countermeasureList.GetItemData(itemIndex)

    #-------------------------------------------------------------------------------------------------------
    def getSetItemsSelected(self):
        id_list = []
        flag = True
        itemIndex = self.countermeasureList.GetFirstSelected()
        id_list.append(self.countermeasureList.GetItemData(itemIndex))
        while flag:
            itemIndex = self.countermeasureList.GetNextSelected(itemIndex)
            if itemIndex != -1:
                id_list.append(self.countermeasureList.GetItemData(itemIndex))
            else:
                flag = False
        return id_list

#-------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------
class CountermeasureEditorView:
    def __init__(self, parent, app, add=True):
        self.Countermeasure = app.Countermeasure
        self.app = app
        self.Dialog = self.app.res.LoadDialog(parent, 'countermeasureEditor')
        self.Dialog.SetSize((340,250))
        btnAddCountermeasure = xrc.XRCCTRL(self.Dialog, 'countermeasure_btnedit')

        self.countermeasure_textIDRef = xrc.XRCCTRL(self.Dialog, 'countermeasure_textIDRef')
        self.countermeasure_textmsg = xrc.XRCCTRL(self.Dialog, 'countermeasure_txtmsg')

        self.countermeasure_textname = xrc.XRCCTRL(self.Dialog, 'countermeasure_textname')
        self.countermeasure_textdescription = xrc.XRCCTRL(self.Dialog, 'countermeasure_textdescription')
        self.countermeasure_checkTotal = xrc.XRCCTRL(self.Dialog, 'countermeasure_checkTotal')

        if(add):
            btnAddCountermeasure.SetLabel('Add')
        else:
            btnAddCountermeasure.SetLabel('Save')

    #-------------------------------------------------------------------------------------------------------
    def Show(self):
        self.Dialog.ShowModal()

    #-------------------------------------------------------------------------------------------------------
    def loadCountermeasure(self, name, description, totally_restritive, idref):
        self.countermeasure_textIDRef.SetValue(idref)
        self.countermeasure_textname.SetValue(name)
        self.countermeasure_textdescription.SetValue(description)
        self.countermeasure_checkTotal.SetValue(totally_restritive)

        '''
        if totally_restritive:
            self.countermeasure_checkTotal.SetValue(True)
        else:
            self.countermeasure_checkTotal.SetValue(False)
        '''
