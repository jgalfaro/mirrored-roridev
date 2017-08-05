__author__ = 'ender_al'
# -*- coding: utf-8 *-*

try:
    import wx
except ImportError:
    raise ImportError,"wxPython module is required"

from wx import xrc

class EquipmentView(wx.Frame):

    def __init__(self, app):
        self.app = app
        self.res = self.app.res
        self.frame = self.res.LoadFrame(self.app.main_frame, 'EquipmentFrame')
        self.frame.SetSize((730,460))

    #-------------------------------------------------------------------------------------------------------
    def show(self):
        self.frame.Show()

    #-------------------------------------------------------------------------------------------------------
    def loadListOfEquipments(self,list):
        self.equipmentList = xrc.XRCCTRL(self.frame, 'equipmentList')
        self.equipmentList.SetSingleStyle(wx.LC_REPORT, True)
        self.equipmentList.InsertColumn(0, 'Name', format=wx.LIST_FORMAT_LEFT, width=-1)
        self.equipmentList.InsertColumn(1, 'Type', format=wx.LIST_FORMAT_LEFT, width=-1)
        self.equipmentList.InsertColumn(2, 'Assigned Mitigation Actions', format=wx.LIST_FORMAT_LEFT, width=-1)

        #Load list of Equipments
        index = 0
        for equipment in list:
            item = self.equipmentList.InsertStringItem(index, str(equipment[1]))
            self.equipmentList.SetItemData(item, equipment[0])

            self.equipmentList.SetStringItem(index, 1, str(equipment[2]))
            self.equipmentList.SetStringItem(index, 2, str(equipment[3]))
            index+=1

        #Get the frame width to equally distribute the size of the list columns
        f_width, f_height = self.frame.GetSizeTuple()

        self.equipmentList.SetColumnWidth(0, f_width/3)
        self.equipmentList.SetColumnWidth(1, f_width/3)
        self.equipmentList.SetColumnWidth(2, f_width/3)


    #-------------------------------------------------------------------------------------------------------
    def getItemCount(self):
        return self.equipmentList.GetSelectedItemCount()

    #-------------------------------------------------------------------------------------------------------
    def getIDItemSelected(self):
        itemIndex = self.equipmentList.GetFirstSelected()
        return self.equipmentList.GetItemData(itemIndex)

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
#-------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------
class EquipmentEditorView:
    def __init__(self, parent, app, add=True):
        self.Equipment = app.Equipment
        self.app = app
        self.Dialog = self.app.res.LoadDialog(parent, 'equipmentEditor')
        self.Dialog.SetSize((300,150))
        btnAddEquipment = xrc.XRCCTRL(self.Dialog, 'equipment_btnedit')

        self.equipment_textIDRef = xrc.XRCCTRL(self.Dialog, 'equipment_textIDRef')
        self.equipment_textmsg = xrc.XRCCTRL(self.Dialog, 'equipment_txtmsg')

        self.equipment_textname = xrc.XRCCTRL(self.Dialog, 'equipment_textname')
        self.equipment_texttype = xrc.XRCCTRL(self.Dialog, 'equipment_texttype')
        if(add):
            btnAddEquipment.SetLabel('Add')
        else:
            btnAddEquipment.SetLabel('Save')

    #-------------------------------------------------------------------------------------------------------
    def Show(self):
        self.Dialog.ShowModal()

    #-------------------------------------------------------------------------------------------------------
    def loadEquipment(self, name, type, IDRef):
        self.equipment_textIDRef.SetValue(IDRef)
        self.equipment_textname.SetValue(name)
        self.equipment_texttype.SetValue(type)

#-------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------
class EquipmentCountermeasureEditorView:
    def __init__(self, parent, app, add=True):
        self.Equipment = app.Equipment
        self.app = app
        self.Dialog = self.app.res.LoadDialog(parent, 'equCouEditor')
        self.Dialog.SetSize((600,580))

        #Load the widgets that will load the list of all the countermeasures registered in the engine
        #and the list of restrictions belonging to the current countermeasure
        self.countermeasureList = xrc.XRCCTRL(self.Dialog, 'equCou_listcoun')
        self.equCouList = xrc.XRCCTRL(self.Dialog, 'equCou_listequCou')

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

        #Get the frame width to equally distribute the size of the list columns
        f_width, f_height = self.Dialog.GetSizeTuple()

        self.countermeasureList.SetColumnWidth(0, f_width/2)
        self.countermeasureList.SetColumnWidth(1, f_width/2)

    #-------------------------------------------------------------------------------------------------------
    def loadListOfEquCou(self,list):

        self.equCouList.SetSingleStyle(wx.LC_REPORT, True)
        self.equCouList.InsertColumn(0, 'Name', format=wx.LIST_FORMAT_LEFT, width=-1)
        self.equCouList.InsertColumn(1, 'Description', format=wx.LIST_FORMAT_LEFT, width=-1)

        #Load into the widget the values of the list
        index = 0
        for restriction in list:
            item = self.equCouList.InsertStringItem(index, str(restriction[1]))
            self.equCouList.SetItemData(item, restriction[0])

            self.equCouList.SetStringItem(index, 1, str(restriction[2]))
            index+=1


        #Get the frame width to equally distribute the size of the list columns
        f_width, f_height = self.Dialog.GetSizeTuple()

        self.equCouList.SetColumnWidth(0, f_width/2)
        self.equCouList.SetColumnWidth(1, f_width/2)

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
