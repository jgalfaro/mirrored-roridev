#!/usr/bin/python
# -*- coding: utf-8 -*-


import platform, os, sys
try:
    import wx
except ImportError:
    raise ImportError,"wxPython module is required"

if (platform.system() == "Linux") and ("Ubuntu" in platform.dist()):
    #Export environment variable to properly show menu bar
    os.environ["UBUNTU_MENUPROXY"] = "0"

from wx import xrc
from RORI import RORICalculation


class rori(wx.App):


    def OnInit(self):
        self.res = xrc.XmlResource('./xrc/RORI.xrc')
        self.main_frame = self.res.LoadFrame(None, 'RORI')

        #Events of Menu
        #Bind Events to the items in the Menu
        self.main_frame.Bind(wx.EVT_MENU, self.onLoadFile, id=xrc.XRCID('rori_load'))
        self.main_frame.Bind(wx.EVT_MENU, self.onGenerateOutputFile, id=xrc.XRCID('rori_generateoutput'))
        self.main_frame.Bind(wx.EVT_BUTTON, self.onPerformEvaluation, id=xrc.XRCID('rori_btncalcul'))
        self.main_frame.Bind(wx.EVT_MENU, self.onExit, id=xrc.XRCID('rori_exit'))
        self.main_frame.Bind(wx.EVT_BUTTON, self.onExit, id=xrc.XRCID('rori_exit1'))

        #Title
        self.title = xrc.XRCCTRL(self.main_frame, 'rori_title')

        #Lists
        self.individualList = xrc.XRCCTRL(self.main_frame, 'rori_listindividual')
        self.combinedList = xrc.XRCCTRL(self.main_frame, 'rori_listcombined')

        self.main_frame.SetSize((600,550))
        self.main_frame.Show()
        self.evaluationOK = False
        self.rori_calculator = None
        return True

    def onLoadFile(self, evt):

        openFileDialog = wx.FileDialog(self.main_frame, "Open RORI input (.xml) file", "", "",
                                       "XML files (*.xml)|*.xml", wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)

        if openFileDialog.ShowModal() == wx.ID_CANCEL:
            return     # the user changed idea...

        # proceed loading the file chosen by the user
        # this can be done with e.g. wxPython input streams:
        #print openFileDialog.GetPath()
        input_path = openFileDialog.GetPath()

        try:
            with open(input_path) as file:
                pass
        except IOError as e:
            print "Unable to open file" #Does not exist OR no read permissions
            wx.LogError("Cannot open file '%s'."%input_path)
            return

        wx.MessageBox("File '%s', successfully loaded!"%input_path)
        self.input_path = input_path
        return



    def onPerformEvaluation(self, evt):
        self.rori_calculator = None
        self.rori_calculator = RORICalculation()

        #Load the Values from the input file
        if not self.rori_calculator.loadFromXML(self.input_path):
            wx.MessageBox("Error Loading the information in the input XML file!!")
            return
        #If the values are OK perform the evaluation
        for org_k, org_v in self.rori_calculator.rori_organizations.iteritems():
            for inc_k, inc_v in self.rori_calculator.rori_incidents.iteritems():
                #Change title
                self.title.SetLabel(inc_v['name'] + " incident at the organization: " + org_v['name'])

                #Check if the required information to perform the RORI calculation has been given
                if self.rori_calculator.informationRequired:
                    if not self.rori_calculator.getIndividualRORI(org_v, org_k, inc_v, inc_k):
                        wx.MessageBox("Error performing the Individual RORI evaluation!!")
                        return
                    else:
                        #-------------------------------------
                        # Generation of the list to be loaded in the GUI for the Individual Evaluation
                        individual_list = []
                        best_ind_rori = 0
                        best_id = 0

                        for row in self.rori_calculator.ind_rori:
                            cou_name = self.rori_calculator.rori_countermeasures[row['countermeasure']]['name']
                            cou_equ = self.rori_calculator.rori_countermeasures[row['countermeasure']]['id_equipment']
                            #print rori_calculator.rori_equipments
                            if cou_equ != "":
                                cou_equ = self.rori_calculator.rori_equipments[cou_equ]['name']
                            rori_index = round(row['rori'],2)

                            if row['rori'] >= best_ind_rori:
                                best_ind_rori = row['rori']
                                best_id = row['countermeasure']

                            individual_list.append([row['countermeasure'],cou_name, cou_equ, rori_index])

                        #Load the list of individual RORI index on GUI
                        self.loadListIndividual(individual_list, best_id)

                    #-------------------------------------------------------
                    # Combined Countermeasure Evaluation
                    #Check if the required information to perform the combination of countermeasures has been given
                    if self.rori_calculator.toBeCombined:
                        if not self.rori_calculator.getCombinedRORI(org_v, org_k, inc_v, inc_k):
                            wx.MessageBox("Error performing the Combined RORI evaluation!!")
                            return
                        else:
                            #Create the list to be shown in the GUI
                            combined_list = []
                            best_comb_rori = 0
                            best_id = 0
                            i = 0
                            for row in self.rori_calculator.combined_rori:
                                comb_ids = (', ').join(sorted(row['countermeasures']))
                                comb_ARC = str(round(row['ARC'],2))
                                comb_COV = str(round(row['COV'],2))
                                comb_EF = str(round(row['EF'],2))
                                comb_RM = str(round(row['RM'],2))
                                comb_rori = str(round(row['rori'],2))

                                if row['rori'] >= best_comb_rori:
                                    best_comb_rori = row['rori']
                                    best_id = i

                                combined_list.append([comb_ids,comb_ARC, comb_COV,comb_EF,comb_RM,comb_rori])
                                i += 1
                            #Load the list of individual RORI index on GUI
                            self.loadListCombined(combined_list, best_id)
                    else:
                        wx.MessageBox("There is not combined countermeasure evaluation due to lack of individual values of EF and COV for the countermeasures")
                        self.combinedList.ClearAll()
                else:
                    wx.MessageBox("Error: There is information required to perform the RORI evaluation that has not been given")
                    return

        self.evaluationOK = True
        return

    #--------------------------------------------------------------------------------------------------------------
    def loadListIndividual(self,list, best):

        self.individualList.ClearAll()

        self.individualList.SetSingleStyle(wx.LC_REPORT, True)
        self.individualList.InsertColumn(0, 'ID', format=wx.LIST_FORMAT_LEFT,width=-1)
        self.individualList.InsertColumn(1, 'Name', format=wx.LIST_FORMAT_LEFT, width=-1)
        self.individualList.InsertColumn(2, 'Equipment', format=wx.LIST_FORMAT_LEFT, width=-1)
        self.individualList.InsertColumn(3, 'RORI', format=wx.LIST_FORMAT_LEFT, width=-1)

        #Load list of Incidents
        index = 0
        for rori_individual in list:
            item = self.individualList.InsertStringItem(index, str(rori_individual[0]))
            #individualList.SetItemData(item, rori_individual[0])
            self.individualList.SetStringItem(index, 1, str(rori_individual[1]))
            self.individualList.SetStringItem(index, 2, str(rori_individual[2]))
            self.individualList.SetStringItem(index, 3, str(rori_individual[3]))

            if rori_individual[0] == best:
                self.individualList.SetItemBackgroundColour(index,wx.BLUE)
                self.individualList.SetItemTextColour(index, wx.WHITE)
            index+=1

        #Get the frame width to equally distribute the size of the list columns
        f_width, f_height = self.main_frame.GetSizeTuple()

        self.individualList.SetColumnWidth(0, f_width/4)
        self.individualList.SetColumnWidth(1, f_width/4)
        self.individualList.SetColumnWidth(2, f_width/4)
        self.individualList.SetColumnWidth(3, f_width/4)

    #--------------------------------------------------------------------------------------------------
    def loadListCombined(self,list, best):
        self.combinedList.SetSingleStyle(wx.LC_REPORT, True)
        self.combinedList.InsertColumn(0, 'Combinations', format=wx.LIST_FORMAT_LEFT,width=-1)
        self.combinedList.InsertColumn(1, 'ARC', format=wx.LIST_FORMAT_LEFT, width=-1)
        self.combinedList.InsertColumn(2, 'COV', format=wx.LIST_FORMAT_LEFT, width=-1)
        self.combinedList.InsertColumn(3, 'EF', format=wx.LIST_FORMAT_LEFT, width=-1)
        self.combinedList.InsertColumn(4, 'RM', format=wx.LIST_FORMAT_LEFT, width=-1)
        self.combinedList.InsertColumn(5, 'RORI index', format=wx.LIST_FORMAT_LEFT, width=-1)

        #Load list of Incidents
        index = 0
        for rori_combined in list:
            item = self.combinedList.InsertStringItem(index, str(rori_combined[0]))

            self.combinedList.SetStringItem(index, 1, str(rori_combined[1]))
            self.combinedList.SetStringItem(index, 2, str(rori_combined[2]))
            self.combinedList.SetStringItem(index, 3, str(rori_combined[3]))
            self.combinedList.SetStringItem(index, 4, str(rori_combined[4]))
            self.combinedList.SetStringItem(index, 5, str(rori_combined[5]))

            if index == best:
                self.combinedList.SetItemBackgroundColour(index,wx.BLUE)
                self.combinedList.SetItemTextColour(index, wx.WHITE)
            index+=1

        #Get the frame width to equally distribute the size of the list columns
        f_width, f_height = self.main_frame.GetSizeTuple()

        self.combinedList.SetColumnWidth(0, f_width/6)
        self.combinedList.SetColumnWidth(1, f_width/6)
        self.combinedList.SetColumnWidth(2, f_width/6)
        self.combinedList.SetColumnWidth(3, f_width/6)
        self.combinedList.SetColumnWidth(4, f_width/6)
        self.combinedList.SetColumnWidth(5, f_width/6)

    #------------------------------------------------------------------------
    def onGenerateOutputFile(self, event):

        if self.evaluationOK:
            saveFileDialog = wx.FileDialog(self.main_frame, "Save RORI output file", "", "",
                                       "xml files (*.xml)|*.xml", wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)

            if saveFileDialog.ShowModal() == wx.ID_CANCEL:
                return     # the user changed idea...

            # save the current contents in the file
            # this can be done with e.g. wxPython output streams:
            output_stream = saveFileDialog.GetPath()
            
            if output_stream == "":
                wx.MessageBox('Please give a name to the output file!!!')
                return
            
            #If the user has not given an XML file extension, add it
            if output_stream.find('.xml') == -1:
                output_stream += ".xml"
                
            #Generation of OutputFile
            self.rori_calculator.rori_file.write(output_stream, pretty_print=True)
            #Read the XML file
            try:
                with open(output_stream) as file:
                    wx.MessageBox("File '%s', successfully generated!!!"%output_stream)
            except IOError as e:
                wx.MessageBox("Error generating the file '%s'!!!"%output_stream)

        else:
            wx.MessageBox("There is nothing to generate since any RORI evaluation has been performed!!!")

        return

    #-------------------------------------------------------------------------------------------------------------
    def onExit(self, evt):
       self.Exit()

def main():
    app = rori()
    app.MainLoop()

if __name__ == '__main__':
    main()


