#!/usr/bin/python
from lxml import etree
from decimal import *
from itertools import combinations
import sys, getopt

class RORICalculation:
    def __init__(self):
        self.rori_organizations = {}
        self.rori_incidents = {}
        self.rori_equipments = {}
        self.rori_countermeasures = {}
        self.rori_risk_mitigation = {}
        self.rori_annual_response_cost = {}
        self.rori_annual_loss_expectancy = {}

        # informationRequired will be check before performing the RORI evaluation in order to know if all the info
        # required to perform the calculation has been given
        self.informationRequired = True

    #---------------------------------
    def getOrganization(self, organizations):
        """Extract all the attributes from the organization list. Returns a dictionary with the organizations and its attributes"""
    
        dict_organizations = {} #Empty dictionary to save the organizations

        for org in organizations:
            #Empty dictionary to save the attributes of the Organization
            org_att = {}
            org_att['name'] = org.attrib['name']
            org_att['description'] = org.attrib['description']
            org_att['id_equipments'] = org.attrib['id_equipments'].replace(" ", "").split(',')

            # If the required information for the Organization is not given the RORI evaluation cannot be done
            if (org_att['name'] or org_att['id_equipments'] or org.attrib['id']) == "":
                self.informationRequired = "Org"

            #Append the attributes to the list of Organizations
            dict_organizations[org.attrib['id']] = org_att
    
        return dict_organizations
    
    #---------------------------------
    def getEquipments(self, equipments):
        """Extract all the attributes from the equipment list. Returns a dictionary with the equipments and its attributes"""
    
        dict_equipments = {} #Empty dictionary to save the equipments
        for equ in equipments:
            #Empty dictionary to save the attributes of the Equipment
            equ_att = {}
    
            equ_att['name'] = equ.attrib['name']
            equ_att['type'] = equ.attrib['type']
            equ_att['AEV'] = equ.attrib['AEV']

            # If the required information for the Equipment is not given the RORI evaluation cannot be done
            if (equ_att['name'] or equ_att['AEV'] or equ.attrib['id']) == "":
                self.informationRequired = "Equ"

            #Append the attributes to the list of Equipments
            dict_equipments[equ.attrib['id']] = equ_att
    
        return dict_equipments
    
    #---------------------------------
    def getCountermeasures(self, countermeasures):
        """Extract all the attributes from the countermeasure list. Returns a dictionary with the countermeasures and its attributes"""
        dict_countermeasures = {} #Empty dictionary to save the countermeasures
        for cou in countermeasures:
            #Empty dictionary to save the attributes of each Countermeasure
            cou_att = {}
            cou_att['name'] = cou.attrib['name']
            cou_att['description'] = cou.attrib['description']
    
            if cou.attrib['totally_restrictive'] == "yes":
                cou_att['totally_restrictive'] = True
                cou_att['restriction'] = []
            else:
                cou_att['totally_restrictive'] = False
                cou_att['restriction'] = cou.attrib['restriction'].replace(" ", "").split(',')
    
            cou_att['id_equipment'] = cou.attrib['id_equipment']
            cou_att['id_rm'] = cou.attrib['id_rm']
            cou_att['id_arc'] = cou.attrib['id_arc']

            # If the required information for the Countermeasure is not given, the RORI evaluation cannot be done
            if (cou_att['name'] or cou_att['id_rm'] or cou_att['id_arc'] or cou.attrib['id']) == " ":
                self.informationRequired = "Cou"
    
            #Append the attributes to the list of Equipments
            dict_countermeasures[cou.attrib['id']] = cou_att
    
        return dict_countermeasures

    #---------------------------------
    def getIncidents(self, incidents):
        """Extract all the attributes from the Incident's list. Returns a dictionary with the incidents and its attributes"""
    
        dict_incidents = {} #Empty dictionary to save the Incidents
        for inc in incidents:
            #Empty dictionary to save the attributes of the Incidents
            inc_att = {}
            inc_att['name'] = inc.attrib['name']
            inc_att['description'] = inc.attrib['description']
            inc_att['risk_level'] = inc.attrib['risk_level']
            inc_att['id_countermeasure'] = inc.attrib['id_countermeasure'].replace(" ", "").split(',')
            inc_att['id_organization'] = inc.attrib['id_organization']
            inc_att['id_ale'] = inc.attrib['id_ale']

            # If the required information for the Incident is not given the RORI evaluation cannot be done
            if (inc_att['name'] or inc_att['id_countermeasure'] or inc_att['id_organization'] or inc.att['id_ale'] or inc.attrib['id']) == "":
                self.informationRequired = "Inc"

            #Append the attributes to the dictionary of Incidents
            dict_incidents[inc.attrib['id']] = inc_att
    
        return dict_incidents

    #---------------------------------
    def getRM(self, risk_mitigation):
        """Extract all the attributes from the risk mitigation list. Returns a dictionary with the risk mitigation values and its attributes"""
    
        dict_risk_mitigation = {} #Empty dictionary to save the RMs

        # toBeCombined is used by the application to know if there is the complete information to perform
        # the RORI calculation of combined countermeasures
        self.toBeCombined = True
        for rm in risk_mitigation:
            #Empty dictionary to save the attributes of the RMs
            rm_att = {}
            rm_att['RM'] = rm.attrib['RM']
            rm_att['EF'] = rm.attrib['EF']
            rm_att['COV'] = rm.attrib['COV']

            # If any of the information related to the EF or COV is not given it is not possible to perform
            # the RORI calculation of combined countermeasures
            if (rm_att['EF'] or rm_att['COV']) == "":
                self.toBeCombined = False

            # If the required information for the Risk Mitigation is not given the RORI evaluation cannot be done
            if (rm_att['EF'] and rm_att['COV']) == "" and (rm_att['RM'] or rm.attrib['id']) == "":
                self.informationRequired = "RM"

            #Append the attributes to the list of RMs
            dict_risk_mitigation[rm.attrib['id']] = rm_att
    
        return dict_risk_mitigation

    #---------------------------------
    def getARC(self, annual_response_cost):
        """Extract all the attributes from the annual response cost list. Returns a dictionary with the ARC values and its attributes"""
    
        dict_annual_response_costs = {} #Empty dictionary to save the ARCs
        for arc in annual_response_cost:
            #Empty dictionary to save the attributes of the ARCs
            arc_att = {}
            arc_att['COM'] = arc.attrib['COM']
            arc_att['COI'] = arc.attrib['COI']
            arc_att['ODC'] = arc.attrib['ODC']
            arc_att['IC'] = arc.attrib['IC']
            arc_att['total'] = arc.attrib['total']

            # If the input has no total but individual costs, compute the total
            if (arc_att['COM'] and arc_att['COI'] and arc_att['ODC'] and arc_att['IC']) != "" and (arc_att['total'] == ""):
                arc_att['total'] = arc_att['COM'] + arc_att['COI'] + arc_att['ODC'] + arc_att['IC']

            # If the required information for the ARC is not given the RORI evaluation cannot be done
            if (arc_att['total'] or arc.attrib['id']) == "":
                self.informationRequired = "ARC"

            #Append the attributes to the list of ARCs
            dict_annual_response_costs[arc.attrib['id']] = arc_att
    
        return dict_annual_response_costs

    #---------------------------------
    def getALE(self, annual_loss_expectancy):
        """Extract all the attributes from the annual loss expectancy list. Returns a dictionary with the ALE values and its attributes"""
    
        dict_annual_loss_expectancy = {} #Empty dictionary to save the ALEs
        for ale in annual_loss_expectancy:
            #Empty dictionary to save the attributes of the ALEs
            ale_att = {}
            ale_att['LA'] = ale.attrib['LA']
            ale_att['LD'] = ale.attrib['LD']
            ale_att['LR'] = ale.attrib['LR']
            ale_att['LP'] = ale.attrib['LP']
            ale_att['LREC'] = ale.attrib['LREC']
            ale_att['LRPC'] = ale.attrib['LRPC']
            ale_att['OL'] = ale.attrib['OL']
            ale_att['CI'] = ale.attrib['CI']
            ale_att['ARO'] = ale.attrib['ARO']
            ale_att['total'] = ale.attrib['total']

            # If the input has no total but individual costs, compute the total
            if ((ale_att['LA'] and ale_att['LD'] and ale_att['LR'] and ale_att['LP'] and ale_att['LREC'] and ale_att['LRPC'] and ale_att['OL'] and ale_att['CI'] and ale_att['ARO']) != "") and (ale_att['total'] == ""):
                ale_att['total'] = (ale_att['LA'] + ale_att['LD'] + ale_att['LR'] + ale_att['LP'] + ale_att['LREC'] + ale_att['LRPC'] + ale_att['OL'] - ale_att['CI']) * ale_att['ARO']

            # If the required information for the ALE is not given the RORI evaluation cannot be done
            if (ale_att['total'] or ale.attrib['id']) == "":
                self.informationRequired = "ALE"

            #Append the attributes to the list of ALEs
            dict_annual_loss_expectancy[ale.attrib['id']] = ale_att
    
        return dict_annual_loss_expectancy
    
    #---------------------------------
    def individualRORI(self, rori_org, rori_inc):
        
        #print self.rori_organizations
        #rori_org = self.rori_organizations

        #rori_inc = self.rori_incidents
        rori_equ = self.rori_equipments
        rori_cou = self.rori_countermeasures
        rori_rm = self.rori_risk_mitigation 
        rori_arc = self.rori_annual_response_cost
        rori_ale = self.rori_annual_loss_expectancy
        
        list_ind_rori = [] #Empty list to save the RORI index for the countermeasures involved in the incident
    
        #AIV Calculation using the list of equipments of the organization
        self.AIV = 0
        for equ in rori_org['id_equipments']:
            self.AIV += Decimal(rori_equ[equ]['AEV'])
        print self.AIV
    
        #Annual Loss Expectancy for the incident
        self.ALE = Decimal(rori_ale[rori_inc['id_ale']]['total'])
    
        for inc_cou in rori_inc['id_countermeasure']:
    
            if not rori_cou[inc_cou]: #check if there is a countermeasure in the list
                print "Error: Countermeasure not found in the list"
                sys.exit(2)
            else:
                aux = {}
                #Countermeasure to threat the incident
                countermeasure = rori_cou[inc_cou]
    
                #Risk Mitigation Calculation
                #If it has individual values of EF and COV do the calculation, else read the RM value directly
                if self.toBeCombined:
                    cou_rm = Decimal(rori_rm[countermeasure['id_rm']]['EF']) * Decimal(rori_rm[countermeasure['id_rm']]['COV'])
                else:
                    cou_rm = Decimal(rori_rm[countermeasure['id_rm']]['RM'])
    
                #Annual Response Cost
                cou_arc = Decimal(rori_arc[countermeasure['id_arc']]['total'])
    
                #RORI calculation for the current countermeasure
                cou_rori = (((self.ALE * cou_rm) - cou_arc ) / (cou_arc + self.AIV)) * 100
    
                #Save the values in the list of individual RORI values
                aux['countermeasure'] = inc_cou
                aux['rori'] = cou_rori
                list_ind_rori.append(aux)
    
        return list_ind_rori

    #---------------------------------
    def combinedRORI(self):
        #This method generates all the possibles combination of countermeasures given by rori_to_combine list
        #for each subset of the combination the restriction for each countermeasure are checked
        #after the verification, the combined RORI index is calculated for the subset

        #Local variables
        AIV = self.AIV
        ALE = self.ALE
        rori_to_combine = self.rori_to_combine
        rori_countermeasures = self.rori_countermeasures
        rori_arc = self.rori_annual_response_cost
        rori_rm = self.rori_risk_mitigation

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
                            #Avoid to compare a countermeasure with itself
                            if element['countermeasure'] != aux_element['countermeasure']:
                                #If the current countermeasure is in a list of restrictions of other countermeasure
                                # it means that it is mutually restrictive with it.
                                if element['countermeasure'] in rori_countermeasures[aux_element['countermeasure']]['restriction']:
                                    mut_restrictive.append([element['countermeasure'], aux_element['countermeasure']])


        # Discard the duplicated restrictions among the elements of the list
        # e.g; a restriction between 2 countermeasures (id= 1 , id=2) will have an entry [1,2] in the list
        # it should be another entry [2,1] establishing the mutual restriction of countermeasures
        # those entries are then joint into just one entry e.g. [1,2]
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
                        # Determine the intersection between the countermeasures of the  current subset
                        # and the set of restrictions
                        intersection = id_countermeasures.intersection(restriction_set)

                        # If the set of restrictions is equal to the intersection,
                        # the current subset of countermeasures is restricted to be combined
                        if restriction_set == intersection:
                            flag = True

                    if not flag:
                        #print "\nSubset"
                        #print(subset)

                        aux = subset
                        ARC_subset = 0
                        rm_indv = 0
                        for element in subset:
                            # Following equation 4.12 in Gustavo's Thesis: The combined ARC value can be calculated
                            # no mather if the countermeasures are restricted or not
                            ARC_subset += Decimal(rori_arc[rori_countermeasures[element['countermeasure']]['id_arc']]['total'])

                            #Save the sum of individual RM of the elements
                            ele_cov = Decimal(rori_rm[rori_countermeasures[element['countermeasure']]['id_rm']]['COV'])
                            ele_ef = Decimal(rori_rm[rori_countermeasures[element['countermeasure']]['id_rm']]['EF'])
                            rm_indv = rm_indv + (ele_cov*ele_ef)


                        #print "ARC: " + str(ARC_subset)
                        rm_intersection = 0
                        for l in range(0, len(subset)+1):
                            rm_sub_subset = 0
                            for sub_subset in combinations(subset, l):
                                if len(sub_subset) > 1:
                                    list_ef = []
                                    list_cov = []
                                    for element in sub_subset:
                                        ele_cov = Decimal(rori_rm[rori_countermeasures[element['countermeasure']]['id_rm']]['COV'])
                                        ele_ef = Decimal(rori_rm[rori_countermeasures[element['countermeasure']]['id_rm']]['EF'])
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
                            #print l
                            #print "RM Subset "+ str(rm_sub_subset)

                            #rm_intersection has the sum of the RM from the combined set of countermeasures
                            # when the set of countermeasures is even it will add the value to the total, if it's odd it will substract it (Equation 4.13)
                            rm_intersection = rm_intersection + (((-1)**l)*rm_sub_subset)

                        #RM_combined follows equation 4.13 and has the total combined RM value of the set of countermeasures
                        RM_combined = rm_indv - rm_intersection
                        #print "COV " + str(cov_int)
                        #print 'RM ' + str(RM_combined)
                        #print "EF " + str(min(list_ef))

                        #RORI calculation for the subset of combined countermeasure
                        rori_comb = (((ALE * RM_combined) - ARC_subset ) / (ARC_subset + AIV)) * 100
                        #print "RORI " + str(rori_comb)

                        #Dictionary to save all the useful information about the RORI calculation
                        aux_dict = {'countermeasures': id_countermeasures, 'ARC':ARC_subset, 'COV':cov_int,'EF':min(list_ef),'RM':RM_combined,'rori':rori_comb}

                        #Append the dictionary to the list to be returned by the method
                        rori_combined_list.append(aux_dict)

        return rori_combined_list

    #---------------------------------
    def loadFromXML(self, pathRORI): 
        
        #Read the XOrBAC file
        try:
            with open(pathRORI) as file:
                pass
        except IOError as e:
            print "Unable to open file" #Does not exist OR no read permissions
            sys.exit(2)

        try:
            parser = etree.XMLParser(remove_blank_text=True)
            self.rori_file = etree.parse(pathRORI,parser)
        except etree.XMLSyntaxError, e:
            print "Bad XML Syntax on the given file"
            return False

        organizations = self.rori_file.find('//ORGANIZATIONS')
        if organizations is None:
            return False
        self.rori_organizations = self.getOrganization(organizations)

    
        incidents = self.rori_file.find('//INCIDENTS')
        if incidents is None:
            return False
        self.rori_incidents = self.getIncidents(incidents)

    
        equipments = self.rori_file.find('//EQUIPMENTS')
        if equipments is None:
            return False
        self.rori_equipments = self.getEquipments(equipments)

    
        countermeasures = self.rori_file.find('//COUNTERMEASURES')
        if countermeasures is None:
            return False
        self.rori_countermeasures = self.getCountermeasures(countermeasures)


        risk_mitigation = self.rori_file.find('//RISK_MITIGATION')
        if risk_mitigation is None:
            return False
        self.rori_risk_mitigation = self.getRM(risk_mitigation)

    
        annual_response_cost = self.rori_file.find('//ANNUAL_RESPONSE_COST')
        if annual_response_cost is None:
            return False
        self.rori_annual_response_cost = self.getARC(annual_response_cost)

    
        annual_loss_expectancy = self.rori_file.find('//ANNUAL_LOSS_EXPECTANCY')
        if annual_loss_expectancy is None:
            return False
        self.rori_annual_loss_expectancy = self.getALE(annual_loss_expectancy)

        return True

    #---------------------------------
    def getIndividualRORI(self,org_v, org_k, inc_v, inc_k):

        if inc_v['id_organization'] == org_k:
            print "Individual Countermeasure Evaluation for the: "
            print inc_v['name'] + " incident at the organization: " + org_v['name']

            #Call to the Individual RORI evaluation method
            self.ind_rori = self.individualRORI(org_v,inc_v)
            if not self.ind_rori or self.ind_rori==[]:
                print "There was an error on the Individual RORI evaluation!!!"
                return False

            best_ind_rori = 0
            best_cou = ""
            best_equ = ""
            self.avg_ind_rori = 0

            # Append the output of the individual rori to an XML file
            # That file will contain the same info used as an input plus the new output element at the end of it
            xml_root = self.rori_file.getroot()
            #Create the OUTPUT element inside the XML
            xml_output = etree.Element('OUTPUT')
            #Append the INDIVIDUAL subelement that will contain all the rori individual values
            xml_individual = etree.SubElement(xml_output,'INDIVIDUAL')


            print "Countermeasure                        Equipment                          RORI Index"
            i=0
            att = []
            for ind in self.ind_rori:
                #Create the attributes of the XML rori_individual element
                att.append({'id_organization':org_k, 'id_incident':inc_k, 'id_countermeasure': str(ind['countermeasure']),'rori_index':str(round(ind['rori'],2)),'best':"False"})


                cou_name = self.rori_countermeasures[ind['countermeasure']]['name']
                cou_equ = self.rori_countermeasures[ind['countermeasure']]['id_equipment']

                if cou_equ != "":
                    equ_name = self.rori_equipments[cou_equ]['name']
                else:
                    equ_name = "---"

                print cou_name + "                            " + equ_name + "                        " + str(round(ind['rori'],2))

                if ind['rori'] >= best_ind_rori:
                    best_ind_rori = ind['rori']
                    best_index = i
                    best_cou = cou_name
                    best_equ = equ_name

                self.avg_ind_rori += ind['rori']
                i +=1

            #Iterate the list of attributes to establish the best RORI index
            i = 0
            for at in att:
                if i == best_index:
                    at['best'] = "True"
                etree.SubElement(xml_individual, "rori_individual", at)
                i += 1

            #Append the new XML elements to the XML root
            xml_root.append(xml_output)

            #The average RORI index for the individual Countermeasure is:
            self.avg_ind_rori = self.avg_ind_rori/len(self.ind_rori)

            print "\n\nThe best countermeasure based on the RORI index is:"
            print "\""+best_cou + "\" enforced by the equipment: \"" + best_equ + "\" with a RORI index of: "+ str(round(best_ind_rori,2))+"%"

        return True

    #---------------------------------
    def getCombinedRORI(self, org_v, org_k, inc_v, inc_k):
        if inc_v['id_organization'] == org_k:
            print "\n\n\n"
            print "Combined Countermeasure Evaluation for the: "
            print "\""+inc_v['name'] + "\" incident at the organization: " + org_v['name']


            print "The average RORI index for the individual Countermeasure is:"
            print str(round(self.avg_ind_rori,2))

            #Discard countermeasure that are bellow the average and totally restrictive
            self.rori_to_combine = []
            for ind in self.ind_rori:
                if ind['rori'] >= self.avg_ind_rori and not self.rori_countermeasures[ind['countermeasure']]['totally_restrictive']:
                    self.rori_to_combine.append(ind)


            print str(len(self.ind_rori)-len(self.rori_to_combine))+" countermeasures have been discarded for the " \
                                                               "combined evaluation since they are bellow the average or are totally restrictive"
            #Call to the Combined RORI calculation Method
            self.combined_rori = self.combinedRORI()
            if not self.combined_rori or self.combined_rori==[]:
                print "There was an error on the Combined RORI evaluation!!!"
                return False

            best_comb_rori = 0
            best_comb_cou = ""
            best_comb_equ = ""

            # Append the output of the combined rori to the OUTPUT XML element created in the individual calculation
            xml_output = self.rori_file.find('//OUTPUT')
            #Append the COMBINED sub-element that will contain all the rori combined values
            xml_combined = etree.SubElement(xml_output,'COMBINED')

            print "\nCombinations        ARC           COV          EF         RM          RORI Index"
            att = []
            i = 0
            for comb in self.combined_rori:
                cou_name = (', ').join(sorted(comb['countermeasures']))
                comb_ARC = str(round(comb['ARC'],2))
                comb_COV = str(round(comb['COV'],2))
                comb_EF = str(round(comb['EF'],2))
                comb_RM = str(round(comb['RM'],2))
                comb_rori = str(round(comb['rori'],2))

                #Create the attributes of the XML rori_individual element
                att.append({'id_organization':org_k, 'id_incident':inc_k, 'id_countermeasure': cou_name,'rori_index':comb_rori,'best':"False"})

                print cou_name + "    " + comb_ARC + "         " + comb_COV + "         " + comb_EF + "         " + comb_RM+ "         " + comb_rori

                if comb['rori'] >= best_comb_rori:
                    best_comb_rori = comb['rori']
                    best_comb_cou = cou_name
                    best_comb_index = i
                i +=1

            #Iterate the list of attributes to establish the best RORI index
            i = 0
            for at in att:
                if i == best_comb_index:
                    at['best'] = "True"
                etree.SubElement(xml_combined, "rori_combined", at)
                i += 1

            #Append the new XML elements to the XML root
            xml_output.append(xml_combined)
            #print etree.tostring(self.rori_file, pretty_print=True)

            print "\nThe best countermeasure based on the RORI index is:"
            print "\""+best_comb_cou + "\" with a RORI index of: "+ str(round(best_comb_rori,2))+"%"

        return True


def main(argv):
    #pathRORI = "./RORI_input2.xml"
    #rori = RORICalculation(pathRORI)

    inputfile = ''
    outputfile = ''
    try:
        opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
    except getopt.GetoptError:
        print 'Usage: '
        print 'RORI.py -i <inputfile> -o <outputfile>'
        sys.exit(2)

    if not opts:
        print 'Usage: '
        print 'RORI.py -i <inputfile> -o <outputfile>'
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print 'RORI.py -i <inputfile> -o <outputfile>'
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg

    if inputfile != "":
        #Instance of the RORICalculation class
        rori = RORICalculation()

        #Load the Values from the input file
        if not rori.loadFromXML(inputfile):
            print "Error Loading the information in the input XML file!!"
            sys.exit(2)

        for org_k, org_v in rori.rori_organizations.iteritems():
            for inc_k, inc_v in rori.rori_incidents.iteritems():
                #Check if the required information to perform the RORI calculation has been given
                if rori.informationRequired:
                    if not rori.getIndividualRORI(org_v, org_k, inc_v, inc_k):
                        print "Error performing the Individual RORI evaluation!!"
                        sys.exit(2)
                    #Check if the required information to perform the combination of countermeasures has been given
                    if rori.toBeCombined:
                        if not rori.getCombinedRORI(org_v, org_k, inc_v, inc_k):
                            print "Error performing the Combined RORI evaluation!!"
                            sys.exit(2)
                else:
                    print "Error: There is required information to perform the RORI evaluation that has not been given"
                    sys.exit(2)

        #Generation of OutputFile
        if outputfile == "":
            outputfile = 'RORI_Output.xml'
        print "Generating output file: "+outputfile
        rori.rori_file.write(outputfile, pretty_print=True)


if __name__ == "__main__":
    main(sys.argv[1:])
