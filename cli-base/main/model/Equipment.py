__author__ = 'ender_al'
# -*- coding: utf-8 *-*
import lib.db_conn as DBConn
from wx.lib.pubsub import Publisher
import MySQLdb

class Equipment:

    def __init__(self):
        self.id = 0
        self.IDRef = ''
        self.Name = ''
        self.Type = ''
        self.db = DBConn.DBConn()

    #-------------------------------------------------------------------------------------------------------
    def create(self):
        """Create a new registry"""
        query = "INSERT INTO Equipment (IDRef, Name, Type) VALUES (%s, %s, %s)"
        values = (self.IDRef, self.Name, self.Type)

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

        Publisher.sendMessage("equipment_created", None)
        return 0

    #-------------------------------------------------------------------------------------------------------
    def update(self):
        """Update an existing register"""
        query = "UPDATE Equipment SET IDRef = %s, Name = %s, Type = %s WHERE idEquipment = %s"
        values = (self.IDRef, self.Name, self.Type, self.id)
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

        Publisher.sendMessage("equipment_updated", None)
        return 0, result

    #-------------------------------------------------------------------------------------------------------
    def read_all(self):
        """Read all rows"""
        query = "SELECT idEquipment, Name, Type, IDRef FROM Equipment"
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
        query = "SELECT idEquipment, Name, Type, IDRef FROM Equipment WHERE idEquipment = %s"
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
    def delete(self):
        """Delete one or all rows"""
        query = "DELETE FROM Equipment WHERE idEquipment = %s"
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

        Publisher.sendMessage("equipment_deleted", None)
        return 0, result