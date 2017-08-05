__author__ = 'ender_al'
# -*- coding: utf-8 *-*
import lib.db_conn as DBConn
from wx.lib.pubsub import Publisher
import MySQLdb

class Incident:

    def __init__(self):
        self.id = 0
        self.IDRef = ''
        self.Name = ''
        self.Description = ''
        self.Risk_Level = ''
        self.db = DBConn.DBConn()

    #-------------------------------------------------------------------------------------------------------
    def create(self):
        """Create a new registry"""
        query = "INSERT INTO Incident (IDRef, Name, Description, Risk_Level) VALUES (%s, %s, %s, %s)"
        values = (self.IDRef, self.Name, self.Description, self.Risk_Level)

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

        Publisher.sendMessage("incident_created", None)
        return 0

    #-------------------------------------------------------------------------------------------------------
    def update(self):
        """Update an existing register"""
        query = "UPDATE Incident SET IDRef = %s, Name = %s, Description = %s, Risk_Level = %s WHERE idIncident = %s"
        values = (self.IDRef, self.Name, self.Description, self.Risk_Level, self.id)
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

        Publisher.sendMessage("incident_updated", None)
        return 0, result

    #-------------------------------------------------------------------------------------------------------
    def read_all(self):
        """Read all rows"""
        query = "SELECT idIncident, Name, Description, Risk_Level, IDRef FROM Incident"
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
        query = "SELECT idIncident, Name, Description, Risk_Level, IDRef FROM Incident WHERE idIncident = %s"
        values = (self.id)

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
    def readByName(self):
        query = "SELECT idIncident, Name, Description, Risk_Level, IDRef FROM Incident WHERE Name = %s"
        values = (self.Name)

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
    def readByIDRef(self):
        query = "SELECT idIncident, Name, Description, Risk_Level, IDRef FROM Incident WHERE IDRef = %s"
        values = (self.IDRef)

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
        query = "DELETE FROM Incident WHERE idIncident = %s"
        values = self.id

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

        Publisher.sendMessage("incident_deleted", None)
        return 0, result