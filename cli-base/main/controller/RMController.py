__author__ = 'ender_al'

import wx
from wx import xrc
from wx.lib.pubsub import Publisher

from view.RMView import RMView
from model.RM import RM
from model.Countermeasure import Countermeasure
from decimal import *
from lib.utils import checkStringInputType

class RMController:
    def __init__(self, app, parent):
        self.app = app
        self.CountermeasureView = parent
        self.rm_view = RMView(self.CountermeasureView.frame, self.app)

        #Load the buttons of the view
        self.btnOK = xrc.XRCCTRL(self.rm_view.Dialog, 'rm_btnok')
        btnCancel = xrc.XRCCTRL(self.rm_view.Dialog, 'rm_btncancel')

        # Call the onCancel method when window close
        self.rm_view.Dialog.Bind(wx.EVT_CLOSE, self.onCancel)

        #Bind Events to the items in the ToolBar
        self.rm_view.Dialog.Bind(wx.EVT_TOOL, self.onDelete, id=xrc.XRCID('rm_tooldelete'))

        #Load the widget of check box to know if the total value will be given directly
        self.rm_totalok = xrc.XRCCTRL(self.rm_view.Dialog, 'rm_checktotal')

        #Bind events to the checkbox
        self.rm_view.Dialog.Bind(wx.EVT_CHECKBOX, self.onCheckBox, self.rm_totalok)

        #ID of the Countermeasure selected
        self.idCountermeasure = self.CountermeasureView.getIDItemSelected()

        #Instance of the RM
        self.rm = RM()

        #Check if the Countermeasure has already a RM value assigned.
        self.checkRM()

        #Bind events to the buttons
        self.rm_view.Dialog.Bind(wx.EVT_BUTTON, self.onAssignRM, self.btnOK)
        self.rm_view.Dialog.Bind(wx.EVT_BUTTON, self.onCancel, btnCancel)

        #Display the view
        self.rm_view.Show()

    #------------------------------------------------------------------------------------------------------------
    def checkRM(self):
        #Check if the Countermeasure has already a RM value assigned.
        self.rm.FK_Countermeasure = self.idCountermeasure
        (error, values) = self.rm.read_by_countermeasure()
        if error:
            msg= "Error reading the RM value of the Mitigation Action: \n" + values
            wx.MessageBox(msg)
            self.rm_view.Dialog.Close()
        else:
            if not values:
                # If the Countermeasure don't have a value
                # set the addition mode to True
                self.add = True
            else:
                # If it already has a value, load them into the view
                # and set the addition mode to False
                # rm.read_by_countermeasure returns a tuple with the following values: idRM, EF, COV, Total, FK_Countermeasure
                rm_val = []
                #idRM
                rm_val.append(values[0][0])
                #EF
                rm_val.append(values[0][1]*100)
                #COV
                rm_val.append(values[0][2]*100)
                #Total
                rm_val.append(values[0][3]*100)
                #FK_Countermeasure
                rm_val.append(values[0][4])
                self.rm_view.loadRMValues(rm_val)
                self.idRM = values[0][0]
                self.add = False
        return

    #------------------------------------------------------------------------------------------------------------
    def onCheckBox(self,evt):
        if self.rm_totalok.IsChecked():
            self.rm_view.changeTextsInputs(True)
            self.rm_view.rm_total.Enable()
        else:
            self.rm_view.changeTextsInputs(False)
            self.rm_view.rm_total.Disable()
        return

    #------------------------------------------------------------------------------------------------------------
    def onAssignRM(self, evt):
        #The RM instance has the following variables to be defined before creating:
        # idRM, EF, COV, Total, FK_Countermeasure
        self.rm.EF = 0 if self.rm_view.rm_EF.GetValue() == "" else self.rm_view.rm_EF.GetValue()
        self.rm.COV = 0 if self.rm_view.rm_COV.GetValue() == "" else self.rm_view.rm_COV.GetValue()
        self.rm.Total = 0 if self.rm_view.rm_total.GetValue() == "" else self.rm_view.rm_total.GetValue()

        list_val = [self.rm.Total, self.rm.EF, self.rm.COV]

        if not checkStringInputType(list_val,"decimal"):
            wx.MessageBox("One of the inputs has an incorrect format")
            return False

        if not (0 <= Decimal(self.rm.Total) <= 100):
            wx.MessageBox("The Total value should be between 0 and 100")
            return False
        elif not (0 <= Decimal(self.rm.EF) <= 100):
            wx.MessageBox("The EF value should be between 0 and 100")
            return False
        elif not (0 <= Decimal(self.rm.COV) <= 100):
            wx.MessageBox("The COV value should be between 0 and 100")
            return False

        self.rm.EF = Decimal(self.rm.EF)/100
        self.rm.COV = Decimal(self.rm.COV)/100
        self.rm.Total = Decimal(self.rm.Total)/100

        #Check if the user has given the Total value of RM and/or each single values of EF and COV
        if self.rm_totalok.GetValue():

            if self.rm.Total != 0:
                if self.rm.COV != 0 and self.rm.EF == 0:
                    self.rm.EF = self.rm.Total/self.rm.COV
                elif self.rm.COV == 0 and self.rm.EF != 0:
                    self.rm.COV = self.rm.Total/self.rm.EF
                elif self.rm.COV != 0 and self.rm.EF != 0:
                    if not self.rm.Total == (self.rm.COV*self.rm.EF):
                        msg = "The Total value does not correspond to the product of COV and EF.\nDo you want to save the values anyway?"
                        save_confirm = wx.MessageDialog(None, msg, 'Save RM Values Confirmation', wx.YES_NO | wx.ICON_QUESTION)
                        if save_confirm.ShowModal() == wx.ID_NO:
                            return

        else:
            # If the EF and COV are provided, compute the Total RM value
            if self.rm.COV != 0 and self.rm.EF != 0:
                #RM Calculation Following the given in Gustavo's Thesis
                self.rm.Total = (self.rm.EF * self.rm.COV)

        #If everything is OK, Check if is an edition or a creation of the RM value of the current Countermeasure
        self.rm.FK_Countermeasure = self.idCountermeasure

        if self.add:
            error = self.rm.create(True)
            if error:
                msg= "Error assigning the RM value to the Mitigation Action"
                wx.MessageBox(msg)
        else:
            self.rm.id = self.idRM
            (error, values) = self.rm.update(True)
            if error:
                msg= "Error editing the RM value of the Mitigation Action: \n" + values
                wx.MessageBox(msg)

        self.rm_view.Dialog.Close()
        return True

    #------------------------------------------------------------------------------------------------------------
    def onDelete(self, evt):

        if not self.idRM:
            wx.MessageBox("The Mitigation Action don't have an RM value to be deleted!")
        else:
            msg = "Proceed to delete the RM value?"
            del_confirm = wx.MessageDialog(None, msg, 'Delete Confirmation', wx.YES_NO | wx.ICON_QUESTION)
            if del_confirm.ShowModal() == wx.ID_NO:
                return

            self.rm.id = self.idRM
            (error, values) = self.rm.delete()
            if error:
                msg= "There was an error deleting the RM value: \n" + values
                wx.MessageBox(msg)
                self.rm_view.Dialog.Close()

            self.rm_view.clearTextsInputs()
        return

    #------------------------------------------------------------------------------------------------------------
    def onCancel(self,evt):
        self.rm_view.Dialog.Destroy()
