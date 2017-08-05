__author__ = 'ender_al'
# -*- coding: utf-8 *-*

import lib.db_conn as DBConn
from wx.lib.pubsub import Publisher
import MySQLdb


class Restriction:
    def __init__(self):
        self.id = 0
        self.Restriction = 0
        self.FK_Countermeasure = 0
        self.db = DBConn.DBConn()

    #-------------------------------------------------------------------------------------------------------
    def create(self):
        """Create a new registry"""
        query = "INSERT INTO Restriction (Restriction, FK_Countermeasure) VALUES (%s, %s)"
        values = (
            self.Restriction,
            self.FK_Countermeasure)

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

        Publisher.sendMessage("restriction_created", None)
        return 0

    #-------------------------------------------------------------------------------------------------------
    def update(self):
        """Update an existing register"""
        query = "UPDATE Restriction SET Restriction = %s, FK_Countermeasure = %s WHERE idRestriction = %s"

        values = (
            self.Restriction,
            self.FK_Countermeasure, self.id)

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

        Publisher.sendMessage("restriction_updated", None)
        return 0, result

    #-------------------------------------------------------------------------------------------------------
    def read_all(self):
        """Read all rows"""
        query = "SELECT idRestriction, Restriction, FK_Countermeasure FROM Restriction"
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
        query = "SELECT idRestriction, Restriction, FK_Countermeasure FROM Restriction WHERE idRestriction = %s"
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
    def read_by_countermeasure(self):
        query = "SELECT idRestriction, Restriction, FK_Countermeasure FROM Restriction WHERE FK_Countermeasure = %s"
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
    def read_by_restriction_countermeasure(self):
        query = "SELECT idRestriction, Restriction, FK_Countermeasure FROM Restriction WHERE (Restriction = %s AND FK_Countermeasure = %s)"
        values = (self.Restriction, self.FK_Countermeasure)

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
        query = "DELETE FROM Restriction WHERE idRestriction = %s"
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

        Publisher.sendMessage("restriction_deleted", None)
        return 0, result

    #-------------------------------------------------------------------------------------------------------
    def delete_by_countermeasure(self):
        """Delete one or all rows"""
        query = "DELETE FROM Restriction WHERE FK_Countermeasure = %s"
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

        Publisher.sendMessage("restriction_deleted", None)
        return 0, result
