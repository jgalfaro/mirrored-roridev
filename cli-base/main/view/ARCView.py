__author__ = 'ender_al'

try:
    import wx
except ImportError:
    raise ImportError,"wxPython module is required"

from wx import xrc

class ARCView:
    def __init__(self, parent, app):
        self.app = app
        self.Dialog = self.app.res.LoadDialog(parent, 'ARCEditor')
        self.Dialog.SetSize((330,330))

        #Load the widgets related to the ARC
        self.arc_container = xrc.XRCCTRL(self.Dialog, 'arc_container')
        self.arc_COI = xrc.XRCCTRL(self.Dialog, 'arc_textcoi')
        self.arc_COM = xrc.XRCCTRL(self.Dialog, 'arc_textcom')
        self.arc_ODC = xrc.XRCCTRL(self.Dialog, 'arc_textodc')
        self.arc_IC = xrc.XRCCTRL(self.Dialog, 'arc_textic')
        self.arc_total = xrc.XRCCTRL(self.Dialog, 'arc_texttotal')

        #Load the Check Button used to know if the total value will be given
        self.arc_totalok = xrc.XRCCTRL(self.Dialog, 'arc_checktotal')

        #Load the Button
        btnAssignIncident = xrc.XRCCTRL(self.Dialog, 'arc_btnok')
        btnAssignIncident.SetLabel('Assign')

    #-------------------------------------------------------------------------------------------------------
    def Show(self):
        self.Dialog.ShowModal()

    #-------------------------------------------------------------------------------------------------------
    def loadARCValues(self, values):
        #The 'values' variable has the following form
        # idARC, COI, COM, ODC, IC, Total, FK_Countermeasure
        # the following condition will check if all the values related to losses and and costs (COI, COM, ODC, IC) are equal to zero
        # In that case it means that the user had gave the total ARC value
        if values[1] == values[2] == values[3] == values[4] == 0.00:
            #wx.MessageBox("Es un total")
            self.arc_totalok.SetValue(True)
            self.changeTextsInputs(True)
            #Display the "Total" ARC from the values array
            self.arc_total.SetValue(str(values[5]))
        else:
            #The user had gave individual losses and costs values
            self.changeTextsInputs(False)
            self.arc_totalok.SetValue(False)

            self.arc_COI.SetValue(str(values[1]))
            self.arc_COM.SetValue(str(values[2]))
            self.arc_ODC.SetValue(str(values[3]))
            self.arc_IC.SetValue(str(values[4]))

            self.arc_total.SetValue(str(values[5]))

    #-------------------------------------------------------------------------------------------------------
    def changeTextsInputs(self, is_total):
        #Disable the single costs text fields and enable the 'Total' text field if the user will provide the total cost
        # otherwise disable the 'Total' text fields and enable the single costs text field
        if is_total:

            self.clearTextsInputs()
            #Disable the cost text fields
            self.arc_COI.Disable()
            self.arc_COM.Disable()
            self.arc_ODC.Disable()
            self.arc_IC.Disable()

            #Enable the Total and Annual Rate of Occurrence text field
            self.arc_total.Enable()
        else:
            self.arc_COI.Enable()
            self.arc_COM.Enable()
            self.arc_ODC.Enable()
            self.arc_IC.Enable()
            #Disable the Total text field
            self.arc_total.Disable()
        return

    #-------------------------------------------------------------------------------------------------------
    def clearTextsInputs(self):
        #Clear the Values in the Losses and costs text fields
        self.arc_COI.SetValue("0.00")
        self.arc_COM.SetValue("0.00")
        self.arc_ODC.SetValue("0.00")
        self.arc_IC.SetValue("0.00")
        self.arc_total.SetValue("0.00")

