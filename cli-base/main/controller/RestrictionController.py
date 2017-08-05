__author__ = 'ender_al'

import wx
from wx import xrc
from wx.lib.pubsub import Publisher

from view.RestrictionView import RestrictionView
from model.Restriction import Restriction
from model.Countermeasure import Countermeasure

class RestrictionController:
    def __init__(self, app, parent):
        self.app = app
        self.CountermeasureView = parent
        self.restriction_view = RestrictionView(self.CountermeasureView.frame, self.app)

        #When Close the window destroy the wx instance
        self.restriction_view.Dialog.Bind(wx.EVT_CLOSE, self.onCancel)

        #Load the buttons of the view
        self.btnOK = xrc.XRCCTRL(self.restriction_view.Dialog, 'restriction_btnok')
        btnCancel = xrc.XRCCTRL(self.restriction_view.Dialog, 'restriction_btncancel')

        #Bind events to the buttons
        self.restriction_view.Dialog.Bind(wx.EVT_BUTTON, self.onAssignCountermeasureRestriction, self.btnOK)
        self.restriction_view.Dialog.Bind(wx.EVT_BUTTON, self.onCancel, btnCancel)

        #Bind Events to the items in the ToolBar
        self.restriction_view.Dialog.Bind(wx.EVT_TOOL, self.onDelete, id=xrc.XRCID('restriction_tooldelete'))

        #Subscribe to the messages given by the model. In case of any change, the list of elements will be updated
        Publisher.subscribe(self.restrictionModified, 'restriction_created')
        Publisher.subscribe(self.restrictionModified, 'restriction_updated')
        Publisher.subscribe(self.restrictionModified, 'restriction_deleted')

        #ID of the Countermeasure selected
        self.idCountermeasure = self.CountermeasureView.getIDItemSelected()

        #Instance of the Restriction, Countermeasure model
        self.restriction = Restriction()
        self.countermeasure = Countermeasure()

        #Filters
        self.GUIcountermeasures = []
        self.GUIrestrictions = []
        self.txtFilter1 = xrc.XRCCTRL(self.restriction_view.Dialog, 'restriction_txtfilter1')
        self.btnFilter1 = xrc.XRCCTRL(self.restriction_view.Dialog, 'restriction_btnfilter1')
        self.txtFilter2 = xrc.XRCCTRL(self.restriction_view.Dialog, 'restriction_txtfilter2')
        self.btnFilter2 = xrc.XRCCTRL(self.restriction_view.Dialog, 'restriction_btnfilter2')
        self.restriction_view.Dialog.Bind(wx.EVT_BUTTON, self.onFilter1, self.btnFilter1)
        self.restriction_view.Dialog.Bind(wx.EVT_TEXT_ENTER, self.onFilter1, self.txtFilter1)
        self.restriction_view.Dialog.Bind(wx.EVT_BUTTON, self.onFilter2, self.btnFilter2)
        self.restriction_view.Dialog.Bind(wx.EVT_TEXT_ENTER, self.onFilter2, self.txtFilter2)

        #Load the list of countermeasures and restrictions of the selected countermeasure in the view
        self.loadListOfCountermeasures()
        self.loadListOfRestrictions()

        #Display the view
        self.restriction_view.Show()

    #-------------------------------------------------------------------------------------------------------
    def restrictionModified(self, msg):
        self.loadListOfRestrictions()

    #-------------------------------------------------------------------------------------------------------
    def loadListOfCountermeasures(self):
        (error, list) = self.countermeasure.read_all()
        if error:
            msg= "Error reading the list of Mitigation Actions: \n" + list
            wx.MessageBox(msg)
            self.onCancel()
        else:
            # The countermeasure.read_all() method will return a list of tuples. Each tuple has the following values:
            # (idCountermeasure, Name, Description, Totally_Restrictive)

            #Exclude from the returned list the current countermeasure
            cou_list = []
            for cou in list:
                if cou[0] != self.idCountermeasure:
                    cou_list.append(cou)

            self.GUIcountermeasures = cou_list
            self.restriction_view.loadListOfCountermeasures(cou_list)

    #-------------------------------------------------------------------------------------------------------
    def loadListOfRestrictions(self):
        self.restriction.FK_Countermeasure = self.idCountermeasure
        (error, list) = self.restriction.read_by_countermeasure()
        if error:
            msg= "Error reading the list of Restrictions of the Mitigation Action: \n" + list
            wx.MessageBox(msg)
            self.onCancel(True)
        else:
            # The restriction.read_by_countermeasure() method will return a list of tuples. Each tuple has the following values:
            # (idRestriction, Restriction, FK_Countermeasure)

            # The GUI should display the information related to the restricted countermeasures, such as name and description:
            # not only the ids. It's necessary to create a list with the right values
            res_list = []
            for res in list:
                idRestriction = res[0]

                #Read the name and description values of the restriction:
                self.countermeasure.id = res[1] #res[1] is the id of the countermeasure that will have a conflict
                (error, value) = self.countermeasure.read()
                # The countermeasure.read() method will return a tuple with following values:
                # (idCountermeasure, Name, Description, Totally_Restrictive)
                if error:
                    msg= "Error reading the list of Mitigation Actions: \n" + list
                    wx.MessageBox(msg)
                    self.onCancel(True)
                else:
                    res_name = value[0][1]
                    res_desc = value[0][2]

                # Append the values to the list to be displayed on the GUI
                res_list.append([idRestriction,res_name,res_desc])

            self.GUIrestrictions = res_list
            self.restriction_view.loadListOfRestrictions(res_list)
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
            self.restriction_view.loadListOfCountermeasures(new_list)
        else:
            self.restriction_view.loadListOfCountermeasures(self.GUIcountermeasures)
    #-------------------------------------------------------------------------------------------------------
    def onFilter2(self,event):
        new_list = []
        string = self.txtFilter2.GetValue().upper()
        if string !="":
            for item in self.GUIrestrictions:
                for sub_item in item:
                    if type(sub_item) is str:
                        if any([string in sub_item.upper()]):
                            new_list.append(item)
                            break
            self.restriction_view.loadListOfRestrictions(new_list)
        else:
            self.restriction_view.loadListOfRestrictions(self.GUIrestrictions)

    #-------------------------------------------------------------------------------------------------------
    def onAssignCountermeasureRestriction(self, evt):
        #Check if there is selected any item in the countermeasure list
        count = self.restriction_view.getItemCount(self.restriction_view.countermeasureList)
        if (count == 0):
            wx.MessageBox("Please select a Mitigation Action to assign a Restriction!")
        elif (count > 1):
            wx.MessageBox("Please select just one Mitigation Action to assign a Restriction!")
        else:
            #Grab the id of the selected Countermeasure
            idRestriction = self.restriction_view.getIDItemSelected(self.restriction_view.countermeasureList)
            self.restriction.Restriction = idRestriction
            self.restriction.FK_Countermeasure = self.idCountermeasure

            #Check if the Restriction is already assigned to the Countermeasure
            (error, value) = self.restriction.read_by_restriction_countermeasure()

            if error:
                msg= "Error reading the Restriction value of the Mitigation Action: \n" + value
                wx.MessageBox(msg)
                self.onCancel(True)
            else:
                if not value:
                    self.restriction.create()
                else:
                    wx.MessageBox("Restriction already assigned to the Mitigation Action!")
        return

    #-------------------------------------------------------------------------------------------------------
    def onDelete(self, evt):
        count = self.restriction_view.getItemCount(self.restriction_view.restrictionList)
        if (count == 0):
            wx.MessageBox("Please select a Restriction in the list to be deleted!")
        else:
            msg = "Proceed to delete "+str(count)+" elements?"
            del_confirm = wx.MessageDialog(None, msg, 'Delete Confirmation', wx.YES_NO | wx.ICON_QUESTION)
            if del_confirm.ShowModal() == wx.ID_NO:
                return

            item_list = self.restriction_view.getSetItemsSelected(self.restriction_view.restrictionList)

            for id_restriction in item_list:
                self.restriction.id = id_restriction
                (error, values) = self.restriction.delete()
                if error:
                    msg= "There was an error deleting the restriction of the Mitigation Action: \n" + values
                    wx.MessageBox(msg)
                    self.onCancel(True)
        return

    #-------------------------------------------------------------------------------------------------------
    def onCancel(self,evt):
        self.restriction_view.Dialog.Destroy()
