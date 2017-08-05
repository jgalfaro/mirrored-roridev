__author__ = 'ender_al'
# -*- coding: utf-8 *-*
import lib.db_conn as DBConn
from wx.lib.pubsub import Publisher
import MySQLdb

class AEV:
    def __init__(self):
        self.id = 0
        self.EC = 0
        self.SC = 0
        self.PC = 0
        self.RV = 0
        self.OC = 0
        self.NEquipments = 0
        self.Total = 0
        self.FK_Organization = 0
        self.FK_Equipment = 0
        self.db = DBConn.DBConn()

    #-------------------------------------------------------------------------------------------------------
    def create(self):
        """Create a new registry"""
        query = "INSERT INTO AEV (EC, SC, PC, RV, OC, NEquipments, Total, FK_Organization, FK_Equipment) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        values = (
            self.EC,
            self.SC,
            self.PC,
            self.RV,
            self.OC,
            self.NEquipments,
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

        Publisher.sendMessage("aev_created", None)
        return 0

    #-------------------------------------------------------------------------------------------------------
    def update(self):
        """Update an existing register"""
        query = "UPDATE AEV SET EC = %s, SC = %s, PC = %s, RV = %s, OC = %s, NEquipments = %s,Total = %s, FK_Organization = %s, FK_Equipment = %s  WHERE idAEV = %s"

        values = (
            self.EC,
            self.SC,
            self.PC,
            self.RV,
            self.OC,
            self.NEquipments,
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

        Publisher.sendMessage("aev_updated", None)
        return 0, result

    #-------------------------------------------------------------------------------------------------------
    def read_all(self):
        """Read all rows"""
        query = "SELECT idAEV, EC, SC, PC, RV, OC, NEquipments, Total, FK_Organization, FK_Equipment FROM AEV"
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
        query = "SELECT idAEV, EC, SC, PC, RV, OC, NEquipments, Total, FK_Organization, FK_Equipment FROM AEV WHERE idAEV = %s"
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
        query = "SELECT idAEV, EC, SC, PC, RV, OC, NEquipments, Total, FK_Organization, FK_Equipment FROM AEV WHERE FK_Equipment = %s"
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
        query = "SELECT idAEV, EC, SC, PC, RV, OC, NEquipments, Total, FK_Organization, FK_Equipment FROM AEV WHERE FK_Organization = %s"
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
        query = "SELECT idAEV, EC, SC, PC, RV, OC, NEquipments, Total, FK_Organization, FK_Equipment FROM AEV WHERE FK_Equipment = %s AND FK_Organization = %s"
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
        query = "DELETE FROM AEV WHERE idAEV = %s"
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

        Publisher.sendMessage("aev_deleted", None)
        return 0, result

    #-------------------------------------------------------------------------------------------------------
    def delete_by_organization_equipment(self):
        """Delete one or all rows"""
        query = "DELETE FROM AEV WHERE FK_Organization = %s AND FK_Equipment = %s"
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

        Publisher.sendMessage("aev_deleted", None)
        return 0, result