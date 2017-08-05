__author__ = 'ender_al'
# -*- coding: utf-8 *-*
import lib.db_conn as DBConn
from wx.lib.pubsub import Publisher
import MySQLdb

class RORICal:

    def __init__(self):
        self.idOrg = 0
        self.idInc = 0
        self.idCou = 0
        self.db = DBConn.DBConn()

    #-------------------------------------------------------------------------------------------------------
    def readOrgInc(self):
        query = "SELECT inc.idIncident, inc.Name, inc.IDRef FROM Incident inc Inner Join ALE ale ON inc.idIncident = ale.FK_Incident where ale.FK_Organization = %s"
        values = (self.idOrg)

        try:
            result = self.db.execute(query, values)
        except MySQLdb.Error, e:
            try:
                error = "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
                print error
                return 1, error
            except IndexError:
                error = "MySQL Error: %s" % str(e)
                print error
                return 1, error
        return 0, result

    #-------------------------------------------------------------------------------------------------------
    def readIncCou(self):
        query = "SELECT cou.idCountermeasure, cou.Name, cou.Totally_Restrictive, cou.FK_Equipment, cou.IDRef FROM Countermeasure cou Inner Join Incident_has_Countermeasure IHC ON cou.idCountermeasure = IHC.FK_Countermeasure where IHC.FK_Incident = %s"
        values = (self.idInc)

        try:
            result = self.db.execute(query, values)
        except MySQLdb.Error, e:
            try:
                error = "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
                print error
                return 1, error
            except IndexError:
                error = "MySQL Error: %s" % str(e)
                print error
                return 1, error
        return 0, result

    #-------------------------------------------------------------------------------------------------------
    def readResCou(self):
        query = "SELECT Restriction FROM Restriction WHERE FK_Countermeasure = %s"
        values = (self.idCou)

        try:
            result = self.db.execute(query, values)
        except MySQLdb.Error, e:
            try:
                error = "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
                print error
                return 1, error
            except IndexError:
                error = "MySQL Error: %s" % str(e)
                print error
                return 1, error
        return 0, result

    #-------------------------------------------------------------------------------------------------------
    def readARCCou(self):
        query = "SELECT idARC FROM ARC WHERE FK_Countermeasure = %s"
        values = (self.idCou)

        try:
            result = self.db.execute(query, values)
        except MySQLdb.Error, e:
            try:
                error = "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
                print error
                return 1, error
            except IndexError:
                error = "MySQL Error: %s" % str(e)
                print error
                return 1, error
        return 0, result

    #-------------------------------------------------------------------------------------------------------
    def readRMCou(self):
        query = "SELECT idRM FROM ARC WHERE FK_Countermeasure = %s"
        values = (self.idCou)

        try:
            result = self.db.execute(query, values)
        except MySQLdb.Error, e:
            try:
                error = "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
                print error
                return 1, error
            except IndexError:
                error = "MySQL Error: %s" % str(e)
                print error
                return 1, error
        return 0, result