__author__ = 'ender_al'
# -*- coding: utf-8 *-*

import wx
from wx import xrc
from wx.lib.pubsub import Publisher

from view.EquipmentView import EquipmentView, EquipmentEditorView, EquipmentCountermeasureEditorView
from model.Countermeasure import Countermeasure

class EquipmentController:

    def __init__(self, app):
        self.app = app
        self.equipment_view = EquipmentView(app)

        #Menu Items
        self.equipment_view.frame.Bind(wx.EVT_MENU, self.onCreateEquipment, id=xrc.XRCID('equipment_mitcreate'))
        self.equipment_view.frame.Bind(wx.EVT_MENU, self.onEditEquipment, id=xrc.XRCID('equipment_mitedit'))
        self.equipment_view.frame.Bind(wx.EVT_MENU, self.onDeleteEquipment, id=xrc.XRCID('equipment_mitdelete'))
        self.equipment_view.frame.Bind(wx.EVT_MENU, self.onExit, id=xrc.XRCID('equipment_exit'))

        #ToolBar
        self.equipment_view.frame.Bind(wx.EVT_TOOL, self.onCreateEquipment, id=xrc.XRCID('equipment_toolcreate'))
        self.equipment_view.frame.Bind(wx.EVT_TOOL, self.onEditEquipment, id=xrc.XRCID('equipment_tooledit'))
        self.equipment_view.frame.Bind(wx.EVT_TOOL, self.onDeleteEquipment, id=xrc.XRCID('equipment_tooldelete'))
        self.equipment_view.frame.Bind(wx.EVT_TOOL, self.onRelationEquCou, id=xrc.XRCID('equipment_toolequ-cou'))

        #Message from the Equipment Model
        Publisher.subscribe(self.equipmentModified, 'equipment_deleted')
        Publisher.subscribe(self.equipmentModified, 'equipment_created')
        Publisher.subscribe(self.equipmentModified, 'equipment_updated')
        #Publisher.subscribe(self.equipmentModified, 'countermeasure_updated')
        Publisher.subscribe(self.equipmentModified, 'equipment_created')
        Publisher.subscribe(self.equipmentModified, 'equipment_updated')

        #Filter
        self.txtFilter = xrc.XRCCTRL(self.equipment_view.frame, 'equ_txtfilter')
        self.btnFilter = xrc.XRCCTRL(self.equipment_view.frame, 'equ_btnfilter')
        self.equipment_view.frame.Bind(wx.EVT_TEXT_ENTER, self.onFilterEquipment, self.txtFilter)
        self.equipment_view.frame.Bind(wx.EVT_BUTTON, self.onFilterEquipment, self.btnFilter)
        self.GUIequipments = []

        #Load equipment list
        self.loadListOfEquipments_controller()
        self.equipment_view.show()

    #------------------------------------------------------------------------------------------------------------
    def loadListOfEquipments_controller(self):
        (error, list) = self.app.Equipment.read_all()
        if error:
            msg= "Error reading the list of PEPs: \n" + list
            wx.MessageBox(msg)
        else:
            #Create a list of equipments with the countermeasures assigned to it
            # The Equipment.read_all() method will return a list of tuples. Each tuple has the following values:
            # (idEquipment, Name, Type, IDRef)

            #Clear the Filter text
            self.txtFilter.SetValue("")

            countermeasure = Countermeasure()
            equ_list = []
            for equ in list:
                idEqu = equ[0]
                nameEqu = equ[1]
                descEqu = equ[2]

                # Select all the countermeasure assigned to the current equipment
                countermeasure.FK_Equipment = idEqu
                (cou_error, cou_list) = countermeasure.readByEquipment()
                if cou_error:
                    msg= "Error reading the list of Mitigation Actions: \n" + cou_list
                    wx.MessageBox(msg)
                    self.onCancel()
                else:
                    # The countermeasure.readByEquipment() method will return a list of tuples. Each tuple has the following values:
                    # (idCountermeasure, Name, Description, Totally_Restrictive, FK_Equipment)

                    nameList = []
                    for cou in cou_list:
                        nameList.append(cou[1])

                    equ_list.append([idEqu, nameEqu, descEqu, ','.join(nameList)])

            self.GUIequipments = equ_list
            self.equipment_view.loadListOfEquipments(equ_list)

    #-------------------------------------------------------------------------------------------------------
    def onFilterEquipment(self,event):
        new_list = []
        string = self.txtFilter.GetValue().upper()
        if string !="":
            for item in self.GUIequipments:
                for sub_item in item:
                    if type(sub_item) is str:
                        if any([string in sub_item.upper()]):
                            new_list.append(item)
                            break
            self.equipment_view.loadListOfEquipments(new_list)
        else:
            self.equipment_view.loadListOfEquipments(self.GUIequipments)

    #------------------------------------------------------------------------------------------------------------
    def equipmentModified(self, mensaje):
        self.loadListOfEquipments_controller()

    #------------------------------------------------------------------------------------------------------------
    def onCreateEquipment(self, evt):
        editor = EquipmentEditorController(self.app,  self.equipment_view, True)

    #------------------------------------------------------------------------------------------------------------
    def onEditEquipment(self, evt):
        #Check if the dialog was already created
        equ_frame = self.app.main_frame.FindWindowByName("EquipmentFrame")
        edt_diag = equ_frame.FindWindowByName("equipmentEditor")

        if not edt_diag:
            count = self.equipment_view.getItemCount()
            if (count == 0):
                wx.MessageBox("Please select a PEP to edit!")
            elif (count > 1):
                wx.MessageBox("Please select just one PEP to be edited!")
            else:
                editor = EquipmentEditorController(self.app,  self.equipment_view, False)
        else:
            edt_diag.Raise()

        return

    #------------------------------------------------------------------------------------------------------------
    def onDeleteEquipment(self, evt):
        count = self.equipment_view.getItemCount()
        if (count == 0):
            wx.MessageBox("Please select an PEP to be deleted!")
        else:
            msg = "Proceed to delete "+str(count)+" elements?"
            del_confirm = wx.MessageDialog(None, msg, 'Delete Confirmation', wx.YES_NO | wx.ICON_QUESTION)

            if del_confirm.ShowModal() == wx.ID_NO:
                return
            item_list = self.equipment_view.getSetItemsSelected()

            for id in item_list:
                self.app.Equipment.id = id
                (error, values) = self.app.Equipment.delete()
                if error:
                    msg= "There was an error deleting the PEP: \n" + values
                    wx.MessageBox(msg)

    #------------------------------------------------------------------------------------------------------------
    def onRelationEquCou(self, evt):
        #Check if the dialog was already created
        equ_frame = self.app.main_frame.FindWindowByName("EquipmentFrame")
        equCou_diag = equ_frame.FindWindowByName("equCouEditor")

        if not equCou_diag:
            count = self.equipment_view.getItemCount()
            if (count == 0):
                wx.MessageBox("Please select a PEP to assign Mitigation Actions!")
            elif (count > 1):
                wx.MessageBox("Please select just one PEP to assign Mitigation Actions!")
            else:
                editor = EquipmentCountermeasureEditorController(self.app, self.equipment_view)
        else:
            equCou_diag.Raise()

        return


    #------------------------------------------------------------------------------------------------------------
    def onExit(self, evt):
       self.equipment_view.frame.Destroy()

#------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------
class EquipmentEditorController:

    def __init__(self, app, parent, add=True):
        self.app = app
        self.EquipmentView = parent
        self.equipment_edtview = EquipmentEditorView(self.EquipmentView.frame, self.app, add)
        btnAddEquipment = xrc.XRCCTRL(self.equipment_edtview.Dialog, 'equipment_btnedit')
        btnCancel = xrc.XRCCTRL(self.equipment_edtview.Dialog, 'equipment_btncancel')

        self.equipment_edtview.Dialog.Bind(wx.EVT_BUTTON, self.onCancel, btnCancel)
        self.equipment_edtview.Dialog.Bind(wx.EVT_CLOSE, self.onCancel)

        if(add):
            self.equipment_edtview.Dialog.Bind(wx.EVT_BUTTON, self.onAddEquipment, btnAddEquipment)
            self.equipment_edtview.Show()
        else:
            self.idEquipment = self.EquipmentView.getIDItemSelected()
            equipment = self.app.Equipment
            equipment.id = self.idEquipment
            (error, values) = equipment.read()
            if error:
                msg= "Error reading the values from the PEP: \n" + values
                wx.MessageBox(msg)
                self.onCancel(True)
            else:
                name = values[0][1]
                type = values[0][2]
                IDRef = values[0][3]
                self.equipment_edtview.loadEquipment(name, type, IDRef)
                self.equipment_edtview.Dialog.Bind(wx.EVT_BUTTON, self.onEditEquipment, btnAddEquipment)
                self.equipment_edtview.Show()
        return

    #------------------------------------------------------------------------------------------------------------
    def onAddEquipment(self, evt):
        idref = self.equipment_edtview.equipment_textIDRef.GetValue()
        name = self.equipment_edtview.equipment_textname.GetValue()
        type = self.equipment_edtview.equipment_texttype.GetValue()

        if idref == '':
            self.equipment_edtview.equipment_textmsg.SetForegroundColour((255,0,0)) # set text color
            self.equipment_edtview.equipment_textmsg.SetLabel('* Mandatory Fields\nID cannot be empty!')
            return
        elif name == '':
            self.equipment_edtview.equipment_textmsg.SetForegroundColour((255,0,0)) # set text color
            self.equipment_edtview.equipment_textmsg.SetLabel('* Mandatory Fields\nName cannot be empty!')
            return
        elif type == '':
            self.equipment_edtview.equipment_textmsg.SetForegroundColour((255,0,0)) # set text color
            self.equipment_edtview.equipment_textmsg.SetLabel('* Mandatory Fields\nType cannot be empty!')
            return

        equipment = self.app.Equipment
        equipment.IDRef = idref
        equipment.Name = name
        equipment.Type = type
        error = equipment.create()
        if error:
            msg= "Error creating PEPs: \n"
            wx.MessageBox(msg)
            self.onCancel(True)
        #self.loadListOfEquipments()
        self.equipment_edtview.Dialog.Close()
        return

    #------------------------------------------------------------------------------------------------------------
    def onEditEquipment(self, evt):
        idref = self.equipment_edtview.equipment_textIDRef.GetValue()
        name = self.equipment_edtview.equipment_textname.GetValue()
        type = self.equipment_edtview.equipment_texttype.GetValue()

        if idref == '':
            self.equipment_edtview.equipment_textmsg.SetForegroundColour((255,0,0)) # set text color
            self.equipment_edtview.equipment_textmsg.SetLabel('* Mandatory Fields\nID cannot be empty!')
            return
        elif name == '':
            self.equipment_edtview.equipment_textmsg.SetForegroundColour((255,0,0)) # set text color
            self.equipment_edtview.equipment_textmsg.SetLabel('* Mandatory Fields\nName cannot be empty!')
            return
        elif type == '':
            self.equipment_edtview.equipment_textmsg.SetForegroundColour((255,0,0)) # set text color
            self.equipment_edtview.equipment_textmsg.SetLabel('* Mandatory Fields\nType cannot be empty!')
            return

        equipment = self.app.Equipment
        equipment.id = self.idEquipment
        equipment.IDRef = idref
        equipment.Name = name
        equipment.Type = type
        (error, values) = equipment.update()
        if error:
            msg= "Error editing the PEP: \n" + values
            wx.MessageBox(msg)
            self.onCancel(True)
        #self.loadListOfEquipments()
        self.equipment_edtview.Dialog.Close()
        return

    #------------------------------------------------------------------------------------------------------------
    def onCancel(self,evt):
        self.equipment_edtview.Dialog.Destroy()

#------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------
class EquipmentCountermeasureEditorController:

    def __init__(self, app, parent):
        self.app = app
        self.EquipmentView = parent
        self.equCou_view = EquipmentCountermeasureEditorView(self.EquipmentView.frame, self.app)

        #When Close the window destroy the wx instance
        self.equCou_view.Dialog.Bind(wx.EVT_CLOSE, self.onCancel)

        #Load the buttons of the view
        self.btnOK = xrc.XRCCTRL(self.equCou_view.Dialog, 'equCou_btnok')
        btnCancel = xrc.XRCCTRL(self.equCou_view.Dialog, 'equCou_btncancel')

        #Bind events to the buttons
        self.equCou_view.Dialog.Bind(wx.EVT_BUTTON, self.onAssignEquipmentCountermeasure, self.btnOK)
        self.equCou_view.Dialog.Bind(wx.EVT_BUTTON, self.onCancel, btnCancel)

        #Bind Events to the items in the ToolBar
        self.equCou_view.Dialog.Bind(wx.EVT_TOOL, self.onDelete, id=xrc.XRCID('equCou_tooldelete'))

        #Subscribe to the messages given by the model. In case of any change,
        # the list of elements will be updated in the GUI
        Publisher.subscribe(self.equCouModified, 'countermeasure_equipment_added')
        Publisher.subscribe(self.equCouModified, 'countermeasure_equipment_removed')


        #ID of the Equipment selected
        self.idEquipment = self.EquipmentView.getIDItemSelected()

        #Instance of the Countermeasure model
        #self.restriction = Restriction()
        self.countermeasure = Countermeasure()

        #Filters
        self.GUIcountermeasures = []
        self.GUIequ_countermeasures = []
        self.txtFilter1 = xrc.XRCCTRL(self.equCou_view.Dialog, 'equCou_txtfilter1')
        self.btnFilter1 = xrc.XRCCTRL(self.equCou_view.Dialog, 'equCou_btnfilter1')
        self.txtFilter2 = xrc.XRCCTRL(self.equCou_view.Dialog, 'equCou_txtfilter2')
        self.btnFilter2 = xrc.XRCCTRL(self.equCou_view.Dialog, 'equCou_btnfilter2')
        self.equCou_view.Dialog.Bind(wx.EVT_BUTTON, self.onFilter1, self.btnFilter1)
        self.equCou_view.Dialog.Bind(wx.EVT_TEXT_ENTER, self.onFilter1, self.txtFilter1)
        self.equCou_view.Dialog.Bind(wx.EVT_BUTTON, self.onFilter2, self.btnFilter2)
        self.equCou_view.Dialog.Bind(wx.EVT_TEXT_ENTER, self.onFilter2, self.txtFilter2)

        #Load the list of all available countermeasures and countermeasures of the selected equipment in the view
        self.loadListOfCountermeasures()
        self.loadListOfEquCou()

        #Display the view
        self.equCou_view.Show()
        return

    #-------------------------------------------------------------------------------------------------------
    def equCouModified(self, msg):
        self.loadListOfCountermeasures()
        self.loadListOfEquCou()
        return

    #-------------------------------------------------------------------------------------------------------
    def loadListOfCountermeasures(self):
        (error, list) = self.countermeasure.read_all()
        if error:
            msg= "Error reading the list of Mitigation Actions: \n" + list
            wx.MessageBox(msg)
            self.onCancel()
        else:
            # The countermeasure.read_all() method will return a list of tuples. Each tuple has the following values:
            # (idCountermeasure, Name, Description, Totally_Restrictive, FK_Equipment)

            #Exclude from the returned list the countermeasures already assigned to an equipment (FK_Equipment != Null)
            cou_list = []
            for cou in list:
                if not cou[4]:
                    cou_list.append(cou)

            self.GUIcountermeasures = cou_list
            self.equCou_view.loadListOfCountermeasures(cou_list)
        return

    #-------------------------------------------------------------------------------------------------------
    def loadListOfEquCou(self):
        (error, list) = self.countermeasure.read_all()
        if error:
            msg= "Error reading the list of Mitigation Actions: \n" + list
            wx.MessageBox(msg)
            self.onCancel()
        else:
            # The countermeasure.read_all() method will return a list of tuples. Each tuple has the following values:
            # (idCountermeasure, Name, Description, Totally_Restrictive, FK_Equipment)

            #Exclude from the returned list the countermeasures that aren't assigned to the
            # current equipment (FK_Equipment == idEquipment)
            cou_list = []
            for cou in list:
                if cou[4] == self.idEquipment:
                    cou_list.append(cou)

            self.GUIequ_countermeasures = cou_list
            self.equCou_view.loadListOfEquCou(cou_list)
        return

    #-------------------------------------------------------------------------------------------------------
    def onFilter1(self,event):
        new_list = []
        string = self.txtFilter1.GetValue().upper()
        if string !="":
            for item in self.GUIcountermeasures:
                for sub_item in item:
                    if type(sub_item) is str:
                        if any([string in sub_item.upper()]):
                            new_list.append(item)
                            break
            self.equCou_view.loadListOfCountermeasures(new_list)
        else:
            self.equCou_view.loadListOfCountermeasures(self.GUIcountermeasures)
        return
    #-------------------------------------------------------------------------------------------------------
    def onFilter2(self,event):
        new_list = []
        string = self.txtFilter2.GetValue().upper()
        if string !="":
            for item in self.GUIequ_countermeasures:
                for sub_item in item:
                    if type(sub_item) is str:
                        if any([string in sub_item.upper()]):
                            new_list.append(item)
                            break
            self.equCou_view.loadListOfEquCou(new_list)
        else:
            self.equCou_view.loadListOfEquCou(self.GUIequ_countermeasures)
        return
    #-------------------------------------------------------------------------------------------------------
    def onAssignEquipmentCountermeasure(self, evt):
        #Check if there is selected any item in the countermeasure list
        count = self.equCou_view.getItemCount(self.equCou_view.countermeasureList)
        if (count == 0):
            wx.MessageBox("Please select a Mitigation Action to be assigned to the PEP!")
        elif (count > 1):
            wx.MessageBox("Please select just one Mitigation Action be assigned to the PEP!")
        else:
            #Grab the id of the selected Countermeasure
            idCountermeasure = self.equCou_view.getIDItemSelected(self.equCou_view.countermeasureList)
            self.countermeasure.id = idCountermeasure
            self.countermeasure.FK_Equipment = self.idEquipment

            (error, value) = self.countermeasure.assignEquipment()
            if error:
                msg= "Error updating the PEP value of the Mitigation Action: \n" + value
                wx.MessageBox(msg)
                self.onCancel(True)
        Publisher.sendMessage("equipment_updated", None)
        return

    #-------------------------------------------------------------------------------------------------------
    def onDelete(self, evt):
        count = self.equCou_view.getItemCount(self.equCou_view.equCouList)
        if (count == 0):
            wx.MessageBox("Please select a Mitigation Action assigned to the PEP to be deleted!")
        else:
            msg = "Proceed to delete "+str(count)+" elements?"
            del_confirm = wx.MessageDialog(None, msg, 'Delete Confirmation', wx.YES_NO | wx.ICON_QUESTION)
            if del_confirm.ShowModal() == wx.ID_NO:
                return

            item_list = self.equCou_view.getSetItemsSelected(self.equCou_view.equCouList)

            for id_cou in item_list:
                self.countermeasure.id = id_cou
                self.countermeasure.FK_Equipment = self.idEquipment
                (error, values) = self.countermeasure.removeEquipment()
                if error:
                    msg= "There was an error deleting the Mitigation Actions assigned to the PEP: \n" + values
                    wx.MessageBox(msg)
                    self.onCancel(True)
        Publisher.sendMessage("equipment_updated", None)
        return

    #-------------------------------------------------------------------------------------------------------
    def onCancel(self,evt):
        self.equCou_view.Dialog.Destroy()
        return
