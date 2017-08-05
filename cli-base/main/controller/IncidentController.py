__author__ = 'ender_al'
# -*- coding: utf-8 *-*

import wx
from wx import xrc
from wx.lib.pubsub import Publisher

from view.IncidentView import IncidentView, IncidentEditorView, IncidentCountermeasureEditorView
from model.Countermeasure import Countermeasure
from model.IncidentHasCountermeasure import IncidentHasCountermeasure

class IncidentController:

    def __init__(self, app):
        self.app = app
        self.incident_view = IncidentView(app)

        #Items del Menú
        self.incident_view.frame.Bind(wx.EVT_MENU, self.onCreateIncident, id=xrc.XRCID('incident_mitcreate'))
        self.incident_view.frame.Bind(wx.EVT_MENU, self.onEditIncident, id=xrc.XRCID('incident_mitedit'))
        self.incident_view.frame.Bind(wx.EVT_MENU, self.onDeleteIncident, id=xrc.XRCID('incident_mitdelete'))
        self.incident_view.frame.Bind(wx.EVT_MENU, self.onExit, id=xrc.XRCID('incident_exit'))

        #ToolBar
        self.incident_view.frame.Bind(wx.EVT_TOOL, self.onCreateIncident, id=xrc.XRCID('incident_toolcreate'))
        self.incident_view.frame.Bind(wx.EVT_TOOL, self.onEditIncident, id=xrc.XRCID('incident_tooledit'))
        self.incident_view.frame.Bind(wx.EVT_TOOL, self.onDeleteIncident, id=xrc.XRCID('incident_tooldelete'))
        self.incident_view.frame.Bind(wx.EVT_TOOL, self.onRelationIncCou, id=xrc.XRCID('incident_toolinc-cou'))

        #Message from the Incident Model
        Publisher.subscribe(self.incidentModified, 'incident_deleted')
        Publisher.subscribe(self.incidentModified, 'IncidentHasCountermeasure_created')
        Publisher.subscribe(self.incidentModified, 'IncidentHasCountermeasure_deleted')
        Publisher.subscribe(self.incidentModified, 'incident_created')
        Publisher.subscribe(self.incidentModified, 'incident_updated')

        #Filter
        self.txtFilter = xrc.XRCCTRL(self.incident_view.frame, 'inc_txtfilter')
        self.btnFilter = xrc.XRCCTRL(self.incident_view.frame, 'inc_btnfilter')
        self.incident_view.frame.Bind(wx.EVT_TEXT_ENTER, self.onFilterIncident, self.txtFilter)
        self.incident_view.frame.Bind(wx.EVT_BUTTON, self.onFilterIncident, self.btnFilter)
        self.GUIincidents = []

        #Cargo la lista de incident
        self.loadListOfIncidents_controller()
        self.incident_view.show()

    #-------------------------------------------------------------------------------------------------------
    def loadListOfIncidents_controller(self):
        (error, list) = self.app.Incident.read_all()
        if error:
            msg= "Error reading the list of Detrimental Events: \n" + list
            wx.MessageBox(msg)
        else:
            #Create a list of incidents with the countermeasures assigned to it
            # The Incident.read_all() method will return a list of tuples. Each tuple has the following values:
            # (idIncident, Name, Description, Risk_Level)

            #Clear the Filter text
            self.txtFilter.SetValue("")

            countermeasure = Countermeasure()
            IncHasCou = IncidentHasCountermeasure()
            inc_list = []
            for inc in list:
                idInc = inc[0]
                nameInc = inc[1]
                descInc = inc[2]
                riskLevelInc = inc[3]

                # Select all the countermeasure assigned to the current incident
                IncHasCou.FK_Incident = idInc
                (IHC_error, IHC_list) = IncHasCou.readByIncident()
                if IHC_error:
                    msg= "Error reading the list of Mitigation Actions assigned to the Detrimental Event: \n" + IHC_list
                    wx.MessageBox(msg)
                    self.onExit(True)
                else:

                    couNameList = [] #list to save the names of the countermeasures assigned to the Incident

                    # The IncHasCou.readByIncident() method returns a list of tuples with the Countermeasures ID
                    # assigned to the current Incident
                    for IHC in IHC_list:
                        # For each Countermeasure assigned to the Incident, read its values
                        countermeasure.id = IHC[0]
                        (cou_error, cou_value) = countermeasure.read()
                        if cou_error:
                            msg= "Error reading the values of the Mitigation Action assigned to the Detrimental Event: \n" + cou_value
                            wx.MessageBox(msg)
                            self.onExit(True)
                        else:
                            # Add the name of the countermeasure to the list of the countermeasures assigned to the incident
                            couNameList.append(cou_value[0][1])

                    #Risk Level's Full Description
                    if inc[3] == 'L':
                        riskLevelInc = "Low"
                    elif inc[3] == 'M':
                        riskLevelInc = "Medium"
                    elif inc[3] == 'H':
                        riskLevelInc = "High"

                    inc_list.append([idInc, nameInc, descInc, riskLevelInc, ','.join(couNameList)])

            self.GUIincidents = inc_list
            self.incident_view.loadListOfIncidents(inc_list)

    #-------------------------------------------------------------------------------------------------------
    def onFilterIncident(self,event):
        new_list = []
        string = self.txtFilter.GetValue().upper()
        if string !="":
            for item in self.GUIincidents:
                for sub_item in item:
                    if type(sub_item) is str:
                        if any([string in sub_item.upper()]):
                            new_list.append(item)
                            break
            self.incident_view.loadListOfIncidents(new_list)
        else:
            self.incident_view.loadListOfIncidents(self.GUIincidents)
    #-------------------------------------------------------------------------------------------------------
    def incidentModified(self, mensaje):
        self.loadListOfIncidents_controller()

    #-------------------------------------------------------------------------------------------------------
    def onCreateIncident(self, evt):
        editor = IncidentEditorController(self.app,  self.incident_view, True)

    #-------------------------------------------------------------------------------------------------------
    def onEditIncident(self, evt):
        #Check if the dialog was already created
        inc_frame = self.app.main_frame.FindWindowByName("IncidentFrame")
        edt_diag = inc_frame.FindWindowByName("incidentEditor")

        if not edt_diag:
            count = self.incident_view.getItemCount()
            if (count == 0):
                wx.MessageBox("Please select a Detrimental Event to edit!")
            elif (count > 1):
                wx.MessageBox("Please select just one Detrimental Event to be edited!")
            else:
                editor = IncidentEditorController(self.app,  self.incident_view, False)
        else:
            edt_diag.Raise()

        return

    #-------------------------------------------------------------------------------------------------------
    def onDeleteIncident(self, evt):
        count = self.incident_view.getItemCount()
        if (count == 0):
            wx.MessageBox("Please select a Detrimental Event to be deleted!")
        else:
            msg = "Proceed to delete "+str(count)+" elements?"
            del_confirm = wx.MessageDialog(None, msg, 'Delete Confirmation', wx.YES_NO | wx.ICON_QUESTION)

            if del_confirm.ShowModal() == wx.ID_NO:
                return
            item_list = self.incident_view.getSetItemsSelected()

            for id in item_list:
                self.app.Incident.id = id
                (error, values) = self.app.Incident.delete()
                if error:
                    msg= "There was an error deleting the Detrimental Event: \n" + values
                    wx.MessageBox(msg)

    #-------------------------------------------------------------------------------------------------------
    def onRelationIncCou(self, evt):
        #Check if the dialog was already created
        inc_frame = self.app.main_frame.FindWindowByName("IncidentFrame")
        incCou_diag = inc_frame.FindWindowByName("incCouEditor")

        if not incCou_diag:
            count = self.incident_view.getItemCount()
            if (count == 0):
                wx.MessageBox("Please select a Detrimental Event to assign Mitigation Actions!")
            elif (count > 1):
                wx.MessageBox("Please select just one Detrimental Event to assign Mitigation Actions!")
            else:
                editor = IncidentCountermeasureEditorController(self.app, self.incident_view)
        else:
            incCou_diag.Raise()

        return

    #-------------------------------------------------------------------------------------------------------
    def onExit(self, evt):
       self.incident_view.frame.Destroy()

#-------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------
class IncidentEditorController:

    def __init__(self, app, parent, add=True):
        self.app = app
        self.IncidentView = parent
        self.incident_edtview = IncidentEditorView(self.IncidentView.frame, self.app, add)
        btnAddIncident = xrc.XRCCTRL(self.incident_edtview.Dialog, 'incident_btnedit')
        btnCancel = xrc.XRCCTRL(self.incident_edtview.Dialog, 'incident_btncancel')

        self.incident_edtview.Dialog.Bind(wx.EVT_BUTTON, self.onCancel, btnCancel)
        self.incident_edtview.Dialog.Bind(wx.EVT_CLOSE, self.onCancel)

        if(add):
            self.incident_edtview.Dialog.Bind(wx.EVT_BUTTON, self.onAddIncident, btnAddIncident)
            self.incident_edtview.Show()
        else:
            self.idIncident = self.IncidentView.getIDItemSelected()
            incident = self.app.Incident
            incident.id = self.idIncident
            (error, values) = incident.read()
            if error:
                msg= "Error reading the values from the Detrimental Event: \n" + values
                wx.MessageBox(msg)
            else:
                name = values[0][1]
                description = values[0][2]
                risk_level = values[0][3]
                IDRef = values[0][4]
                self.incident_edtview.loadIncident(name, description, risk_level, IDRef)
                self.incident_edtview.Dialog.Bind(wx.EVT_BUTTON, self.onEditIncident, btnAddIncident)
                self.incident_edtview.Show()

    #-------------------------------------------------------------------------------------------------------
    def onAddIncident(self, evt):
        idref = self.incident_edtview.incident_textIDRef.GetValue()
        name = self.incident_edtview.incident_textname.GetValue()
        description = self.incident_edtview.incident_textdescription.GetValue()
        risk_level = self.incident_edtview.incident_risklevel.GetCurrentSelection()

        if idref == '':
            self.incident_edtview.incident_textmsg.SetForegroundColour((255,0,0)) # set text color
            self.incident_edtview.incident_textmsg.SetLabel('* Mandatory Fields\nID cannot be empty!')
            return
        elif name == '':
            self.incident_edtview.incident_textmsg.SetForegroundColour((255,0,0)) # set text color
            self.incident_edtview.incident_textmsg.SetLabel('* Mandatory Fields\nName cannot be empty!')
            return

        incident = self.app.Incident
        incident.IDRef = idref
        incident.Name = name
        incident.Description = description

        if risk_level == 0:
            risk_level = 'L'
        elif risk_level == 1:
            risk_level = 'M'
        elif risk_level == 2:
            risk_level = 'H'

        incident.Risk_Level = risk_level
        error = incident.create()
        if error:
            msg= "Error creating Detrimental Events: \n"
            wx.MessageBox(msg)
            self.onCancel()
        #self.loadListOfIncidents()
        self.incident_edtview.Dialog.Close()
        return

    #-------------------------------------------------------------------------------------------------------
    def onEditIncident(self, evt):
        idref = self.incident_edtview.incident_textIDRef.GetValue()
        name = self.incident_edtview.incident_textname.GetValue()
        description = self.incident_edtview.incident_textdescription.GetValue()
        risk_level = self.incident_edtview.incident_risklevel.GetCurrentSelection()

        if idref == '':
            self.incident_edtview.incident_textmsg.SetForegroundColour((255,0,0)) # set text color
            self.incident_edtview.incident_textmsg.SetLabel('* Mandatory Fields\nID cannot be empty!')
            return
        elif name == '':
            self.incident_edtview.incident_textmsg.SetForegroundColour((255,0,0)) # set text color
            self.incident_edtview.incident_textmsg.SetLabel('* Mandatory Fields\nName cannot be empty!')
            return

        if risk_level == 0:
            risk_level = 'L'
        elif risk_level == 1:
            risk_level = 'M'
        elif risk_level == 2:
            risk_level = 'H'

        incident = self.app.Incident
        incident.id = self.idIncident

        incident.IDRef = idref
        incident.Name = name
        incident.Description = description
        incident.Risk_Level = risk_level
        (error, values) = incident.update()
        if error:
            msg= "Error editing the Detrimental Event: \n" + values
            wx.MessageBox(msg)
            self.onCancel()
        #self.loadListOfIncidents()
        self.incident_edtview.Dialog.Close()
        return

    #-------------------------------------------------------------------------------------------------------
    def onCancel(self,evt):
        self.incident_edtview.Dialog.Destroy()


#------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------
class IncidentCountermeasureEditorController:

    def __init__(self, app, parent):
        self.app = app
        self.IncidentView = parent
        self.incCou_view = IncidentCountermeasureEditorView(self.IncidentView.frame, self.app)

        #When Close the window destroy the wx instance
        self.incCou_view.Dialog.Bind(wx.EVT_CLOSE, self.onCancel)

        #Load the buttons of the view
        self.btnOK = xrc.XRCCTRL(self.incCou_view.Dialog, 'incCou_btnok')
        btnCancel = xrc.XRCCTRL(self.incCou_view.Dialog, 'incCou_btncancel')

        #Bind events to the buttons
        self.incCou_view.Dialog.Bind(wx.EVT_BUTTON, self.onAssignIncidentCountermeasure, self.btnOK)
        self.incCou_view.Dialog.Bind(wx.EVT_BUTTON, self.onCancel, btnCancel)

        #Bind Events to the items in the ToolBar
        self.incCou_view.Dialog.Bind(wx.EVT_TOOL, self.onDelete, id=xrc.XRCID('incCou_tooldelete'))

        #Subscribe to the messages given by the model. In case of any change,
        # the list of elements will be updated in the GUI
        Publisher.subscribe(self.incCouModified, 'IncidentHasCountermeasure_created')
        Publisher.subscribe(self.incCouModified, 'IncidentHasCountermeasure_deleted')

        #ID of the Incident selected
        self.idIncident = self.IncidentView.getIDItemSelected()

        #Instance of the Countermeasure and IncidentHasCountermeasure model
        self.IncHasCou = IncidentHasCountermeasure()
        self.countermeasure = Countermeasure()

        #Filters
        self.GUIcountermeasures = []
        self.GUIinc_countermeasures = []
        self.txtFilter1 = xrc.XRCCTRL(self.incCou_view.Dialog, 'incCou_txtfilter1')
        self.btnFilter1 = xrc.XRCCTRL(self.incCou_view.Dialog, 'incCou_btnfilter1')
        self.txtFilter2 = xrc.XRCCTRL(self.incCou_view.Dialog, 'incCou_txtfilter2')
        self.btnFilter2 = xrc.XRCCTRL(self.incCou_view.Dialog, 'incCou_btnfilter2')
        self.incCou_view.Dialog.Bind(wx.EVT_BUTTON, self.onFilter1, self.btnFilter1)
        self.incCou_view.Dialog.Bind(wx.EVT_TEXT_ENTER, self.onFilter1, self.txtFilter1)
        self.incCou_view.Dialog.Bind(wx.EVT_BUTTON, self.onFilter2, self.btnFilter2)
        self.incCou_view.Dialog.Bind(wx.EVT_TEXT_ENTER, self.onFilter2, self.txtFilter2)

        #Load the list of all available countermeasures and countermeasures of the selected incident in the view
        self.loadListOfCountermeasures()
        self.loadListOfIncCou()

        #Display the view
        self.incCou_view.Show()

    #-------------------------------------------------------------------------------------------------------
    def incCouModified(self, msg):
        self.loadListOfCountermeasures()
        self.loadListOfIncCou()

    #-------------------------------------------------------------------------------------------------------
    def loadListOfCountermeasures(self):
        (error, list) = self.countermeasure.read_all()
        if error:
            msg= "Error reading the list of Mitigation Actions: \n" + list
            wx.MessageBox(msg)
            self.onCancel(True)
        else:

            self.IncHasCou.FK_Incident = self.idIncident
            (IHC_error, IHC_list) = self.IncHasCou.readByIncident()
            #IncHasCou.readByIncident() will return a list of all the Countermeasures assigned to a given Incident
            if IHC_error:
                msg= "Error reading the list of Mitigation Actions assigned to the Detrimental Event: \n" + list
                wx.MessageBox(msg)
                self.onCancel(True)
            else:
                cou_list = []
                IHC = []
                #Convert the returned sequence of sequences from IncHasCou.readByIncident() into a single list of
                #countermeasures IDs
                for ihc in IHC_list:
                    IHC.append(ihc[0])

                for cou in list:
                    # The countermeasure.read_all() method will return a list of tuples. Each tuple has the following values:
                    # (idCountermeasure, Name, Description, Totally_Restrictive, FK_Equipment)
                    if not cou[0] in IHC: #Exclude from the list the countermeasures already assigned to an incident
                        cou_list.append(cou)

            self.GUIcountermeasures = cou_list
            self.incCou_view.loadListOfCountermeasures(cou_list)

    #-------------------------------------------------------------------------------------------------------
    def loadListOfIncCou(self):
        (error, list) = self.countermeasure.read_all()
        if error:
            msg= "Error reading the list of Mitigation Actions: \n" + list
            wx.MessageBox(msg)
            self.onCancel()
        else:
            self.IncHasCou.FK_Incident = self.idIncident
            (IHC_error, IHC_list) = self.IncHasCou.readByIncident()
            #IncHasCou.readByIncident() will return a list of all the Countermeasures assigned to a given Incident
            if IHC_error:
                msg= "Error reading the list of Mitigation Actions assigned to the Detrimental Event: \n" + IHC_list
                wx.MessageBox(msg)
                self.onCancel(True)
            else:
                cou_list = []
                IHC = []
                #Convert the returned sequence of sequences from IncHasCou.readByIncident() into a single list of
                #countermeasures IDs
                for ihc in IHC_list:
                    IHC.append(ihc[0])

                for cou in list:
                    # The countermeasure.read_all() method will return a list of tuples. Each tuple has the following values:
                    # (idCountermeasure, Name, Description, Totally_Restrictive, FK_Equipment)
                    if cou[0] in IHC: #Exclude from the list the countermeasures not assigned to the current incident
                        cou_list.append(cou)

            self.GUIinc_countermeasures = cou_list
            self.incCou_view.loadListOfIncCou(cou_list)
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
            self.incCou_view.loadListOfCountermeasures(new_list)
        else:
            self.incCou_view.loadListOfCountermeasures(self.GUIcountermeasures)
    #-------------------------------------------------------------------------------------------------------
    def onFilter2(self,event):
        new_list = []
        string = self.txtFilter2.GetValue().upper()
        if string !="":
            for item in self.GUIinc_countermeasures:
                for sub_item in item:
                    if type(sub_item) is str:
                        if any([string in sub_item.upper()]):
                            new_list.append(item)
                            break
            self.incCou_view.loadListOfIncCou(new_list)
        else:
            self.incCou_view.loadListOfIncCou(self.GUIinc_countermeasures)

    #-------------------------------------------------------------------------------------------------------
    def onAssignIncidentCountermeasure(self, evt):
        #Check if there is selected any item in the countermeasure list
        count = self.incCou_view.getItemCount(self.incCou_view.countermeasureList)
        if (count == 0):
            wx.MessageBox("Please select a Mitigation Action to be assigned to the Detrimental Event!")
        elif (count > 1):
            wx.MessageBox("Please select just one Mitigation Action be assigned to the Detrimental Event!")
        else:
            #Grab the id of the selected Countermeasure
            idCountermeasure = self.incCou_view.getIDItemSelected(self.incCou_view.countermeasureList)
            self.IncHasCou.FK_Countermeasure = idCountermeasure
            self.IncHasCou.FK_Incident = self.idIncident

            #Check if the Incident is already assigned to the Countermeasure
            (error_read, value_read) = self.IncHasCou.read()
            if error_read:
                msg= "Error reading the Mitigation Actions assigned to the Detrimental Event: \n" + value_read
                wx.MessageBox(msg)
                self.onCancel(True)
            else:
                if not value_read: #The Countermeasure is not assigned to the Incident
                    error = self.IncHasCou.create()
                    if error:
                        msg= "Error assigning the Mitigation Action to the Detrimental Event: \n" + value_read
                        wx.MessageBox(msg)
                        self.onCancel(True)
                else:
                    msg= "The Mitigation Action has already been assigned to the Detrimental Event!"
                    wx.MessageBox(msg)
        return

    #-------------------------------------------------------------------------------------------------------
    def onDelete(self, evt):
        count = self.incCou_view.getItemCount(self.incCou_view.incCouList)
        if (count == 0):
            wx.MessageBox("Please select a Mitigation Action assigned to the Detrimental Event to be deleted!")
        else:
            msg = "Proceed to delete "+str(count)+" elements?"
            del_confirm = wx.MessageDialog(None, msg, 'Delete Confirmation', wx.YES_NO | wx.ICON_QUESTION)
            if del_confirm.ShowModal() == wx.ID_NO:
                return

            item_list = self.incCou_view.getSetItemsSelected(self.incCou_view.incCouList)

            for id_cou in item_list:
                self.IncHasCou.FK_Countermeasure = id_cou
                self.IncHasCou.FK_Incident = self.idIncident
                (error, values) = self.IncHasCou.delete()
                if error:
                    msg= "There was an error deleting the Mitigation Actions assigned to the Detrimental Event: \n" + values
                    wx.MessageBox(msg)
                    self.onCancel(True)
        return

    #-------------------------------------------------------------------------------------------------------
    def onCancel(self,evt):
        self.incCou_view.Dialog.Destroy()
