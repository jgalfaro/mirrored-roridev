__author__ = 'ender_al'
# -*- coding: utf-8 *-*

import wx
from wx import xrc
from itertools import combinations

from view.RORICalView import RORICalView, RORIResultsView, RMDialog, EFDialog
from model.Organization import Organization
from model.Incident import Incident
from model.Countermeasure import Countermeasure
from model.RORICal import RORICal
from model import ALE,AEV,ARC,RM,Equipment
from lib.utils import checkStringInputType
from decimal import Decimal
from lxml import etree
from datetime import datetime
import subprocess as sub
import os

class RORICalController:

    def __init__(self, app):
       self.app = app
       self.RORICal_view = RORICalView(app)

       #Menu Items
       #self.RORICal_view.frame.Bind(wx.EVT_MENU, self.onCreateRORICal, id=xrc.XRCID('roriCal_mitcreate'))
       #self.RORICal_view.frame.Bind(wx.EVT_MENU, self.onEditRORICal, id=xrc.XRCID('RORICal_mitedit'))
       #self.RORICal_view.frame.Bind(wx.EVT_MENU, self.onDeleteRORICal, id=xrc.XRCID('RORICal_mitdelete'))
       self.RORICal_view.frame.Bind(wx.EVT_MENU, self.onExit, id=xrc.XRCID('RORICal_exit'))

       #Bind a method for each time an Organization is selected in the view
       self.RORICal_view.frame.Bind(wx.EVT_CHOICE, self.onSelectedOrganization, self.RORICal_view.orgListChoice)
       #List to save the ID of the organizations, it will be used to know which organization is selected from the
       #list of choices in the view
       self.orgListID = []

       #Bind a method for each time an Incident is selected in the view
       self.RORICal_view.frame.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onSelectedIncident, self.RORICal_view.incidentList)

       #Bind a method when the Calculation button is pressed
       self.RORICal_view.frame.Bind(wx.EVT_BUTTON, self.onPerformCalculation, self.RORICal_view.calculationButton)

       #Instance of model
       self.Organization = Organization()
       self.Incident = Incident()
       self.Countermeasure = Countermeasure()
       self.RORICal = RORICal()

       #
       self.incidents = []
       self.organizations_names = []

       #IDs of the elements required to start the calculation of the RORI index
       self.idOrg = 0
       self.idInc = 0

       #Load list of Organizations
       self.loadListOfOrganizations_controller()
       self.RORICal_view.show()

    #------------------------------------------------------------------------------------------------------------
    def loadListOfOrganizations_controller(self):
        (error, values) = self.Organization.read_all()
        #List to be passed to the view with the names of the organizations
        orgNames = []
        if error:
            msg= "Error reading the list of Organizations: \n" + values
            wx.MessageBox(msg)
        else:
            #
            for organization in values:
                self.orgListID.append(organization[0])
                orgNames.append(organization[1])

            self.RORICal_view.loadListOfOrganizations(orgNames)
            self.organizations_names = orgNames

    #------------------------------------------------------------------------------------------------------------
    def onSelectedOrganization(self, evt):
        # Each time an Organization is selected in the view, grab its ID from the orgListID and display the list of
        # Incidents assigned to the Organization in the view
        self.idOrg = self.orgListID.__getitem__(self.RORICal_view.orgListChoice.GetCurrentSelection())
        self.RORICal.idOrg = self.idOrg

        # Fetch the Incidents assigned to the Organization
        (error, values) = self.RORICal.readOrgInc()
        if error:
            msg= "Error reading the list of Detrimental Events of the Organizations: \n" + values
            wx.MessageBox(msg)
        else:
            if not values:
                msg= "The Organization does not have any Detrimental Events assigned"
                wx.MessageBox(msg)
                #If there are not Incidents assigned, clear the lists and disable the calculation button
                self.RORICal_view.incidentList.ClearAll()
                self.RORICal_view.countermeasureList.ClearAll()
                self.RORICal_view.calculationButton.Disable()
            else:
                self.RORICal_view.loadListOfIncidents(values)
                self.incidents = values

        return

    #------------------------------------------------------------------------------------------------------------
    def onSelectedIncident(self, evt):
        # Each time an Incident is selected in the view, grab its ID and display the list of
        # Countermeasures assigned

        count = self.RORICal_view.getIncidentItemCount()
        if (count > 1):
            wx.MessageBox("The RORI evaluation can be performed just on one Detrimental Event at a time!")
            self.RORICal_view.countermeasureList.ClearAll()
        elif (count == 1):
            # Load information about countermeasures assigned to the selected Incident
            self.idInc = self.RORICal_view.getIDIncidentItemSelected()
            self.RORICal.idInc = self.idInc
            # Fetch the Countermeasures assigned to the Incident
            (error, values) = self.RORICal.readIncCou()
            if error:
                msg= "Error reading the list of Mitigation Actions assigned to the Detrimental Event: \n" + values
                wx.MessageBox(msg)
            else:
                if not values:
                    msg= "The Detrimental Event does not have any Mitigation Actions assigned"
                    wx.MessageBox(msg)
                    #If there are not Countermeasures assigned, clear the lists and disable the calculation button
                    self.RORICal_view.countermeasureList.ClearAll()
                    self.RORICal_view.calculationButton.Disable()
                else:
                    # Enable the Calculation Button
                    self.RORICal_view.calculationButton.Enable()
                    self.RORICal_view.loadListOfCountermeasures(values)

        return
    #------------------------------------------------------------------------------------------------------------
    def onPerformCalculation(self, evt):
        # If the frame that displays the results is already created raised it, otherwise create a new instance
        frame = self.app.main_frame.FindWindowByName("RORIResults_Frame")
        if not frame:
            for inc in self.incidents:
                if self.idInc == inc[0]:
                    incName = inc[1]
                    incIDRef = inc[2]

            orgName = self.organizations_names.__getitem__(self.RORICal_view.orgListChoice.GetCurrentSelection())
            self.RORIResultsController = RORIResultsController(self.app, self.RORICal_view, self.idOrg, self.idInc, orgName, incName, incIDRef)
        else:
            frame.Raise()
        return


    #------------------------------------------------------------------------------------------------------------
    def onExit(self, evt):
       self.RORICal_view.frame.Destroy()


#------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------
class RORIResultsController:

    def __init__(self, app, parent, idOrg, idInc, orgName, incName, incIDRef):
        self.app = app
        self.RORICalView = parent
        self.RORIResults_View = RORIResultsView(self.RORICalView.frame, self.app)

        # Instance of radioBox with combination criteria displayed on the GUI
        self.radioBox_CombCriteria = xrc.XRCCTRL(self.RORIResults_View.results_frame, 'rori_CombCriteria')
        # Bind an event to the radioBox to get the criteria selected
        self.RORIResults_View.results_frame.Bind(wx.EVT_RADIOBOX, self.onCriteriaSelected, self.radioBox_CombCriteria)

        #Combinations criteria are All Countermeasures (0, Default), Above Individual RORI average (1), Custom Selection
        # of countermeasures (2) and Combination Threshold (3)
        self.SelectedCriteria = 0

        # CombinationThreshold will be given by the user; is used to exclude from the combined evaluation all the
        # countermeasures which individual RORI index is bellow it's value.
        self.CombinationThreshold = 0

        # Bind to the Combination Button the event handler
        self.RORIResults_View.results_frame.Bind(wx.EVT_BUTTON, self.onCombinedEvaluationButton, id=xrc.XRCID('rori_btnComb'))

        #Instance of models used to retrieve data from DB in order to perform RORI evaluation
        self.RORICal = RORICal()
        self.ARC = ARC.ARC()
        self.RM = RM.RM()
        self.ALE = ALE.ALE()
        self.AEV = AEV.AEV()
        self.Equipment = Equipment.Equipment()

        self.idOrg = idOrg
        self.orgName = orgName
        self.idInc = idInc
        self.incName = incName
        self.incIDRef = incIDRef

        self.toBeCombined = True
        self.informationRequired = True
        self.AIV_value = 0
        self.ALE_value = 0

        #Perform Individual Evaluation
        self.rori_ind = self.performIndividualEvaluation()
        if self.rori_ind != False:
            self.RORIResults_View.showResults()
            # Discard countermeasures that doesn't have the individual COV and EF values
            cou_to_combine = self.discardCouNotCombinable(self.rori_ind)
            # Perform the Default Combined Evaluation
            if len(cou_to_combine):
                self.performCombinedEvaluation(cou_to_combine)
        else:
            msg = "Error performing the RORI evaluation!!!"
            wx.MessageBox(msg, style=wx.OK|wx.ICON_ERROR)
            return


    #-------------------------------------------------------------------------------------------------
    def onCriteriaSelected(self,event):
        self.SelectedCriteria = self.radioBox_CombCriteria.GetSelection()
        self.RORIResults_View.selectAllItems(False)

        #Custom Selection
        if self.SelectedCriteria == 2:
            wx.MessageBox("Select the Mitigation Actions to be combined from the list with individual RORI results")
            self.RORIResults_View.selectAllItems(True)
        #If the Criteria Selected is 3 (Give an specific threshold) pop a Dialog asking for the threshold value
        elif self.SelectedCriteria == 3:
            self.RORIResults_View.loadThresholdDialog()
            threshold = self.RORIResults_View.TDialog.GetValue()
            if not checkStringInputType(threshold,"decimal"):
                wx.MessageBox("Threshold has an incorrect format")
                return
            else:
                self.CombinationThreshold = Decimal(threshold)
                label = "Above Specific Threshold: "+ threshold
                self.radioBox_CombCriteria.SetItemLabel(3,label)

            self.RORIResults_View.TDialog.Destroy()
    #---------------------------------------------------------------------------------------------
    def discardCouNotCombinable(self, cou_to_combine):
        cou = ""
        new_cou = []

        for ind in cou_to_combine:
            if not self.rori_countermeasures[ind['countermeasure']]['to_combine']:
                cou += "\n - "+ind['countermeasure_name']
            else:
                new_cou.append(ind)

        if cou != "":
            message = "The Mitigation Actions:"+cou
            message += "\n\nWill not be included in the combined RORI evaluation due to missing information about COV and EF."
            wx.MessageBox(message)

        return new_cou

    #---------------------------------------------------------------------------------------------
    def onCombinedEvaluationButton(self,event):
            # Perform the combination based on the Selected Criteria:
            # 0 - Combine all countermeasures (Default Criteria)
            # 1 - Combine only the countermeasures above the average RORI index on the individual countermeasure evaluation
            # 2 - Combination of selected countermeasures
            # 3 - Above an specific threshold

            if self.SelectedCriteria == 0:
                # Pass all the countermeasures with the individual RORI evaluation
                new_cou = self.rori_ind
            elif self.SelectedCriteria == 1:
                rori_sum = 0
                for ind in self.rori_ind:
                    rori_sum = rori_sum + ind['rori']

                rori_avg = rori_sum/len(self.rori_ind)
                new_cou = []
                for ind in self.rori_ind:
                    if ind['rori'] >= rori_avg:
                        new_cou.append(ind)

            elif self.SelectedCriteria == 2:
                count = self.RORIResults_View.getIndividualItemCount()
                if (count < 2):
                    wx.MessageBox("Please select at least 2 Mitigation Actions to be combined!")
                    return
                else:
                    # Grab from the view a list with the ID of the selected countermeasures
                    id_cou = self.RORIResults_View.getItemsSelected()
                    new_cou = []
                    for ind in self.rori_ind:
                        if ind['countermeasure'] in id_cou:
                            new_cou.append(ind)
            else:
                new_cou = []
                for ind in self.rori_ind:
                    if ind['rori'] >= self.CombinationThreshold:
                        new_cou.append(ind)


            # Discard countermeasures that doesn't have the individual COV and EF values
            cou_to_combine = self.discardCouNotCombinable(new_cou)
            # Check if the number of countermeasures to combine is at least 2
            if len(cou_to_combine) < 2:
                msg = 'The number of Mitigation Actions is not sufficient to perform the combined evaluation'
                wx.MessageBox(msg, style=wx.OK|wx.ICON_ERROR)
                return
            else:
                # Call the Combined Evaluation passing only the countermeasures selected
                self.performCombinedEvaluation(cou_to_combine)



    #-------------------------------------------------------------------------------------------------
    def performIndividualEvaluation(self):

        #Load the Required Information prior to perform the RORI evaluation
        Cou_RM_value = self.getCount_RM_Info()
        self.AIV_value = self.getAIV(self.idOrg)
        self.ALE_value = self.getALE(self.idOrg,self.idInc)

        if (not Cou_RM_value) or (not self.AIV_value) or (not self.ALE_value) or (not self.informationRequired):
            msg = "Error retrieving the required information to perform the RORI evaluation!!"
            wx.MessageBox(msg, style=wx.OK|wx.ICON_ERROR)
            return False
        else:
            # Call to the individual RORI evaluation
            rori_ind = self.individualRORI(self.rori_countermeasures,self.rori_risk_mitigation,self.AIV_value,self.ALE_value)

            #Change title
            self.RORIResults_View.title.SetLabel("'"+self.incName+"' Detrimental Event at the organization: '" + self.orgName+"'")

            #Check if the required information to perform the RORI calculation has been given

            if not rori_ind:
                wx.MessageBox("Error performing the Individual RORI evaluation!!", style=wx.OK|wx.ICON_ERROR)
                return False
            else:
                #-------------------------------------
                # Generation of the list to be loaded in the GUI for the Individual Evaluation
                individual_list = []
                best_ind_rori = 0
                best_id = 0

                for row in rori_ind:
                    cou_name = row['countermeasure_name']
                    cou_equ = row['equipment_name']

                    rori_index = round(row['rori'],2)

                    if row['rori'] >= best_ind_rori:
                        best_ind_rori = row['rori']
                        best_id = row['countermeasure']

                    cou_IDRef = self.rori_countermeasures[row['countermeasure']]['IDRef']

                    individual_list.append([row['countermeasure'],cou_name, cou_equ, rori_index,cou_IDRef])

                #Load the list of individual RORI index on GUI
                self.RORIResults_View.loadListIndividual(individual_list, best_id)

        return rori_ind

    #-------------------------------------------------------------------------------------------------
    #-------------------------------------------------------------------------------------------------
    #-------------------------------------------------------------------------------------------------
    #-------------------------------------------------------------------------------------------------
    #-------------------------------------------------------------------------------------------------
    def performCombinedEvaluation(self, cou_to_combine):

        #-------------------------------------------------------
        # Combined Countermeasure Evaluation
        #Check if the required information to perform the combination of countermeasures has been given
        if self.toBeCombined:

            rori_comb = self.combinedRORI(self.rori_countermeasures, cou_to_combine, self.rori_risk_mitigation, self.AIV_value, self.ALE_value)

            if not rori_comb:
                msg = "Error performing the combined RORI evaluation!!\n\n"
                msg = msg +"Please check if the Mitigation Actions selected are all mutually restrictive"
                wx.MessageBox(msg, style=wx.OK|wx.ICON_ERROR)
                return
            else:
                #Create the list to be shown in the GUI
                combined_list = []
                best_comb_rori = 0
                best_id = 0
                j = 0

                # Sort the rori_comb list of dictionary by rori index in decreasing order
                newlist = sorted(rori_comb, key=lambda k: k['rori'], reverse=True)
                rori_comb = newlist

                for row in rori_comb:
                    #comb_ids = (', ').join(list(row['countermeasures']))
                    comb_ids = (', ').join([self.rori_countermeasures[i]['IDRef'] for i in list(row['countermeasures'])])
                    comb_ARC = str(round(row['ARC'],2))
                    comb_COV = str(round(row['COV'],2))
                    comb_EF = str(round(row['EF'],2))
                    comb_RM = str(round(row['RM'],2))
                    comb_rori = str(round(row['rori'],2))

                    if row['rori'] >= best_comb_rori:
                        best_comb_rori = row['rori']
                        best_id = j

                    combined_list.append([comb_ids,comb_ARC, comb_COV,comb_EF,comb_RM,comb_rori])
                    j = j+1

                # Load the list of individual RORI index on GUI
                self.RORIResults_View.loadListCombined(combined_list, best_id)
        else:
            wx.MessageBox("Due to lack of individual values of EF and COV for the Mitigation Actions \n a combined Mitigation Action evaluation is not possible!", style=wx.OK|wx.ICON_ERROR)
            self.RORIResults_View.combinedList.ClearAll()

        return

    #-------------------------------------------------------------------------------------------------
    #-------------------------------------------------------------------------------------------------
    #-------------------------------------------------------------------------------------------------
    def getCount_RM_Info(self):

        dict_countermeasures = {} #Empty dictionary to save the countermeasures
        dict_risk_mitigation = {} #Empty dictionary to save the RMs
        missingRM = {} #Empty dictionary to save the countermeasures with missing RM information

        #######################################################
        #### Get All countermeasures assigned to the Incident
        #######################################################
        self.RORICal.idInc = self.idInc
        (cou_error, cou_values) = self.RORICal.readIncCou()
        # self.RORICal.readIncCou() returns in the variable values a tuple of tuples with the following data
        # ((idCountermeasure, Name, Totally_Restrictive, FK_Equipment, IDRef))
        if cou_error:
            msg= "Error reading the list of Mitigation Actions: \n" + cou_values
            wx.MessageBox(msg, style=wx.OK|wx.ICON_ERROR)
            return False
        else:
            # For each countermeasure populate the dictionaries that will be used in the RORI evaluation
            for cou in cou_values:
                #Empty dictionary to save the attributes of each Countermeasure
                cou_att = {}
                cou_att['name'] = cou[1]
                cou_att['IDRef'] = cou[4]

                #######################################################
                #### For each countermeasure
                #### Get Information related to the Restrictions
                #######################################################
                # Check if the countermeasure is totally restrictive,
                if cou[2]:
                    cou_att['totally_restrictive'] = True
                    cou_att['restriction'] = []
                else: #If is not totally restrictive check if it has any restrictions
                    cou_att['totally_restrictive'] = False
                    #
                    self.RORICal.idCou = cou[0]
                    (res_error, res_values) = self.RORICal.readResCou()
                    if res_error:
                        msg= "Error reading the list of Restrictions: \n" + res_values
                        wx.MessageBox(msg)
                        return False
                    else:
                        # List to save the ID of the restrictive countermeasures
                        list_rest =[]
                        for rest in res_values:
                            list_rest.append(rest[0])

                        cou_att['restriction'] = list_rest


                #######################################################
                #### For each countermeasure
                ### Get information related to the Equipment
                #######################################################
                if not cou[3]:
                    msg= "The Mitigation Action '"+ cou[1] +"' is not assigned to any PEP.\n"
                    msg+="Would you like to continue with the evaluation discarding the Mitigation Action?"
                    del_confirm = wx.MessageDialog(None, msg, 'Missing PEP', wx.YES_NO | wx.ICON_QUESTION)
                    if del_confirm.ShowModal() == wx.ID_YES:
                        continue
                    else:
                        return False
                else:
                    self.Equipment.id = cou[3]
                    (equ_error, equ_values) = self.Equipment.read()
                    if equ_error:
                        msg= "Error reading the PEP Values of the Mitigation Action: \n" + equ_values
                        wx.MessageBox(msg, style=wx.OK|wx.ICON_ERROR)
                        return False
                    else:
                        # self.Equipment.read() query returns a tuple of tuples with the following data
                        # ((idEquipment, Name, Type))
                        cou_att['equipment_name'] = equ_values[0][1]


                #######################################################
                #### For each countermeasure
                ### Get information related to Risk Mitigation
                #######################################################
                # In this part there are several cases where the Attack Volume could be called in order to get the
                # missing information related to the Risk Mitigation of the Countermeasure
                #

                self.RM.FK_Countermeasure = cou[0]
                (rm_error, rm_values) = self.RM.read_by_countermeasure()
                if rm_error:
                    msg= "Error reading the Risk Mitigation Values of the Mitigation Action: \n" + rm_values
                    wx.MessageBox(msg, style=wx.OK|wx.ICON_ERROR)
                    return False
                else:
                    #Empty dictionary to save the attributes of the RMs
                    rm_att = {}

                    if not rm_values:
                        # Append to the missingRM list a new entry with RM_id equal to -1 that will represent
                        # that there isn't a RM entry for the current countermeasure in the database.
                        missingRM[cou[0]]= {'cou_id':cou[0],'cou_IDRef':cou[4],'cou_name':cou[1],'RM_id':-1,'EF':0,'COV':0,'total':0}
                        cou_att['id_rm'] = -1
                        cou_att['to_combine'] = False

                    else:
                        # self.RM.read_by_countermeasure() query returns a tuple of tuples with the following data
                        # ((idRM, EF, COV, Total, FK_Countermeasure))
                        cou_att['id_rm'] = rm_values[0][0]
                        rm_att['EF'] = rm_values[0][1]
                        rm_att['COV'] = rm_values[0][2]
                        rm_att['RM'] = rm_values[0][3]

                        # If any of the information related to the EF or COV is not given it is not possible to perform
                        # the RORI calculation of combined countermeasures
                        if (rm_att['EF'] != 0) and (rm_att['COV'] != 0) and (rm_att['RM'] != 0):
                            cou_att['to_combine'] = True
                        else:
                            cou_att['to_combine'] = False
                            missingRM[cou[0]] = {'cou_id':cou[0], 'cou_IDRef':cou[4],'cou_name':cou[1],'RM_id':rm_values[0][0],'EF':rm_att['EF'],'COV':rm_att['COV'],'total':rm_att['RM']}

                        #Append the attributes to the list of RMs
                        dict_risk_mitigation[rm_values[0][0]] = rm_att

                #######################################################
                #### For each countermeasure
                ### Get information related to Annual Response Cost
                #######################################################
                self.ARC.FK_Countermeasure = cou[0]
                (arc_error, arc_values) = self.ARC.read_by_countermeasure()
                if arc_error:
                    msg= "Error reading the Annual Response Cost values of the Mitigation Action: \n" + arc_values
                    wx.MessageBox(msg, style=wx.OK|wx.ICON_ERROR)
                    return False
                else:
                    if not arc_values:
                        msg= "The Mitigation Action " + cou[1] + " has not ARC assigned. \n The evaluation cannot be performed"
                        wx.MessageBox(msg, style=wx.OK|wx.ICON_ERROR)
                        self.informationRequired = False
                        return False
                    else:
                        # self.ARC.read_by_countermeasure() query returns a tuple of tuples with the following data
                        # ((idARC, COI, COM, ODC, IC, Total, FK_Countermeasure))
                        cou_att['arc'] = arc_values[0][5]

                #Append the attributes to the dictionary of Countermeasures
                dict_countermeasures[cou[0]] = cou_att


        self.rori_countermeasures = dict_countermeasures
        self.rori_risk_mitigation = dict_risk_mitigation

        #Check if there is any entries in the MissingRM list, if so, call the getMissingRMValues method in order to get them
        if len(missingRM)>0:
            self.getMissingRMValues(missingRM)
        return True

    #-------------------------------------------------------------------------------------------------
    #-------------------------------------------------------------------------------------------------
    #-------------------------------------------------------------------------------------------------
    def getMissingRMValues(self, missingRM):

        ask_EF = []
        ask_COV = []
        cou_names = ""

        for key, item in missingRM.iteritems():
            status = ""
            if item['COV']==item['EF']==item['total']==0:
                status += "Not values assigned"
                ask_EF.append(item)
                ask_COV.append(item)
            elif item['COV']!=0:
                status += "Missing COV"
                ask_EF.append(item)
            elif item['EF']!=0:
                status += "Missing EF"
                ask_COV.append(item)
            else:
                status += "Missing COV and EF"
                ask_COV.append(item)

            cou_names+="\n -"+item['cou_name']+" ("+status+")"

        msg= "There is missing RM information in the following Mitigation Actions:\n" + cou_names
        msg=msg+"\n\nWould you like to?\n"
        msg=msg+"* Discard the Mitigation Actions without COV and EF in the combined RORI calculation process.\n"
        msg=msg+"* Calculate the missing RM information using the Attack Volume module.\n"
        msg=msg+"* Abort RORI calculation."

        dlg = RMDialog(msg)
        result = dlg.ShowModal()
        if result == 0: #Discard the Countermeasures that doesn't have a RM assigned
            for key,item in missingRM.iteritems():
                if item['total']==0:
                    del self.rori_countermeasures[key]

        elif result == 1:#Use AV module
            # If there are countermeasures with missing EF values
            # display the dialog that will ask for them
            if len(ask_EF)>0:
                ef_dlg = EFDialog(ask_EF)
                result = ef_dlg.ShowModal()
                if result != wx.ID_OK:
                    self.informationRequired = False
                    return

                #Grab EF Values from the Dialog
                for item in ask_EF:
                    ef_value = ef_dlg.textFields[item['cou_id']].GetValue()
                    if not checkStringInputType(ef_value,"decimal"):
                        wx.MessageBox("One of the inputs has an incorrect format")
                        self.informationRequired = False
                        return
                    elif not (0 < Decimal(ef_value) <= 100):
                        wx.MessageBox("The EF value should be between 0 and 100")
                        self.informationRequired = False
                        return

                    #Update the missingRM dictionary with the EF value:
                    missingRM[item['cou_id']]['EF']=Decimal(ef_value)/100
            # If there are countermeasures with missing COV values
            # call the AV module
            if len(ask_COV):
                #Call the AV volume to calculate the COV of countermeasures
                coverages = self.getCOV(ask_COV)
                if not coverages:
                    wx.MessageBox("Error in the calculation of coverages!!")
                    self.informationRequired = False
                    return
                else:
                    # Update the missingRM dictionary with the COV values returned by the AV module
                    # the AV module Returns value between 0-100, the value will be divided by 100 so it will have
                    # the same representation as the one save in the RORI_DB database
                    for key,item in coverages.iteritems():
                        missingRM[key]['COV']=Decimal(item)/100

            #Finalizar con incluir los datos en la BD usando el missingRM actualizado y actualizar el dict rori_riskmitigation
            self.updateRM(missingRM)

        else:#Abort Calculation
            self.informationRequired = False
            return

    #-------------------------------------------------------------------------------------------------
    #-------------------------------------------------------------------------------------------------
    #----------------------------------------------------------------------------------------------------
    def getCOV(self,cou_COV):
        #Create the XML output file and passed it to the Attack Volume module
        xml_root = etree.Element("RORI_AV")
        #The AV module should not display any graphics
        xml_root.append(etree.Element("MODE", graphic="false"))
        #Create the Organization XML element
        xml_root.append(etree.Element("ORGANISATION", name="SCADA"))
        #Create the Incident XML element
        xml_inc = etree.SubElement(xml_root,'INCIDENTS')
        # ID incident selected
        id_inc = self.incIDRef

        # Create incident Sub-element
        etree.SubElement(xml_inc, "incident", {'id':str(id_inc), 'name':self.incName, 'id_countermeasure': (', '.join(x['cou_IDRef'] for x in cou_COV))})

        #Create the COUNTERMEASURES XML element
        xml_cou = etree.SubElement(xml_root,'COUNTERMEASURES')
        # Create countermeasure Sub-elements
        #<countermeasure id="C5" name="Enable Multiple Monitoring Indication" COV=""/>
        for cou in cou_COV:
            etree.SubElement(xml_cou, "countermeasure", {'id':cou['cou_IDRef'], 'name':cou['cou_name'], 'COV':""})

        #Append the new XML elements to the XML root
        xml_root.append(xml_inc)
        xml_root.append(xml_cou)

        #Append the root to a XML document
        xml_doc = etree.ElementTree(xml_root)

        #print etree.tostring(xml_doc, pretty_print=True)

        # Write the output XML document
        tstamp = datetime.now().__str__().replace(" ","_").replace(":","-").replace(".","-")
        request_xml_path = "./AV_request/"+self.incName.replace(" ","-")+"_"+tstamp
        xml_doc.write(request_xml_path+"_request.xml", pretty_print=True)

        #Call AV module
        try:
            #attack_volume = sub.Popen(["more", "./output.xml"], stdout=sub.PIPE,stderr=sub.PIPE)
            #output, errors = attack_volume.communicate()
            #print output
            #print errors
            #return_code = sub.call("more fk")
            #return_code = sub.check_call(["cat", "output.xml"])
            #sub.check_call(['ls' ,'-lh'])
            return_code = sub.call(['attack-volume', '-i', request_xml_path+"_request.xml", '-o', request_xml_path+"_output.xml"])
            if return_code != 0:
                wx.MessageBox('Error running the Attack Volume module')
                return
        except OSError as e:
            print "Error executing command: "
            print e

        #Read the output generated by the AV volume
        try:
            with open(request_xml_path+"_output.xml") as file:
                pass
        except IOError as e:
            print "Unable to open file Returned by the AV module" #Does not exist OR no read permissions
            return False

        try:
            parser = etree.XMLParser(remove_blank_text=True)
            output_file = etree.parse(request_xml_path+"_output.xml",parser)
        except etree.XMLSyntaxError, e:
            print "Bad XML Syntax on the given file"
            return False

        out_countermeasures = output_file.find('//COUNTERMEASURES')
        if out_countermeasures is None:
            return False
        else:
            coverage = {}
            for oc in out_countermeasures:
                for cCOV in cou_COV:
                    if cCOV['cou_IDRef'] == oc.attrib['id']:
                        coverage[int(cCOV['cou_id'])] = 0 if oc.attrib['COV'].replace(" ", "") == "" else oc.attrib['COV']
                        break

        return coverage

    #----------------------------------------------------------------------------------------------------
    def getCOV_REAL(self,cou_COV):
        #Create the XML output file and passed it to the Attack Volume module
        xml_root = etree.Element("RORI_AV")
        #The AV module should not display any graphics
        xml_root.append(etree.Element("MODE", graphic="false"))
        #Create the Organization XML element
        xml_root.append(etree.Element("ORGANISATION", name=self.orgName))
        #Create the Incident XML element
        xml_inc = etree.SubElement(xml_root,'INCIDENTS')
        # ID incident selected
        id_inc = self.incIDRef

        # Create incident Sub-element
        etree.SubElement(xml_inc, "incident", {'id':str(id_inc), 'name':self.incName, 'id_countermeasure': (', '.join(x['cou_IDRef'] for x in cou_COV))})

        #Create the COUNTERMEASURES XML element
        xml_cou = etree.SubElement(xml_root,'COUNTERMEASURES')
        # Create countermeasure Sub-elements
        #<countermeasure id="C5" name="Enable Multiple Monitoring Indication" COV=""/>
        for cou in cou_COV:
            etree.SubElement(xml_cou, "countermeasure", {'id':cou['cou_IDRef'], 'name':cou['cou_name'], 'COV':""})

        #Append the new XML elements to the XML root
        xml_root.append(xml_inc)
        xml_root.append(xml_cou)

        #Append the root to a XML document
        xml_doc = etree.ElementTree(xml_root)

        #print etree.tostring(xml_doc, pretty_print=True)

        # Write the output XML document
        tstamp = datetime.now().__str__().replace(" ","_").replace(":","-").replace(".","-")
        request_xml_path = "./AV_request/"+self.incName.replace(" ","-")+"_"+tstamp
        xml_doc.write(request_xml_path+"_request.xml", pretty_print=True)
        #Call AV module
        try:
            #attack_volume = sub.Popen(["more", "./output.xml"], stdout=sub.PIPE,stderr=sub.PIPE)
            #output, errors = attack_volume.communicate()
            #print output
            #print errors
            #return_code = sub.call("more fk")
            #return_code = sub.check_call(["cat", "output.xml"])
            #sub.check_call(['ls' ,'-lh'])
            return_code = sub.call(['attack-volume', '-i', request_xml_path+"_request.xml", '-o', request_xml_path+"_output.xml"])
            if return_code != 0:
                wx.MessageBox('Error running the Attack Volume module')
                return
        except OSError as e:
            print "Error executing command: "
            print e

        #Read the output generated by the AV volume
        try:
            with open(request_xml_path+"_output.xml") as file:
                pass
        except IOError as e:
            print "Unable to open file Returned by the AV module" #Does not exist OR no read permissions
            return False

        try:
            parser = etree.XMLParser(remove_blank_text=True)
            output_file = etree.parse(request_xml_path+"_output.xml",parser)
        except etree.XMLSyntaxError, e:
            print "Bad XML Syntax on the given file"
            return False

        out_countermeasures = output_file.find('//COUNTERMEASURES')
        if out_countermeasures is None:
            return False
        else:
            coverage = {}
            for oc in out_countermeasures:
                for cCOV in cou_COV:
                    if cCOV['cou_IDRef'] == oc.attrib['id']:
                        coverage[int(cCOV['cou_id'])] = 0 if oc.attrib['COV'].replace(" ", "") == "" else oc.attrib['COV']
                        break

        return coverage

    #-------------------------------------------------------------------------------------------------
    #-------------------------------------------------------------------------------------------------
    #-------------------------------------------------------------------------------------------------
    def updateRM(self, missingRM):

        for key,item in missingRM.iteritems():
            self.RM.id = item['RM_id']
            self.RM.COV = item['COV']
            self.RM.EF = item['EF']
            self.RM.Total = item['total']
            self.RM.FK_Countermeasure = key

            if self.RM.Total != 0:
                if self.RM.COV != 0 and self.RM.EF == 0:
                    self.RM.EF = self.RM.Total/self.RM.COV
                    self.rori_countermeasures[key]['to_combine'] = True
                elif self.RM.COV == 0 and self.RM.EF != 0:
                    self.RM.COV = self.RM.Total/self.RM.EF
                    self.rori_countermeasures[key]['to_combine'] = True
                else:
                    wx.MessageBox("The AV module was not able to find any value of COV for the Mitigation Action:\n\n"+item['cou_name']+"\n\nIt will not be included the combined evaluation process!!!")
            else:
                # If the EF and COV are provided, compute the Total RM value
                if self.RM.COV != 0 and self.RM.EF != 0:
                    #RM Calculation Following the given in Gustavo's Thesis
                    self.rori_countermeasures[key]['to_combine'] = True
                    self.RM.Total = (self.RM.EF * self.RM.COV)
                elif self.RM.COV == 0 or self.RM.EF == 0:
                    wx.MessageBox("The AV module was not able to find any value of COV for the Mitigation Action:\n\n"+item['cou_name']+"\n\nIt will be included on the evaluation process!!!")
                    del self.rori_countermeasures[key]

            if self.RM.id == -1:
                error = self.RM.create(False)
                if error:
                    msg= "Error assigning the RM value to the Mitigation Action"
                    wx.MessageBox(msg)
                    self.informationRequired = False
                    return
                else:
                    error, values = self.RM.read_by_countermeasure()
                    if error:
                        msg= "Error reading the RM value of the Mitigation Action: \n" + values
                        wx.MessageBox(msg)
                        self.informationRequired = False
                        return
                    self.RM.id = values[0][0]
                    self.rori_risk_mitigation[self.RM.id] = {'RM': self.RM.Total, 'EF': self.RM.EF, 'COV': self.RM.COV}
                    self.rori_countermeasures[key]['id_rm'] = self.RM.id

            else:
                (error, values) = self.RM.update(False)
                if error:
                    msg= "Error editing the RM value of the Mitigation Action: \n" + values
                    wx.MessageBox(msg)
                    self.informationRequired = False
                    return
                self.rori_risk_mitigation[self.RM.id] = {'RM': self.RM.Total, 'EF': self.RM.EF, 'COV': self.RM.COV}


    #-------------------------------------------------------------------------------------------------
    #-------------------------------------------------------------------------------------------------
    #-------------------------------------------------------------------------------------------------
    def getAIV(self, idOrg):
        self.AEV.FK_Organization = idOrg
        (aev_error, aev_values) = self.AEV.read_by_organization()
        if aev_error:
            msg= "Error reading the Annual Infrastructure values of the Organization: \n" + aev_values
            wx.MessageBox(msg, style=wx.OK|wx.ICON_ERROR)
            self.informationRequired = False
            return False
        else:
            AIV = 0
            # self.AEV.read_by_organization() query returns a tuple of tuples with the following data
            # ((idAEV, EC, SC, PC, RV, OC, NEquipments, Total, FK_Organization, FK_Equipment))
            for aev in aev_values:
                AIV += aev[7]

        return AIV

    #-------------------------------------------------------------------------------------------------
    #-------------------------------------------------------------------------------------------------
    #-------------------------------------------------------------------------------------------------
    def getALE(self, idOrg, idInc):

        self.ALE.FK_Organization = idOrg
        self.ALE.FK_Incident = idInc
        (ale_error, ale_values) = self.ALE.read_by_incident_organization()
        if ale_error:
            msg= "Error reading the Annual Loss Expectancy values: \n" + ale_values
            wx.MessageBox(msg, style=wx.OK|wx.ICON_ERROR)
            self.informationRequired = False
            return False
        else:
            # self.AEV.read_by_organization() query returns a tuple of tuples with the following data
            # ((idALE, LA, LD, LR, LP, LREC, LRPC, OL, CI, ARO, Total, FK_Incident, FK_Organization))
            if ale_values[0][10]!=0:
                return ale_values[0][10]
            else:
                return False

    #-------------------------------------------------------------------------------------------------
    #-------------------------------------------------------------------------------------------------
    #-------------------------------------------------------------------------------------------------
    #-------------------------------------------------------------------------------------------------
    def individualRORI(self, countermeasures, risk_mitigation, AIV, ALE):
        """This method to computes the RORI index for a given incident in a given organization.

        Args:
          rori_org: A dictionary with the values (attributes) of the organization on which the RORI evaluation will be performed
          rori_inc: A dictionary with the values (attributes) of the incident of the organization

        Returns:
          List of dictionaries with the values related to the ID of the countermeasures that treats the incident and their corresponding RORI index
          Example:
            [{'countermeasure':(String), 'rori':(Decimal)}]
        """
        rori_cou = countermeasures
        rori_rm = risk_mitigation

        list_ind_rori = [] #Empty list to save the RORI index for the countermeasures involved in the incident

        for key, countermeasure in rori_cou.iteritems():
            aux = {}
            #Countermeasure to threat the incident
            #countermeasure = rori_cou[inc_cou]

            #Risk Mitigation Calculation
            cou_rm = rori_rm[countermeasure['id_rm']]['RM']

            #Annual Response Cost
            cou_arc = countermeasure['arc']

            #RORI calculation for the current countermeasure
            cou_rori = (((ALE * cou_rm) - cou_arc ) / (cou_arc + AIV)) * 100

            #Save the values in the list of individual RORI values
            aux['countermeasure'] = key
            aux['countermeasure_name'] = countermeasure['name']
            aux['equipment_name'] = countermeasure['equipment_name']
            aux['rori'] = cou_rori
            list_ind_rori.append(aux)

        return list_ind_rori

    #-------------------------------------------------------------------------------------------------
    #-------------------------------------------------------------------------------------------------
    #-------------------------------------------------------------------------------------------------
    #-------------------------------------------------------------------------------------------------
    def combinedRORI(self, countermeasures, countermeasures_to_combine, risk_mitigation, AIV, ALE):
        """This method generates all the possibles combination of countermeasures given by rori_to_combine list
        for each subset of the combination the restriction for each countermeasure are checked
        after the verification, the combined RORI index is calculated for the subset

        Returns:
          List of dictionaries with the values related to the ID of the countermeasures that treats the incident and their corresponding RORI index
          Example:
          Dictionary to save all the useful information about the RORI calculation
          [{'countermeasures': (Set), 'ARC':(Decimal), 'COV':(Decimal),'EF':(Decimal),'RM':(Decimal),'rori':(Decimal)}]
        """

        #Local variables
        #AIV = self.AIV
        #ALE = self.ALE
        rori_to_combine = countermeasures_to_combine
        rori_countermeasures = countermeasures
        #rori_arc = self.rori_annual_response_cost
        rori_rm = risk_mitigation

        #List to save the values of all the RORI values of the countermeasure combinations
        rori_combined_list = []
        mut_restrictive = []

        #First iterate over the possible combinations to get the restrictions
        for L in range(0, len(rori_to_combine)+1):
            for subset in combinations(rori_to_combine, L):
                #print(subset)
                if len(subset) > 1:
                    aux = subset
                    for element in subset:
                        #Check Restrictions on each countermeasure of the subset
                        for aux_element in aux:
                            #Avoid comparison of a countermeasure with itself
                            if element['countermeasure'] != aux_element['countermeasure']:
                                #If the current countermeasure is in a list of restrictions of other countermeasure
                                # it means that it is mutually restrictive with it.
                                if element['countermeasure'] in rori_countermeasures[aux_element['countermeasure']]['restriction']:
                                    mut_restrictive.append([element['countermeasure'], aux_element['countermeasure']])


        # Discard the duplicated restrictions among the elements of the list
        # e.g; a restriction between 2 countermeasures (id= 1 , id=2) will have an entry [1,2] in the list
        # and there should be another entry [2,1] establishing the mutual restriction of countermeasures
        # Those 2 entries represent the same restriction, hence one of them should be discarded
        # cou_index will save the ID of all the countermeasures along with it's restrictions
        mut_restrictive.sort()
        cou_index = []
        for el in mut_restrictive:
            el.sort()
            if el not in cou_index:
                cou_index.append(el)

        #Begin the Calculation based on the restrictions of each subset of countermeasures
        for L in range(0, len(rori_to_combine)+1):
            for subset in combinations(rori_to_combine, L):

                if len(subset) > 1:
                    # Collect all the countermeasure's id in of the current subset in a set element
                    # that will be used to determine if the subset is restricted
                    id_countermeasures = set()
                    for el in subset:
                        id_countermeasures.add(el['countermeasure'])

                    flag = False

                    for restriction in cou_index:
                        restriction_set = set(restriction)
                        # Determine the intersection between the countermeasures of the current subset
                        # and the set of restrictions
                        intersection = id_countermeasures.intersection(restriction_set)

                        # If the set of restrictions is equal to the intersection,
                        # the current subset of countermeasures is restricted to be combined
                        if restriction_set == intersection:
                            flag = True

                    if not flag:
                        ARC_subset = 0
                        rm_indiv = 0
                        for element in subset:
                            # Following equation 4.12 in Gustavo's Thesis: The combined ARC value can be calculated
                            # no mather if the countermeasures are restricted or not
                            ARC_subset += rori_countermeasures[element['countermeasure']]['arc']

                            #Save the sum of individual RM of the elements
                            ele_cov = rori_rm[rori_countermeasures[element['countermeasure']]['id_rm']]['COV']
                            ele_ef = rori_rm[rori_countermeasures[element['countermeasure']]['id_rm']]['EF']
                            rm_indiv = rm_indiv + (ele_cov*ele_ef)

                        rm_intersection = 0
                        for l in range(0, len(subset)+1):
                            rm_sub_subset = 0
                            for sub_subset in combinations(subset, l):
                                if len(sub_subset) > 1:
                                    list_ef = []
                                    list_cov = []
                                    for element in sub_subset:
                                        ele_cov = rori_rm[rori_countermeasures[element['countermeasure']]['id_rm']]['COV']
                                        ele_ef = rori_rm[rori_countermeasures[element['countermeasure']]['id_rm']]['EF']
                                        list_ef.append(ele_ef)
                                        list_cov.append(ele_cov)

                                    #Following Equation 4.16 in Gustavo's Thesis for the calculation of the coverage intersection:
                                    if sum(list_cov) <= len(sub_subset)-1:
                                        cov_int_low = 0
                                    else:
                                        cov_int_low = sum(list_cov) - (len(sub_subset)-1)

                                    cov_int = (cov_int_low + min(list_cov))/2

                                    #rm_int has the RM value of the intersection of the current set of countermeasures
                                    rm_int = cov_int * min(list_ef)
                                    #rm_sub_subset has the sum of all the individual intersection RM from the subset of countermeasures
                                    rm_sub_subset += rm_int

                            #rm_intersection has the sum of the RM from the combined set of countermeasures
                            # when the set of countermeasures is even it will add the value to the total, if it's odd it will substract it (Equation 4.13)
                            rm_intersection = rm_intersection + (((-1)**l)*rm_sub_subset)

                        #RM_combined follows equation 4.13 and has the total combined RM value of the set of countermeasures
                        RM_combined = rm_indiv - rm_intersection

                        #RORI calculation for the subset of combined countermeasure
                        rori_comb = (((ALE * RM_combined) - ARC_subset ) / (ARC_subset + AIV)) * 100

                        #Dictionary to save all the useful information about the RORI calculation
                        aux_dict = {'countermeasures': id_countermeasures, 'ARC':ARC_subset, 'COV':cov_int,'EF':min(list_ef),'RM':RM_combined,'rori':rori_comb}

                        #Append the dictionary to the list to be returned by the method
                        rori_combined_list.append(aux_dict)

        return rori_combined_list

    #------------------------------------------------------------------------------------------------------------
    def onExit(self, evt):
       self.RORIResults_View.frame.Destroy()
