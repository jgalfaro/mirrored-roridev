__author__ = 'ender_al'
# -*- coding: utf-8 *-*
import lib.db_conn as DBConn
from wx.lib.pubsub import Publisher
import MySQLdb

class AIV:
    def __init__(self):
        self.id = 0
        self.EC = 0
        self.SC = 0
        self.PC = 0
        self.RV = 0
        self.OC = 0
        self.Total = 0
        self.FK_Organization = 0
        self.FK_Equipment = 0
        self.db = DBConn.DBConn()

    #-------------------------------------------------------------------------------------------------------
    def create(self):
        """Create a new registry"""
        query = "INSERT INTO AIV (EC, SC, PC, RV, OC, Total, FK_Organization, FK_Equipment) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        values = (
            self.EC,
            self.SC,
            self.PC,
            self.RV,
            self.OC,
            self.Total,
            self.FK_Organization,
            self.FK_Equipment)

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

        Publisher.sendMessage("aiv_created", None)
        return 0

    #-------------------------------------------------------------------------------------------------------
    def update(self):
        """Update an existing register"""
        query = "UPDATE AIV SET EC = %s, SC = %s, PC = %s, RV = %s, OC = %s, Total = %s, FK_Organization = %s, FK_Equipment = %s  WHERE idAIV = %s"

        values = (
            self.EC,
            self.SC,
            self.PC,
            self.RV,
            self.OC,
            self.Total,
            self.FK_Organization,
            self.FK_Equipment, self.id)

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

        Publisher.sendMessage("aiv_updated", None)
        return 0, result

    #-------------------------------------------------------------------------------------------------------
    def read_all(self):
        """Read all rows"""
        query = "SELECT idAIV, EC, SC, PC, RV, OC, Total, FK_Organization, FK_Equipment FROM AIV"
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
        query = "SELECT idAIV, EC, SC, PC, RV, OC, Total, FK_Organization, FK_Equipment FROM AIV WHERE idAIV = %s"
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
    def read_by_equipment(self):
        query = "SELECT idAIV, EC, SC, PC, RV, OC, Total, FK_Organization, FK_Equipment FROM AIV WHERE FK_Equipment = %s"
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
    def read_by_organization(self):
        query = "SELECT idAIV, EC, SC, PC, RV, OC, Total, FK_Organization, FK_Equipment FROM AIV WHERE FK_Organization = %s"
        values = (self.FK_Organization)

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
    def read_by_equipment_organization(self):
        query = "SELECT idAIV, EC, SC, PC, RV, OC, Total, FK_Organization, FK_Equipment FROM AIV WHERE FK_Equipment = %s AND FK_Organization = %s"
        values = (self.FK_Equipment, self.FK_Organization)

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
        query = "DELETE FROM AIV WHERE idAIV = %s"
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

        Publisher.sendMessage("aiv_deleted", None)
        return 0, result

    #-------------------------------------------------------------------------------------------------------
    def delete_by_organization_equipment(self):
        """Delete one or all rows"""
        query = "DELETE FROM AIV WHERE FK_Organization = %s AND FK_Equipment = %s"
        values = (self.FK_Organization, self.FK_Equipment)

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

        Publisher.sendMessage("aiv_deleted", None)
        return 0, result