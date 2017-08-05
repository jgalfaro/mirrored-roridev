__author__ = 'ender_al'

import wx
from wx import xrc
from wx.lib.pubsub import Publisher

from view.ARCView import ARCView
from model.ARC import ARC
from model.Countermeasure import Countermeasure
from decimal import *
from lib.utils import checkStringInputType

class ARCController:
    def __init__(self, app, parent):
        self.app = app
        self.CountermeasureView = parent
        self.arc_view = ARCView(self.CountermeasureView.frame, self.app)

        #Load the buttons of the view
        self.btnOK = xrc.XRCCTRL(self.arc_view.Dialog, 'arc_btnok')
        btnCancel = xrc.XRCCTRL(self.arc_view.Dialog, 'arc_btncancel')

        # Call the onCancel method when window close
        self.arc_view.Dialog.Bind(wx.EVT_CLOSE, self.onCancel)

        #Bind Events to the items in the ToolBar
        self.arc_view.Dialog.Bind(wx.EVT_TOOL, self.onDelete, id=xrc.XRCID('arc_tooldelete'))

        #Load the widget of check box to know if the total value will be given directly
        self.arc_totalok = xrc.XRCCTRL(self.arc_view.Dialog, 'arc_checktotal')

        #Bind events to the checkbox
        self.arc_view.Dialog.Bind(wx.EVT_CHECKBOX, self.onCheckBox, self.arc_totalok)

        #ID of the Countermeasure selected
        self.idCountermeasure = self.CountermeasureView.getIDItemSelected()

        #Instance of the ARC
        self.arc = ARC()

        #Check if the Countermeasure has already a ARC value assigned.
        self.checkARC()

        #Bind events to the buttons
        self.arc_view.Dialog.Bind(wx.EVT_BUTTON, self.onAssignARC, self.btnOK)
        self.arc_view.Dialog.Bind(wx.EVT_BUTTON, self.onCancel, btnCancel)

        #Display the view
        self.arc_view.Show()

    #------------------------------------------------------------------------------------------------------------
    def checkARC(self):
        #Check if the Countermeasure has already a ARC value assigned.
        self.arc.FK_Countermeasure = self.idCountermeasure
        (error, values) = self.arc.read_by_countermeasure()
        if error:
            msg= "Error reading the ARC value of the Mitigation Action: \n" + values
            wx.MessageBox(msg)
            self.arc_view.Dialog.Close()
        else:
            if not values:
                # If the Countermeasure don't have a value
                # set the addition mode to True
                self.add = True
            else:
                # If it already has a value, load them into the view
                # and set the addition mode to False
                self.arc_view.loadARCValues(values[0])
                self.idARC = values[0][0]
                self.add = False
        return

    #------------------------------------------------------------------------------------------------------------
    def onCheckBox(self,evt):
        if self.arc_totalok.IsChecked():
            self.arc_view.changeTextsInputs(True)
        else:
            self.arc_view.changeTextsInputs(False)
        return

    #------------------------------------------------------------------------------------------------------------
    def onAssignARC(self, evt):
        #Check if the user will give the Total value of ARC or each single cost and loss
        if self.arc_totalok.GetValue():
            #The ARC instance has the following variables to be defined before creating:
            #  idARC, COM, COI, ODC, IC, Total, FK_Countermeasure
            self.arc.COM = self.arc.COI = self.arc.ODC = self.arc.IC = 0

            self.arc.Total = self.arc_view.arc_total.GetValue()
            #Check if the values provided have a valid format
            #------------------------------------
            list_val = [self.arc.Total]
            if not checkStringInputType(list_val,"decimal"):
                wx.MessageBox("One of the inputs has an incorrect format")
                return False
            else:
                self.arc.Total = Decimal(self.arc.Total)

        else:
            self.arc.COM = 0 if self.arc_view.arc_COM.GetValue() == "" else self.arc_view.arc_COM.GetValue()
            self.arc.COI = 0 if self.arc_view.arc_COI.GetValue() == "" else self.arc_view.arc_COI.GetValue()
            self.arc.ODC = 0 if self.arc_view.arc_ODC.GetValue() == "" else self.arc_view.arc_ODC.GetValue()
            self.arc.IC = 0 if self.arc_view.arc_IC.GetValue() == "" else self.arc_view.arc_IC.GetValue()

            #Check if the values provided have a valid format
            #------------------------------------
            list_val = [self.arc.COM,self.arc.COI,self.arc.ODC,self.arc.IC]
            if not checkStringInputType(list_val,"decimal"):
                wx.MessageBox("One of the inputs has an incorrect format")
                return False
            else:
                self.arc.COM = Decimal(self.arc.COM)
                self.arc.COI = Decimal(self.arc.COI)
                self.arc.ODC = Decimal(self.arc.ODC)
                self.arc.IC = Decimal(self.arc.IC)

            #ARC Calculation Following the given in Gustavo's Thesis
            self.arc.Total = (self.arc.COM + self.arc.COI + self.arc.ODC + self.arc.IC)

        if self.arc.Total == 0:
            wx.MessageBox("The value of ARC could not be zero!!")
            return False

        #If everything is OK, Check if is and edition or a creation of the ARC value of the current Countermeasure

        self.arc.FK_Countermeasure = self.idCountermeasure

        if self.add:
            error = self.arc.create()
            if error:
                msg= "Error assigning the ARC value to the Mitigation Action"
                wx.MessageBox(msg)
        else:
            self.arc.id = self.idARC
            (error, values) = self.arc.update()
            if error:
                msg= "Error editing the ARC value of the Mitigation Action: \n" + values
                wx.MessageBox(msg)

        self.arc_view.Dialog.Close()
        return True

    #------------------------------------------------------------------------------------------------------------
    def onDelete(self, evt):

        if not self.idARC:
            wx.MessageBox("The Mitigation Action don't have an ARC value to be deleted!")
        else:
            msg = "Proceed to delete the ARC value?"
            del_confirm = wx.MessageDialog(None, msg, 'Delete Confirmation', wx.YES_NO | wx.ICON_QUESTION)
            if del_confirm.ShowModal() == wx.ID_NO:
                return

            self.arc.id = self.idARC
            (error, values) = self.arc.delete()
            if error:
                msg= "There was an error deleting the ARC value: \n" + values
                wx.MessageBox(msg)
                self.arc_view.Dialog.Close()

            self.arc_view.clearTextsInputs()
        return

    #------------------------------------------------------------------------------------------------------------
    def onCancel(self,evt):
        self.arc_view.Dialog.Destroy()
