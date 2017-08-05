__author__ = 'ender_al'
# -*- coding: utf-8 *-*

import lib.db_conn as DBConn
from wx.lib.pubsub import Publisher
import MySQLdb


class ALE:
    def __init__(self):
        self.id = 0
        self.LA = 0
        self.LD = 0
        self.LR = 0
        self.LP = 0
        self.LREC = 0
        self.LRPC = 0
        self.OL = 0
        self.CI = 0
        self.ARO = 0
        self.Total = 0
        self.FK_Incident = 0
        self.FK_Organization = 0
        self.db = DBConn.DBConn()

    #-------------------------------------------------------------------------------------------------------
    def create(self):
        """Create a new registry"""
        query = "INSERT INTO ALE (LA, LD, LR, LP, LREC, LRPC, OL, CI, ARO, Total, FK_Incident, FK_Organization) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        values = (
            self.LA,
            self.LD,
            self.LR,
            self.LP,
            self.LREC,
            self.LRPC,
            self.OL,
            self.CI,
            self.ARO,
            self.Total,
            self.FK_Incident,
            self.FK_Organization)

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

        Publisher.sendMessage("ale_created", None)
        return 0

    #-------------------------------------------------------------------------------------------------------
    def update(self):
        """Update an existing register"""
        query = "UPDATE ALE SET LA = %s, LD = %s, LR = %s, LP = %s, LREC = %s, LRPC = %s, OL = %s, CI = %s, ARO = %s, Total = %s, FK_Incident = %s, FK_Organization = %s WHERE idALE = %s"

        values = (
            self.LA,
            self.LD,
            self.LR,
            self.LP,
            self.LREC,
            self.LRPC,
            self.OL,
            self.CI,
            self.ARO,
            self.Total,
            self.FK_Incident,
            self.FK_Organization, self.id)

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

        Publisher.sendMessage("ale_updated", None)
        return 0, result

    #-------------------------------------------------------------------------------------------------------
    def read_all(self):
        """Read all rows"""
        query = "SELECT idALE, LA, LD, LR, LP, LREC, LRPC, OL, CI, ARO, Total, FK_Incident, FK_Organization FROM ALE"
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
        query = "SELECT idALE, LA, LD, LR, LP, LREC, LRPC, OL, CI, ARO, Total, FK_Incident, FK_Organization FROM ALE WHERE idALE = %s"
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
    def read_by_incident(self):
        query = "SELECT idALE, LA, LD, LR, LP, LREC, LRPC, OL, CI, ARO, Total, FK_Incident, FK_Organization FROM ALE WHERE FK_Incident = %s"
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
    def read_by_organization(self):
        query = "SELECT idALE, LA, LD, LR, LP, LREC, LRPC, OL, CI, ARO, Total, FK_Incident, FK_Organization FROM ALE WHERE FK_Organization = %s"
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
    def read_by_incident_organization(self):
        query = "SELECT idALE, LA, LD, LR, LP, LREC, LRPC, OL, CI, ARO, Total, FK_Incident, FK_Organization FROM ALE WHERE FK_Incident = %s AND FK_Organization = %s"
        values = (self.FK_Incident, self.FK_Organization)

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
        query = "DELETE FROM ALE WHERE idALE = %s"
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

        Publisher.sendMessage("ale_deleted", None)
        return 0, result

    #-------------------------------------------------------------------------------------------------------
    def delete_by_organization_incident(self):
        """Delete one or all rows"""
        query = "DELETE FROM ALE WHERE FK_Organization = %s AND FK_Incident = %s"
        values = (self.FK_Organization, self.FK_Incident)

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

        Publisher.sendMessage("ale_deleted", None)
        return 0, result