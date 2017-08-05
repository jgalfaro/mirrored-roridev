#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'ender_al'


import platform, os
try:
    import wx
except ImportError:
    raise ImportError,"wxPython module is required"

if (platform.system() == "Linux") and ("Ubuntu" in platform.dist()):
    #Export environment variable to properly show menu bar
    os.environ["UBUNTU_MENUPROXY"] = "0"

from wx import xrc
from controller.OrganizationController import OrganizationController
from model.Organization import Organization
from controller.EquipmentController import EquipmentController
from model.Equipment import Equipment
from controller.IncidentController import IncidentController
from model.Incident import Incident
from controller.CountermeasureController import CountermeasureController
from model.Countermeasure import Countermeasure
from controller.RORICalController import RORICalController
from controller.GraphRepresentationController import GraphRepresentationController


class roriEngine(wx.App):


    def OnInit(self):
        self.res = xrc.XmlResource('./xrc/GUI.xrc')
        self.main_frame = self.res.LoadFrame(None, 'Main')

        #Events of buttons
        self.main_frame.Bind(wx.EVT_BUTTON, self.onClickOrganization, id=xrc.XRCID('main_bpOrganization'))
        self.main_frame.Bind(wx.EVT_BUTTON, self.onClickEquipment, id=xrc.XRCID('main_bpEquipment'))
        self.main_frame.Bind(wx.EVT_BUTTON, self.onClickIncidents, id=xrc.XRCID('main_bpIncidents'))
        self.main_frame.Bind(wx.EVT_BUTTON, self.onClickCountermeasures, id=xrc.XRCID('main_bpCountermeasures'))
        self.main_frame.Bind(wx.EVT_BUTTON, self.onClickRORICal, id=xrc.XRCID('main_bpRORICalculation'))
        self.main_frame.Bind(wx.EVT_BUTTON, self.onClickGraphRepresentation, id=xrc.XRCID('main_bpGraphRepresentation'))

        self.Bind(wx.EVT_CLOSE, self.onExit)

        self.main_frame.Show()
        return True

    def onClickOrganization(self, evt):
        #Check if the frame was already created
        frame = self.main_frame.FindWindowByName("OrganizationFrame")
        if not frame:
            self.Organization = Organization()
            self.OrganizationController = OrganizationController(self)
        else:
            frame.Raise()
        return

    def onClickEquipment(self, evt):
        #Check if the frame was already created
        frame = self.main_frame.FindWindowByName("EquipmentFrame")
        if not frame:
            self.Equipment = Equipment()
            self.EquipmentController = EquipmentController(self)
        else:
            frame.Raise()
        return

    def onClickIncidents(self, evt):
        #Check if the frame was already created
        frame = self.main_frame.FindWindowByName("IncidentFrame")
        if not frame:
            self.Incident = Incident()
            self.IncidentController = IncidentController(self)
        else:
            frame.Raise()
        return

    def onClickCountermeasures(self, evt):
        #Check if the frame was already created
        frame = self.main_frame.FindWindowByName("CountermeasureFrame")
        if not frame:
            self.Countermeasure = Countermeasure()
            self.CountermeasureController = CountermeasureController(self)
        else:
            frame.Raise()
        return

    def onClickRORICal(self, evt):
        #Check if the frame was already created
        frame = self.main_frame.FindWindowByName("RORICalFrame")
        if not frame:
            #self.RORICal = RORICal()
            self.RORICalController = RORICalController(self)
        else:
            frame.Raise()
        return

    def onClickGraphRepresentation(self, evt):
        #Check if the frame was already created
        frame = self.main_frame.FindWindowByName("GraphFrame")
        if not frame:
            #self.RORICal = RORICal()
            self.GraphRepresentationController = GraphRepresentationController(self)
        else:
            frame.Raise()
        return

    def onExit(self, evt):
        self.Destroy()

def main():
    app = roriEngine()
    app.MainLoop()

if __name__ == '__main__':
    main()

