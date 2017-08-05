__author__ = 'ender_al'
# -*- coding: utf-8 *-*

import wx
from wx import xrc
from wx.lib.pubsub import Publisher

from view.OrganizationView import OrganizationView
from view.OrganizationView import OrganizationEditorView
from controller.AEVController import AEVController
from controller.ALEController import ALEController
from model.AEV import AEV


class OrganizationController:

    def __init__(self, app):
        self.app = app
        self.org_view = OrganizationView(app)

        #Close the Frame
        #self.org_view.frame.Bind(wx.EVT_CLOSE,self.onClose)

        #Bind Events to the items in the Menu
        self.org_view.frame.Bind(wx.EVT_MENU, self.onCreateOrganization, id=xrc.XRCID('org_mitcreate'))
        self.org_view.frame.Bind(wx.EVT_MENU, self.onEditOrganization, id=xrc.XRCID('org_mitedit'))
        self.org_view.frame.Bind(wx.EVT_MENU, self.onDeleteOrganization, id=xrc.XRCID('org_mitdelete'))
        self.org_view.frame.Bind(wx.EVT_MENU, self.onExit, id=xrc.XRCID('org_exit'))

        #Bind Events to the items in the ToolBar
        self.org_view.frame.Bind(wx.EVT_TOOL, self.onCreateOrganization, id=xrc.XRCID('org_toolcreate'))
        self.org_view.frame.Bind(wx.EVT_TOOL, self.onEditOrganization, id=xrc.XRCID('org_tooledit'))
        self.org_view.frame.Bind(wx.EVT_TOOL, self.onDeleteOrganization, id=xrc.XRCID('org_tooldelete'))
        self.org_view.frame.Bind(wx.EVT_TOOL, self.onRelationOrgEqu, id=xrc.XRCID('org_toolorg-equ'))
        self.org_view.frame.Bind(wx.EVT_TOOL, self.onRelationOrgInc, id=xrc.XRCID('org_toolorg-inc'))

        #Subscribe to the messages given by the model. In case of any change the list of elements will be updated
        Publisher.subscribe(self.organizationModified, 'organization_deleted')
        Publisher.subscribe(self.organizationModified, 'aev_created')
        Publisher.subscribe(self.organizationModified, 'aev_deleted')
        Publisher.subscribe(self.organizationModified, 'aev_updated')
        Publisher.subscribe(self.organizationModified, 'organization_created')
        Publisher.subscribe(self.organizationModified, 'organization_updated')


        #Filter
        self.txtFilter = xrc.XRCCTRL(self.org_view.frame, 'org_txtfilter')
        self.btnFilter = xrc.XRCCTRL(self.org_view.frame, 'org_btnfilter')
        self.org_view.frame.Bind(wx.EVT_TEXT_ENTER, self.onFilterOrganization, self.txtFilter)
        self.org_view.frame.Bind(wx.EVT_BUTTON, self.onFilterOrganization, self.btnFilter)
        self.GUIorganizations = []

        #Load the list of organizations in the View
        self.loadListOfOrganizations_controller()
        self.org_view.show()

    #------------------------------------------------------------------------------------------------------------
    def loadListOfOrganizations_controller(self):
        (error, values) = self.app.Organization.read_all()
        if error:
            msg= "Error reading the list of Organizations: \n" + values
            wx.MessageBox(msg)
        else:
            #Clear the Filter input
            self.txtFilter.SetValue("")

            #Get the AIV for each organization
            aev = AEV()
            list_org = []
            for org in values:
                aev.FK_Organization = org[0]
                error, aev_values = aev.read_by_organization()
                if error:
                    msg= "Error reading the list of Organizations: \n" + aev_values
                    wx.MessageBox(msg)
                total_aev = 0
                for org_aev in aev_values:
                    #Get the total value of the aev
                    total_aev += org_aev[7]
                #Convert tuple to list
                lorg = list(org)
                #Append the AIV Value to the list passed to the view
                lorg.append(total_aev)
                list_org.append(lorg)

            self.GUIorganizations = list_org
            self.org_view.loadListOfOrganizations(list_org)

    #-------------------------------------------------------------------------------------------------------
    def onFilterOrganization(self,event):
        new_list = []
        string = self.txtFilter.GetValue().upper()
        if string !="":
            for item in self.GUIorganizations:
                for sub_item in item:
                    if type(sub_item) is str:
                        if any([string in sub_item.upper()]):
                            new_list.append(item)
                            break
            self.org_view.loadListOfOrganizations(new_list)
        else:
            self.org_view.loadListOfOrganizations(self.GUIorganizations)

    #------------------------------------------------------------------------------------------------------------
    def organizationModified(self, msg):
        self.loadListOfOrganizations_controller()

    #------------------------------------------------------------------------------------------------------------
    def onCreateOrganization(self, evt):
        editor = OrganizationEditorController(self.app, self.org_view, True)

    #------------------------------------------------------------------------------------------------------------
    def onEditOrganization(self, evt):
        #Check if the dialog was already created
        org_frame = self.app.main_frame.FindWindowByName("OrganizationFrame")
        edt_diag = org_frame.FindWindowByName("orgEditor")

        if not edt_diag:
            count = self.org_view.getItemCount()
            if (count == 0):
                wx.MessageBox("Please select an Organization to edit!")
            elif (count > 1):
                wx.MessageBox("Please select just one Organization to be edited!")
            else:
                editor = OrganizationEditorController(self.app, self.org_view, False)
        else:
            edt_diag.Raise()

        return

    #------------------------------------------------------------------------------------------------------------
    def onDeleteOrganization(self, evt):
        count = self.org_view.getItemCount()
        if (count == 0):
            wx.MessageBox("Please select an Organization to be deleted!")
        else:
            msg = "Proceed to delete "+str(count)+" elements?"
            del_confirm = wx.MessageDialog(None, msg, 'Delete Confirmation', wx.YES_NO | wx.ICON_QUESTION)
            if del_confirm.ShowModal() == wx.ID_NO:
                return

            item_list = self.org_view.getSetItemsSelected()

            for id in item_list:
                self.app.Organization.id = id
                (error, values) = self.app.Organization.delete()
                if error:
                    msg= "There was an error deleting the organization: \n" + values
                    wx.MessageBox(msg)

    #------------------------------------------------------------------------------------------------------------
    def onRelationOrgEqu(self, evt):
        #Check if the dialog was already created
        org_frame = self.app.main_frame.FindWindowByName("OrganizationFrame")
        aev_diag = org_frame.FindWindowByName("AEVEditor")

        if not aev_diag:
            count = self.org_view.getItemCount()
            if (count == 0):
                wx.MessageBox("Please select an Organization to assign an PEP!")
            elif (count > 1):
                wx.MessageBox("Please select just one Organization to assign to an PEP!")
            else:
                editor = AEVController(self.app, self.org_view)
        else:
            aev_diag.Raise()

        return

    #------------------------------------------------------------------------------------------------------------
    def onRelationOrgInc(self, evt):
        #Check if the dialog was already created
        org_frame = self.app.main_frame.FindWindowByName("OrganizationFrame")
        ale_diag = org_frame.FindWindowByName("ALEEditor")

        if not ale_diag:
            count = self.org_view.getItemCount()
            if (count == 0):
                wx.MessageBox("Please select an Organization to assign an Detrimental Event!")
            elif (count > 1):
                wx.MessageBox("Please select just one Organization to assign to an Detrimental Event!")
            else:
                editor = ALEController(self.app, self.org_view)
        else:
            ale_diag.Raise()

        return

    #------------------------------------------------------------------------------------------------------------
    def onExit(self, evt):
       self.org_view.frame.Destroy()

#------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------
class OrganizationEditorController:

    def __init__(self, app, parent, add=True):
        self.app = app
        self.OrganizationView = parent
        self.org_edtview = OrganizationEditorView(self.OrganizationView.frame, self.app, add)
        btnAddOrganization = xrc.XRCCTRL(self.org_edtview.Dialog, 'org_btnedit')
        btnCancel = xrc.XRCCTRL(self.org_edtview.Dialog, 'org_btncancel')

        self.org_edtview.Dialog.Bind(wx.EVT_BUTTON, self.onCancel, btnCancel)
        self.org_edtview.Dialog.Bind(wx.EVT_CLOSE, self.onCancel)

        if(add):
            self.org_edtview.Dialog.Bind(wx.EVT_BUTTON, self.onAddOrganization, btnAddOrganization)
            self.org_edtview.Show()
        else:
            self.idOrganization = self.OrganizationView.getIDItemSelected()
            org = self.app.Organization
            org.id = self.idOrganization
            (error, values) = org.read()
            if error:
                msg= "Error reading the values from the organization: \n" + values
                wx.MessageBox(msg)
                self.onCancel(True)
            else:
                name = values[0][1]
                description = values[0][2]
                self.org_edtview.loadOrganization(name, description)
                self.org_edtview.Dialog.Bind(wx.EVT_BUTTON, self.onEditOrganization, btnAddOrganization)
                self.org_edtview.Show()

    #------------------------------------------------------------------------------------------------------------
    def onAddOrganization(self, evt):
        name = self.org_edtview.org_textname.GetValue()
        description = self.org_edtview.org_textdescription.GetValue()

        if name == '':
            self.org_edtview.org_textmsg.SetForegroundColour((255,0,0)) # set text color
            self.org_edtview.org_textmsg.SetLabel('* Mandatory Fields\nName cannot be empty!')
            return

        org = self.app.Organization
        org.Name = name
        org.Description = description
        error = org.create()
        if error:
            msg= "Error creating Organizations: \n"
            self.onCancel(True)
            wx.MessageBox(msg)

        self.org_edtview.Dialog.Close()
        return


    #------------------------------------------------------------------------------------------------------------
    def onEditOrganization(self, evt):
        name = self.org_edtview.org_textname.GetValue()
        description = self.org_edtview.org_textdescription.GetValue()

        if name == '':
            self.org_edtview.org_textmsg.SetForegroundColour((255,0,0)) # set text color
            self.org_edtview.org_textmsg.SetLabel('* Mandatory Fields\nName cannot be empty!')
            return

        org = self.app.Organization
        org.id = self.idOrganization
        org.Name = name
        org.Description = description
        (error, values) = org.update()
        if error:
            msg= "Error editing the organization: \n" + values
            self.onCancel(True)
            wx.MessageBox(msg)

        self.org_edtview.Dialog.Close()
        return

    #------------------------------------------------------------------------------------------------------------
    def onCancel(self,evt):
        self.org_edtview.Dialog.Destroy()
