__author__ = 'ender_al'
# -*- coding: utf-8 *-*

import wx
from wx import xrc
from wx.lib.pubsub import Publisher

from view.CountermeasureView import CountermeasureView
from view.CountermeasureView import CountermeasureEditorView
from controller.ARCController import ARCController
from controller.RestrictionController import RestrictionController
from controller.RMController import RMController
from model.Restriction import Restriction
from model.ARC import ARC
from model.RM import RM

class CountermeasureController:

    def __init__(self, app):

        self.app = app
        self.countermeasure_view = CountermeasureView(app)
        self.countermeasure_view.frame.Bind(wx.EVT_CLOSE, self.onExit)

        #Menu Items
        self.countermeasure_view.frame.Bind(wx.EVT_MENU, self.onCreateCountermeasure, id=xrc.XRCID('countermeasure_mitcreate'))
        self.countermeasure_view.frame.Bind(wx.EVT_MENU, self.onEditCountermeasure, id=xrc.XRCID('countermeasure_mitedit'))
        self.countermeasure_view.frame.Bind(wx.EVT_MENU, self.onDeleteCountermeasure, id=xrc.XRCID('countermeasure_mitdelete'))
        self.countermeasure_view.frame.Bind(wx.EVT_MENU, self.onExit, id=xrc.XRCID('countermeasure_exit'))

        #ToolBar
        self.countermeasure_view.frame.Bind(wx.EVT_TOOL, self.onCreateCountermeasure, id=xrc.XRCID('countermeasure_toolcreate'))
        self.countermeasure_view.frame.Bind(wx.EVT_TOOL, self.onEditCountermeasure, id=xrc.XRCID('countermeasure_tooledit'))
        self.countermeasure_view.frame.Bind(wx.EVT_TOOL, self.onDeleteCountermeasure, id=xrc.XRCID('countermeasure_tooldelete'))
        self.countermeasure_view.frame.Bind(wx.EVT_TOOL, self.onAssignRM, id=xrc.XRCID('countermeasure_toolcou-rm'))
        self.countermeasure_view.frame.Bind(wx.EVT_TOOL, self.onAssignARC, id=xrc.XRCID('countermeasure_toolcou-arc'))
        self.countermeasure_view.frame.Bind(wx.EVT_TOOL, self.onAssignRestriction, id=xrc.XRCID('countermeasure_toolcou-res'))

        # Subscribe to all the messages that may change the display of values in the GUI
        Publisher.subscribe(self.countermeasureModified, 'countermeasure_deleted')
        Publisher.subscribe(self.countermeasureModified, 'restriction_created')
        Publisher.subscribe(self.countermeasureModified, 'restriction_updated')
        Publisher.subscribe(self.countermeasureModified, 'restriction_deleted')
        Publisher.subscribe(self.countermeasureModified, 'rm_created')
        Publisher.subscribe(self.countermeasureModified, 'rm_updated')
        Publisher.subscribe(self.countermeasureModified, 'rm_deleted')
        Publisher.subscribe(self.countermeasureModified, 'arc_created')
        Publisher.subscribe(self.countermeasureModified, 'arc_updated')
        Publisher.subscribe(self.countermeasureModified, 'arc_deleted')
        Publisher.subscribe(self.countermeasureModified, 'countermeasure_created')
        Publisher.subscribe(self.countermeasureModified, 'countermeasure_updated')

        #Filter
        self.txtFilter = xrc.XRCCTRL(self.countermeasure_view.frame, 'cou_txtfilter')
        self.btnFilter = xrc.XRCCTRL(self.countermeasure_view.frame, 'cou_btnfilter')
        self.countermeasure_view.frame.Bind(wx.EVT_TEXT_ENTER, self.onFilterCountermeasure, self.txtFilter)
        self.countermeasure_view.frame.Bind(wx.EVT_BUTTON, self.onFilterCountermeasure, self.btnFilter)

        # Load the list of countermeasures to be displayed on the GUI
        self.GUIcountermeasures = []
        self.loadListOfCountermeasures_controller()
        self.countermeasure_view.show()

    #-------------------------------------------------------------------------------------------------
    def loadListOfCountermeasures_controller(self):
        (error, list) = self.app.Countermeasure.read_all()
        if error:
            msg= "Error reading the list of Mitigation Actions: \n" + list
            wx.MessageBox(msg)
        else:
            # The countermeasure.read_all() method will return a list of tuples. Each tuple has the following values:
            # (idCountermeasure, Name, Description, Totally_Restrictive, FK_Equipment)

            #Clear the Filter text
            self.txtFilter.SetValue("")

            # Create a list of countermeasures including its ARC and RM values along with the restrictions
            # to be displayed on the GUI
            cou_list = []
            for cou in list:
                idCou = cou[0]
                cou_name = cou[1]
                cou_desc = cou[2]

                #Load the RM of the Countermeasure
                risk_mitigation = RM()
                risk_mitigation.FK_Countermeasure = idCou
                (error, rm_val) = risk_mitigation.read_by_countermeasure()
                if error:
                    msg= "Error reading the Risk Mitigation value of the Mitigation Action: \n" + list
                    wx.MessageBox(msg)
                    self.onExit(True)
                else:
                    # The risk_mitigation.read_by_countermeasure() method will return a list of tuples.
                    # Each tuple has the following values:
                    # (idRM, EF, COV, Total, FK_Countermeasure)

                    # Save the total value that comes from the tuple
                    if len(rm_val)==0:
                        cou_RM = "N/A"
                    else:
                        cou_RM = rm_val[0][3]*100

                #Load the ARC of the Countermeasure
                annual_response_cost = ARC()
                annual_response_cost.FK_Countermeasure = idCou
                (error, arc_val) = annual_response_cost.read_by_countermeasure()
                if error:
                    msg= "Error reading the Risk Mitigation value of the Mitigation Action: \n" + list
                    wx.MessageBox(msg)
                    self.onExit(True)
                else:
                    # The annual_response_cost.read_by_countermeasure() method will return a list of tuples.
                    # Each tuple has the following values:
                    # (idARC, COI, COM, ODC, IC, Total, FK_Countermeasure)

                    # Save the total value that comes from the tuple
                    if len(arc_val)==0:
                        cou_ARC = "N/A"
                    else:
                        cou_ARC = arc_val[0][5]
                # If the countermeasure is totally restrictive it means that it does not have specific restrictions
                # else load the list of restrictions
                if cou[3]==1:
                    cou_list.append([idCou,cou_name,cou_desc,cou_RM,cou_ARC,'Totally Restrictive'])
                else:
                    # Load the list of restrictions
                    restriction = Restriction()
                    restriction.FK_Countermeasure = idCou
                    (error,r_list) = restriction.read_by_countermeasure()

                    if error:
                        msg= "Error reading the list of Restrictions of the Mitigation Action: \n" + list
                        wx.MessageBox(msg)
                        self.onExit(True)
                    else:
                        # The restriction.read_by_countermeasure() method will return a list of tuples. Each tuple has the following values:
                        # (idRestriction, Restriction, FK_Countermeasure)

                        # The GUI should display the information related to the name of the restricted Mitigation Actions,
                        # It's necessary to create a list with the right values
                        res_gui_list = []
                        for res in r_list:
                            #Read the name and description values of the restriction:
                            self.app.Countermeasure.id = res[1] #res[1] is the id of the countermeasure that will have a conflict
                            (error, value) = self.app.Countermeasure.read()
                            # The countermeasure.read() method will return a tuple with following values:
                            # (idCountermeasure, Name, Description, Totally_Restrictive, FK_Equipment)
                            if error:
                                msg= "Error reading the list of Mitigation Actions: \n" + list
                                wx.MessageBox(msg)
                                self.onExit(True)
                            else:
                                res_name = value[0][1]
                            # Append the name to the list to be displayed on the GUI
                            res_gui_list.append(res_name)

                        cou_list.append([idCou,cou_name,cou_desc,cou_RM,cou_ARC,','.join(res_gui_list)])

            self.GUIcountermeasures = cou_list
            self.countermeasure_view.loadListOfCountermeasures(cou_list)


    #-------------------------------------------------------------------------------------------------------
    def onFilterCountermeasure(self,event):
        new_list = []
        string = self.txtFilter.GetValue().upper()
        if string !="":
            for item in self.GUIcountermeasures:
                for sub_item in item:
                    if type(sub_item) is str:
                        if any([string in sub_item.upper()]):
                            new_list.append(item)
                            break
            self.countermeasure_view.loadListOfCountermeasures(new_list)
        else:
            self.countermeasure_view.loadListOfCountermeasures(self.GUIcountermeasures)

    #-------------------------------------------------------------------------------------------------
    def countermeasureModified(self, msg):
        self.loadListOfCountermeasures_controller()

    #-------------------------------------------------------------------------------------------------
    def onCreateCountermeasure(self, evt):
        editor = CountermeasureEditorController(self.app, self.countermeasure_view, True)

    #-------------------------------------------------------------------------------------------------
    def onEditCountermeasure(self, evt):
        #Check if the dialog was already created
        cou_frame = self.app.main_frame.FindWindowByName("CountermeasureFrame")
        edt_diag = cou_frame.FindWindowByName("countermeasureEditor")

        if not edt_diag:
            count = self.countermeasure_view.getItemCount()
            if (count == 0):
                wx.MessageBox("Please select a Mitigation Action to edit!")
            elif (count > 1):
                wx.MessageBox("Please select just one Mitigation Action to be edited!")
            else:
                editor = CountermeasureEditorController(self.app,  self.countermeasure_view, False)
        else:
            edt_diag.Raise()

        return

    #-------------------------------------------------------------------------------------------------
    def onDeleteCountermeasure(self, evt):
        count = self.countermeasure_view.getItemCount()
        if (count == 0):
            wx.MessageBox("Please select a Mitigation Action to be deleted!")
        else:
            msg = "Proceed to delete "+str(count)+" elements?"
            del_confirm = wx.MessageDialog(None, msg, 'Delete Confirmation', wx.YES_NO | wx.ICON_QUESTION)

            if del_confirm.ShowModal() == wx.ID_NO:
                return
            item_list = self.countermeasure_view.getSetItemsSelected()

            for id in item_list:
                self.app.Countermeasure.id = id
                (error, values) = self.app.Countermeasure.delete()
                if error:
                    msg= "There was an error deleting the Mitigation Action: \n" + values
                    wx.MessageBox(msg)

    #--------------------------------------------------------------------------------------------------
    def onAssignRM(self, evt):
        count = self.countermeasure_view.getItemCount()
        if (count == 0):
            wx.MessageBox("Please select a Mitigation Action to assign a RM value!")
        elif (count > 1):
            wx.MessageBox("Please select just one Mitigation Action to assign a RM value!")
        else:
            editor = RMController(self.app, self.countermeasure_view)

    #--------------------------------------------------------------------------------------------------
    def onAssignARC(self, evt):
        count = self.countermeasure_view.getItemCount()
        if (count == 0):
            wx.MessageBox("Please select a Mitigation Action to assign an ARC value!")
        elif (count > 1):
            wx.MessageBox("Please select just one Mitigation Action to assign an ARC value!")
        else:
            editor = ARCController(self.app, self.countermeasure_view)

    #-------------------------------------------------------------------------------------------------
    def onAssignRestriction(self, evt):
        count = self.countermeasure_view.getItemCount()
        if (count == 0):
            wx.MessageBox("Please select a Mitigation Action to assign a Restriction!")
        elif (count > 1):
            wx.MessageBox("Please select just one Mitigation Action to assign a Restriction!")
        else:
            #Grab the id of the Countermeasure selected
            idCountermeasure = self.countermeasure_view.getIDItemSelected()

            countermeasure = self.app.Countermeasure
            countermeasure.id = idCountermeasure
            (error, value) = countermeasure.read()

            if error:
                msg= "Error reading the values of the Mitigation Actions: \n" + value
                wx.MessageBox(msg)
                self.onCancel(True)
            else:
                # The returned value of the countermeasure.read() method has the following form:
                # [[idCountermeasure, Name, Description, Totally_Restrictive, FK_Equipment]]

                #Check if the Countermeasure is Totally Restrictive
                if value[0][3]:
                    msg= "The Mitigation Action selected is Totally Restrictive, so there is no need to assign Restrictions to it!"
                    wx.MessageBox(msg)
                else:
                    editor = RestrictionController(self.app, self.countermeasure_view)

    #-------------------------------------------------------------------------------------------------------
    def onExit(self, evt):
        self.countermeasure_view.frame.Destroy()

#-------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------
class CountermeasureEditorController:

    def __init__(self, app, parent, add=True):
        self.app = app
        self.CountermeasureView = parent
        self.countermeasure_edtview = CountermeasureEditorView(self.CountermeasureView.frame, self.app, add)
        btnAddCountermeasure = xrc.XRCCTRL(self.countermeasure_edtview.Dialog, 'countermeasure_btnedit')
        btnCancel = xrc.XRCCTRL(self.countermeasure_edtview.Dialog, 'countermeasure_btncancel')

        # Call the onCancel method when window close
        self.countermeasure_edtview.Dialog.Bind(wx.EVT_CLOSE, self.onCancel)

        self.countermeasure_edtview.Dialog.Bind(wx.EVT_BUTTON, self.onCancel, btnCancel)

        if(add):
            self.countermeasure_edtview.Dialog.Bind(wx.EVT_BUTTON, self.onAddCountermeasure, btnAddCountermeasure)
            self.countermeasure_edtview.Show()
        else:
            self.idCountermeasure = self.CountermeasureView.getIDItemSelected()
            countermeasure = self.app.Countermeasure
            countermeasure.id = self.idCountermeasure
            (error, values) = countermeasure.read()
            if error:
                msg= "Error reading the values from the Mitigation Action: \n" + values
                wx.MessageBox(msg)
            else:
                name = values[0][1]
                description = values[0][2]
                totally_restrictive = values[0][3]
                idref = values[0][5]
                self.countermeasure_edtview.loadCountermeasure(name, description, totally_restrictive,idref)
                self.countermeasure_edtview.Dialog.Bind(wx.EVT_BUTTON, self.onEditCountermeasure, btnAddCountermeasure)
                self.countermeasure_edtview.Show()

    #------------------------------------------------------------------------------------------------------------
    def onAddCountermeasure(self, evt):
        idref = self.countermeasure_edtview.countermeasure_textIDRef.GetValue()
        name = self.countermeasure_edtview.countermeasure_textname.GetValue()
        description = self.countermeasure_edtview.countermeasure_textdescription.GetValue()
        totally_restrictive = self.countermeasure_edtview.countermeasure_checkTotal.GetValue()

        if idref == '':
            self.countermeasure_edtview.countermeasure_textmsg.SetForegroundColour((255,0,0)) # set text color
            self.countermeasure_edtview.countermeasure_textmsg.SetLabel('* Mandatory Fields\nID cannot be empty!')
            return
        elif name == '':
            self.countermeasure_edtview.countermeasure_textmsg.SetForegroundColour((255,0,0)) # set text color
            self.countermeasure_edtview.countermeasure_textmsg.SetLabel('* Mandatory Fields\nName cannot be empty!')
            return

        countermeasure = self.app.Countermeasure
        countermeasure.IDRef = idref
        countermeasure.Name = name
        countermeasure.Description = description
        countermeasure.Totally_Restrictive = totally_restrictive

        error = countermeasure.create()
        if error:
            msg= "Error creating Mitigation Actions: \n"
            self.onCancel(True)
            wx.MessageBox(msg)
            return
        #self.loadListOfCountermeasures()
        self.countermeasure_edtview.Dialog.Close()
        return

    #------------------------------------------------------------------------------------------------------------
    def onEditCountermeasure(self, evt):

        idref = self.countermeasure_edtview.countermeasure_textIDRef.GetValue()
        name = self.countermeasure_edtview.countermeasure_textname.GetValue()
        description = self.countermeasure_edtview.countermeasure_textdescription.GetValue()
        totally_restrictive = self.countermeasure_edtview.countermeasure_checkTotal.GetValue()

        if idref == '':
            self.countermeasure_edtview.countermeasure_textmsg.SetForegroundColour((255,0,0)) # set text color
            self.countermeasure_edtview.countermeasure_textmsg.SetLabel('* Mandatory Fields\nID cannot be empty!')
            return
        elif name == '':
            self.countermeasure_edtview.countermeasure_textmsg.SetForegroundColour((255,0,0)) # set text color
            self.countermeasure_edtview.countermeasure_textmsg.SetLabel('* Mandatory Fields\nName cannot be empty!')
            return

        countermeasure = self.app.Countermeasure
        countermeasure.id = self.idCountermeasure
        countermeasure.IDRef = idref
        countermeasure.Name = name
        countermeasure.Description = description
        countermeasure.Totally_Restrictive = totally_restrictive
        (error, values) = countermeasure.update()
        if error:
            msg= "Error editing the Mitigation Action: \n" + values
            self.onCancel(True)
            wx.MessageBox(msg)
            return
        #self.loadListOfCountermeasures()
        self.countermeasure_edtview.Dialog.Close()
        return

    #------------------------------------------------------------------------------------------------------------
    def onCancel(self,evt):
        self.countermeasure_edtview.Dialog.Destroy()
        #self.countermeasure_edtview.Dialog.EndModal(wx.ID_CANCEL)

