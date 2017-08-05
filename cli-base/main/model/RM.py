__author__ = 'ender_al'
# -*- coding: utf-8 *-*

import lib.db_conn as DBConn
from wx.lib.pubsub import Publisher
import MySQLdb


class RM:
    def __init__(self):
        self.id = 0
        self.EF = 0
        self.COV = 0
        self.Total = 0
        self.FK_Countermeasure = 0
        self.db = DBConn.DBConn()

    #-------------------------------------------------------------------------------------------------------
    def create(self, publish):
        """Create a new registry"""
        query = "INSERT INTO RM (EF, COV, Total, FK_Countermeasure) VALUES (%s, %s, %s, %s)"
        values = (
            self.EF,
            self.COV,
            self.Total,
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
        if publish:
            Publisher.sendMessage("rm_created", None)
        return 0

    #-------------------------------------------------------------------------------------------------------
    def update(self,publish):
        """Update an existing register"""
        query = "UPDATE RM SET EF = %s, COV = %s, Total = %s, FK_Countermeasure = %s WHERE idRM = %s"

        values = (
            self.EF,
            self.COV,
            self.Total,
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

        if publish:
            Publisher.sendMessage("rm_updated", None)
        return 0, result

    #-------------------------------------------------------------------------------------------------------
    def read_all(self):
        """Read all rows"""
        query = "SELECT idRM, EF, COV, Total, FK_Countermeasure FROM RM"
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
        query = "SELECT idRM, EF, COV, Total, FK_Countermeasure FROM RM WHERE idRM = %s"
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
        return 0, result

    #-------------------------------------------------------------------------------------------------------
    def read_by_countermeasure(self):
        query = "SELECT idRM, EF, COV, Total, FK_Countermeasure FROM RM WHERE FK_Countermeasure = %s"
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
        return 0, result

    #-------------------------------------------------------------------------------------------------------
    def delete(self):
        """Delete one or all rows"""
        query = "DELETE FROM RM WHERE idRM = %s"
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

        Publisher.sendMessage("rm_deleted", None)
        return 0, result

    #-------------------------------------------------------------------------------------------------------
    def delete_by_countermeasure(self):
        """Delete one or all rows"""
        query = "DELETE FROM RM WHERE FK_Countermeasure = %s"
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

        Publisher.sendMessage("rm_deleted", None)
        return 0, result