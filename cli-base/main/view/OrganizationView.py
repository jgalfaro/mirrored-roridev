__author__ = 'ender_al'
# -*- coding: utf-8 *-*

try:
    import wx
except ImportError:
    raise ImportError,"wxPython module is required"

from wx import xrc

class OrganizationView(wx.Frame):

    def __init__(self, app):
        self.app = app
        self.res = self.app.res
        self.frame = self.res.LoadFrame(self.app.main_frame, 'OrganizationFrame')
        self.frame.SetSize((732,462))

    #-------------------------------------------------------------------------------------------------------
    def show(self):
        self.frame.Show()

    #-------------------------------------------------------------------------------------------------------
    def loadListOfOrganizations(self,list):
        self.organizationList = xrc.XRCCTRL(self.frame, 'organizationList')
        self.organizationList.SetSingleStyle(wx.LC_REPORT, True)
        self.organizationList.InsertColumn(0, 'Name', format=wx.LIST_FORMAT_LEFT, width=-1)
        self.organizationList.InsertColumn(1, 'Description', format=wx.LIST_FORMAT_LEFT, width=-1)
        self.organizationList.InsertColumn(2, 'AIV', format=wx.LIST_FORMAT_LEFT, width=-1)

        #Load the list of organizations
        index = 0
        for organization in list:
            item = self.organizationList.InsertStringItem(index, str(organization[1]))
            self.organizationList.SetItemData(item, organization[0])

            self.organizationList.SetStringItem(index, 1, str(organization[2]))
            self.organizationList.SetStringItem(index, 2, str(organization[3]))
            index+=1

        #Get the frame width to equally distribute the size of the columns
        f_width, f_height = self.frame.GetSizeTuple()
        num_col = self.organizationList.GetColumnCount()

        self.organizationList.SetColumnWidth(0, f_width/num_col)
        self.organizationList.SetColumnWidth(1, f_width/num_col)
        self.organizationList.SetColumnWidth(2, f_width/num_col)

    #-------------------------------------------------------------------------------------------------------
    def getItemCount(self):
        return self.organizationList.GetSelectedItemCount()

    #-------------------------------------------------------------------------------------------------------
    def getIDItemSelected(self):
        itemIndex = self.organizationList.GetFirstSelected()
        return self.organizationList.GetItemData(itemIndex)

    #-------------------------------------------------------------------------------------------------------
    def getSetItemsSelected(self):
        id_list = []
        flag = True
        itemIndex = self.organizationList.GetFirstSelected()
        id_list.append(self.organizationList.GetItemData(itemIndex))
        while flag:
            itemIndex = self.organizationList.GetNextSelected(itemIndex)
            if itemIndex != -1:
                id_list.append(self.organizationList.GetItemData(itemIndex))
            else:
                flag = False

        return id_list

#-------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------
class OrganizationEditorView:
    def __init__(self, parent, app, add=True):
        self.Organization = app.Organization
        self.app = app
        self.Dialog = self.app.res.LoadDialog(parent, 'orgEditor')
        self.Dialog.SetSize((340,260))
        btnAddOrganization = xrc.XRCCTRL(self.Dialog, 'org_btnedit')


        self.org_textmsg = xrc.XRCCTRL(self.Dialog, 'org_txtmsg')

        self.org_textname = xrc.XRCCTRL(self.Dialog, 'org_textname')
        self.org_textdescription = xrc.XRCCTRL(self.Dialog, 'org_textdescription')
        if(add):
            btnAddOrganization.SetLabel('Add')
        else:
            btnAddOrganization.SetLabel('Save')

    #-------------------------------------------------------------------------------------------------------
    def Show(self):
        self.Dialog.ShowModal()

    #-------------------------------------------------------------------------------------------------------
    def loadOrganization(self, name, description):
        self.org_textname.SetValue(name)
        self.org_textdescription.SetValue(description)