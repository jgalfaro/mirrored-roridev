__author__ = 'ender_al'
# -*- coding: utf-8 *-*

import lib.db_conn as DBConn
from wx.lib.pubsub import Publisher
import MySQLdb


class ARC:
    def __init__(self):
        self.id = 0
        self.COI = 0
        self.COM = 0
        self.ODC = 0
        self.IC = 0
        self.Total = 0
        self.FK_Countermeasure = 0
        self.db = DBConn.DBConn()

    #-------------------------------------------------------------------------------------------------------
    def create(self):
        """Create a new registry"""
        query = "INSERT INTO ARC (COI, COM, ODC, IC, Total, FK_Countermeasure) VALUES (%s, %s, %s, %s, %s, %s)"
        values = (
            self.COI,
            self.COM,
            self.ODC,
            self.IC,
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

        Publisher.sendMessage("arc_created", None)
        return 0

    #-------------------------------------------------------------------------------------------------------
    def update(self):
        """Update an existing register"""
        query = "UPDATE ARC SET COI = %s, COM = %s, ODC = %s, IC = %s, Total = %s, FK_Countermeasure = %s WHERE idARC = %s"

        values = (
            self.COI,
            self.COM,
            self.ODC,
            self.IC,
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

        Publisher.sendMessage("arc_updated", None)
        return 0, result

    #-------------------------------------------------------------------------------------------------------
    def read_all(self):
        """Read all rows"""
        query = "SELECT idARC, COI, COM, ODC, IC, Total, FK_Countermeasure FROM ARC"
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
        query = "SELECT idARC, COI, COM, ODC, IC, Total, FK_Countermeasure FROM ARC WHERE idARC = %s"
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
        query = "SELECT idARC, COI, COM, ODC, IC, Total, FK_Countermeasure FROM ARC WHERE FK_Countermeasure = %s"
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
        query = "DELETE FROM ARC WHERE idARC = %s"
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

        Publisher.sendMessage("arc_deleted", None)
        return 0, result