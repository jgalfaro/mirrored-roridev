__author__ = 'ender_al'
# -*- coding: utf-8 *-*
import lib.db_conn as DBConn
from wx.lib.pubsub import Publisher
import MySQLdb

class IncidentHasCountermeasure:

    def __init__(self):
        self.FK_Incident = 0
        self.FK_Countermeasure = 0
        self.db = DBConn.DBConn()

    #-------------------------------------------------------------------------------------------------------
    def create(self):
        """Create a new registry"""
        query = "INSERT INTO Incident_has_Countermeasure (FK_Incident, FK_Countermeasure) VALUES (%s,%s)"
        values = (self.FK_Incident,self.FK_Countermeasure)

        try:
            self.db.execute(query, values)
        except MySQLdb.Error, e:
            try:
                error = "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
                print error
                return error
            except IndexError:
                error = "MySQL Error: %s" % str(e)
                print error
                return error

        Publisher.sendMessage("IncidentHasCountermeasure_created", None)
        return 0

    #-------------------------------------------------------------------------------------------------------
    def read_all(self):
        """Read all rows"""
        query = "SELECT FK_Incident, FK_Countermeasure FROM Incident_has_Countermeasure"
        try:
            result = self.db.execute(query)
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
    def read(self):
        query = "SELECT * FROM Incident_has_Countermeasure WHERE FK_Incident = %s AND FK_Countermeasure = %s"
        values = (self.FK_Incident, self.FK_Countermeasure)

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
    def readByIncident(self):
        query = "SELECT FK_Countermeasure FROM Incident_has_Countermeasure WHERE FK_Incident = %s"
        values = (self.FK_Incident)

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
    def readByCountermeasure(self):
        query = "SELECT FK_Incident FROM Incident_has_Countermeasure WHERE FK_Countermeasure = %s"
        values = (self.FK_Countermeasure)

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
    def delete(self):
        """Delete one or all rows"""
        query = "DELETE FROM Incident_has_Countermeasure WHERE (FK_Incident = %s AND FK_Countermeasure = %s)"
        values = (self.FK_Incident, self.FK_Countermeasure)

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

        Publisher.sendMessage("IncidentHasCountermeasure_deleted", None)
        return 0, result

    #-------------------------------------------------------------------------------------------------------
    def deleteByIncident(self):
        """Delete one or all rows"""
        query = "DELETE FROM Incident_has_Countermeasure WHERE FK_Incident = %s"
        values = self.FK_Incident

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

        Publisher.sendMessage("IncidentHasCountermeasure_deleted", None)
        return 0, result

    #-------------------------------------------------------------------------------------------------------
    def deleteByCountermeasure(self):
        """Delete one or all rows"""
        query = "DELETE FROM Incident_has_Countermeasure WHERE FK_Countermeasure = %s"
        values = self.FK_Countermeasure

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

        Publisher.sendMessage("IncidentHasCountermeasure_deleted", None)
        return 0, result