__author__ = 'ender_al'
# -*- coding: utf-8 *-*

from itertools import combinations
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
import json

class RORI_SRD:
    def __init__(self, idOrg, orgName, incIDRef, incName):
        #List to save the ID of the organizations, it will be used to know which organization is selected from the
        #list of choices in the view
        self.orgListID = []

        #Instance of models used to retrieve data from DB in order to perform RORI evaluation
        self.Organization = Organization()
        self.Incident = Incident()
        self.Countermeasure = Countermeasure()
        self.RORICal = RORICal()
        self.ARC = ARC.ARC()
        self.RM = RM.RM()
        self.ALE = ALE.ALE()
        self.AEV = AEV.AEV()
        self.Equipment = Equipment.Equipment()

        #
        self.incidents = []
        self.organizations_names = []

        #IDs of the elements required to start the calculation of the RORI index
        self.idOrg = 0
        self.idInc = 0

        #Combinations criteria are All Mitigation Actions (0, Default), Above Individual RORI average (1), Custom Selection
        # of Mitigation Actions (2) and Combination Threshold (3)
        self.SelectedCriteria = 0

        # CombinationThreshold will be given by the user; is used to exclude from the combined evaluation all the
        # Mitigation Actions which individual RORI index is bellow it's value.
        self.CombinationThreshold = 0

        self.idOrg = idOrg
        self.orgName = orgName
        self.incName = incName
        #incIDRef is not the ID of the Database but the ID given by hand by the external source of info,
        # this will be used to be matched against the info on the AV module
        self.incIDRef = incIDRef
        self.idInc = None

        self.toBeCombined = True
        self.informationRequired = True
        self.AIV_value = 0
        self.ALE_value = 0

        # Flags that establish the output information to be displayed
        # if BestMA=True the output displayed will have only the information about the best MA in the individual RORI evaluation
        # if BestRP=True the output displayed will have only the information about the best RP in the combined RORI evaluation
        # if JSON=True the output displayed will have only the information about the best RP or best MA in JSON format
        self.BestMA = False
        self.BestRP = False
        self.JSON = False
        
        #JSON dictionary to save the results
        self.json_output = {"mitigationActions": [], "responsePlanID": None}


    #------------------------------------------------------------------------------------------------------------
    def checkParameters(self):
        print 'Checking Parameters Given'
        #Check if the Organization info given is saved on the DB:
        if self.idOrg is not None:
            self.Organization.id = self.idOrg
            (error, values) = self.Organization.read()
            if error:
                print "Error reading the list of Organizations: \n" + values
                return 1
            else:
                if len(values) == 1:
                    for organization in values:
                        self.orgName = organization[1]
                else:
                    print "There is not organization with the ID '" + str(self.idOrg) + "' in the system."
                    return 1
        elif self.orgName is not None:
            self.Organization.Name = self.orgName
            (error, values) = self.Organization.readByName()
            if error:
                print "Error reading the list of Organizations: \n" + values
                return 1
            else:
                if len(values) > 0:
                    for organization in values:
                        self.idOrg = organization[0]
                else:
                    print "There is not organization with the Name '" + self.orgName + "' in the system."
                    return 1
        else:
            print 'An ID or name of an Organization should be given in order to perform the RORI evaluation'
            return 1



        #Check if the Incident info given is saved on the DB:
        if self.incIDRef is not None:
            self.RORICal.idOrg = self.idOrg
            # Fetch the Incidents assigned to the Organization
            (error, values) = self.RORICal.readOrgInc()
            if error:
                print "Error reading the list of Detrimental Events of the Organizations: \n" + values
                return 1
            else:
                if not values:
                    print "The Organization does not have any Detrimental Events assigned"
                    return 1
                else:
                    for incident in values:
                        if incident[2] == self.incIDRef:
                            self.idInc = incident[0]
                            self.incName = incident[1]
                            break
                    if not self.idInc:
                        print "There is not Detrimental Event with the ID '" + str(self.incIDRef) + "' in the system."
                        return 1

        elif self.incName is not None:
            self.RORICal.idOrg = self.idOrg
            # Fetch the Incidents assigned to the Organization
            (error, values) = self.RORICal.readOrgInc()
            if error:
                print "Error reading the list of Detrimental Event of the Organizations: \n" + values
                return 1
            else:
                if not values:
                    print "The Organization does not have any Detrimental Event assigned"
                    return 1
                else:
                    for incident in values:
                        if incident[1] == self.incName:
                            self.idInc = incident[0]
                            self.incIDRef = incident[2]
                            break
                    if not self.idInc:
                        print "There is not Detrimental Event with the Name '" + str(self.incIDRef) + "' in the system."
                        return 1
        else:
            print 'An ID or name of a Detrimental Event should be given in order to perform the RORI evaluation'
            return 1

        return 0

    #---------------------------------------------------------------------------------------------
    def generateJSONOutput(self):
        # Create a RP ID
        tstamp = datetime.now().__str__().replace(" ","_").replace(":","-").replace(".","-")
        idRP = "RORI_RP_"+tstamp
        self.json_output["responsePlanID"] = idRP
        
        print "\n--------------------------------------------------------------------------------"
        print "Generating JSON output\n"
        print json.dumps(self.json_output, sort_keys=True, indent=4, separators=(',', ': '))
        #Write output to file
        print "\n>>> JSON output was saved on file: "+idRP+".json"
        json_file_output = open(idRP+".json",'w')
        json.dump(self.json_output,json_file_output, sort_keys=True, indent=4, separators=(',', ': '))

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
            print message

        return new_cou

    #---------------------------------------------------------------------------------------------
    def applyCombinationCriteria(self,listofma):
            # Perform the combination based on the Selected Criteria:
            # 0 - Combine all Mitigation Actions (Default Criteria)
            # 1 - Combine only the Mitigation Actions above the average RORI index on the individual Mitigation Action evaluation
            # 2 - Combination of selected Mitigation Actions
            # 3 - Above an specific threshold

            if self.SelectedCriteria == 0:
                # Pass all the Mitigation Actions with the individual RORI evaluation
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

                if len(listofma)< 2:
                    print "\n[ERROR] Please provide at least 2 Mitigation Actions to be combined!"
                    return
                else:
                    # Grab from the view a list with the ID of the selected Mitigation Actions
                    id_cou = []
                    for key,val in self.rori_countermeasures.iteritems():
                        if val['IDRef'] in listofma:
                            id_cou.append(key)

                    if len(id_cou) == 0:
                        print '\n[ERROR] The list of mitigation actions given as a parameter is not valid'
                        return

                    new_cou = []
                    for ind in self.rori_ind:
                        if ind['countermeasure'] in id_cou:
                            new_cou.append(ind)
            else:
                new_cou = []
                if not checkStringInputType(self.CombinationThreshold,"decimal"):
                    print "\n[ERROR] The threshold value given has an incorrect format"
                    return
                self.CombinationThreshold = Decimal(self.CombinationThreshold)
                for ind in self.rori_ind:
                    if ind['rori'] >= self.CombinationThreshold:
                        new_cou.append(ind)


            # Discard Mitigation Actions that doesn't have the individual COV and EF values
            cou_to_combine = self.discardCouNotCombinable(new_cou)
            # Check if the number of Mitigation Actions to combine is at least 2
            if len(cou_to_combine) < 2:
                print '\n[ERROR] The number of Mitigation Actions is not sufficient to perform the combined evaluation'
                return
            else:
                # Call the Combined Evaluation passing only the Mitigation Actions selected
                self.performCombinedEvaluation(cou_to_combine)

    #-------------------------------------------------------------------------------------------------
    def performIndividualEvaluation(self):

        #Load the Required Information prior to perform the RORI evaluation
        Cou_RM_value = self.getCount_RM_Info()
        self.AIV_value = self.getAIV(self.idOrg)
        self.ALE_value = self.getALE(self.idOrg,self.idInc)

        if (not Cou_RM_value) or (not self.AIV_value) or (not self.ALE_value) or (not self.informationRequired):
            print "Error retrieving the required information to perform the RORI evaluation!!"
            return 1
        else:
            # Call to the individual RORI evaluation
            rori_ind = self.individualRORI(self.rori_countermeasures,self.rori_risk_mitigation,self.AIV_value,self.ALE_value)

            #Change title
            print "Performing RORI evaluation for:"
            print ("'"+self.incName+"' incident at the organization: '" + self.orgName+"'")

            #Check if the required information to perform the RORI calculation has been given

            if not rori_ind:
                print "Error performing the Individual RORI evaluation!!"
                return 1
            else:
                #-------------------------------------
                # Generation of the list to be loaded in the GUI for the Individual Evaluation
                individual_list = []
                best_ind_rori = 0
                best_id = 0

                for row in rori_ind:
                    cou_name = row['countermeasure_name']
                    cou_equ = row['equipment_name']
                    cou_equ_IDRef = row['equipment_IDRef']
                    rori_index = round(row['rori'],2)

                    if row['rori'] >= best_ind_rori:
                        best_ind_rori = row['rori']
                        best_id = row['countermeasure']

                    cou_IDRef = self.rori_countermeasures[row['countermeasure']]['IDRef']

                    individual_list.append([cou_IDRef,cou_name, cou_equ, rori_index,row['countermeasure'],cou_equ_IDRef])

                #Dict to save a list of individual results
                json_ind_results = {"individualEvaluation":[]}

                # Print Results to console
                if self.BestMA:
                    print "\n--------------------------------------------------------------------------------"
                    print "Best Mitigation Action"
                    template = "{0:4}|{1:45}|{2:10}|{3:8}" # column widths: 8, 10, 15, 7, 10
                    print template.format("ID", "NAME", "EQUIPMENT ID", "RORI") # header
                    for rec in individual_list:
                        #msg = template.format(*rec)
                        msg = template.format(rec[0],rec[1],rec[5],rec[3])
                        if rec[4]==best_id:
                            json_ind_results['individualEvaluation'].append({"enforcementPoint": rec[5], "mitigationActionID": rec[0],"RORI_Index":rec[3]})
                            print msg
                            break
                    self.json_output['mitigationActions'].append(json_ind_results)
                    print "--------------------------------------------------------------------------------"
                elif not self.BestRP:
                    print "\n--------------------------------------------------------------------------------"
                    print "Individual Results"
                    template = "{0:4}|{1:45}|{2:10}|{3:8}" # column widths: 8, 10, 15, 7, 10
                    print template.format("ID", "NAME", "EQUIPMENT ID", "RORI") # header
                    for rec in individual_list:
                        msg = template.format(rec[0],rec[1],rec[5],rec[3])
                        json_ind_results['individualEvaluation'].append({"enforcementPoint": rec[5], "mitigationActionID": rec[0],"RORI_Index":rec[3]})
                        #json_output["RORI_Index"]=rec[3]
                        if rec[4]==best_id:
                            print msg + " <-- Best RORI index"
                        else:
                            print msg
                    self.json_output['mitigationActions'].append(json_ind_results)
                    print "--------------------------------------------------------------------------------"

                #self.RORIResults_View.loadListIndividual(individual_list, best_id)

        return rori_ind

    #-------------------------------------------------------------------------------------------------
    #-------------------------------------------------------------------------------------------------
    #-------------------------------------------------------------------------------------------------
    #-------------------------------------------------------------------------------------------------
    #-------------------------------------------------------------------------------------------------
    def performCombinedEvaluation(self, cou_to_combine):

        #-------------------------------------------------------
        # Combined Mitigation Action Evaluation
        #Check if the required information to perform the combination of Mitigation Actions has been given
        if self.toBeCombined:

            rori_comb = self.combinedRORI(self.rori_countermeasures, cou_to_combine, self.rori_risk_mitigation, self.AIV_value, self.ALE_value)

            if not rori_comb:
                msg = "Error performing the combined RORI evaluation!!\n\n"
                msg = msg +"Please check if the Mitigation Actions selected are all mutually restrictive"
                print msg
                return 1
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
                    #comb_ids = (', ').join(list(row['Mitigation Actions']))
                    comb_ids = (', ').join([self.rori_countermeasures[i]['IDRef'] for i in list(row['countermeasures'])])
                    comb_ARC = str(round(row['ARC'],2))
                    comb_COV = str(round(row['COV'],2))
                    comb_EF = str(round(row['EF'],2))
                    comb_RM = str(round(row['RM'],2))
                    comb_rori = str(round(row['rori'],2))

                    if not self.BestRP and not self.BestMA:
                        json_comb_results = {"individualEvaluation":[]}
                        for i in list(row['countermeasures']):
                            for ri in self.rori_ind:
                                if ri['countermeasure'] == i:
                                    json_comb_results['individualEvaluation'].append({"enforcementPoint": ri['equipment_IDRef'], "mitigationActionID": self.rori_countermeasures[i]['IDRef'], "RORI_Index":round(ri['rori'],2)})

                        json_comb_results['RORI_Combined'] = round(row['rori'],2)
                        self.json_output['mitigationActions'].append(json_comb_results)

                    if row['rori'] >= best_comb_rori:
                        best_comb_rori = row['rori']
                        best_id = j

                    combined_list.append([comb_ids,comb_ARC, comb_COV,comb_EF,comb_RM,comb_rori])
                    j = j+1


                # Combined Results to console

                if self.BestRP:
                    #Save only best result on JSON
                    json_comb_results = {"individualEvaluation":[]}
                    for i in list(rori_comb[best_id]['countermeasures']):
                        for j in self.rori_ind:
                            if j['countermeasure'] == i:
                                json_comb_results['individualEvaluation'].append({"enforcementPoint": j['equipment_IDRef'], "mitigationActionID": self.rori_countermeasures[i]['IDRef'], "RORI_Index":round(j['rori'],2)})
                    json_comb_results['RORI_Combined'] = round(rori_comb[best_id]['rori'],2)
                    self.json_output['mitigationActions'].append(json_comb_results)

                    print "\n--------------------------------------------------------------------------------"
                    print "Best Response Plan"
                    template = "{0:20}|{1:8}|{2:8}|{3:8}|{4:8}|{5:8}" # column widths: 8, 10, 15, 7, 10
                    print template.format("Mitigation Actions", "ARC", "COV", "EF", "RM","RORI Index") # header
                    index = 0
                    for rec in combined_list:
                        msg = template.format(*rec)
                        if index==best_id:
                            print msg
                            break
                        index +=1
                    print "--------------------------------------------------------------------------------"
                elif not self.BestMA:
                    print "\n--------------------------------------------------------------------------------"
                    print "Combined Results"
                    template = "{0:20}|{1:8}|{2:8}|{3:8}|{4:8}|{5:8}" # column widths: 8, 10, 15, 7, 10
                    print template.format("Response Plans", "ARC", "COV", "EF", "RM","RORI Index") # header
                    index = 0
                    for rec in combined_list:
                        msg = template.format(*rec)
                        if index==best_id:
                            print msg + " <-- Best RORI index"
                        else:
                            print msg
                        index +=1
                    print "--------------------------------------------------------------------------------"

        else:
            print("Due to lack of individual values of EF and COV for the Mitigation Actions \n a combined Mitigation Action evaluation is not possible!")

        return

    #-------------------------------------------------------------------------------------------------
    #-------------------------------------------------------------------------------------------------
    #-------------------------------------------------------------------------------------------------
    def getCount_RM_Info(self):

        dict_countermeasures = {} #Empty dictionary to save the Mitigation Actions
        dict_risk_mitigation = {} #Empty dictionary to save the RMs
        missingRM = {} #Empty dictionary to save the Mitigation Actions with missing RM information

        #######################################################
        #### Get All Mitigation Actions assigned to the Incident
        #######################################################
        self.RORICal.idInc = self.idInc
        (cou_error, cou_values) = self.RORICal.readIncCou()
        # self.RORICal.readIncCou() returns in the variable values a tuple of tuples with the following data
        # ((idMitigation Action, Name, Totally_Restrictive, FK_Equipment, IDRef))
        if cou_error:
            print "Error reading the list of Mitigation Actions: \n" + cou_values
            return False
        else:
            # For each Mitigation Action populate the dictionaries that will be used in the RORI evaluation
            for cou in cou_values:
                #Empty dictionary to save the attributes of each Mitigation Action
                cou_att = {}
                cou_att['name'] = cou[1]
                cou_att['IDRef'] = cou[4]

                #######################################################
                #### For each Mitigation Action
                #### Get Information related to the Restrictions
                #######################################################
                # Check if the Mitigation Action is totally restrictive,
                if cou[2]:
                    cou_att['totally_restrictive'] = True
                    cou_att['restriction'] = []
                else: #If is not totally restrictive check if it has any restrictions
                    cou_att['totally_restrictive'] = False
                    #
                    self.RORICal.idCou = cou[0]
                    (res_error, res_values) = self.RORICal.readResCou()
                    if res_error:
                        print "Error reading the list of Restrictions: \n" + res_values
                        return False
                    else:
                        # List to save the ID of the restrictive Mitigation Actions
                        list_rest =[]
                        for rest in res_values:
                            list_rest.append(rest[0])

                        cou_att['restriction'] = list_rest


                #######################################################
                #### For each Mitigation Action
                ### Get information related to the Equipment
                #######################################################
                if not cou[3]:
                    msg= "The Mitigation Action '"+ cou[1] +"' is not assigned to any equipment.\n"
                    msg+="Would you like to continue with the evaluation discarding the Mitigation Action?"
                    print msg
                    option = raw_input("YES/NO?:")
                    if option.upper == "YES" or option.upper == "Y":
                        continue
                    else:
                        return False
                else:
                    self.Equipment.id = cou[3]
                    (equ_error, equ_values) = self.Equipment.read()
                    if equ_error:
                        print "Error reading the Equipment Values of the Mitigation Action: \n" + equ_values
                        return False
                    else:
                        # self.Equipment.read() query returns a tuple of tuples with the following data
                        # ((idEquipment, Name, Type, IDRef))
                        cou_att['equipment_name'] = equ_values[0][1]
                        cou_att['equipment_IDRef'] = equ_values[0][3]


                #######################################################
                #### For each Mitigation Action
                ### Get information related to Risk Mitigation
                #######################################################
                # In this part there are several cases where the Attack Volume could be called in order to get the
                # missing information related to the Risk Mitigation of the Mitigation Action
                #

                self.RM.FK_Countermeasure = cou[0]
                (rm_error, rm_values) = self.RM.read_by_countermeasure()
                if rm_error:
                    print "Error reading the Risk Mitigation Values of the Mitigation Action: \n" + rm_values
                    return False
                else:
                    #Empty dictionary to save the attributes of the RMs
                    rm_att = {}

                    if not rm_values:
                        # Append to the missingRM list a new entry with RM_id equal to -1 that will represent
                        # that there isn't a RM entry for the current Mitigation Action in the database.
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
                    print "Error reading the Annual Response Cost values of the Mitigation Action: \n" + arc_values
                    return False
                else:
                    if not arc_values:
                        print "The Mitigation Action " + cou[1] + " has not ARC assigned. \n The evaluation cannot be performed"
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

        msg="\n\n**************************************************************************************************"
        msg=msg+"\nThere is missing RM information in the following Mitigation Actions:\n" + cou_names
        msg=msg+"\n\nWould you like to?\n"
        msg=msg+"* Discard the Mitigation Actions without COV and EF in the combined RORI calculation process.\n"
        msg=msg+"* Calculate the missing RM information using the Attack Volume module.\n"
        msg=msg+"* Abort RORI calculation.\n\n"

        print msg
        result = raw_input("Discard (D) - Calculate (C) - Abort (A)?:")
        if result.upper() == 'D': #Discard the Mitigation Actions that doesn't have a RM assigned
            for key,item in missingRM.iteritems():
                if item['total']==0:
                    del self.rori_countermeasures[key]

        elif result.upper() == 'C':#Use AV module
            # If there are Mitigation Actions with missing EF values
            # display the dialog that will ask for them
            if len(ask_EF)>0:
                print "\nPlease introduce the EF values of the following Mitigation Actions:\n"
                #Grab EF Values from console
                for item in ask_EF:
                    ef_value = raw_input([item['cou_name']])
                    if not checkStringInputType(ef_value,"decimal"):
                        print "The input for EF has an incorrect format"
                        self.informationRequired = False
                        return
                    elif not (0 < Decimal(ef_value) <= 100):
                        print "The EF value should be between 0 and 100"
                        self.informationRequired = False
                        return

                    #Update the missingRM dictionary with the EF value:
                    missingRM[item['cou_id']]['EF']=Decimal(ef_value)/100
            # If there are Mitigation Actions with missing COV values
            # call the AV module
            if len(ask_COV):
                #Call the AV volume to calculate the COV of Mitigation Actions
                coverages = self.getCOV(ask_COV)
                if not coverages:
                    print "Error in the calculation of coverages!!"
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

        elif result.upper() == 'A':#Abort Calculation
            self.informationRequired = False
            return
        else:
            print '\n[ERROR] Bad option given'
            self.informationRequired = False
            return


    #----------------------------------------------------------------------------------------------------
    def getCOV(self,cou_COV):
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
                print 'Error running the Attack Volume module'
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
                    print "The AV module was not able to find any value of COV for the Mitigation Action:\n\n"+item['cou_name']+"\n\nIt will not be included the combined evaluation process!!!"
            else:
                # If the EF and COV are provided, compute the Total RM value
                if self.RM.COV != 0 and self.RM.EF != 0:
                    #RM Calculation Following the given in Gustavo's Thesis
                    self.rori_countermeasures[key]['to_combine'] = True
                    self.RM.Total = (self.RM.EF * self.RM.COV)
                elif self.RM.COV == 0 or self.RM.EF == 0:
                    print "The AV module was not able to find any value of COV for the Mitigation Action:\n\n"+item['cou_name']+"\n\nIt will be included on the evaluation process!!!"
                    del self.rori_countermeasures[key]

            if self.RM.id == -1:
                error = self.RM.create(False)
                if error:
                    print "Error assigning the RM value to the Mitigation Action"
                    self.informationRequired = False
                    return
                else:
                    error, values = self.RM.read_by_countermeasure()
                    if error:
                        print "Error reading the RM value of the Mitigation Action: \n" + values
                        self.informationRequired = False
                        return
                    self.RM.id = values[0][0]
                    self.rori_risk_mitigation[self.RM.id] = {'RM': self.RM.Total, 'EF': self.RM.EF, 'COV': self.RM.COV}
                    self.rori_countermeasures[key]['id_rm'] = self.RM.id

            else:
                (error, values) = self.RM.update(False)
                if error:
                    print "Error editing the RM value of the Mitigation Action: \n" + values
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
            print "Error reading the Annual Infrastructure values of the Organization: \n" + aev_values
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
            print "Error reading the Annual Loss Expectancy values: \n" + ale_values
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
          List of dictionaries with the values related to the ID of the Mitigation Actions that treats the incident and their corresponding RORI index
          Example:
            [{'countermeasure':(String), 'rori':(Decimal)}]
        """
        rori_cou = countermeasures
        rori_rm = risk_mitigation

        list_ind_rori = [] #Empty list to save the RORI index for the Mitigation Actions involved in the incident

        for key, countermeasure in rori_cou.iteritems():
            aux = {}
            #Mitigation Action to threat the incident
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
            aux['equipment_IDRef'] = countermeasure['equipment_IDRef']
            aux['rori'] = cou_rori
            list_ind_rori.append(aux)

        return list_ind_rori

    #-------------------------------------------------------------------------------------------------
    #-------------------------------------------------------------------------------------------------
    #-------------------------------------------------------------------------------------------------
    #-------------------------------------------------------------------------------------------------
    def combinedRORI(self, countermeasures, countermeasures_to_combine, risk_mitigation, AIV, ALE):
        """This method generates all the possibles combination of Mitigation Actions given by rori_to_combine list
        for each subset of the combination the restriction for each Mitigation Action are checked
        after the verification, the combined RORI index is calculated for the subset

        Returns:
          List of dictionaries with the values related to the ID of the Mitigation Actions that treats the incident and their corresponding RORI index
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
       exit(1)



