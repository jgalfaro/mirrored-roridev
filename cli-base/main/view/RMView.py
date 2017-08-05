__author__ = 'ender_al'

try:
    import wx
except ImportError:
    raise ImportError,"wxPython module is required"

from wx import xrc

class RMView:
    def __init__(self, parent, app):
        self.app = app
        self.Dialog = self.app.res.LoadDialog(parent, 'RMEditor')
        self.Dialog.SetSize((295,235))

        #Load the widgets related to the RM
        self.rm_container = xrc.XRCCTRL(self.Dialog, 'rm_container')
        self.rm_EF = xrc.XRCCTRL(self.Dialog, 'rm_textef')
        self.rm_COV = xrc.XRCCTRL(self.Dialog, 'rm_textcov')
        self.rm_total = xrc.XRCCTRL(self.Dialog, 'rm_texttotal')

        #Load the Check Button used to know if the total value will be given
        self.rm_totalok = xrc.XRCCTRL(self.Dialog, 'rm_checktotal')

        #Load the Button
        btnAssignIncident = xrc.XRCCTRL(self.Dialog, 'rm_btnok')
        btnAssignIncident.SetLabel('Assign')

    #-------------------------------------------------------------------------------------------------------
    def Show(self):
        self.Dialog.ShowModal()

    #-------------------------------------------------------------------------------------------------------
    def loadRMValues(self, values):
        #The 'values' variable has the following form
        # idRM, EF, COV, Total, FK_Countermeasure
        self.rm_EF.SetValue(str(values[1]))
        self.rm_COV.SetValue(str(values[2]))
        self.rm_total.SetValue(str(values[3]))

    #-------------------------------------------------------------------------------------------------------
    def changeTextsInputs(self, is_total):
        #Disable the single costs text fields and enable the 'Total' text field if the user will provide the total cost
        # otherwise disable the 'Total' text fields and enable the single costs text field
        if is_total:
            #self.clearTextsInputs()
            #Disable the cost text fields
            #self.rm_EF.Disable()
            #self.rm_COV.Disable()

            #Enable the Total and Annual Rate of Occurrence text field
            self.rm_total.Enable()
        else:
            #self.rm_EF.Enable()
            #self.rm_COV.Enable()

            #Disable the Total text field
            self.rm_total.Disable()
        return

    #-------------------------------------------------------------------------------------------------------
    def clearTextsInputs(self):
        #Clear the Values in the Losses and costs text fields
        self.rm_EF.SetValue("0.00")
        self.rm_COV.SetValue("0.00")
        self.rm_total.SetValue("0.00")

