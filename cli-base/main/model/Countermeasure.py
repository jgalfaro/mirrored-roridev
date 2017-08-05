__author__ = 'ender_al'
# -*- coding: utf-8 *-*
import lib.db_conn as DBConn
from wx.lib.pubsub import Publisher
import MySQLdb

class Countermeasure:

    def __init__(self):
        self.id = 0
        self.IDRef = ''
        self.Name = ''
        self.Description = ''
        self.Totally_Restrictive = ''
        self.FK_Equipment = None
        self.db = DBConn.DBConn()

    #-------------------------------------------------------------------------------------------------------
    def create(self):
        """Create a new registry"""
        query = "INSERT INTO Countermeasure (IDRef, Name, Description, Totally_Restrictive, FK_Equipment) VALUES (%s, %s, %s, %s, %s)"
        values = (self.IDRef, self.Name, self.Description, self.Totally_Restrictive, self.FK_Equipment)

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

        Publisher.sendMessage("countermeasure_created", None)
        return 0

    #-------------------------------------------------------------------------------------------------------
    def update(self):
        """Update an existing register"""
        query = "UPDATE Countermeasure SET IDRef = %s, Name = %s, Description = %s, Totally_Restrictive = %s WHERE idCountermeasure = %s"
        values = (self.IDRef, self.Name, self.Description, self.Totally_Restrictive, self.id)
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

        Publisher.sendMessage("countermeasure_updated", None)
        return 0, result

    #-------------------------------------------------------------------------------------------------------
    def assignEquipment(self):
        """Update an existing register"""
        query = "UPDATE Countermeasure SET FK_Equipment = %s WHERE idCountermeasure = %s"
        values = (self.FK_Equipment, self.id)
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

        Publisher.sendMessage("countermeasure_equipment_added", None)
        return 0, result

    #-------------------------------------------------------------------------------------------------------
    def removeEquipment(self):
        """Update an existing register"""
        query = "UPDATE Countermeasure SET FK_Equipment = NULL WHERE (FK_Equipment = %s AND idCountermeasure = %s)"
        values = (self.FK_Equipment, self.id)
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

        Publisher.sendMessage("countermeasure_equipment_removed", None)
        return 0, result

    #-------------------------------------------------------------------------------------------------------
    def read_all(self):
        """Read all rows"""
        query = "SELECT idCountermeasure, Name, Description, Totally_Restrictive, FK_Equipment, IDRef FROM Countermeasure"
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
        query = "SELECT idCountermeasure, Name, Description, Totally_Restrictive, FK_Equipment, IDRef FROM Countermeasure WHERE idCountermeasure = %s"
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
    def readByEquipment(self):
        query = "SELECT idCountermeasure, Name, Description, Totally_Restrictive, FK_Equipment, IDRef FROM Countermeasure WHERE FK_Equipment = %s"
        values = (self.FK_Equipment)

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
        #query = "DELETE FROM Countermeasure WHERE idCountermeasure = %s"
        query1 = "DELETE a.*, b.* FROM Countermeasure a LEFT JOIN Restriction b ON b.Restriction = a.idCountermeasure WHERE a.idCountermeasure = %s"
        values = self.id

        try:
            result = self.db.execute(query1, values)

        except MySQLdb.Error, e:
            try:
                error = "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
                print error
                return 1, error
            except IndexError:
                error = "MySQL Error: %s" % str(e)
                print error
                return 1, error

        Publisher.sendMessage("countermeasure_deleted", None)
        return 0, result